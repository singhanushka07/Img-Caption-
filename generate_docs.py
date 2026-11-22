"""
Generate 3 PDF documentation files for the IMG Caption Platform.
Run: python generate_docs.py
Output: docs/ folder
"""
from fpdf import FPDF
import os

os.makedirs("docs", exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# Base PDF class with consistent styling
# ─────────────────────────────────────────────────────────────────────────────

def _s(text: str) -> str:
    """Sanitise text to latin-1 safe characters."""
    return (text
        .replace("—", "--")   # em dash
        .replace("–", "-")    # en dash
        .replace("’", "'")    # right single quote
        .replace("‘", "'")    # left single quote
        .replace("“", '"')    # left double quote
        .replace("”", '"')    # right double quote
        .replace("•", "*")    # bullet
        .replace("●", "*")    # filled circle
        .replace("○", "o")    # empty circle
        .replace("◦", "o")    # open circle
        .replace("→", "->")   # right arrow
        .replace("←", "<-")   # left arrow
        .replace("·", ".")    # middle dot
        .encode("latin-1", errors="replace").decode("latin-1")
    )


class DocPDF(FPDF):
    def __init__(self, title=""):
        super().__init__()
        self.doc_title = title
        self.set_margins(20, 20, 20)
        self.set_auto_page_break(auto=True, margin=22)

    # Auto-sanitise all text output
    def cell(self, *args, **kwargs):
        args = tuple(_s(a) if isinstance(a, str) else a for a in args)
        kwargs = {k: _s(v) if isinstance(v, str) else v for k, v in kwargs.items()}
        return super().cell(*args, **kwargs)

    def multi_cell(self, *args, **kwargs):
        args = tuple(_s(a) if isinstance(a, str) else a for a in args)
        kwargs = {k: _s(v) if isinstance(v, str) else v for k, v in kwargs.items()}
        return super().multi_cell(*args, **kwargs)

    def header(self):
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(120, 120, 140)
        super().cell(0, 8, _s(self.doc_title), align="L")
        self.set_font("Helvetica", "", 8)
        super().cell(0, 8, f"Page {self.page_no()}", align="R", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(60, 60, 80)
        self.line(20, 18, 190, 18)
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(120, 120, 140)
        self.cell(0, 10, "IMG Caption Platform  |  Nexus Vision v2.0  |  Multi-Agent AI System", align="C")

    def cover(self, num: str, title: str, subtitle: str):
        self.add_page()
        self.ln(30)
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(100, 100, 200)
        super().cell(0, 10, _s(f"DOCUMENT {num}"), align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(6)
        self.set_font("Helvetica", "B", 26)
        self.set_text_color(20, 20, 40)
        self.set_x(self.l_margin)
        super().multi_cell(170, 12, _s(title), align="C")
        self.ln(6)
        self.set_font("Helvetica", "", 12)
        self.set_text_color(80, 80, 110)
        self.set_x(self.l_margin)
        super().multi_cell(170, 8, _s(subtitle), align="C")
        self.ln(20)
        self.set_draw_color(100, 100, 200)
        self.set_line_width(0.5)
        self.line(50, self.get_y(), 160, self.get_y())
        self.ln(20)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(120, 120, 140)
        super().cell(0, 8, "IMG Caption Platform -- Nexus Vision v2.0", align="C", new_x="LMARGIN", new_y="NEXT")
        super().cell(0, 8, "Multi-Agent Agentic AI  |  LangGraph  |  BLIP  |  FAISS  |  GPT-4o", align="C")

    def h1(self, text: str):
        self.ln(6)
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(30, 30, 80)
        self.set_x(self.l_margin)
        super().multi_cell(170, 9, _s(text))
        self.set_draw_color(100, 100, 200)
        self.set_line_width(0.4)
        self.line(20, self.get_y(), 190, self.get_y())
        self.ln(4)

    def h2(self, text: str):
        self.ln(4)
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(50, 50, 130)
        self.set_x(self.l_margin)
        super().multi_cell(170, 8, _s(text))
        self.ln(1)

    def h3(self, text: str):
        self.ln(2)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(80, 80, 160)
        self.set_x(self.l_margin)
        super().multi_cell(170, 7, _s(text))

    def body(self, text: str):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 60)
        self.set_x(self.l_margin)
        super().multi_cell(170, 6, _s(text))
        self.ln(1)

    def bullet(self, text: str, indent: int = 6):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 60)
        x = self.l_margin + indent
        self.set_x(x)
        super().multi_cell(170 - indent, 6, _s(f"  *  {text}"))

    def sub_bullet(self, text: str):
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(70, 70, 90)
        self.set_x(self.l_margin + 10)
        super().multi_cell(160, 6, _s(f"      o  {text}"))

    def code(self, text: str):
        self.set_font("Courier", "", 8.5)
        self.set_fill_color(240, 240, 248)
        self.set_text_color(40, 40, 100)
        self.set_x(self.l_margin + 4)
        super().multi_cell(166, 5.5, _s(text), fill=True)
        self.ln(1)

    def tag(self, label: str, value: str):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(80, 80, 160)
        super().cell(38, 6, _s(f"{label}:"), new_x="RIGHT", new_y="TOP")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(40, 40, 60)
        super().multi_cell(132, 6, _s(value))
        self.ln(0)

    def qa_q(self, text: str):
        self.ln(3)
        self.set_fill_color(235, 235, 255)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(30, 30, 100)
        self.set_x(self.l_margin)
        super().multi_cell(170, 7, _s(f"Q:  {text}"), fill=True)

    def qa_a(self, text: str):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 60)
        self.set_x(self.l_margin + 4)
        super().multi_cell(166, 6, _s(f"A:  {text}"))
        self.ln(1)

    def info_box(self, text: str):
        self.set_fill_color(230, 240, 255)
        self.set_draw_color(100, 130, 220)
        self.set_font("Helvetica", "I", 9.5)
        self.set_text_color(40, 60, 120)
        self.set_x(self.l_margin)
        super().multi_cell(170, 6, _s(text), fill=True, border=1)
        self.ln(2)

    def warn_box(self, text: str):
        self.set_fill_color(255, 248, 225)
        self.set_draw_color(200, 160, 50)
        self.set_font("Helvetica", "I", 9.5)
        self.set_text_color(100, 70, 10)
        self.set_x(self.l_margin)
        super().multi_cell(170, 6, _s(text), fill=True, border=1)
        self.ln(2)


# =============================================================================
# PDF 1 — TECH STACK
# =============================================================================

