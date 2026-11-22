import io
import uuid
import hashlib
from PIL import Image
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.agents.graph import get_caption_workflow
from app.agents.router import get_rag_memory
from app.agents.translation import translate_caption
from app.tracking.mlflow_tracker import CaptionTracker
from app.tracking import local_tracker
from app.vqa.conversation import VQAConversation
from app.styles.prompts import AVAILABLE_STYLES
from app.config import settings

app = FastAPI(
    title="IMG Caption - Multi-Agent Image Captioning Platform",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

tracker = CaptionTracker()
vqa_engine = VQAConversation()


class CaptionResponse(BaseModel):
    caption: str
    model_used: str
    tier: int
    clip_score: float
    judge_score: int
    latency_ms: float
    cost_usd: float
    escalation_count: int
    history: list[dict]
    refinements: dict = {}
    language: str = "English"
    translated_caption: str = ""
    confidence_score: float = 0.0
    confidence_explanation: str = ""
    complexity_label: str = ""
    detected_objects: list[dict] = []


class VQAResponse(BaseModel):
    answer: str
    tokens_used: int
    history_length: int


class StatsResponse(BaseModel):
    total_runs: int
    avg_cost: float
    avg_latency: float
    avg_clip_score: float = 0.0
    avg_judge_score: float = 0.0
    total_cost: float = 0.0
    avg_escalations: float = 0.0
    model_usage: dict = {}
    style_usage: dict = {}
    tier_usage: dict = {}
    recent_runs: list = []


@app.get("/")
def root():
    return {
        "message": "IMG Caption - Multi-Agent Image Captioning Platform",
        "endpoints": ["/caption", "/caption/compare", "/vqa", "/stats"],
        "styles": AVAILABLE_STYLES,
        "languages": settings.available_languages,
    }


@app.post("/caption", response_model=CaptionResponse)
async def generate_caption(
    image: UploadFile = File(...),
    style: str = Form("descriptive"),
    language: str = Form("English"),
):
    if style not in AVAILABLE_STYLES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid style. Choose from: {AVAILABLE_STYLES}",
        )

    image_bytes = await image.read()
    pil_image = Image.open(io.BytesIO(image_bytes))
    image_hash = hashlib.md5(image_bytes).hexdigest()

    workflow = get_caption_workflow()
    result = workflow.invoke(
        {
            "image": pil_image,
            "image_bytes": image_bytes,
            "style": style,
        },
        {"recursion_limit": 25}
    )

    critic = result.get("critic_result", {})
    clip_score = critic.get("clip_score", 0.0)
    judge_scores = critic.get("judge_scores", {})
    judge_score = judge_scores.get("overall", 0)
    history = result.get("history", [])
    final_tier = history[-1]["tier"] if history else 1
    final_model = history[-1]["model"] if history else "unknown"
    caption = result.get("caption", "")

    translated = translate_caption(caption, language)

    rag = get_rag_memory()
    rag.add_caption(
        image_hash=image_hash,
        caption=caption,
        style=style,
        model_name=final_model,
        clip_score=clip_score,
        image=pil_image,
    )

    tracker.log_caption_run(
        model_name=final_model,
        style=style,
        caption=caption,
        clip_score=clip_score,
        judge_score=judge_score,
        latency_ms=result.get("total_latency", 0),
        cost_usd=result.get("total_cost", 0),
        escalation_count=result.get("escalation_count", 0),
        tier_used=final_tier,
        image_hash=image_hash,
    )

    return CaptionResponse(
        caption=caption,
        model_used=final_model,
        tier=final_tier,
        clip_score=clip_score,
        judge_score=judge_score,
        latency_ms=result.get("total_latency", 0),
        cost_usd=result.get("total_cost", 0),
        escalation_count=result.get("escalation_count", 0),
        history=history,
        refinements=result.get("refinements", {}),
        language=language,
        translated_caption=translated if language != "English" else "",
        confidence_score=result.get("confidence_score", 0.0),
        confidence_explanation=result.get("confidence_explanation", ""),
        complexity_label=result.get("complexity_label", ""),
        detected_objects=result.get("detected_objects", []),
    )


@app.post("/caption/compare")
async def compare_captions(image: UploadFile = File(...)):
    image_bytes = await image.read()
    pil_image = Image.open(io.BytesIO(image_bytes))

    results = {}
    workflow = get_caption_workflow()

    for style in AVAILABLE_STYLES:
        result = workflow.invoke(
            {
                "image": pil_image,
                "image_bytes": image_bytes,
                "style": style,
            },
            {"recursion_limit": 25}
        )

        critic = result.get("critic_result", {})
        history = result.get("history", [])
        final_model = history[-1]["model"] if history else "unknown"

        results[style] = {
            "caption": result["caption"],
            "model_used": final_model,
            "clip_score": critic.get("clip_score", 0),
            "judge_score": critic.get("judge_scores", {}).get("overall", 0),
            "cost_usd": result.get("total_cost", 0),
            "latency_ms": result.get("total_latency", 0),
        }

    return {"styles": results}


@app.post("/vqa", response_model=VQAResponse)
async def visual_qa(
    image: UploadFile = File(...),
    question: str = Form(...),
    session_id: str = Form(None),
):
    if not session_id:
        session_id = str(uuid.uuid4())

    image_bytes = await image.read()
    pil_image = Image.open(io.BytesIO(image_bytes))

    result = vqa_engine.ask(session_id, pil_image, question)

    return VQAResponse(**result)


@app.get("/health")
def health():
    return {
        "has_openai": settings.has_openai,
        "blip_ready": True,
        "faiss_memory": True,
        "version": "2.0",
    }


@app.get("/stats", response_model=StatsResponse)
def get_stats():
    stats = local_tracker.get_stats()
    return StatsResponse(**stats)


@app.get("/styles")
def get_styles():
    return {"styles": AVAILABLE_STYLES}


@app.get("/languages")
def get_languages():
    return {"languages": settings.available_languages}
