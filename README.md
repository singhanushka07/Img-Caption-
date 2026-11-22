# IMG Caption - Multi-Agent Image Captioning Platform

A production-grade **multi-agent image captioning system** built with **LangGraph**, featuring a 3-tier model routing pipeline (BLIP &rarr; GPT-4o-mini &rarr; GPT-4o), dual quality gates (CLIP + LLM-as-Judge), FAISS semantic memory, YOLOv8 object detection, and a polished Gradio + FastAPI interface.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [LangGraph Pipeline](#langgraph-pipeline)
- [Multi-Agent System](#multi-agent-system)
- [Quality Gates](#quality-gates)
- [RAG Memory System](#rag-memory-system)
- [Caption Styles](#caption-styles)
- [API Endpoints](#api-endpoints)
- [Getting Started](#getting-started)
- [Usage Guide](#usage-guide)
- [UI Walkthrough](#ui-walkthrough)
- [Docker](#docker)
- [Testing](#testing)
- [Configuration](#configuration)

---

## Architecture Overview

```
                        +-------------------+
                        |   Image Upload    |
                        +--------+----------+
                                 |
                        +--------v----------+
                        |    Route Node     |
                        |  - FAISS RAG ctx  |
                        |  - OpenCV complex |
                        |  - Tier selection |
                        +--------+----------+
                                 |
                        +--------v----------+
                        |  Object Detector  |
                        |    (YOLOv8n)      |
                        +--------+----------+
                                 |
                        +--------v----------+
                        | Generate Caption  |
                        |  Tier 1: BLIP     |
                        |  Tier 2: GPT-mini |
                        |  Tier 3: GPT-4o   |
                        +--------+----------+
                                 |
                        +--------v----------+
                        |   Critic Agent    |
                        |  - CLIPScore      |
                        |  - LLM Judge      |
                        |  - Confidence     |
                        +--------+----------+
                                 |
                    +------------+------------+
                    |                         |
            [PASS: score >= threshold]  [FAIL: score < threshold]
                    |                         |
           +--------v----------+     +--------v----------+
           |  Refinement Agent |     |   Escalate Node   |
           |  - Alt-text       |     |  tier++ (max 3)   |
           |  - SEO variant    |     +--------+----------+
           +--------+----------+              |
                    |                 (loop back to Generate)
                    v
               [END: Final Caption]
```

---

## Key Features

| # | Feature | Description |
|---|---------|-------------|
| 01 | **3-Tier Model Routing** | BLIP (local, free) &rarr; GPT-4o-mini &rarr; GPT-4o with automatic escalation |
| 02 | **Dual Quality Gates** | CLIPScore cosine similarity + LLM-as-Judge (GPT-4o-mini, threshold-gated) |
| 03 | **FAISS RAG Memory** | Persistent semantic memory using SentenceTransformer + CLIP dual-index retrieval |
| 04 | **5 Caption Styles** | Descriptive, Creative, Technical, Concise, Social Media |
| 05 | **Visual QA** | Multi-turn conversational visual Q&A powered by GPT-4o-mini |
| 06 | **Smart Routing** | OpenCV complexity analysis (edge density, color variance, texture) for intelligent tier selection |
| 07 | **Object Detection** | YOLOv8n pre-pass injects detected objects as context for scene-aware captioning |
| 08 | **Caption Refinement** | Auto-generates accessible alt-text + SEO-optimized variants |
| 09 | **Multi-Language** | Translation to 7 languages (English, Spanish, French, German, Chinese, Japanese, Hindi) |
| 10 | **Confidence Scoring** | 0-100 confidence score with human-readable explanations |
| 11 | **Real-time Analytics** | Live dashboard with tier distribution, quality scores, cost tracking, latency charts |
| 12 | **Cost Tracking** | Per-run token-level cost calculation with cumulative spend visualization |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Orchestration** | LangGraph (StateGraph with conditional edges) |
| **Local Model** | BLIP (Salesforce/blip-image-captioning-large) |
| **Cloud Models** | GPT-4o-mini (Tier 2), GPT-4o (Tier 3) via OpenAI API |
| **Quality - CLIP** | OpenAI CLIP (ViT-B/32) for image-text similarity scoring |
| **Quality - Judge** | GPT-4o-mini LLM-as-Judge with structured rubric |
| **Object Detection** | YOLOv8n (Ultralytics) |
| **RAG** | FAISS (flat inner product) + SentenceTransformer (all-MiniLM-L6-v2) |
| **Image Analysis** | OpenCV (Canny edges, HSV color, Laplacian texture) |
| **Backend** | FastAPI + Uvicorn |
| **UI** | Gradio (custom CSS design system) |
| **Frontend (alt)** | React + TypeScript + Tailwind CSS + Vite |
| **Experiment Tracking** | MLflow + JSON-based local tracker |
| **Charts** | Plotly |
| **Containerization** | Docker |

---

## Project Structure

```
IMG Caption/
├── app/
│   ├── agents/
│   │   ├── graph.py              # LangGraph StateGraph definition
│   │   ├── state.py              # CaptionState TypedDict
│   │   ├── router.py             # RAG context + complexity routing
│   │   ├── caption_agent.py      # 3-tier caption generation
│   │   ├── critic_agent.py       # CLIPScore + LLM Judge
│   │   ├── confidence.py         # Confidence score computation
│   │   ├── complexity.py         # OpenCV image complexity analyzer
│   │   ├── object_detector.py    # YOLOv8 detection agent
│   │   ├── refinement_agent.py   # Alt-text + SEO refinements
│   │   └── translation.py        # Multi-language translation
│   ├── models/
│   │   ├── base.py               # Abstract CaptionModel + CaptionResult
│   │   ├── blip_model.py         # BLIP local inference (Tier 1)
│   │   └── openai_model.py       # GPT-4o-mini / GPT-4o (Tier 2/3)
│   ├── rag/
│   │   └── memory.py             # FAISS dual-index RAG memory
│   ├── styles/
│   │   └── prompts.py            # 5 style prompt templates
│   ├── tracking/
│   │   ├── local_tracker.py      # JSONL-based run tracking
│   │   └── mlflow_tracker.py     # MLflow experiment tracking
│   ├── vqa/
│   │   └── conversation.py       # Multi-turn Visual QA engine
│   ├── config.py                 # Pydantic settings (env-driven)
│   └── main.py                   # FastAPI application
├── ui/
│   └── gradio_app.py             # Gradio UI (1300+ lines, custom CSS)
├── frontend/                     # React + TypeScript alternative UI
│   ├── src/
│   │   ├── App.tsx
│   │   ├── pages/
│   │   └── components/
│   ├── package.json
│   └── vite.config.ts
├── tests/                        # Pytest test suite
│   ├── test_agents.py
│   ├── test_models.py
│   ├── test_rag.py
│   ├── test_complexity.py
│   ├── test_confidence.py
│   ├── test_object_detector.py
│   ├── test_refinement.py
│   └── test_translation.py
├── data/
│   ├── faiss_index/              # Persisted FAISS indexes
│   └── runs.jsonl                # Run history for analytics
├── docs/                         # PDF documentation
│   ├── 01_tech_stack.pdf
│   ├── 02_questions_and_answers.pdf
│   └── 03_gaps_and_improvements.pdf
├── .env                          # API keys (included for convenience)
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Container setup
├── app.py                        # Gradio-only entry point
├── run.py                        # FastAPI + Gradio entry point
└── yolov8n.pt                    # YOLOv8 nano weights
```

---

## LangGraph Pipeline

The system uses a **LangGraph StateGraph** with 6 nodes and conditional edges:

```
Entry → route → detect_objects → generate → critique ──┐
                                     ▲                   │
                                     │          [PASS] → refine → END
                                     │          [FAIL] → escalate ─┘
                                     └────────────────────┘
```

### Node Descriptions

| Node | Purpose |
|------|---------|
| `route` | Retrieves RAG context from FAISS, analyzes image complexity via OpenCV, selects starting tier |
| `detect_objects` | Runs YOLOv8n to detect objects; injects structured context ("Detected: 2 persons, 1 car") |
| `generate` | Generates caption using the current tier's model (BLIP / GPT-4o-mini / GPT-4o) |
| `critique` | Evaluates caption with CLIPScore + LLM Judge; computes confidence score |
| `refine` | Generates alt-text and SEO variants using GPT-4o-mini |
| `escalate` | Increments tier (max 3), loops back to `generate` |

### Conditional Edge Logic

```python
def should_escalate(state):
    if critic_result passes:        return "accept"   # → refine → END
    if tier >= 3 or escalations >= 2: return "accept"  # max retries
    return "escalate"                                   # tier++ → generate
```

---

## Multi-Agent System

### Agent 1: Router Agent (`router.py`)
- Queries FAISS for similar past captions (text + image embeddings)
- Runs OpenCV complexity analysis (edge density, color variance, texture)
- Complex images start at Tier 2 (GPT-4o-mini) instead of Tier 1 (BLIP)

### Agent 2: Object Detector (`object_detector.py`)
- YOLOv8n pre-pass with confidence threshold (0.3)
- Aggregates detections by label with counts
- Injects context: `"Detected objects: 2 persons (0.89), 1 car (0.76)"`

### Agent 3: Caption Generator (`caption_agent.py`)
- **Tier 1 (BLIP):** Local inference, zero cost, ~200-500ms
- **Tier 2 (GPT-4o-mini):** Cloud API, ~$0.0001/caption, ~1-2s
- **Tier 3 (GPT-4o):** Cloud API, high-detail vision, ~$0.001/caption, ~2-4s
- Automatic fallback: if BLIP fails → escalate to GPT; if GPT fails → fall back to BLIP

### Agent 4: Critic Agent (`critic_agent.py`)
- **CLIPScore:** Cosine similarity between image and caption embeddings (threshold: 0.25)
- **LLM Judge:** GPT-4o-mini rates accuracy, detail, style match, fluency (1-10 each)
- Combined pass/fail determines escalation

### Agent 5: Confidence Scorer (`confidence.py`)
- Weighted combination: 50% CLIP normalized + 50% Judge normalized
- Score range: 0-100 with labels (High/Moderate/Low)
- Human-readable explanations

### Agent 6: Refinement Agent (`refinement_agent.py`)
- **Alt-text:** Accessible description for screen readers (<125 chars)
- **SEO:** Search-optimized meta description (<160 chars)

### Agent 7: Translation Agent (`translation.py`)
- GPT-4o-mini translation to 7 languages
- Preserves tone and meaning

---

## Quality Gates

### Gate 1: CLIPScore
```
CLIP(image, caption) → cosine similarity → threshold ≥ 0.25
```
Uses OpenAI CLIP ViT-B/32. Measures how well the caption semantically matches the image.

### Gate 2: LLM-as-Judge
```
GPT-4o-mini evaluates on 4 criteria (1-10 each):
  - Accuracy: How well does it describe what's in the image?
  - Detail: Is the level of detail appropriate for the style?
  - Style Match: Does it match the requested style?
  - Fluency: Is it well-written and natural?
  - Overall: Combined score (threshold ≥ 7)
```

### Decision Logic
- Both gates must pass for acceptance
- If CLIP model unavailable, relies on LLM Judge alone
- If no OpenAI key, accepts based on CLIPScore only (offline mode)

---

## RAG Memory System

### Dual-Index Architecture
1. **Text Index:** SentenceTransformer (all-MiniLM-L6-v2) encodes captions → FAISS IndexFlatIP
2. **Image Index:** CLIP ViT-B/32 encodes images → FAISS IndexFlatIP

### Combined Retrieval
```
combined_score = 0.6 * text_similarity + 0.4 * image_similarity
```
Top-k results injected as context for caption generation.

### Persistence
- Indexes saved to `data/faiss_index/caption_index.faiss` and `clip_image_index.faiss`
- Metadata stored in `data/faiss_index/entries.json`
- Survives restarts — cumulative knowledge base

---

## Caption Styles

| Style | Description | Example Prompt |
|-------|-------------|----------------|
| **Descriptive** | Detailed, factual description | "Describe main subjects, actions, setting, colors, lighting" |
| **Creative** | Artistic, narrative caption | "Use vivid language, metaphors, storytelling elements" |
| **Technical** | Precise, analytical description | "Focus on composition, color palette, objects, textures" |
| **Concise** | Single sentence summary | "Single, concise sentence capturing the essence" |
| **Social Media** | Engaging, shareable caption | "Catchy, with emojis and 3-5 hashtags" |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/caption` | Generate a caption (image + style + language) |
| `POST` | `/caption/compare` | Generate captions in all 5 styles |
| `POST` | `/vqa` | Visual question answering |
| `GET` | `/stats` | Analytics dashboard data |
| `GET` | `/health` | System health check |
| `GET` | `/styles` | List available styles |
| `GET` | `/languages` | List available languages |

### Example: Generate Caption
```bash
curl -X POST http://localhost:8000/caption \
  -F "image=@photo.jpg" \
  -F "style=descriptive" \
  -F "language=English"
```

### Response
```json
{
  "caption": "A golden retriever sits on a wooden dock overlooking a serene lake...",
  "model_used": "BLIP",
  "tier": 1,
  "clip_score": 0.3142,
  "judge_score": 8,
  "latency_ms": 342.5,
  "cost_usd": 0.0,
  "escalation_count": 0,
  "confidence_score": 85.2,
  "confidence_explanation": "High confidence. The caption closely matches...",
  "complexity_label": "medium",
  "detected_objects": [{"label": "dog", "confidence": 0.92, "count": 1}],
  "refinements": {
    "alt_text": "Golden retriever sitting on dock by lake",
    "seo": "Golden retriever on wooden dock overlooking calm lake at sunset"
  }
}
```

---

## Getting Started

### Prerequisites
- Python 3.10+
- ~4 GB disk space (for ML model downloads on first run)

### Installation

```bash
# Clone the repository
git clone https://github.com/singhanushka07/Img-Caption-.git
cd Img-Caption-

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate          # Windows

# Install dependencies
pip install -r requirements.txt
```

### Add Your OpenAI API Key

Open the `.env` file and replace the placeholder with your actual OpenAI API key:

```
OPENAI_API_KEY=sk-proj-your-actual-key-here
```

You can get an API key from [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys).

> **Note:** Without an OpenAI key the system still works in **offline mode** using BLIP (Tier 1 only). The key enables Tier 2/3 (GPT-4o-mini / GPT-4o), LLM Judge, Visual QA, refinements, and translation.

### Run the Application

**Option 1: Gradio + FastAPI (recommended)**
```bash
python run.py
```
Opens:
- **Gradio UI** at `http://localhost:7860`
- **FastAPI** at `http://localhost:8000`
- **API Docs** at `http://localhost:8000/docs`

**Option 2: Gradio only**
```bash
python app.py
```

### First Run
On first launch, the system will automatically download:
- BLIP model (~1.5 GB)
- CLIP model (~600 MB)
- SentenceTransformer (~90 MB)
- YOLOv8n weights (~6 MB)

These are cached after the first download.

---

## Usage Guide

### Caption Generation
1. Open `http://localhost:7860`
2. Navigate to **Caption Studio** tab
3. Upload an image
4. Select a caption style (descriptive, creative, technical, concise, social_media)
5. Choose output language
6. Click **Generate Caption**
7. View: caption, quality metrics, agent log, confidence score, refinements

### Style Comparison
1. Upload an image in Caption Studio
2. Click **Compare All 5 Styles**
3. See the same image captioned in all 5 styles side-by-side

### Visual QA
1. Navigate to **Visual QA** tab
2. Upload an image
3. Ask questions about the image (multi-turn conversation)
4. Click **New Session** to reset

### Analytics Dashboard
1. Navigate to **Analytics** tab
2. View: KPI cards, tier distribution chart, quality scores, cost tracking, latency analysis
3. Click **Refresh** for latest data

---

## UI Walkthrough

The Gradio UI features a professional SaaS-style design with 5 tabs:

### Home Page
- Hero section with system status badges (Online/Offline, BLIP Ready, FAISS Memory)
- KPI cards: Images processed, Avg CLIP Score, Total API Spend, Local inference %
- Pipeline flow visualization showing all 10 processing nodes
- Performance charts: tier distribution, quality scores, cumulative cost

### Caption Studio
- Image upload with style dropdown (5 styles) and language selector (7 languages)
- Real-time agent log with color-coded entries (green=pass, orange=escalate, blue=RAG)
- Metrics table: Combined score, CLIP, LLM Judge, Verdict
- Confidence bar (0-100) with explanation
- Refinements panel: alt-text + SEO variants with copy buttons
- Translation panel for non-English outputs

### Visual QA
- Multi-turn chat interface with image grounding
- Session-aware conversation history
- GPT-4o-mini powered visual understanding

### Analytics
- KPI summary cards
- Plotly charts: tier distribution (donut), style usage (horizontal bar), quality scores (bar with threshold line), response latency (color-coded bar)

### About
- Feature cards documenting all 8 major capabilities
- LangGraph decision flow diagram

---

## Docker

```bash
# Build
docker build -t img-caption .

# Run
docker run -p 7860:7860 -p 8000:8000 img-caption
```

The Docker image uses Python 3.11-slim and includes all system dependencies for OpenCV and ML models.

---

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test module
pytest tests/test_agents.py -v
pytest tests/test_rag.py -v
pytest tests/test_complexity.py -v
```

Test suite covers:
- Agent pipeline integration
- Model inference (BLIP + OpenAI)
- RAG memory operations
- Complexity analysis
- Confidence scoring
- Object detection
- Refinement generation
- Translation

---

## Configuration

All settings are environment-driven via `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | *(add yours)* | OpenAI API key for Tier 2/3 + Judge — get one at [platform.openai.com](https://platform.openai.com/api-keys) |
| `BLIP_MODEL_NAME` | `Salesforce/blip-image-captioning-base` | HuggingFace BLIP model |
| `CLIP_SCORE_THRESHOLD` | `0.25` | Minimum CLIP similarity to pass |
| `LLM_JUDGE_THRESHOLD` | `7` | Minimum judge score (1-10) to pass |
| `YOLO_CONFIDENCE_THRESHOLD` | `0.3` | YOLO detection confidence cutoff |
| `CLIP_IMAGE_WEIGHT` | `0.4` | Weight for image similarity in RAG |
| `FASTAPI_PORT` | `8000` | FastAPI server port |
| `GRADIO_PORT` | `7860` | Gradio UI port |
| `FAISS_INDEX_PATH` | `./data/faiss_index` | FAISS index storage location |

### Offline Mode
If `OPENAI_API_KEY` is not set or empty, the system automatically falls back to **offline mode**:
- Only Tier 1 (BLIP) is available
- LLM Judge is skipped; quality gating uses CLIPScore only
- Refinements return the original caption
- VQA is disabled

---

## How It Works - Step by Step

1. **Image Upload** &rarr; User uploads image with style preference
2. **RAG Retrieval** &rarr; FAISS searches for similar past captions (text + image)
3. **Complexity Analysis** &rarr; OpenCV computes edge density, color variance, texture
4. **Tier Selection** &rarr; Complex images start at Tier 2; simple images at Tier 1
5. **Object Detection** &rarr; YOLOv8n detects objects, formats context string
6. **Caption Generation** &rarr; Selected model generates caption with style prompt + RAG context + object context
7. **Quality Evaluation** &rarr; CLIPScore + LLM Judge rate the caption
8. **Decision** &rarr; Pass? Go to refinement. Fail? Escalate to next tier (max 2 escalations)
9. **Refinement** &rarr; Generate alt-text + SEO variants
10. **Translation** &rarr; Translate to target language if not English
11. **Memory Storage** &rarr; Caption + embeddings stored in FAISS for future retrievals
12. **Analytics Logging** &rarr; Run metrics appended to JSONL for dashboard

---

## License

This project is for educational and research purposes.

---

Built with LangGraph, BLIP, GPT-4o, CLIP, FAISS, YOLOv8, FastAPI, and Gradio.