def make_pdf1():
    pdf = DocPDF("IMG Caption Platform  |  PDF 1: Tech Stack & Architecture")
    pdf.cover("01", "Tech Stack & Architecture", "Every technology, library, and framework used\nin the IMG Caption Platform — what it is and what it does.")

    # ── 1. System Overview ───────────────────────────────────────────────────
    pdf.add_page()
    pdf.h1("1. System Overview")
    pdf.body(
        "The IMG Caption Platform is a production-grade multi-agent AI system that "
        "generates high-quality image captions using a 3-tier model routing strategy. "
        "It combines local vision models, cloud LLMs, semantic memory, and dual-gate "
        "quality control into a single cohesive pipeline exposed via both a Gradio web "
        "UI and a FastAPI REST API."
    )
    pdf.ln(2)
    pdf.h2("Architecture Layers")
    layers = [
        ("Presentation Layer", "Gradio 6.0 web UI (5 pages) + FastAPI REST endpoints"),
        ("Orchestration Layer", "LangGraph StateGraph — routes, generates, critiques, escalates"),
        ("Model Layer",         "BLIP (local) / GPT-4o-mini (Tier 2) / GPT-4o (Tier 3)"),
        ("Memory Layer",        "FAISS vector store + SentenceTransformer embeddings"),
        ("Quality Layer",       "CLIPScore (cosine sim) + LLM-as-Judge (GPT-4o-mini)"),
        ("Tracking Layer",      "Local JSONL tracker + optional MLflow experiment logging"),
        ("Config Layer",        "Pydantic Settings with .env file support"),
    ]
    for name, desc in layers:
        pdf.tag(name, desc)
    pdf.ln(2)
    pdf.info_box(
        "Entry Points:\n"
        "  run.py      — FastAPI on :8000 (daemon thread) + Gradio on :7860\n"
        "  app.py      — Gradio-only (HuggingFace Spaces compatible)\n"
        "  app/main.py — FastAPI application (REST API)"
    )

    # ── 2. Core AI / ML Stack ────────────────────────────────────────────────
    pdf.add_page()
    pdf.h1("2. Core AI / ML Stack")

    pdf.h2("2.1  BLIP — Bootstrapping Language-Image Pre-training")
    pdf.tag("Library",  "transformers (Hugging Face)")
    pdf.tag("Model",    "Salesforce/blip-image-captioning-large")
    pdf.tag("Type",     "Vision-Language Model (encoder-decoder)")
    pdf.tag("Tier",     "1 — local, free, no API key required")
    pdf.tag("File",     "app/models/blip_model.py")
    pdf.ln(1)
    pdf.body(
        "BLIP is a vision-language model pre-trained by Salesforce that can generate "
        "natural language descriptions of images. It uses a visual encoder (ViT) and a "
        "text decoder (BERT-style). The platform loads it as a singleton to avoid "
        "repeated model loading (~1.8 GB). It runs fully offline — no API key needed. "
        "BLIP processes the image and optionally incorporates a style prompt and RAG "
        "context to produce the initial caption."
    )
    pdf.bullet("Singleton pattern: loaded once, reused across all requests")
    pdf.bullet("Runs on CPU by default; MPS/CUDA used if available (auto-detect)")
    pdf.bullet("Generation config: max_new_tokens=200, num_beams=4, temperature=1.0")

    pdf.h2("2.2  GPT-4o-mini — Tier 2 Vision LLM")
    pdf.tag("Provider", "OpenAI API")
    pdf.tag("Model",    "gpt-4o-mini")
    pdf.tag("Tier",     "2 — cloud, requires OPENAI_API_KEY")
    pdf.tag("File",     "app/models/openai_model.py")
    pdf.ln(1)
    pdf.body(
        "GPT-4o-mini is OpenAI's small, fast multimodal model. When the Tier-1 BLIP "
        "caption fails the quality gates, the pipeline escalates to GPT-4o-mini. It "
        "receives the image as a base64-encoded JPEG at 'low' detail level (to reduce "
        "token costs), along with a style prompt and optional RAG context."
    )
    pdf.bullet("Pricing: $0.15/M input tokens, $0.60/M output tokens")
    pdf.bullet("Image detail: 'low' (saves tokens vs high)")
    pdf.bullet("max_tokens=300, temperature=0.7")

    pdf.h2("2.3  GPT-4o — Tier 3 Vision LLM")
    pdf.tag("Provider", "OpenAI API")
    pdf.tag("Model",    "gpt-4o")
    pdf.tag("Tier",     "3 — cloud, highest quality, highest cost")
    pdf.tag("File",     "app/models/openai_model.py")
    pdf.ln(1)
    pdf.body(
        "GPT-4o is OpenAI's flagship multimodal model. It is only invoked when both "
        "Tier-1 and Tier-2 captions fail the quality critic. It receives the image at "
        "'high' detail level for maximum accuracy. As the final tier, its output is "
        "always accepted regardless of quality score."
    )
    pdf.bullet("Pricing: $2.50/M input tokens, $10.00/M output tokens")
    pdf.bullet("Image detail: 'high' (full resolution patches)")
    pdf.bullet("Always accepted — stops escalation loop")

    pdf.h2("2.4  CLIP — Contrastive Language-Image Pre-training")
    pdf.tag("Library",  "transformers + torch")
    pdf.tag("Model",    "openai/clip-vit-base-patch32")
    pdf.tag("Purpose",  "CLIPScore quality gate")
    pdf.tag("File",     "app/agents/critic_agent.py")
    pdf.ln(1)
    pdf.body(
        "CLIP is used as the first quality gate to measure semantic alignment between "
        "the generated caption and the image. The platform encodes both the image and "
        "the caption text into the CLIP embedding space, then computes cosine similarity. "
        "A score above the configured threshold (default 0.2) means the caption is "
        "semantically aligned with the image."
    )
    pdf.bullet("Runs locally, no API call required")
    pdf.bullet("Singleton class variable — shared across all CriticAgent instances")
    pdf.bullet("torch.no_grad() used for inference efficiency")
    pdf.bullet("Fallback: returns 0.0 on any exception (never crashes)")

    pdf.h2("2.5  SentenceTransformer — RAG Embeddings")
    pdf.tag("Library",  "sentence-transformers")
    pdf.tag("Model",    "all-MiniLM-L6-v2")
    pdf.tag("Purpose",  "Encode captions into vectors for FAISS retrieval")
    pdf.tag("File",     "app/rag/memory.py")
    pdf.ln(1)
    pdf.body(
        "SentenceTransformer encodes text (captions) into dense 384-dimensional vectors. "
        "These vectors are stored in the FAISS index and used to retrieve semantically "
        "similar past captions when a new image is processed. This provides contextual "
        "grounding for the caption generation prompts."
    )
    pdf.bullet("384-dimension output embeddings")
    pdf.bullet("Lightweight: ~80MB, fast CPU inference")

    pdf.h2("2.6  OpenCV -- Image Complexity Analysis")
    pdf.tag("Library",  "opencv-python-headless")
    pdf.tag("Purpose",  "Smart routing via image complexity estimation")
    pdf.tag("File",     "app/agents/complexity.py")
    pdf.ln(1)
    pdf.body(
        "OpenCV is used to estimate image complexity before caption generation, enabling "
        "smart routing that skips directly to higher-tier models for complex scenes. "
        "Three metrics are computed: edge density (Canny edge detection), color variance "
        "(HSV standard deviation), and texture richness (Laplacian variance). A weighted "
        "composite score determines the complexity label."
    )
    pdf.bullet("Edge density: cv2.Canny(gray, 100, 200), ratio of edge pixels to total")
    pdf.bullet("Color variance: HSV H+S channel std-dev, normalized to 0-1")
    pdf.bullet("Texture: Laplacian variance, normalized to 0-1")
    pdf.bullet("Composite: edge*0.4 + color*0.3 + texture*0.3")
    pdf.bullet("Labels: simple (<0.3), medium (0.3-0.6), complex (>0.6)")
    pdf.bullet("Routing: simple -> Tier 1, complex -> Tier 2 (if API available)")
    pdf.bullet("Fully offline, pure CPU computation, <10ms per image")

    pdf.h2("2.7  YOLOv8n -- Object Detection Pre-pass")
    pdf.tag("Library",  "ultralytics")
    pdf.tag("Model",    "YOLOv8n (~6MB)")
    pdf.tag("Purpose",  "Detect objects to provide structured context for captioning")
    pdf.tag("File",     "app/agents/object_detector.py")
    pdf.ln(1)
    pdf.body(
        "YOLOv8n (You Only Look Once, nano variant) runs real-time object detection as a "
        "pre-pass before caption generation. Detected objects with labels, confidence scores, "
        "and counts are formatted into a context string (e.g. 'Detected objects: 2 dogs "
        "(0.92), 1 car (0.85)') and passed alongside RAG context to the caption model. "
        "This gives all tiers richer grounding about what is in the image."
    )
    pdf.bullet("Auto-downloads on first use (~6MB), then runs fully offline")
    pdf.bullet("Confidence threshold: 0.3 (configurable via YOLO_CONFIDENCE_THRESHOLD)")
    pdf.bullet("Aggregates by class: count occurrences, keep max confidence per label")
    pdf.bullet("Singleton pattern to avoid reloading model on each request")

    pdf.h2("2.8  CLIP Image Embeddings in RAG")
    pdf.tag("Purpose",  "Visual similarity retrieval alongside semantic text matching")
    pdf.tag("File",     "app/rag/memory.py")
    pdf.ln(1)
    pdf.body(
        "In addition to the SentenceTransformer text embeddings, the RAG memory now stores "
        "CLIP image embeddings in a second FAISS index. When retrieving similar past captions, "
        "both text similarity and visual similarity are blended with a configurable weight "
        "(default: 0.4 image, 0.6 text). This enables finding captions from visually similar "
        "images, not just semantically similar caption text."
    )
    pdf.bullet("Dual FAISS indices: caption_index.faiss (text) + clip_image_index.faiss (image)")
    pdf.bullet("CLIP ViT-B/32 image embeddings (512-dim), reuses the model from CriticAgent")
    pdf.bullet("Combined scoring: text_weight * text_sim + image_weight * image_sim")
    pdf.bullet("Backward compatible: falls back to text-only if CLIP unavailable or index empty")
    pdf.bullet("Weight configurable via CLIP_IMAGE_WEIGHT env var (default 0.4)")

    # ── 3. Orchestration & Pipeline ──────────────────────────────────────────
    pdf.add_page()
    pdf.h1("3. Orchestration & Pipeline")

    pdf.h2("3.1  LangGraph — StateGraph Workflow Engine")
    pdf.tag("Library", "langgraph")
    pdf.tag("File",    "app/agents/graph.py")
    pdf.ln(1)
    pdf.body(
        "LangGraph is a library built on top of LangChain for building stateful, "
        "multi-step AI pipelines as directed graphs. The platform defines a StateGraph "
        "with 6 nodes and conditional edge logic:"
    )
    pdf.code(
        "route_node\n"
        "  |-- RAG retrieval (text + CLIP image) + complexity analysis + tier selection\n"
        "  v\n"
        "detect_objects_node\n"
        "  |-- YOLOv8n object detection pre-pass\n"
        "  v\n"
        "generate_caption_node\n"
        "  |-- BLIP/GPT-4o-mini/GPT-4o based on current_tier\n"
        "  |-- Receives RAG context + object context\n"
        "  v\n"
        "critique_node\n"
        "  |-- CLIPScore + LLM Judge evaluation + confidence scoring\n"
        "  |-- if passes OR tier==3  --> refine_node\n"
        "  |-- if fails AND tier<3   --> escalate_node --> generate_caption_node\n"
        "  v\n"
        "refine_node\n"
        "  |-- Generates alt-text + SEO variants via GPT-4o-mini\n"
        "  v\n"
        "END"
    )
    pdf.bullet("State is a TypedDict (CaptionState) passed between nodes")
    pdf.bullet("Conditional edge: should_escalate() checks passes flag and current tier")
    pdf.bullet("Max escalations: 2 (Tier 1 -> 2 -> 3), then always accept")
    pdf.bullet("New nodes: detect_objects (YOLO pre-pass), refine (alt-text + SEO post-pass)")
    pdf.bullet("Compiled to a runnable: workflow.invoke(state_dict)")

    pdf.h2("3.2  CaptionState — Pipeline State Schema")
    pdf.tag("File", "app/agents/state.py")
    pdf.ln(1)
    pdf.body("TypedDict with total=False (all keys optional). Key fields:")
    fields = [
        ("image",            "PIL.Image.Image -- the input image"),
        ("image_bytes",      "bytes -- JPEG bytes for hashing"),
        ("style",            "str -- one of 5 caption styles"),
        ("rag_context",      "str -- retrieved similar captions from FAISS"),
        ("caption",          "str -- current best caption"),
        ("current_tier",     "int -- 1/2/3, current model tier"),
        ("critic_result",    "dict -- clip_score, judge_scores, passes"),
        ("history",          "list[dict] -- per-tier generation history"),
        ("total_cost",       "float -- cumulative USD cost"),
        ("total_latency",    "float -- cumulative latency in ms"),
        ("escalation_count", "int -- number of tier escalations"),
        ("complexity_score", "float -- 0.0-1.0 image complexity (NEW)"),
        ("complexity_label", "str -- simple/medium/complex (NEW)"),
        ("detected_objects", "list[dict] -- YOLO detections (NEW)"),
        ("object_context",   "str -- formatted detection string (NEW)"),
        ("refinements",      "dict -- alt_text + seo variants (NEW)"),
        ("language",         "str -- target output language (NEW)"),
        ("translated_caption", "str -- translated version (NEW)"),
        ("confidence_score", "float -- 0-100 normalized (NEW)"),
        ("confidence_explanation", "str -- plain English (NEW)"),
    ]
    for k, v in fields:
        pdf.tag(k, v)

    pdf.h2("3.3  Route Node — RAG Context + Tier Init")
    pdf.tag("File", "app/agents/router.py")
    pdf.ln(1)
    pdf.body(
        "The route_node initializes the pipeline state: retrieves the top-k semantically "
        "similar past captions from FAISS memory (if any exist), formats them as a "
        "context string, and sets current_tier=1 to start at BLIP."
    )

    # ── 4. Memory & RAG ──────────────────────────────────────────────────────
    pdf.add_page()
    pdf.h1("4. Memory & Retrieval-Augmented Generation")

    pdf.h2("4.1  FAISS — Facebook AI Similarity Search")
    pdf.tag("Library", "faiss-cpu")
    pdf.tag("Index",   "IndexFlatIP (inner product = cosine sim on normalized vecs)")
    pdf.tag("File",    "app/rag/memory.py")
    pdf.ln(1)
    pdf.body(
        "FAISS is a library by Meta for efficient similarity search over dense vectors. "
        "The platform uses IndexFlatIP (flat inner product index) which is equivalent to "
        "cosine similarity when vectors are L2-normalized. The index is persisted to disk "
        "at ./data/faiss_index/ so memory survives across sessions."
    )
    pdf.bullet("Vectors stored: SentenceTransformer 384-dim caption embeddings")
    pdf.bullet("Persisted: index.faiss + metadata.json")
    pdf.bullet("Retrieval: top-3 similar captions returned as RAG context")
    pdf.bullet("Add: each successful caption is added after generation")
    pdf.bullet("Metadata stored per entry: image_hash, style, model_name, clip_score, timestamp")

    pdf.h2("4.2  RAGMemory Class")
    pdf.tag("File",   "app/rag/memory.py")
    pdf.body(
        "Wraps FAISS + SentenceTransformer into a simple interface. "
        "add_caption() encodes and stores. retrieve_similar() encodes the query "
        "and returns the top-k most similar stored captions. Auto-loads from disk "
        "on startup if index exists."
    )

    # ── 5. Quality Control ───────────────────────────────────────────────────
    pdf.add_page()
    pdf.h1("5. Quality Control System")

    pdf.h2("5.1  Dual-Gate Quality Architecture")
    pdf.body(
        "Every generated caption passes through two independent quality gates before "
        "being accepted or escalating to the next tier:"
    )
    pdf.bullet("Gate 1 — CLIPScore: Vision-language cosine similarity (local, fast)")
    pdf.bullet("Gate 2 — LLM Judge: GPT-4o-mini rates caption 1-10 on 4 criteria")
    pdf.body("Both gates must pass for the caption to be accepted (in online mode).")

    pdf.h2("5.2  CLIPScore (Gate 1)")
    pdf.body(
        "Computes cosine similarity between CLIP image embedding and CLIP text embedding "
        "of the caption. A score >= clip_score_threshold (default: 0.2) passes this gate."
    )
    pdf.tag("Threshold", "0.2 (configurable via CLIP_SCORE_THRESHOLD env var)")
    pdf.tag("Range",     "0.0 to 1.0 (1.0 = perfectly aligned)")
    pdf.tag("Typical",   "0.15-0.35 for decent captions, >0.30 excellent")

    pdf.h2("5.3  LLM-as-Judge (Gate 2)")
    pdf.body(
        "GPT-4o-mini evaluates the caption against the image on 4 criteria using a "
        "structured prompt. Returns numeric scores 1-10 for each:"
    )
    criteria = [
        ("Accuracy",    "How well the caption describes what is visually present"),
        ("Detail",      "Whether the level of detail matches the requested style"),
        ("Style Match", "How well the caption fits the requested style (e.g. creative, technical)"),
        ("Fluency",     "Natural language quality — grammar, flow, readability"),
        ("Overall",     "Composite score — this is the gate threshold check"),
    ]
    for c, d in criteria:
        pdf.tag(c, d)
    pdf.ln(1)
    pdf.tag("Threshold", "7/10 (configurable via LLM_JUDGE_THRESHOLD env var)")
    pdf.body(
        "Fallback when offline: LLM judge is skipped; judge scores default to 7 "
        "(passes). Only CLIP gate is enforced in offline mode."
    )

    # ── 6. Web Framework Stack ───────────────────────────────────────────────
    pdf.add_page()
    pdf.h1("6. Web Framework Stack")

    pdf.h2("6.1  Gradio 6.0 — Web UI")
    pdf.tag("Library",  "gradio >= 6.0")
    pdf.tag("Port",     "7860")
    pdf.tag("File",     "ui/gradio_app.py")
    pdf.ln(1)
    pdf.body(
        "Gradio is a Python library for building ML demo web UIs with minimal code. "
        "Version 6.0 moved css/js/theme parameters from gr.Blocks() to demo.launch(). "
        "The platform builds a 5-tab application using gr.Blocks with custom CSS (sci-fi "
        "Nexus Vision theme), custom JS (overflow fix for sticky nav), and a custom "
        "dark theme via gr.themes.Base."
    )
    pdf.bullet("5 pages: Home, Caption Studio, Visual QA, Analytics, About")
    pdf.bullet("Components: gr.Image, gr.Textbox, gr.Dropdown, gr.Button, gr.Plot, gr.Chatbot, gr.HTML")
    pdf.bullet("Custom theme: Exo 2 body font, JetBrains Mono, cyan/purple/green neon palette")
    pdf.bullet("Sticky navbar via CSS [role='tablist'] + position:sticky")
    pdf.bullet("Plotly charts for tier distribution, quality scores, cost, latency, style usage")

    pdf.h2("6.2  FastAPI — REST API")
    pdf.tag("Library", "fastapi + uvicorn")
    pdf.tag("Port",    "8000")
    pdf.tag("File",    "app/main.py")
    pdf.ln(1)
    pdf.body("Provides HTTP endpoints for programmatic access to the captioning pipeline:")
    endpoints = [
        ("POST /caption",         "Generate a single caption. Body: {image_b64, style}"),
        ("POST /caption/compare", "Generate captions in all 5 styles simultaneously"),
        ("POST /vqa",             "Ask a question about an image. Body: {image_b64, question, session_id}"),
        ("GET  /stats",           "Return aggregate analytics from the JSONL tracker"),
    ]
    for ep, desc in endpoints:
        pdf.tag(ep, desc)
    pdf.ln(1)
    pdf.body(
        "FastAPI runs in a daemon thread (threading.Thread) when launched via run.py, "
        "so both servers share the same Python process. Uvicorn is the ASGI server."
    )

    # ── 7. Configuration & Tracking ──────────────────────────────────────────
    pdf.add_page()
    pdf.h1("7. Configuration & Experiment Tracking")

    pdf.h2("7.1  Pydantic Settings")
    pdf.tag("Library", "pydantic-settings")
    pdf.tag("File",    "app/config.py")
    pdf.ln(1)
    pdf.body(
        "All configuration is managed via a Pydantic BaseSettings class that reads "
        "from environment variables and/or a .env file. Key settings:"
    )
    settings_list = [
        ("OPENAI_API_KEY",       "OpenAI API key — if empty, system runs offline"),
        ("CLIP_MODEL_NAME",      "HuggingFace model ID for CLIP (default: openai/clip-vit-base-patch32)"),
        ("BLIP_MODEL_NAME",      "HuggingFace model ID for BLIP"),
        ("CLIP_SCORE_THRESHOLD", "Float threshold for CLIPScore gate (default: 0.2)"),
        ("LLM_JUDGE_THRESHOLD",  "Int threshold for LLM judge gate (default: 7)"),
        ("FAISS_INDEX_PATH",     "Path to persist FAISS index (default: ./data/faiss_index)"),
        ("RUNS_FILE",            "Path to JSONL tracking file (default: ./data/runs.jsonl)"),
    ]
    for k, v in settings_list:
        pdf.tag(k, v)
    pdf.ln(1)
    pdf.body("has_openai property: True if OPENAI_API_KEY is non-empty and non-None.")

    pdf.h2("7.2  Local JSONL Tracker")
    pdf.tag("File", "app/tracking/local_tracker.py")
    pdf.ln(1)
    pdf.body(
        "Appends one JSON record per caption run to ./data/runs.jsonl. "
        "Each record captures: model_name, style, tier_used, clip_score, judge_score, "
        "latency_ms, cost_usd, escalation_count, caption_length, image_hash, timestamp. "
        "get_stats() reads all records and returns aggregated metrics: total_runs, "
        "avg_clip_score, total_cost, tier_usage dict, style_usage dict, recent_runs list."
    )

    pdf.h2("7.3  MLflow (Optional)")
    pdf.tag("Library", "mlflow")
    pdf.body(
        "MLflow is integrated optionally for experiment tracking. If MLflow is "
        "installed and a tracking server is configured, runs are logged with parameters "
        "and metrics. Falls back silently if MLflow is unavailable — does not crash "
        "the application."
    )

    # ── 8. Supporting Libraries ───────────────────────────────────────────────
    pdf.add_page()
    pdf.h1("8. Supporting Libraries")

    libs = [
        ("torch",             "PyTorch",              "Deep learning framework for BLIP and CLIP inference. Provides tensor operations, model loading, and GPU/CPU device management."),
        ("transformers",      "Hugging Face Transformers", "Provides pre-trained model architectures and tokenizers. Used to load BLIP (BlipForConditionalGeneration) and CLIP (CLIPModel + CLIPProcessor)."),
        ("Pillow (PIL)",      "Python Imaging Library", "Image loading, format conversion (RGB), resizing, and JPEG encoding. All image I/O in the platform goes through PIL."),
        ("openai",            "OpenAI Python SDK",    "Official Python client for the OpenAI API. Used for GPT-4o-mini and GPT-4o caption generation and LLM-judge evaluation. Also used for Visual QA."),
        ("plotly",            "Plotly Graphing Library", "Interactive chart library used for all analytics visualizations: pie chart (tier distribution), bar charts (quality, style), scatter (cost), dual-axis (latency+cost)."),
        ("sentence_transformers", "SentenceTransformers", "Provides the all-MiniLM-L6-v2 model for encoding captions into 384-dim vectors for FAISS storage and retrieval."),
        ("faiss-cpu",         "FAISS CPU",            "Facebook's vector similarity search library. Used as the vector store for RAG memory. IndexFlatIP for inner-product (cosine) search."),
        ("langgraph",         "LangGraph",            "Graph-based AI workflow engine. Defines the StateGraph with route/generate/critique/escalate nodes and conditional edges."),
        ("langchain",         "LangChain (indirect)",  "LangGraph depends on LangChain for base abstractions. Not directly used in application code."),
        ("uvicorn",           "Uvicorn ASGI Server",  "Production-grade ASGI server for FastAPI. Runs on port 8000 in a daemon thread when using run.py."),
        ("pydantic-settings", "Pydantic Settings",    "Extends Pydantic for settings management with .env file support. All app config is a BaseSettings subclass."),
        ("python-dotenv",     "python-dotenv",        "Loads .env file variables into the environment at startup. Works with Pydantic Settings for local development."),
        ("numpy",             "NumPy",                "Gradio returns images as numpy arrays; platform converts them to PIL for model inference."),
        ("fpdf2",             "fpdf2",                "Pure-Python PDF generation library. Used to generate this documentation."),
    ]

    for lib, name, desc in libs:
        pdf.h3(f"{name}  ({lib})")
        pdf.body(desc)
        pdf.ln(1)

    # ── 9. Caption Refinement & Post-processing ────────────────────────────
    pdf.add_page()
    pdf.h1("9. Caption Refinement & Post-processing")

    pdf.tag("File", "app/agents/refinement_agent.py")
    pdf.ln(1)
    pdf.body(
        "After a caption is accepted by the quality gates, a RefinementAgent generates "
        "purpose-driven variants: accessible alt-text and SEO-optimized meta descriptions. "
        "This runs as the final graph node (refine_node) before END, so only the accepted "
        "caption is refined -- no wasted API calls on escalated drafts."
    )
    pdf.bullet("Alt-text: concise, factual, main subject first, under 125 characters")
    pdf.bullet("SEO: keyword-optimized meta description, under 160 characters")
    pdf.bullet("Two separate GPT-4o-mini calls (text-only, no image needed)")
    pdf.bullet("Offline mode: returns original caption for both variants")
    pdf.bullet("Each call wrapped individually -- partial failure returns original for that variant")

    # ── 10. Multi-language Support ───────────────────────────────────────────
    pdf.h1("10. Multi-language Support")

    pdf.tag("File", "app/agents/translation.py")
    pdf.ln(1)
    pdf.body(
        "The platform supports generating captions in 7 languages: English, Spanish, "
        "French, German, Chinese, Japanese, and Hindi. Translation is performed as a "
        "post-graph processing step via GPT-4o-mini, keeping the core captioning pipeline "
        "language-agnostic."
    )
    pdf.bullet("English passthrough: no API call, zero latency")
    pdf.bullet("GPT-4o-mini translation: system prompt enforces tone preservation")
    pdf.bullet("Offline mode: silently returns the English caption")
    pdf.bullet("Language selector in Caption Studio UI and /caption API endpoint")
    pdf.bullet("Configurable via AVAILABLE_LANGUAGES and DEFAULT_LANGUAGE settings")

    # ── 11. Confidence Scoring ───────────────────────────────────────────────
    pdf.h1("11. Confidence Scoring")

    pdf.tag("File", "app/agents/confidence.py")
    pdf.ln(1)
    pdf.body(
        "Every caption receives a normalized 0-100 confidence score combining the CLIP "
        "similarity score and the LLM judge rating. A plain-English explanation is generated "
        "to help users understand why a caption was rated as it was."
    )
    pdf.bullet("Formula: clip_weight * clip_norm + judge_weight * judge_norm")
    pdf.bullet("CLIP normalized: min(clip_score / threshold, 1.0) * 100")
    pdf.bullet("Judge normalized: (overall / 10) * 100")
    pdf.bullet("Three tiers: High (>=85), Moderate (60-84), Low (<60)")
    pdf.bullet("Computed inside critique_node -- no additional graph node or latency")
    pdf.bullet("Displayed in UI with colored badge (green/amber/red) and explanation text")
    pdf.bullet("Weights configurable via CONFIDENCE_CLIP_WEIGHT and CONFIDENCE_JUDGE_WEIGHT")

    pdf.output("docs/01_tech_stack.pdf")
    print("  [OK] docs/01_tech_stack.pdf")


# =============================================================================
# PDF 2 — Q&A
# =============================================================================

def make_pdf2():
    pdf = DocPDF("IMG Caption Platform  |  PDF 2: Questions & Answers")
    pdf.cover("02", "Questions & Answers", "Comprehensive Q&A covering architecture, design decisions,\nmodel routing, quality control, memory, deployment, and more.")

    sections = [
        ("1. Architecture & Design", [
            (
                "What is the overall architecture of the IMG Caption Platform?",
                "It is a multi-agent AI system built around a LangGraph StateGraph pipeline. "
                "A route node initialises the state and fetches RAG context, a generate node "
                "calls the appropriate vision model (BLIP, GPT-4o-mini, or GPT-4o), and a "
                "critique node evaluates the output. If quality is insufficient and the tier "
                "is below 3, an escalate node increments the tier and the pipeline loops back "
                "to generate. The workflow is exposed via a Gradio web UI and a FastAPI REST API."
            ),
            (
                "Why use LangGraph instead of a simple if/else pipeline?",
                "LangGraph provides a clean, declarative way to define stateful agentic workflows "
                "as directed graphs. It handles the loop (escalation) naturally via graph edges, "
                "maintains a typed state dict that flows between nodes, and makes it easy to add "
                "new nodes (e.g. a re-ranking step) without rewriting control flow. It also "
                "integrates with LangSmith for tracing."
            ),
            (
                "What is the 3-tier model routing strategy?",
                "Tier 1 is BLIP (local, free). Tier 2 is GPT-4o-mini (cheap cloud). Tier 3 is "
                "GPT-4o (premium cloud). The pipeline starts at Tier 1 and only escalates if the "
                "quality critic rejects the caption. This minimises cost: most captions are "
                "generated locally for free; cloud models are only invoked when necessary."
            ),
            (
                "How does the escalation loop work and what prevents infinite loops?",
                "After each generation, the critique node evaluates the caption. The "
                "should_escalate() function checks two conditions: (1) did the caption pass "
                "both quality gates? and (2) is the current tier already at 3? If either "
                "condition is true, it returns 'accept' and the graph ends. Otherwise it "
                "returns 'escalate'. Since there are only 3 tiers, the loop can run at most "
                "3 times (1->2->3->accept)."
            ),
            (
                "Why is BLIP used as Tier 1 rather than a smaller cloud model?",
                "BLIP is free (no API cost), runs offline, loads once as a singleton, and "
                "produces reasonable captions for most common images. This means the platform "
                "works even without an internet connection or API key, and the majority of "
                "use cases are handled at zero cost."
            ),
            (
                "What is the offline-first design principle?",
                "The system is designed to always produce a result. Without an OpenAI API key, "
                "BLIP generates captions, the LLM judge is skipped (defaulting to pass), and "
                "only CLIPScore is used for quality evaluation. Visual QA returns a friendly "
                "'no key configured' message. No 'Failed to fetch' errors occur."
            ),
        ]),
        ("2. Quality Control", [
            (
                "What are the two quality gates?",
                "Gate 1: CLIPScore — cosine similarity between CLIP image and text embeddings. "
                "Threshold: 0.2 (configurable). Gate 2: LLM-as-Judge — GPT-4o-mini rates the "
                "caption 1-10 on accuracy, detail, style match, and fluency. Threshold: 7/10. "
                "Both must pass in online mode. In offline mode, only Gate 1 is checked."
            ),
            (
                "What is CLIPScore and why is it used?",
                "CLIP (Contrastive Language-Image Pre-training) maps both images and text into "
                "a shared embedding space. Cosine similarity in that space measures how "
                "semantically aligned a caption is with the image — without needing a human "
                "label. A low CLIPScore means the caption describes something different from "
                "what is in the image. It runs locally, is fast, and is free."
            ),
            (
                "What happens when the CLIPScore is below the threshold?",
                "The critic_result.passes flag is set to False. The should_escalate() function "
                "checks this flag. If the current tier is below 3, the escalate_node increments "
                "the tier and the pipeline regenerates with a higher-quality model."
            ),
            (
                "How does the LLM-as-Judge work technically?",
                "The critic encodes the image as a base64 JPEG at 'low' detail and sends it "
                "along with the caption and style to GPT-4o-mini. A structured prompt asks the "
                "model to output numeric scores in a fixed format. The response is parsed line "
                "by line. If parsing fails for a criterion, it defaults to 5."
            ),
            (
                "What is the combined score displayed in the metrics table?",
                "Combined = (min(clip_score / threshold, 1.0) + overall_judge_score / 10) / 2. "
                "This normalises both scores to a 0-1 range and averages them into a single "
                "composite quality metric."
            ),
            (
                "Can the thresholds be tuned?",
                "Yes. Set CLIP_SCORE_THRESHOLD and LLM_JUDGE_THRESHOLD in your .env file or "
                "as environment variables. Lower thresholds accept more captions at Tier 1 "
                "(cheaper, faster). Higher thresholds force more escalations to GPT-4o-mini/4o "
                "(better quality, higher cost)."
            ),
        ]),
        ("3. Memory & RAG", [
            (
                "What is Retrieval-Augmented Generation (RAG) in this context?",
                "Before generating a caption, the route node retrieves the top-3 most "
                "semantically similar past captions from the FAISS index. These are passed "
                "as a 'context' string to the caption model, grounding the new generation "
                "in previous high-quality outputs for similar images. This improves consistency "
                "and style adherence over time."
            ),
            (
                "How is FAISS used in this platform?",
                "FAISS stores 384-dimensional SentenceTransformer vectors for each caption "
                "that was successfully generated and accepted. IndexFlatIP (inner product on "
                "L2-normalised vectors) is equivalent to cosine similarity search. The index "
                "and accompanying metadata JSON are persisted to ./data/faiss_index/ so memory "
                "survives across server restarts."
            ),
            (
                "What metadata is stored alongside each FAISS vector?",
                "image_hash (MD5 of the JPEG bytes), caption text, style, model_name used, "
                "clip_score, and ISO timestamp. This metadata is stored in metadata.json "
                "and loaded back when the server starts."
            ),
            (
                "Does RAG improve quality measurably?",
                "In the early sessions it has no effect (empty index). As the index grows, "
                "the retrieved context gives the model examples of what good captions for "
                "similar images look like, which tends to improve style consistency. The "
                "effect is strongest for GPT-4o-mini/4o which can follow few-shot examples well."
            ),
        ]),
        ("4. Models & Inference", [
            (
                "How is the BLIP model loaded and why as a singleton?",
                "BLIPCaptionModel is instantiated once and stored in a module-level variable "
                "_blip_model. Subsequent calls to _get_model(1) return the same instance. "
                "Loading BLIP (~1.8 GB) takes 20-60 seconds. Singleton avoids re-loading on "
                "every request, making inference fast after warmup."
            ),
            (
                "How does the platform handle OpenAI API failures gracefully?",
                "Three layers of fallback: (1) caption_agent.py wraps the model call in "
                "try/except — if an OpenAI call fails for any reason, it falls back to "
                "Tier 1 BLIP. (2) conversation.py wraps the VQA API call and returns a "
                "readable error message to the chat. (3) gradio_app.py wraps the entire "
                "workflow in try/except and displays a styled error card — never 'Failed to fetch'."
            ),
            (
                "What image formats does the platform accept?",
                "Gradio accepts any image format it can decode (JPEG, PNG, WebP, BMP, GIF). "
                "Internally all images are converted to RGB PIL Images. For API calls, "
                "images are base64-encoded as JPEG at quality=85 to balance size and fidelity."
            ),
            (
                "How is cost tracked per request?",
                "OpenAICaptionModel reads the response.usage object from the OpenAI API "
                "response, which reports prompt_tokens and completion_tokens. These are "
                "multiplied by the per-model per-token pricing constants defined in PRICING "
                "dict. BLIP has zero cost. Costs are accumulated across tiers in total_cost "
                "and persisted to the JSONL tracker."
            ),
        ]),
        ("5. UI & Frontend", [
            (
                "How is the sci-fi Nexus Vision theme implemented?",
                "Pure CSS injected via the css= parameter to demo.launch(). The design uses "
                "CSS custom properties for the color palette (neon cyan #00f5ff, deep space "
                "black #000811, etc.), Google Fonts (Orbitron for headers, Exo 2 for body, "
                "JetBrains Mono for code), CSS keyframe animations (pageIn, flowPipe, "
                "neonGlow, scan), and a repeating-linear-gradient scanline overlay."
            ),
            (
                "Why does the navbar use [role='tablist'] as a CSS selector?",
                "Gradio renders its tab navigation using ARIA roles. The actual DOM element "
                "has role='tablist'. Targeting this ARIA attribute is more stable than "
                "targeting internal Gradio class names (like .tab-nav) which may change "
                "between Gradio versions."
            ),
            (
                "How are the Plotly charts styled to match the sci-fi theme?",
                "A _CB dict defines the base layout: transparent backgrounds, dark grid "
                "lines at 5% cyan opacity, Exo 2 font, Orbitron title font. Chart traces "
                "use the neon palette (green for BLIP, amber for GPT-mini, pink for GPT-4o). "
                "Charts are rendered in gr.Plot components inside .gr-plot containers styled "
                "with dark surface background and cyan border."
            ),
            (
                "Why were the chart update_layout() calls split into two separate calls?",
                "Python does not allow duplicate keyword arguments in a function call. "
                "_CB (chart base dict) already contains 'legend' and 'yaxis' keys. Passing "
                "**_CB plus legend=... or yaxis=... in the same update_layout() call raises "
                "TypeError: multiple values for keyword argument. The fix is to call "
                "update_layout(**_CB, ...) first, then fig.update_layout(yaxis=...) separately."
            ),
            (
                "What is the agent decision log and how is it built?",
                "The agent log is a styled HTML div that mimics a terminal. Each log line "
                "is color-coded by type (green=pass, amber=escalate, cyan=RAG, red=error) "
                "and has a staggered CSS animation (logIn) for a typewriter effect. The "
                "background is deep black with horizontal scanline texture."
            ),
        ]),
        ("6. Deployment & Operations", [
            (
                "How do you run the platform locally?",
                "Install dependencies: pip install -r requirements.txt. "
                "Set your OpenAI key (optional): create .env with OPENAI_API_KEY=sk-... "
                "Run: python run.py. "
                "Access: http://localhost:7860 (Gradio UI), http://localhost:8000/docs (FastAPI)."
            ),
            (
                "How do you deploy to HuggingFace Spaces?",
                "Use app.py as the entry point (Spaces expects app.py by default). "
                "The file exposes the Gradio demo with demo.launch(). Set OPENAI_API_KEY "
                "as a Space secret in the HuggingFace settings. The FAISS index will be "
                "ephemeral (reset on Space restart) unless you use persistent storage."
            ),
            (
                "What environment variables are required vs optional?",
                "Required: none (the platform runs fully offline without any env vars). "
                "Optional but recommended: OPENAI_API_KEY (enables Tier 2/3 and VQA). "
                "Optional tuning: CLIP_SCORE_THRESHOLD, LLM_JUDGE_THRESHOLD, "
                "FAISS_INDEX_PATH, RUNS_FILE, BLIP_MODEL_NAME, CLIP_MODEL_NAME."
            ),
            (
                "How long does the first startup take?",
                "BLIP (~1.8 GB) and CLIP (~600 MB) are downloaded from HuggingFace Hub on "
                "first run. This can take 2-10 minutes depending on connection speed. "
                "Subsequent startups load from the local HuggingFace cache (~5-30 seconds). "
                "SentenceTransformer (~80 MB) loads quickly."
            ),
            (
                "Does the platform support GPU inference?",
                "Yes. BLIP and CLIP both check for CUDA availability (torch.cuda.is_available()) "
                "and MPS (Apple Silicon). If a GPU is available, models are moved to it "
                "automatically. No manual configuration is required."
            ),
            (
                "How is the FAISS index persisted?",
                "After each successful caption, RAGMemory.add_caption() adds the vector to "
                "the in-memory FAISS index and immediately writes both index.faiss and "
                "metadata.json to FAISS_INDEX_PATH. On server startup, if the files exist, "
                "the index is loaded from disk."
            ),
        ]),
        ("7. Caption Styles", [
            (
                "What are the 5 caption styles?",
                "descriptive: Objective, detailed description of all visual elements. "
                "creative: Artistic, poetic language with emotional tone and metaphor. "
                "technical: Formal, precise language appropriate for documentation or alt text. "
                "concise: Single sentence, maximum information density. "
                "social_media: Engaging, emoji-friendly, hashtag-ready caption for social platforms."
            ),
            (
                "How are style prompts implemented?",
                "app/styles/prompts.py defines a STYLE_PROMPTS dict mapping style names to "
                "instruction strings. get_style_prompt(style) returns the prompt. "
                "This prompt is appended to the model's user message to steer generation."
            ),
            (
                "Can users compare all 5 styles at once?",
                "Yes. The 'Compare All 5 Styles' button in Caption Studio calls "
                "compare_all_styles() which iterates over all AVAILABLE_STYLES, invokes "
                "the full pipeline for each, and returns a styled HTML card for each result."
            ),
        ]),
        ("8. Smart Routing & Complexity", [
            (
                "How does smart routing work?",
                "Before generating a caption, OpenCV analyzes the image for edge density "
                "(Canny), color variance (HSV), and texture richness (Laplacian). These three "
                "metrics are combined into a composite score (0-1). Images scoring above 0.6 "
                "('complex') skip Tier 1 (BLIP) and route directly to Tier 2 (GPT-4o-mini), "
                "avoiding a wasted BLIP attempt on scenes it cannot handle well."
            ),
            (
                "What happens with complex images in offline mode?",
                "If no OpenAI API key is configured, the smart router falls back to Tier 1 "
                "(BLIP) regardless of complexity. BLIP is the only available model offline, "
                "so the complexity analysis still runs and is logged, but the tier selection "
                "is overridden to 1."
            ),
            (
                "Can complexity thresholds be tuned?",
                "Yes. Set COMPLEXITY_EDGE_THRESHOLD (default 0.15) and "
                "COMPLEXITY_COLOR_THRESHOLD (default 50.0) as environment variables. "
                "The composite score weights (edge 0.4, color 0.3, texture 0.3) and label "
                "boundaries (simple < 0.3, medium 0.3-0.6, complex > 0.6) are defined in "
                "app/agents/complexity.py."
            ),
        ]),
        ("9. Object Detection", [
            (
                "What model is used for object detection?",
                "YOLOv8n (nano variant) from Ultralytics, approximately 6MB. It auto-downloads "
                "on first use and then runs fully offline. It detects 80 COCO object classes "
                "including people, animals, vehicles, furniture, and common household items."
            ),
            (
                "How do detected objects improve captions?",
                "Detected object labels and counts are formatted into a context string "
                "(e.g. 'Detected objects: 2 dogs (0.92), 1 car (0.85)') and passed to the "
                "caption model alongside RAG context. This structured grounding helps all tiers "
                "-- especially BLIP -- identify and describe objects they might otherwise miss, "
                "such as small background items or partially occluded subjects."
            ),
            (
                "Does object detection work offline?",
                "Yes, fully. YOLOv8n runs locally on CPU or GPU. The model weights are cached "
                "after the first download. No API key or internet connection is needed for "
                "subsequent uses. The confidence threshold (default 0.3) filters out low-quality "
                "detections."
            ),
        ]),
        ("10. CLIP Image RAG", [
            (
                "How does dual-index RAG work?",
                "The RAG memory maintains two separate FAISS indices: one for SentenceTransformer "
                "text embeddings (384-dim) and one for CLIP image embeddings (512-dim). When "
                "retrieving context, both indices are queried and their similarity scores are "
                "blended: combined = text_weight * text_score + image_weight * image_score. "
                "This finds captions from visually similar images, not just semantically similar text."
            ),
            (
                "What if CLIP is unavailable?",
                "The system falls back gracefully to text-only retrieval. If the CLIP model fails "
                "to load, or if the image index is empty (e.g. on first run), retrieve_combined() "
                "returns results using only the text similarity index -- identical to the previous "
                "behavior."
            ),
            (
                "How is the blend weight configured?",
                "Set the CLIP_IMAGE_WEIGHT environment variable (default 0.4). This means image "
                "similarity contributes 40% and text similarity contributes 60% to the combined "
                "score. A value of 0.0 disables image similarity entirely; 1.0 uses only image "
                "similarity (not recommended)."
            ),
        ]),
        ("11. Caption Refinement", [
            (
                "What refinement variants are generated?",
                "Two variants: (1) Alt-text -- concise, factual, accessibility-optimized, under "
                "125 characters, suitable for screen readers and image alt attributes. (2) SEO -- "
                "keyword-optimized meta description, under 160 characters, suitable for image "
                "search indexing and social media previews."
            ),
            (
                "Does refinement work offline?",
                "In offline mode (no OpenAI API key), the refinement agent returns the original "
                "caption for both alt-text and SEO variants. No error is shown -- the refinements "
                "panel simply displays the original caption in both fields."
            ),
        ]),
        ("12. Multi-language", [
            (
                "How does translation work?",
                "After the caption is accepted and refined by the graph pipeline, a separate "
                "translation step calls GPT-4o-mini with a system prompt enforcing accurate, "
                "tone-preserving translation. English is a passthrough (no API call). The "
                "translation runs outside the graph to avoid translating drafts that get escalated."
            ),
            (
                "What languages are supported?",
                "English (default, passthrough), Spanish, French, German, Chinese, Japanese, "
                "and Hindi. The language list is configurable via the AVAILABLE_LANGUAGES setting. "
                "A language dropdown in Caption Studio and a 'language' parameter in the /caption "
                "API endpoint allow selection."
            ),
        ]),
        ("13. Confidence Scoring", [
            (
                "How is the confidence score calculated?",
                "A weighted combination of normalized CLIP and LLM judge scores: "
                "score = clip_weight * (clip_score/threshold * 100) + judge_weight * (overall/10 * 100). "
                "Default weights are 0.5/0.5. The result is clamped to 0-100 and rounded to 1 decimal. "
                "Three tiers: High (>=85), Moderate (60-84), Low (<60)."
            ),
            (
                "What does the confidence explanation say?",
                "A plain-English sentence describing the confidence level. High: 'The caption "
                "closely matches the image content (CLIP: X) and received strong quality ratings "
                "(Y/10).' Moderate: includes the LLM judge's reason if available. Low: warns "
                "that the caption may not fully capture the image content. The explanation is "
                "displayed in the UI metrics panel."
            ),
        ]),
    ]

    for section_title, qas in sections:
        pdf.add_page()
        pdf.h1(section_title)
        for q, a in qas:
            pdf.qa_q(q)
            pdf.qa_a(a)

    pdf.output("docs/02_questions_and_answers.pdf")
    print("  [OK] docs/02_questions_and_answers.pdf")


# =============================================================================
# PDF 3 — GAPS, IMPROVEMENTS & MISSING TOPICS
# =============================================================================

def make_pdf3():
    pdf = DocPDF("IMG Caption Platform  |  PDF 3: Gaps, Improvements & Extensions")
    pdf.cover("03", "Gaps, Improvements & Extensions", "Security gaps, missing features, performance optimisations,\nproduction hardening, and future roadmap topics.")

    # ── 1. Security ──────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.h1("1. Security Gaps")
    pdf.warn_box(
        "The current platform has NO authentication or authorisation. Anyone who can "
        "reach port 7860 or 8000 can upload images, run the pipeline, and consume your "
        "OpenAI quota. These gaps must be closed before any public deployment."
    )

    pdf.h2("1.1  Authentication")
    pdf.body("Current state: None. The Gradio UI and FastAPI endpoints are completely open.")
    pdf.bullet("Add Gradio auth: demo.launch(auth=[(\"user\", \"pass\")]) for basic protection")
    pdf.bullet("FastAPI: Add OAuth2 Bearer token or API key header validation")
    pdf.bullet("Production: Use a reverse proxy (nginx) with TLS + basic auth or OAuth2")

    pdf.h2("1.2  API Key Exposure")
    pdf.body(
        "The OpenAI key is loaded from environment/config and passed directly to the "
        "OpenAI client. If the FastAPI /caption endpoint is open, an attacker can drain "
        "your API quota by spamming requests."
    )
    pdf.bullet("Add rate limiting: slowapi or fastapi-limiter (e.g. 10 requests/minute/IP)")
    pdf.bullet("Add request size limits: reject images > 10MB")
    pdf.bullet("Never log or return the API key in error messages")

    pdf.h2("1.3  Input Validation")
    pdf.body("FastAPI endpoints accept arbitrary base64 data. No file-type validation.")
    pdf.bullet("Validate that decoded bytes are valid image data before processing")
    pdf.bullet("Limit accepted MIME types to image/jpeg, image/png, image/webp")
    pdf.bullet("Add maximum image dimension constraints to prevent OOM attacks")

    pdf.h2("1.4  CORS Policy")
    pdf.body("FastAPI has no explicit CORS configuration.")
    pdf.bullet("Add CORSMiddleware with explicit allowed origins for production")
    pdf.bullet("Gradio has its own CORS handling but should also be configured")

    # ── 2. Performance ───────────────────────────────────────────────────────
    pdf.add_page()
    pdf.h1("2. Performance Gaps")

    pdf.h2("2.1  Concurrency")
    pdf.body(
        "The current BLIP model is a singleton with no thread safety. If two users "
        "submit captions simultaneously, the BLIP inference runs sequentially because "
        "the GIL and singleton pattern serialize GPU/CPU access."
    )
    pdf.bullet("Add a threading.Lock around BLIP inference for thread safety")
    pdf.bullet("For high-load: run a model server (TorchServe, Triton) in a separate process")
    pdf.bullet("Gradio queue: enable demo.queue() with max_size and status_update_rate")

    pdf.h2("2.2  BLIP Startup Latency")
    pdf.body(
        "BLIP and CLIP load lazily on first request, causing a 10-30 second delay for "
        "the first user. Subsequent requests are fast."
    )
    pdf.bullet("Pre-warm at startup: call _get_model(1) and _get_critic() in a background thread at launch")
    pdf.bullet("Add a 'Model Loading...' progress indicator in the UI")

    pdf.h2("2.3  CLIP Score on Every Request")
    pdf.body(
        "CLIPScore is computed synchronously in the critique node. For large images "
        "this can add 100-500ms per caption attempt."
    )
    pdf.bullet("Cache CLIPScore results by image_hash to avoid recomputing for identical images")
    pdf.bullet("Run CLIP in a thread pool executor to avoid blocking the event loop")

    pdf.h2("2.4  FAISS Index Scalability")
    pdf.body(
        "IndexFlatIP performs exact (brute-force) search. For small indexes (<10k vectors) "
        "this is fine. Beyond 100k vectors it becomes slow."
    )
    pdf.bullet("Switch to IndexIVFFlat for approximate search at scale (with train step)")
    pdf.bullet("Add periodic index compaction to remove duplicate image_hash entries")
    pdf.bullet("Consider IndexHNSWFlat for sub-millisecond ANN at any scale")

    # ── 3. Missing Features ──────────────────────────────────────────────────
    pdf.add_page()
    pdf.h1("3. Missing Features")

    pdf.h2("3.1  Caption Editing & Human Feedback")
    pdf.body(
        "Users cannot edit the generated caption in the UI. There is no mechanism to "
        "provide thumbs-up/down feedback that could be used to retrain or fine-tune."
    )
    pdf.bullet("Add an editable Textbox for the caption output")
    pdf.bullet("Add a 'Save to Memory' button that stores the human-edited caption in FAISS")
    pdf.bullet("Add thumbs up/down buttons that log feedback to runs.jsonl with a 'human_rating' field")

    pdf.h2("3.2  Batch Processing")
    pdf.body("The platform processes one image at a time. No bulk upload or batch API.")
    pdf.bullet("Add a batch upload component (gr.File with file_count='multiple')")
    pdf.bullet("FastAPI: Add POST /caption/batch endpoint accepting a list of images")
    pdf.bullet("Use asyncio.gather for concurrent OpenAI calls in batch mode")

    pdf.h2("3.3  Caption Export")
    pdf.body("No way to export generated captions or download results.")
    pdf.bullet("Add a 'Download Caption' button using gr.DownloadButton")
    pdf.bullet("Export as TXT, JSON, or CSV for batch results")

    pdf.h2("3.4  Image History / Gallery")
    pdf.body("The UI does not show previously processed images or their captions.")
    pdf.bullet("Add a gallery page showing recent runs with thumbnail, caption, score, and cost")
    pdf.bullet("Read from runs.jsonl and display paginated results")

    pdf.h2("3.5  Model Selection Override")
    pdf.body("Users cannot force a specific tier. The pipeline always starts at Tier 1.")
    pdf.bullet("Add a 'Force Tier' dropdown in Caption Studio for power users")
    pdf.bullet("Add a 'Fast Mode' toggle that uses GPT-4o-mini directly (skip BLIP)")

    pdf.h2("3.6  Streaming Output")
    pdf.body(
        "Caption generation is blocking — the UI shows nothing until the full caption "
        "is ready. For GPT-4o (Tier 3) this can take 5-15 seconds."
    )
    pdf.bullet("Use OpenAI streaming API (stream=True) and yield tokens progressively")
    pdf.bullet("Gradio supports streaming via generator functions (yield from event handler)")

    pdf.h2("3.7  Image Preprocessing")
    pdf.body("No image preprocessing pipeline.")
    pdf.bullet("Add auto-resize to maximum safe dimension (e.g. 1024px) to reduce token cost")
    pdf.bullet("Add contrast/brightness normalisation for dark or washed-out images")
    pdf.bullet("Add rotation correction using EXIF orientation data")
    pdf.info_box(
        "UPDATE v2.0: Image complexity analysis (OpenCV) now runs as a pre-pass before "
        "captioning, analyzing edge density, color variance, and texture to enable smart "
        "routing. Additionally, YOLOv8n object detection provides structured scene context. "
        "See Sections 2.6 and 2.7 in PDF 01 (Tech Stack)."
    )

    # ── 4. Observability ─────────────────────────────────────────────────────
    pdf.add_page()
    pdf.h1("4. Observability Gaps")

    pdf.h2("4.1  Structured Logging")
    pdf.body(
        "The platform uses print() for startup messages and relies on exception "
        "tracebacks for errors. No structured logging is in place."
    )
    pdf.bullet("Replace print() with Python's logging module (structlog for JSON logs)")
    pdf.bullet("Log each pipeline step: tier, latency, score, cost, image_hash")
    pdf.bullet("Log OpenAI API errors with status codes and retry counts")

    pdf.h2("4.2  Health Check Endpoint")
    pdf.body("FastAPI has no /health endpoint for load balancers or uptime monitors.")
    pdf.bullet("Add GET /health that returns model load status, FAISS index size, and API key presence")
    pdf.bullet("Add GET /ready that returns 503 until BLIP and CLIP are loaded")

    pdf.h2("4.3  MLflow Integration Completeness")
    pdf.body(
        "MLflow is referenced as optional but the tracking calls are minimal. "
        "The full MLflow experiment tracking capability is not utilised."
    )
    pdf.bullet("Log all CaptionState fields as MLflow run params and metrics")
    pdf.bullet("Log the CLIP embedding as a numpy artifact for analysis")
    pdf.bullet("Create named experiments per style for comparison")

    pdf.h2("4.4  Error Monitoring")
    pdf.body("No error aggregation or alerting.")
    pdf.bullet("Integrate Sentry for exception capture: sentry_sdk.init(dsn='...')")
    pdf.bullet("Add custom metrics for escalation rate, rejection rate, avg cost per tier")

    # ── 5. Code Quality ───────────────────────────────────────────────────────
    pdf.add_page()
    pdf.h1("5. Code Quality & Testing Gaps")

    pdf.h2("5.1  No Test Suite")
    pdf.body(
        "The platform has no unit tests, integration tests, or evaluation harness. "
        "This is the most significant gap for production readiness."
    )
    pdf.bullet("Unit tests for _parse_judge_response() with malformed LLM output")
    pdf.bullet("Unit tests for CLIPScore with known image-caption pairs")
    pdf.bullet("Unit tests for RAGMemory add/retrieve cycle")
    pdf.bullet("Integration test for the full LangGraph pipeline with a fixture image")
    pdf.bullet("Mock OpenAI API calls in tests using unittest.mock")

    pdf.h2("5.2  Type Safety")
    pdf.body("The codebase uses TypedDict with total=False which makes all fields optional.")
    pdf.bullet("Add runtime validation (pydantic model) for CaptionState at node boundaries")
    pdf.bullet("Add mypy type checking to CI pipeline")

    pdf.h2("5.3  requirements.txt Pinning")
    pdf.body("Version pinning strategy is unknown without seeing the current requirements.txt.")
    pdf.bullet("Pin all direct dependencies to exact versions for reproducibility")
    pdf.bullet("Use pip-compile (pip-tools) to generate a locked requirements.txt")
    pdf.bullet("Separate requirements into base, dev, and optional (mlflow, gpu) groups")

    pdf.h2("5.4  Configuration Validation")
    pdf.body("Settings are loaded but not validated at startup.")
    pdf.bullet("Add a startup check that validates FAISS_INDEX_PATH is writable")
    pdf.bullet("Warn (don't crash) if OPENAI_API_KEY looks invalid (wrong prefix/length)")
    pdf.bullet("Log the effective config (redacting the key) at startup for debuggability")

    # ── 6. Production Readiness ───────────────────────────────────────────────
    pdf.add_page()
    pdf.h1("6. Production Readiness Gaps")

    pdf.h2("6.1  Process Management")
    pdf.body(
        "run.py starts FastAPI in a daemon thread which dies if the main process "
        "(Gradio) crashes. In production, each service should be managed independently."
    )
    pdf.bullet("Use supervisor, systemd, or Docker to manage FastAPI and Gradio as separate services")
    pdf.bullet("Or use a single Uvicorn process with Gradio mounted as a sub-app")

    pdf.h2("6.2  Containerisation")
    pdf.body("No Dockerfile provided.")
    pdf.bullet("Create a multi-stage Dockerfile: builder stage installs deps, runtime stage is lean")
    pdf.bullet("Cache HuggingFace model downloads in the Docker layer for faster startup")
    pdf.bullet("Use .dockerignore to exclude data/, __pycache__, .env")

    pdf.h2("6.3  Persistent Storage in Cloud")
    pdf.body(
        "FAISS index and runs.jsonl are written to the local filesystem. "
        "In containerised or serverless deployments these are ephemeral."
    )
    pdf.bullet("Mount a persistent volume for ./data/ in Docker/Kubernetes")
    pdf.bullet("Or migrate storage to S3/GCS (FAISS index as object, runs as DynamoDB/Firestore)")

    pdf.h2("6.4  Cost Controls")
    pdf.body("No hard spending limits on the OpenAI API usage.")
    pdf.bullet("Add a daily/monthly cost budget in settings; reject requests when budget is exceeded")
    pdf.bullet("Add per-session cost tracking and show running total in the UI")
    pdf.bullet("Alert (email/Slack) when daily spend exceeds a threshold")

    # ── 7. Future Roadmap ────────────────────────────────────────────────────
    pdf.add_page()
    pdf.h1("7. Future Roadmap & Extensions")

    roadmap = [
        ("Fine-tuning Loop",
         "Collect human-rated captions, fine-tune BLIP on domain-specific images "
         "to improve Tier 1 quality and reduce cloud escalation rate."),
        ("Multi-image Captioning",
         "Extend the pipeline to handle sequences of images (video frames, product "
         "galleries) and generate coherent multi-image narratives."),
        ("Caption Re-ranking",
         "Generate N captions at each tier and use CLIPScore + LLM Judge to select "
         "the best one rather than stopping at the first passing caption."),
        ("Multimodal RAG  [IMPLEMENTED in v2.0]",
         "CLIP image embeddings are now stored alongside text embeddings in a dual "
         "FAISS index, enabling visual similarity retrieval. See Section 2.8 in PDF 01."),
        ("Caption Translation  [IMPLEMENTED in v2.0]",
         "GPT-4o-mini translation is now available for 7 languages with a language "
         "selector in the UI and /caption API. See Section 10 in PDF 01."),
        ("A/B Testing Framework",
         "Run two pipeline configurations simultaneously on the same image and compare "
         "output quality, cost, and latency to find optimal threshold settings."),
        ("LangSmith Tracing",
         "Integrate LangSmith for full pipeline trace visualisation -- see exactly which "
         "nodes ran, how long each took, and what state was passed between them."),
        ("WebSocket Streaming",
         "Expose a WebSocket endpoint for real-time streaming of the pipeline steps "
         "as they complete, enabling a live agent-log view in the UI."),
        ("Mobile-Responsive UI",
         "The current UI is desktop-first. Add responsive breakpoints and a simplified "
         "mobile layout for on-device image capture and captioning."),
        ("Offline Translation (MarianMT)",
         "Use Hugging Face MarianMT models for fully offline caption translation, "
         "removing the GPT-4o-mini dependency for multi-language support."),
        ("Custom Refinement Plugins",
         "Allow users to define their own refinement prompts (e.g. brand voice, "
         "compliance language) as pluggable modules registered via settings."),
        ("Complexity Model Fine-tuning",
         "Train a small classifier on domain-specific images to replace the heuristic "
         "complexity scoring with a learned model for better tier routing."),
        ("Multi-Object Scene Graphs",
         "Extend YOLO detection into relationship detection -- not just 'dog' and 'ball' "
         "but 'dog playing with ball' -- for richer scene understanding context."),
    ]
    for title, desc in roadmap:
        pdf.h3(f"  {title}")
        pdf.body(f"    {desc}")
        pdf.ln(1)

    pdf.info_box(
        "Priority recommendations (impact vs. effort):\n"
        "  COMPLETED in v2.0: Multimodal RAG, Caption Translation, Object Detection,\n"
        "    Smart Routing, Confidence Scoring, Caption Refinement\n"
        "  HIGH impact, LOW effort:  Rate limiting, health endpoint, streaming\n"
        "  HIGH impact, HIGH effort: Fine-tuning, offline translation, scene graphs\n"
        "  LOW impact, LOW effort:   Caption export, model selection override\n"
        "  LONG TERM: LangSmith tracing, A/B framework, custom refinement plugins"
    )

    pdf.output("docs/03_gaps_and_improvements.pdf")
    print("  [OK] docs/03_gaps_and_improvements.pdf")


# =============================================================================
# Run all
# =============================================================================
if __name__ == "__main__":
    print("Generating documentation PDFs...")
    make_pdf1()
    make_pdf2()
    make_pdf3()
    print("\nAll PDFs saved to ./docs/")
    print("  docs/01_tech_stack.pdf")
    print("  docs/02_questions_and_answers.pdf")
    print("  docs/03_gaps_and_improvements.pdf")
