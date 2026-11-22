"""
IMG Caption Platform — Professional SaaS UI
Design tokens, responsive layout, polished charts, no !important spam.
"""
from __future__ import annotations
import io, hashlib, uuid
import gradio as gr
import plotly.graph_objects as go
from PIL import Image
from app.agents.graph import get_caption_workflow
from app.agents.router import get_rag_memory
from app.config import settings
from app.styles.prompts import AVAILABLE_STYLES
from app.tracking import local_tracker
from app.vqa.conversation import VQAConversation
from app.agents.translation import translate_caption

vqa_engine = VQAConversation()

_TIER_COLOR = {1: "#059669", 2: "#2563eb", 3: "#7c3aed"}
_TIER_NAME = {1: "BLIP-L1", 2: "GPT-MINI", 3: "GPT-4O"}

_PIPELINE_NODES = [
    ("INPUT", "#2563eb"), ("RAG+CLIP", "#7c3aed"), ("COMPLEXITY", "#d97706"),
    ("YOLO", "#dc2626"), ("BLIP-L1", "#059669"), ("CRITIC", "#d97706"),
    ("GPT-MINI", "#2563eb"), ("CRITIC", "#d97706"),
    ("GPT-4O", "#7c3aed"), ("REFINE", "#059669"),
]

_STYLE_COLORS = {
    "descriptive": "#7c3aed", "creative": "#dc2626", "technical": "#2563eb",
    "concise": "#059669", "social_media": "#d97706",
}

# ─────────────────────────────────────────────────────────────────────────────
# CSS — Design Token System
# ─────────────────────────────────────────────────────────────────────────────
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
  --bg: #f8fafc; --surface: #ffffff; --border: #e2e8f0; --border-hover: #cbd5e1;
  --text: #0f172a; --text-secondary: #475569; --text-muted: #94a3b8;
  --primary: #2563eb; --primary-hover: #1d4ed8; --primary-bg: rgba(37,99,235,.06);
  --success: #059669; --success-bg: rgba(5,150,105,.06);
  --warning: #d97706; --warning-bg: rgba(217,119,6,.06);
  --danger: #dc2626; --danger-bg: rgba(220,38,38,.06);
  --purple: #7c3aed; --purple-bg: rgba(124,58,237,.06);
  --shadow-sm: 0 1px 2px rgba(0,0,0,.04);
  --shadow-md: 0 4px 12px rgba(0,0,0,.06);
  --shadow-lg: 0 8px 24px rgba(0,0,0,.08);
  --radius: 12px; --radius-sm: 8px; --radius-xs: 6px;
  --font: 'Inter',system-ui,-apple-system,sans-serif;
  --mono: 'JetBrains Mono',monospace;
}

@keyframes fadeIn { from{opacity:0;transform:translateY(6px)} to{opacity:1;transform:translateY(0)} }
@keyframes logIn { from{opacity:0;transform:translateX(-4px)} to{opacity:1;transform:translateX(0)} }
@keyframes shimmer { 0%{background-position:-200% 0} 100%{background-position:200% 0} }
@keyframes pulse-dot { 0%,100%{opacity:1} 50%{opacity:.4} }

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 0.01ms; transition-duration: 0.01ms; }
}

*, *::before, *::after { box-sizing: border-box; }

.gradio-container {
  background: var(--bg); font-family: var(--font); color: var(--text);
  max-width: 1320px; margin: 0 auto; padding: 0; min-height: 100vh;
}

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border-hover); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

/* ── Navbar ─────────────────────────────────────────────────────────── */
.gradio-container .tab-nav,
.gradio-container [role="tablist"] {
  position: sticky; top: 0; z-index: 600;
  height: 56px; padding: 0 2rem;
  background: rgba(255,255,255,.88); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  border: none; border-bottom: 1px solid var(--border);
  border-radius: 0;
  display: flex; align-items: center; gap: 0;
  overflow-x: auto; flex-wrap: nowrap;
  box-shadow: var(--shadow-sm);
}
.gradio-container .tab-nav::before,
.gradio-container [role="tablist"]::before {
  content: "IMG Caption";
  font-size: .82rem; font-weight: 800; letter-spacing: -.02em; color: var(--text);
  margin-right: 2.5rem; flex-shrink: 0; pointer-events: none; white-space: nowrap;
}
.gradio-container .tab-nav::after,
.gradio-container [role="tablist"]::after { display: none; }
.gradio-container .tab-nav button,
.gradio-container [role="tab"] {
  background: transparent; border: none;
  border-bottom: 2px solid transparent; border-radius: 0;
  height: 56px; padding: 0 1.1rem;
  font-size: .8rem; font-weight: 500; color: var(--text-muted);
  white-space: nowrap; cursor: pointer;
  transition: color .15s, border-color .15s; flex-shrink: 0;
}
.gradio-container .tab-nav button:hover,
.gradio-container [role="tab"]:hover { color: var(--text-secondary); }
.gradio-container .tab-nav button.selected,
.gradio-container [role="tab"][aria-selected="true"] {
  color: var(--primary); border-bottom-color: var(--primary); font-weight: 600;
}

/* ── Panels ─────────────────────────────────────────────────────────── */
.gradio-container .tabs > .tabitem,
.gradio-container [role="tabpanel"] {
  padding: 2rem 2rem; animation: fadeIn .25s ease both;
}
.gradio-container .tabs, .gradio-container .main { overflow: visible; }

/* ── Components ─────────────────────────────────────────────────────── */
.gradio-container .block { border-radius: var(--radius-sm); }
.gradio-container label > span,
.gradio-container .block > label > span,
.gradio-container .block label span {
  font-size: .72rem; font-weight: 600; color: var(--text-secondary);
  text-transform: uppercase; letter-spacing: .04em;
}

/* ── Inputs ─────────────────────────────────────────────────────────── */
.gradio-container textarea,
.gradio-container input[type=text] {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius-sm); color: var(--text);
  font-size: .88rem; line-height: 1.6; padding: .7rem .9rem;
  transition: border-color .15s, box-shadow .15s;
}
.gradio-container textarea:focus,
.gradio-container input[type=text]:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(37,99,235,.08); outline: none;
}
.gradio-container textarea::placeholder,
.gradio-container input::placeholder { color: var(--text-muted); font-size: .82rem; }

/* ── Image upload ───────────────────────────────────────────────────── */
.gradio-container .gr-image,
.gradio-container [data-testid="image"],
.gradio-container .image-container {
  border: 1px solid var(--border); border-radius: var(--radius);
  background: var(--surface); overflow: hidden;
  transition: border-color .15s, box-shadow .15s;
}
.gradio-container .gr-image:hover,
.gradio-container [data-testid="image"]:hover {
  border-color: var(--border-hover); box-shadow: var(--shadow-md);
}

/* ── Buttons ────────────────────────────────────────────────────────── */
.gradio-container button.primary {
  background: var(--primary); border: 1px solid var(--primary);
  border-radius: var(--radius-sm); color: #ffffff;
  font-size: .82rem; font-weight: 600; padding: .65rem 1.4rem;
  cursor: pointer; transition: all .15s;
  box-shadow: 0 1px 2px rgba(37,99,235,.2);
}
.gradio-container button.primary:hover {
  background: var(--primary-hover); border-color: var(--primary-hover);
  box-shadow: 0 4px 12px rgba(37,99,235,.2); transform: translateY(-1px);
}
.gradio-container button.primary:active { transform: translateY(0); }
.gradio-container button.secondary {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius-sm); color: var(--text-secondary);
  font-size: .8rem; font-weight: 500; transition: all .15s;
}
.gradio-container button.secondary:hover {
  background: var(--bg); border-color: var(--border-hover); color: var(--text);
}

/* ── Chatbot ────────────────────────────────────────────────────────── */
.gradio-container .gr-chatbot, .gradio-container .chatbot {
  background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
}

/* ── Plots ──────────────────────────────────────────────────────────── */
.gradio-container .gr-plot {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); overflow: hidden;
  padding: .75rem; transition: box-shadow .15s;
}
.gradio-container .gr-plot:hover { box-shadow: var(--shadow-md); }
.gradio-container .plotly, .gradio-container .js-plotly-plot { background: transparent; }

/* ── Loading ────────────────────────────────────────────────────────── */
.gradio-container .generating {
  background: linear-gradient(90deg, rgba(37,99,235,0), rgba(37,99,235,.06), rgba(37,99,235,0));
  background-size: 200%; animation: shimmer 1.4s infinite;
}

/* ── KPI Cards (CSS hover) ──────────────────────────────────────────── */
.kpi-card {
  transition: box-shadow .2s, transform .2s;
}
.kpi-card:hover {
  box-shadow: var(--shadow-md); transform: translateY(-2px);
}

/* ── Feature Cards (CSS hover) ──────────────────────────────────────── */
.feature-card {
  transition: box-shadow .2s, transform .2s;
}
.feature-card:hover {
  box-shadow: var(--shadow-md); transform: translateY(-1px);
}

/* ── Copy button ────────────────────────────────────────────────────── */
.copy-btn {
  background: var(--bg); border: 1px solid var(--border); border-radius: var(--radius-xs);
  color: var(--text-muted); font-size: .68rem; font-weight: 600; font-family: var(--mono);
  padding: 2px 8px; cursor: pointer; transition: all .15s; text-transform: uppercase;
  letter-spacing: .03em;
}
.copy-btn:hover { background: var(--surface); border-color: var(--border-hover); color: var(--text-secondary); }

/* ── Responsive ─────────────────────────────────────────────────────── */
@media (max-width: 768px) {
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
  .pipeline-flow { gap: 4px; }
  .gradio-container .tab-nav, .gradio-container [role="tablist"] { padding: 0 1rem; }
  .gradio-container .tabs > .tabitem, .gradio-container [role="tabpanel"] { padding: 1.2rem 1rem; }
}
"""

# ─────────────────────────────────────────────────────────────────────────────
# JavaScript
# ─────────────────────────────────────────────────────────────────────────────
JS = """
function copyText(el) {
  const text = el.closest('[data-copy]').querySelector('.copy-target').textContent;
  navigator.clipboard.writeText(text).then(function() {
    var prev = el.textContent; el.textContent = 'Copied!';
    setTimeout(function() { el.textContent = prev; }, 1500);
  });
}
"""

# ─────────────────────────────────────────────────────────────────────────────
# Chart base
# ─────────────────────────────────────────────────────────────────────────────
_CB = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter,system-ui,sans-serif", color="#475569", size=12),
    title_font=dict(family="Inter,system-ui,sans-serif", size=14, color="#0f172a"),
    title_x=0.0,
    margin=dict(t=52, b=44, l=52, r=24),
    hoverlabel=dict(
        bgcolor="#1e293b", font_color="#f8fafc", font_size=12,
        font_family="Inter,system-ui,sans-serif", bordercolor="rgba(0,0,0,0)",
    ),
)
_CB_AXIS = dict(
    gridcolor="#f0f4f8", linecolor="#e2e8f0",
    tickcolor="#94a3b8", tickfont=dict(size=11, color="#64748b"),
    title_font=dict(size=11, color="#94a3b8"),
)
_CB_LEGEND = dict(bgcolor="rgba(0,0,0,0)",
                  font=dict(color="#475569", size=11))


def _chart_base_layout(fig, title: str, **extra):
    fig.update_layout(**_CB, title_text=title, **extra)
    fig.update_layout(xaxis=_CB_AXIS, yaxis=_CB_AXIS, legend=_CB_LEGEND)


# ─────────────────────────────────────────────────────────────────────────────
# HTML helpers
# ─────────────────────────────────────────────────────────────────────────────

def _rgba(hex_color: str, alpha: float) -> str:
    r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
    return f"rgba({r},{g},{b},{alpha})"


def _badge(text: str, color: str) -> str:
    bg = _rgba(color, 0.08)
    bc = _rgba(color, 0.18)
    return (
        f'<span style="display:inline-flex;align-items:center;gap:5px;'
        f'background:{bg};border:1px solid {bc};'
        f'border-radius:var(--radius-xs);padding:3px 10px;font-size:.72rem;font-weight:600;'
        f'color:{color};font-family:var(--mono);'
        f'letter-spacing:.02em;white-space:nowrap;">'
        f'<span style="width:5px;height:5px;border-radius:50%;background:{color};'
        f'display:inline-block;flex-shrink:0;"></span>{text}</span>'
    )


def _sec_head(title: str, badge: str = "", bc: str = "#059669") -> str:
    b = _badge(badge, bc) if badge else ""
    return (
        f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:1rem;">'
        f'<span style="font-size:.72rem;letter-spacing:.06em;'
        f'text-transform:uppercase;color:var(--text-muted);font-weight:600;">{title}</span>{b}</div>'
    )


def _divider() -> str:
    return '<div style="height:1px;margin:1.5rem 0;background:var(--border);"></div>'


def _copy_btn() -> str:
    return '<button class="copy-btn" onclick="copyText(this)">Copy</button>'


def _hero_html() -> str:
    mode_text = "Online" if settings.has_openai else "Offline"
    mode_color = "#059669" if settings.has_openai else "#d97706"
    return f"""
<div style="padding:2.5rem 0 1.5rem;">
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:1.5rem;flex-wrap:wrap;">
    {_badge(mode_text, mode_color)}
    {_badge("BLIP Ready", "#059669")}
    {_badge("FAISS Memory", "#7c3aed")}
    {_badge("v2.0", "#2563eb")}
  </div>

  <div style="font-size:.72rem;letter-spacing:.08em;text-transform:uppercase;
              color:var(--primary);font-weight:600;margin-bottom:.5rem;">
    Multi-Agent Vision Platform
  </div>

  <h1 style="font-size:clamp(1.8rem,4vw,2.6rem);font-weight:800;
             color:var(--text);line-height:1.1;margin:0 0 .8rem;letter-spacing:-.02em;">
    Agentic Image<br>
    <span style="color:var(--primary);">Intelligence</span>
  </h1>

  <p style="font-size:.9rem;color:var(--text-secondary);line-height:1.8;max-width:560px;margin:0 0 1.2rem;">
    Self-evaluating multi-agent pipeline. Routes between BLIP local, GPT-4o-mini,
    and GPT-4o using dual quality gates: CLIP cosine similarity + LLM-as-Judge.
    Persistent FAISS semantic memory across sessions.
  </p>

  <div style="display:flex;gap:6px;flex-wrap:wrap;">
    {_badge("LangGraph", "#7c3aed")}
    {_badge("FAISS + SBERT", "#2563eb")}
    {_badge("CLIP Score", "#059669")}
    {_badge("YOLOv8", "#dc2626")}
    {_badge("FastAPI", "#d97706")}
  </div>
</div>"""


def _kpi_cards_html(stats: dict) -> str:
    n = stats.get("total_runs", 0)
    avg_clip = stats.get("avg_clip_score", 0.0)
    total_cost = stats.get("total_cost", 0.0)
    tu = stats.get("tier_usage", {})
    t1_pct = (tu.get("1", 0) / max(n, 1)) * 100

    cards = [
        ("Images", str(n) if n else "--", "Processed", "#2563eb"),
        ("Quality", f"{avg_clip:.3f}" if n else "--", "Avg CLIP Score", "#7c3aed"),
        ("Cost", f"${total_cost:.4f}" if n else "--", "Total API Spend", "#dc2626"),
        ("Local", f"{t1_pct:.0f}%" if n else "--", "Via BLIP", "#059669"),
    ]
    html = '<div class="kpi-grid" style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:1rem 0;">'
    for code, val, label, color in cards:
        html += f"""
<div class="kpi-card" style="background:var(--surface);border:1px solid var(--border);
            border-top:3px solid {color};border-radius:var(--radius);padding:1.3rem 1.4rem;">
  <div style="font-size:.68rem;font-weight:600;color:{color};text-transform:uppercase;
              letter-spacing:.05em;margin-bottom:.7rem;">{code}</div>
  <div style="font-size:2rem;font-weight:900;color:var(--text);line-height:1;
              margin-bottom:.35rem;font-family:var(--font);">{val}</div>
  <div style="font-size:.75rem;color:var(--text-muted);">{label}</div>
</div>"""
    html += "</div>"
    return html


def _pipeline_html() -> str:
    arrow = ('<svg width="14" height="14" viewBox="0 0 16 16" style="flex-shrink:0;opacity:.4;">'
             '<path d="M6 3l5 5-5 5" stroke="#94a3b8" stroke-width="1.5" fill="none" '
             'stroke-linecap="round" stroke-linejoin="round"/></svg>')
    html = f"""
<div style="background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:1.2rem 1.5rem;">
  <div style="display:flex;align-items:center;gap:10px;margin-bottom:1rem;">
    <span style="font-size:.72rem;font-weight:600;text-transform:uppercase;
                 color:var(--text-muted);letter-spacing:.04em;">Pipeline Flow</span>
    {_badge("Active", "#059669")}
  </div>
  <div class="pipeline-flow" style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;">
"""
    for i, (name, color) in enumerate(_PIPELINE_NODES):
        html += f"""
    <div style="display:inline-flex;align-items:center;gap:5px;
                background:{_rgba(color, 0.06)};border:1px solid {_rgba(color, 0.15)};
                border-radius:var(--radius-xs);padding:5px 12px;
                font-family:var(--mono);font-size:.7rem;
                font-weight:600;color:{color};white-space:nowrap;">
      <span style="width:5px;height:5px;border-radius:50%;background:{color};flex-shrink:0;"></span>
      {name}
    </div>"""
        if i < len(_PIPELINE_NODES) - 1:
            html += arrow
    html += "\n  </div>\n</div>"
    return html


def _meta_chips_html(model: str, latency_ms: float, cost: float,
                     tier: int) -> str:
    tc = _TIER_COLOR.get(tier, "#059669")
    tn = _TIER_NAME.get(tier, f"TIER-{tier}")
    chips = [
        (f"Tier {tier} — {tn}", tc),
        (f"{latency_ms/1000:.1f}s", "#2563eb"),
        (f"${cost:.4f}", "#d97706"),
    ]
    html = '<div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:.5rem;">'
    for text, color in chips:
        html += (
            f'<span style="font-family:var(--mono);font-size:.72rem;'
            f'font-weight:600;color:{color};background:{_rgba(color, 0.06)};'
            f'border:1px solid {_rgba(color, 0.12)};border-radius:var(--radius-xs);'
            f'padding:3px 10px;">{text}</span>'
        )
    html += "</div>"
    return html


def _confidence_html(score: float, explanation: str) -> str:
    if score >= 80:
        color, label = "#059669", "High"
    elif score >= 50:
        color, label = "#d97706", "Moderate"
    else:
        color, label = "#dc2626", "Low"
    return f"""
<div style="padding:12px 14px;border-bottom:1px solid #f1f5f9;">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
    <span style="font-size:.68rem;font-weight:600;text-transform:uppercase;
                 color:var(--text-muted);letter-spacing:.04em;">Confidence</span>
    <div style="display:flex;align-items:center;gap:8px;">
      <span style="font-family:var(--mono);font-size:.9rem;font-weight:700;color:{color};">
        {score:.0f}/100</span>
      <span style="font-size:.65rem;font-weight:600;color:{color};
                   background:{_rgba(color, 0.08)};border:1px solid {_rgba(color, 0.18)};
                   border-radius:4px;padding:1px 7px;text-transform:uppercase;
                   letter-spacing:.03em;">{label}</span>
    </div>
  </div>
  <div style="height:5px;background:#f1f5f9;border-radius:3px;overflow:hidden;">
    <div style="height:100%;width:{min(score, 100):.0f}%;background:{color};
                border-radius:3px;transition:width .6s ease;"></div>
  </div>
  <div style="font-size:.75rem;color:var(--text-muted);margin-top:8px;line-height:1.6;">
    {explanation}</div>
</div>"""


def _metrics_table_html(critic, caption, tier, model, cost,
                        latency_ms, confidence_score=0.0,
                        confidence_explanation="") -> str:
    clip = critic.get("clip_score", 0.0)
    j = critic.get("judge_scores", {})
    ovr = j.get("overall", 0)
    passes = critic.get("passes", False)
    reason = j.get("reason", "")
    thr = max(settings.clip_score_threshold, 0.01)
    comb = (min(clip / thr, 1.0) + ovr / 10) / 2

    tc = _TIER_COLOR.get(tier, "#059669")
    tn = _TIER_NAME.get(tier, f"TIER-{tier}")
    vc = "#059669" if passes else "#d97706"
    vt = "Accepted" if passes else "Escalated"

    rows = [
        ("Combined", f"{comb:.4f}", "#2563eb"),
        ("CLIP", f"{clip:.4f}", "#7c3aed"),
        ("LLM Judge", f"{ovr}/10", "#d97706"),
        ("Verdict", vt, vc),
    ]
    rows_html = ""
    for m, v, c in rows:
        if m == "Verdict":
            val_html = (
                f'<span style="font-family:var(--mono);'
                f'font-size:.78rem;font-weight:700;color:{c};">{v}</span>'
            )
        else:
            val_html = (
                f'<span style="font-family:var(--mono);'
                f'font-size:.78rem;font-weight:600;color:{c};'
                f'background:{_rgba(c, 0.06)};border:1px solid {_rgba(c, 0.12)};'
                f'border-radius:4px;padding:1px 8px;">{v}</span>'
            )
        rows_html += (
            f'<tr style="transition:background .1s;"'
            f' onmouseover="this.style.background=\'#f8fafc\'"'
            f' onmouseout="this.style.background=\'transparent\'">'
            f'<td style="padding:9px 14px;font-size:.73rem;font-weight:600;'
            f'color:var(--text-muted);text-transform:uppercase;letter-spacing:.03em;'
            f'border-bottom:1px solid #f1f5f9;">{m}</td>'
            f'<td style="padding:9px 14px;border-bottom:1px solid #f1f5f9;">'
            f'{val_html}</td></tr>'
        )

    reason_html = ""
    if reason:
        reason_html = (
            f'<div style="padding:.7rem 1rem;font-size:.78rem;color:var(--text-secondary);'
            f'line-height:1.6;border-bottom:1px solid #f1f5f9;">{reason}</div>'
        )

    conf_html = _confidence_html(confidence_score, confidence_explanation) if confidence_score > 0 else ""

    return f"""
<div style="background:var(--surface);border:1px solid var(--border);border-top:3px solid {tc};
            border-radius:var(--radius);overflow:hidden;height:100%;">
  <div style="padding:10px 14px;border-bottom:1px solid #f1f5f9;">
    <span style="font-size:.78rem;font-weight:700;color:{tc};">
      Tier {tier} — {tn}</span>
  </div>
  {conf_html}
  <div style="margin:.7rem;padding:.7rem 1rem;border-left:3px solid {tc};
              background:{_rgba(tc, 0.04)};border-radius:0 var(--radius-sm) var(--radius-sm) 0;
              font-size:.95rem;color:var(--text);line-height:1.7;">{caption}</div>
  <table style="width:100%;border-collapse:collapse;">
    <thead><tr>
      <th style="padding:8px 14px;text-align:left;font-size:.66rem;font-weight:600;
                 text-transform:uppercase;color:var(--text-muted);letter-spacing:.05em;
                 border-bottom:1px solid #f1f5f9;">Metric</th>
      <th style="padding:8px 14px;text-align:left;font-size:.66rem;font-weight:600;
                 text-transform:uppercase;color:var(--text-muted);letter-spacing:.05em;
                 border-bottom:1px solid #f1f5f9;">Value</th>
    </tr></thead>
    <tbody>{rows_html}</tbody>
  </table>
  {reason_html}
  <div style="padding:.7rem 1rem;border-top:1px solid #f1f5f9;
              display:flex;flex-wrap:wrap;gap:14px;font-size:.76rem;">
    <span><span style="color:var(--text-muted);font-weight:500;">Model</span>
      <span style="color:{tc};font-weight:600;margin-left:4px;">{model.upper() if model else "--"}</span></span>
    <span><span style="color:var(--text-muted);font-weight:500;">Cost</span>
      <span style="color:#d97706;font-weight:600;margin-left:4px;">${cost:.4f}</span></span>
    <span><span style="color:var(--text-muted);font-weight:500;">Time</span>
      <span style="color:var(--primary);font-weight:600;margin-left:4px;">{latency_ms:.0f}ms</span></span>
  </div>
</div>"""


def _agent_log_html(lines: list) -> str:
    if not lines:
        content = (
            '<div style="font-family:var(--mono);font-size:.76rem;'
            'color:var(--text-muted);">// Awaiting generation...</div>'
        )
    else:
        content = ""
        for i, line in enumerate(lines):
            delay = f"{i * 0.07:.2f}s"
            if any(k in line for k in ("PASSED", "Accepted", "Stored", "Memory")):
                color = "#059669"
            elif any(k in line for k in ("FAILED", "Escalat", "escalating")):
                color = "#d97706"
            elif "Error" in line:
                color = "#dc2626"
            elif any(k in line for k in ("RAG:", "retrieved", "Retrieved")):
                color = "#2563eb"
            elif "Tier" in line or "tier" in line:
                color = "#7c3aed"
            elif "Confidence" in line:
                color = "#059669"
            elif "YOLO" in line or "Complexity" in line:
                color = "#d97706"
            else:
                color = "var(--text-secondary)"
            num = f'<span style="color:var(--text-muted);user-select:none;min-width:1.6em;display:inline-block;">{i+1:02d}</span> '
            content += (
                f'<div style="font-family:var(--mono);'
                f'font-size:.73rem;color:{color};line-height:2;'
                f'white-space:pre-wrap;opacity:0;'
                f'animation:logIn .2s ease {delay} forwards;">'
                f'{num}{line}</div>'
            )

    return f"""
<div style="background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);
            overflow:hidden;height:100%;">
  <div style="padding:10px 14px;border-bottom:1px solid #f1f5f9;
              display:flex;justify-content:space-between;align-items:center;">
    <div style="display:flex;align-items:center;gap:7px;">
      <span style="width:6px;height:6px;border-radius:50%;background:#059669;
                   display:inline-block;animation:pulse-dot 2s ease infinite;"></span>
      <span style="font-size:.7rem;font-weight:600;text-transform:uppercase;
                   color:var(--text-muted);letter-spacing:.05em;">Agent Log</span>
    </div>
    <span style="font-family:var(--mono);font-size:.65rem;
                 color:var(--text-muted);letter-spacing:.08em;">LIVE</span>
  </div>
  <div style="padding:.8rem 1rem;background:#f8fafc;min-height:200px;max-height:340px;overflow-y:auto;">
    {content}
  </div>
</div>"""


def _style_var_html(variations: dict) -> str:
    if not variations:
        return ""
    html = """
<div style="background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);
            margin-top:.75rem;">
  <div style="padding:10px 14px;border-bottom:1px solid #f1f5f9;
              display:flex;justify-content:space-between;align-items:center;">
    <span style="font-size:.7rem;font-weight:600;text-transform:uppercase;
                 color:var(--text-muted);letter-spacing:.05em;">Style Variations</span>
    <span style="color:var(--text-muted);font-size:.72rem;">5 modes</span>
  </div>
  <div style="padding:1rem;display:flex;flex-direction:column;gap:.8rem;">"""
    for style, text in variations.items():
        color = _STYLE_COLORS.get(style, "#475569")
        label = style.replace("_", " ").title()
        html += f"""
<div data-copy>
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.35rem;">
    <span style="font-size:.7rem;color:{color};font-weight:600;">{label}</span>
    {_copy_btn()}
  </div>
  <div class="copy-target" style="border-left:3px solid {color};padding:.6rem .9rem;
              background:{_rgba(color, 0.03)};border-radius:0 var(--radius-sm) var(--radius-sm) 0;
              font-size:.85rem;color:var(--text-secondary);line-height:1.7;">{text}</div>
</div>"""
    html += "\n  </div>\n</div>"
    return html


def _refinements_html(refinements: dict) -> str:
    if not refinements:
        return ""
    alt_text = refinements.get("alt_text", "")
    seo = refinements.get("seo", "")
    if not alt_text and not seo:
        return ""
    cfg = [
        ("⚙ Alt-Text", alt_text, "#7c3aed", "Accessibility-optimized"),
        ("↑ SEO", seo, "#2563eb", "Search-optimized"),
    ]
    html = (
        '<div style="background:var(--surface);border:1px solid var(--border);'
        'border-radius:var(--radius);margin-top:.75rem;overflow:hidden;">'
        '<div style="padding:10px 14px;border-bottom:1px solid #f1f5f9;'
        'display:flex;align-items:center;gap:8px;">'
        '<span style="font-size:.7rem;font-weight:600;text-transform:uppercase;'
        'color:var(--text-muted);letter-spacing:.05em;">Refinements</span>'
        + _badge("AI", "#7c3aed")
        + '</div><div style="padding:1rem;display:flex;flex-direction:column;gap:.8rem;">'
    )
    for label, text, color, hint in cfg:
        if text:
            html += (
                f'<div data-copy>'
                f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.35rem;">'
                f'<div style="display:flex;align-items:center;gap:8px;">'
                f'<span style="font-size:.7rem;color:{color};font-weight:600;">{label}</span>'
                f'<span style="font-size:.62rem;color:var(--text-muted);font-weight:500;">{hint}</span>'
                f'</div>'
                f'{_copy_btn()}'
                f'</div>'
                f'<div class="copy-target" style="border-left:3px solid {color};padding:.6rem .9rem;'
                f'background:{_rgba(color, 0.03)};border-radius:0 var(--radius-sm) var(--radius-sm) 0;'
                f'font-size:.85rem;color:var(--text-secondary);line-height:1.7;">{text}</div>'
                f'</div>'
            )
    html += '</div></div>'
    return html


def _translation_html(translated: str, language: str) -> str:
    if not translated or language == "English":
        return ""
    color = "#d97706"
    return (
        '<div style="background:var(--surface);border:1px solid var(--border);'
        'border-radius:var(--radius);margin-top:.75rem;overflow:hidden;">'
        '<div style="padding:10px 14px;border-bottom:1px solid #f1f5f9;'
        'display:flex;align-items:center;gap:8px;">'
        '<span style="font-size:.7rem;font-weight:600;text-transform:uppercase;'
        'color:var(--text-muted);letter-spacing:.05em;">Translation</span>'
        + _badge(language, color)
        + '</div><div style="padding:1rem;" data-copy>'
        f'<div style="display:flex;justify-content:flex-end;margin-bottom:.35rem;">{_copy_btn()}</div>'
        f'<div class="copy-target" style="border-left:3px solid {color};padding:.6rem .9rem;'
        f'background:{_rgba(color, 0.03)};border-radius:0 var(--radius-sm) var(--radius-sm) 0;'
        f'font-size:.85rem;color:var(--text-secondary);line-height:1.7;">{translated}</div>'
        '</div></div>'
    )


def _about_html() -> str:
    features = [
        ("[01]", "3-Tier Routing", "BLIP → GPT-4o-mini → GPT-4o with auto-escalation", "#2563eb"),
        ("[02]", "Dual Quality Gates", "CLIPScore + LLM-as-Judge (threshold gated)", "#7c3aed"),
        ("[03]", "FAISS RAG Memory", "SentenceTransformer + CLIP dual-index retrieval", "#059669"),
        ("[04]", "5 Caption Styles", "Descriptive, Creative, Technical, Concise, Social", "#d97706"),
        ("[05]", "Visual QA", "Multi-turn GPT-4o-mini conversation on images", "#dc2626"),
        ("[06]", "Smart Routing", "OpenCV complexity analysis for intelligent tier selection", "#2563eb"),
        ("[07]", "Object Detection", "YOLOv8n pre-pass for scene-aware captioning", "#7c3aed"),
        ("[08]", "Caption Refinement", "Alt-text + SEO variants, multi-language output", "#059669"),
    ]
    cards = "".join(
        f'<div class="feature-card" style="background:var(--surface);border:1px solid var(--border);'
        f'border-top:3px solid {c};border-radius:var(--radius);padding:1.2rem;">'
        f'<div style="font-family:var(--mono);font-size:.68rem;'
        f'color:{c};font-weight:600;margin-bottom:.5rem;">{n}</div>'
        f'<div style="font-size:.85rem;font-weight:700;color:var(--text);'
        f'margin-bottom:.3rem;">{t}</div>'
        f'<div style="font-size:.78rem;color:var(--text-secondary);line-height:1.6;">{d}</div></div>'
        for n, t, d, c in features
    )
    return f"""
<div style="max-width:960px;">
  <div style="margin-bottom:1.5rem;">
    {_sec_head("Documentation", "v2.0", "#2563eb")}
    <h1 style="font-size:1.5rem;font-weight:800;color:var(--text);
               margin:0 0 .6rem;letter-spacing:-.02em;">
      Platform Architecture
    </h1>
    <p style="font-size:.88rem;color:var(--text-secondary);line-height:1.8;max-width:560px;margin:0;">
      Production-grade multi-agent image captioning platform.
      3-tier model routing with FAISS semantic memory and dual-gate quality control.
    </p>
  </div>
  {_divider()}
  <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));
              gap:12px;margin-bottom:1.5rem;">{cards}</div>
  {_divider()}
  <div style="background:var(--surface);border:1px solid var(--border);border-left:3px solid var(--primary);
              border-radius:var(--radius);padding:1.3rem;">
    <div style="font-size:.7rem;font-weight:600;text-transform:uppercase;
                color:var(--text-muted);letter-spacing:.05em;margin-bottom:.8rem;">
      LangGraph Decision Flow
    </div>
    <pre style="font-family:var(--mono);font-size:.76rem;
                color:var(--text-secondary);line-height:2;margin:0;white-space:pre-wrap;">
route_node
  |- RAG context retrieval (FAISS + CLIP dual-index)
  |- Image complexity analysis (OpenCV)
  |- Smart tier selection

detect_objects_node
  |- YOLOv8n object detection pre-pass
  |- Structured context injection

generate_caption_node
  |- Tier 1: BLIP local inference
  |- Tier 2: GPT-4o-mini (if escalated)
  |- Tier 3: GPT-4o (if escalated again)

critique_node
  |- CLIPScore cosine similarity
  |- LLM-as-Judge (GPT-4o-mini, threshold=7)
  |- Confidence scoring (0-100)
  |- [PASS] → refine_node → END
  |- [FAIL + tier&lt;3] → escalate_node → generate_caption_node</pre>
  </div>
</div>"""


# ─────────────────────────────────────────────────────────────────────────────
# Plotly charts
# ─────────────────────────────────────────────────────────────────────────────

def _chart_tier(stats: dict) -> go.Figure:
    tu = stats.get("tier_usage", {})
    lmap = {"1": "BLIP-L1", "2": "GPT-Mini", "3": "GPT-4o"}
    labels = [lmap.get(k, f"Tier {k}") for k in tu]
    values = list(tu.values())
    colors = ["#059669", "#2563eb", "#7c3aed"]
    total = sum(values)
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=.65,
        marker=dict(colors=colors[:len(values)],
                    line=dict(color="#ffffff", width=2.5)),
        textfont=dict(size=11, color="#475569"),
        hovertemplate="<b>%{label}</b><br>Runs: %{value}<br>"
                      "%{percent}<extra></extra>",
    ))
    fig.add_annotation(
        text=f"<b style='font-size:24px;color:#0f172a;'>{total}</b><br>"
             f"<span style='font-size:10px;color:#94a3b8;'>TOTAL</span>",
        x=.5, y=.5, showarrow=False,
        font=dict(size=14, color="#0f172a"),
    )
    if total == 0:
        fig.add_annotation(
            text="<span style='color:#94a3b8;'>No data yet</span>",
            x=.5, y=.5, showarrow=False, font=dict(size=12),
        )
    _chart_base_layout(fig, "Tier Distribution", showlegend=True)
    fig.update_layout(legend=dict(
        orientation="h", x=.5, xanchor="center", y=-.08,
        bgcolor="rgba(0,0,0,0)", font=dict(size=11, color="#475569"),
    ))
    return fig


def _chart_quality(stats: dict) -> go.Figure:
    runs = stats.get("recent_runs", [])
    fig = go.Figure()
    if not runs:
        _chart_base_layout(fig, "Quality Scores")
        fig.add_annotation(text="<span style='color:#94a3b8;'>No data yet</span>",
                           x=.5, y=.5, xref="paper", yref="paper", showarrow=False)
        return fig
    xs = [f"#{i+1}" for i in range(len(runs))]
    ys = [r.get("clip_score", 0) for r in runs]
    tier_colors = [_TIER_COLOR.get(r.get("tier", 1), "#059669") for r in runs]
    fig.add_trace(go.Bar(
        x=xs, y=ys, name="CLIP Score",
        marker=dict(color=tier_colors, line=dict(color="rgba(0,0,0,0)"), opacity=0.85),
        text=[f"{y:.2f}" for y in ys], textposition="outside",
        textfont=dict(size=9, color="#64748b"),
        hovertemplate="Run %{x}<br>CLIP: %{y:.4f}<extra></extra>",
    ))
    fig.add_hline(
        y=settings.clip_score_threshold,
        line=dict(color="#dc2626", width=1.5, dash="dash"),
        annotation_text=f"Threshold ({settings.clip_score_threshold})",
        annotation_font_color="#dc2626", annotation_font_size=10,
        annotation_position="top right",
    )
    _chart_base_layout(fig, "Quality Scores", bargap=.3, showlegend=False)
    y_max = max(max(ys) * 1.15, 1.05) if ys else 1.05
    fig.update_layout(
        xaxis=dict(**_CB_AXIS, title_text="Run"),
        yaxis=dict(range=[0, y_max], **_CB_AXIS, title_text="CLIP Score"),
    )
    return fig


def _chart_cost_cum(stats: dict) -> go.Figure:
    runs = stats.get("recent_runs", [])
    fig = go.Figure()
    if not runs:
        _chart_base_layout(fig, "Cumulative Cost")
        fig.add_annotation(text="<span style='color:#94a3b8;'>No data yet</span>",
                           x=.5, y=.5, xref="paper", yref="paper", showarrow=False)
        return fig
    xs, cum, s = [], [], 0
    for i, r in enumerate(runs):
        s += r.get("cost_usd", 0)
        xs.append(f"#{i+1}")
        cum.append(s)
    fig.add_trace(go.Scatter(
        x=xs, y=cum, mode="lines+markers",
        fill="tozeroy", fillcolor="rgba(37,99,235,.10)",
        line=dict(color="#2563eb", width=2.5, shape="spline"),
        marker=dict(size=6, color="#2563eb"),
        hovertemplate="Run %{x}<br>Total: $%{y:.4f}<extra></extra>",
    ))
    _chart_base_layout(fig, "Cumulative Cost", showlegend=False)
    fig.update_layout(
        xaxis=dict(**_CB_AXIS, title_text="Run"),
        yaxis=dict(tickprefix="$", **_CB_AXIS, title_text="Cumulative ($)"),
    )
    return fig


def _chart_style_usage(stats: dict) -> go.Figure:
    su = stats.get("style_usage", {})
    labels = list(su.keys())
    values = list(su.values())
    total = sum(values) or 1
    colors = [_STYLE_COLORS.get(l, "#475569") for l in labels]
    text_labels = [f"{v} ({v/total*100:.0f}%)" for v in values]
    fig = go.Figure(go.Bar(
        x=values, y=labels, orientation="h",
        marker=dict(color=colors, line=dict(color="rgba(0,0,0,0)"), opacity=0.85),
        text=text_labels, textposition="outside",
        textfont=dict(color="#475569", size=10),
        hovertemplate="<b>%{y}</b>: %{x} runs<extra></extra>",
    ))
    _chart_base_layout(fig, "Style Usage", bargap=.35, showlegend=False)
    fig.update_layout(
        xaxis=dict(**_CB_AXIS, title_text="Runs"),
        yaxis=dict(categoryorder="total ascending", **_CB_AXIS),
    )
    return fig


def _chart_latency(stats: dict) -> go.Figure:
    runs = stats.get("recent_runs", [])
    fig = go.Figure()
    if not runs:
        _chart_base_layout(fig, "Response Latency")
        fig.add_annotation(text="<span style='color:#94a3b8;'>No data yet</span>",
                           x=.5, y=.5, xref="paper", yref="paper", showarrow=False)
        return fig
    xs = [f"#{i+1}" for i in range(len(runs))]
    lat = [r.get("latency_ms", 0) for r in runs]
    costs = [r.get("cost_usd", 0) for r in runs]
    bar_colors = [
        "#059669" if l < 1000 else "#d97706" if l < 3000 else "#dc2626" for l in lat
    ]
    fig.add_trace(go.Bar(
        x=xs, y=lat, name="Latency",
        marker=dict(color=bar_colors, line=dict(color="rgba(0,0,0,0)"), opacity=0.85),
        customdata=costs,
        hovertemplate="Run %{x}<br>Latency: %{y:.0f}ms<br>Cost: $%{customdata:.4f}<extra></extra>",
    ))
    _chart_base_layout(fig, "Response Latency", bargap=.3, showlegend=False)
    fig.update_layout(
        xaxis=dict(**_CB_AXIS, title_text="Run"),
        yaxis=dict(**_CB_AXIS, title_text="Latency (ms)"),
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Event handlers
# ─────────────────────────────────────────────────────────────────────────────

def _pil_from_numpy(arr):
    pil = Image.fromarray(arr)
    buf = io.BytesIO()
    pil.save(buf, format="JPEG", quality=85)
    b = buf.getvalue()
    return pil, b, hashlib.md5(b).hexdigest()


_EMPTY_METRICS = (
    '<div style="background:var(--surface);border:1px solid var(--border);'
    'border-radius:var(--radius);padding:2rem;color:var(--text-muted);'
    'font-family:var(--mono);font-size:.76rem;'
    'min-height:200px;display:flex;align-items:center;'
    'justify-content:center;">Metrics will appear after generation</div>'
)


def generate_caption(image, style: str, language: str = "English"):
    if image is None:
        return ("Upload an image first.", "", _EMPTY_METRICS,
                _agent_log_html([]), "", "")

    pil, byt, img_hash = _pil_from_numpy(image)
    try:
        workflow = get_caption_workflow()
        result = workflow.invoke(
            {"image": pil, "image_bytes": byt, "style": style},
            {"recursion_limit": 25},
        )
    except Exception as exc:
        err_log = _agent_log_html(
            [f"Error: {exc}", "Pipeline failed — check logs"])
        err_metrics = (
            '<div style="background:var(--surface);border:1px solid #fecaca;'
            'border-radius:var(--radius);padding:1.5rem;color:#dc2626;'
            'font-family:var(--mono);font-size:.76rem;">'
            f'Pipeline error: {exc}</div>'
        )
        return f"Error: {exc}", "", err_metrics, err_log, "", ""

    critic = result.get("critic_result", {})
    clip_score = critic.get("clip_score", 0.0)
    j = critic.get("judge_scores", {})
    judge_score = j.get("overall", 0)
    history = result.get("history", [])
    final_model = history[-1]["model"] if history else "BLIP"
    final_tier = history[-1]["tier"] if history else 1
    total_lat = result.get("total_latency", 0.0)
    total_cost = result.get("total_cost", 0.0)
    esc_count = result.get("escalation_count", 0)
    caption = result.get("caption", "")

    complexity_score = result.get("complexity_score", 0.0)
    complexity_label = result.get("complexity_label", "medium")
    object_context = result.get("object_context", "")
    confidence_score = result.get("confidence_score", 0.0)
    confidence_explanation = result.get("confidence_explanation", "")
    refinements = result.get("refinements", {})

    translated = translate_caption(caption, language)
    translated_caption = translated if language != "English" else ""

    rag = get_rag_memory()
    rag.add_caption(
        image_hash=img_hash, caption=caption, style=style,
        model_name=final_model, clip_score=clip_score,
        image=pil,
    )
    local_tracker.log_run(
        model_name=final_model, style=style, tier_used=final_tier,
        clip_score=clip_score, judge_score=judge_score,
        latency_ms=total_lat, cost_usd=total_cost,
        escalation_count=esc_count, caption_length=len(caption),
        image_hash=img_hash,
    )

    n_total = rag.index.ntotal
    n_retrieved = min(3, n_total - 1) if n_total > 1 else 0
    passes = critic.get("passes", False)

    if confidence_score >= 80:
        confidence_label = "High"
    elif confidence_score >= 50:
        confidence_label = "Moderate"
    else:
        confidence_label = "Low"

    log_lines = [
        f"RAG: Retrieved {n_retrieved} similar caption(s) from FAISS"]
    log_lines.append(
        f"Complexity: {complexity_label} (score: {complexity_score:.3f})")
    if object_context:
        log_lines.append(f"YOLO: {object_context}")
    for i, h in enumerate(history):
        log_lines.append(
            f"Tier {h['tier']} ({h['model']}): Generated caption")
        if i == len(history) - 1:
            status = "PASSED" if passes else "FAILED"
            log_lines.append(
                f"Critic (Tier {h['tier']}): "
                f"Score {clip_score:.3f} -- {status}")
        else:
            log_lines.append(
                f"Critic (Tier {h['tier']}): "
                f"Score below threshold -- escalating")
    log_lines.append(f"Decision: Accepted Tier {final_tier} caption")
    log_lines.append(
        f"Style: Caption generated in '{style.replace('_', ' ')}' mode")
    log_lines.append(
        f"Confidence: {confidence_score:.0f}/100 -- {confidence_label}")
    log_lines.append(
        f"Memory: Stored in FAISS index (total: {n_total} entries)")
    if refinements and refinements.get("alt_text") != caption:
        log_lines.append("Refine: Generated alt-text and SEO variants")

    return (
        caption,
        _meta_chips_html(final_model, total_lat, total_cost, final_tier),
        _metrics_table_html(
            critic, caption, final_tier, final_model, total_cost, total_lat,
            confidence_score=confidence_score,
            confidence_explanation=confidence_explanation),
        _agent_log_html(log_lines),
        _refinements_html(refinements),
        _translation_html(translated_caption, language),
    )


def compare_all_styles(image):
    if image is None:
        return (
            '<p style="color:var(--text-muted);padding:2rem;text-align:center;'
            'font-size:.85rem;">Upload an image first.</p>'
        )
    pil, byt, _ = _pil_from_numpy(image)
    workflow = get_caption_workflow()
    variations: dict = {}
    for style in AVAILABLE_STYLES:
        res = workflow.invoke(
            {"image": pil, "image_bytes": byt, "style": style},
            {"recursion_limit": 25},
        )
        variations[style] = res.get("caption", "")
    return _style_var_html(variations)


def vqa_chat(image, question: str, chat_history: list, session_id: str):
    if not question.strip():
        return chat_history, "", session_id
    if image is None:
        h = list(chat_history or [])
        h.append({"role": "user", "content": question})
        h.append({"role": "assistant", "content": "Upload an image first."})
        return h, "", session_id
    pil = Image.fromarray(image)
    res = vqa_engine.ask(session_id, pil, question)
    h = list(chat_history or [])
    h.append({"role": "user", "content": question})
    h.append({"role": "assistant", "content": res["answer"]})
    return h, "", session_id


def new_vqa_session(session_id: str):
    vqa_engine.clear_session(session_id)
    return [], "", str(uuid.uuid4())


def refresh_dashboard():
    stats = local_tracker.get_stats()
    return (
        _kpi_cards_html(stats),
        _chart_tier(stats),
        _chart_style_usage(stats),
        _chart_quality(stats),
        _chart_latency(stats),
    )


def refresh_home():
    stats = local_tracker.get_stats()
    return (
        _kpi_cards_html(stats),
        _chart_tier(stats),
        _chart_quality(stats),
        _chart_cost_cum(stats),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Gradio Theme
# ─────────────────────────────────────────────────────────────────────────────
_THEME = gr.themes.Soft(
    primary_hue=gr.themes.colors.blue,
    secondary_hue=gr.themes.colors.slate,
    neutral_hue=gr.themes.colors.slate,
    text_size=gr.themes.sizes.text_md,
    spacing_size=gr.themes.sizes.spacing_md,
    radius_size=gr.themes.sizes.radius_md,
    font=[gr.themes.GoogleFont("Inter"), "system-ui", "sans-serif"],
    font_mono=[gr.themes.GoogleFont("JetBrains Mono"), "monospace"],
).set(
    body_background_fill="#f8fafc",
    block_background_fill="#ffffff",
    block_border_color="#e2e8f0",
    block_border_width="1px",
    block_label_background_fill="transparent",
    block_label_text_color="#475569",
    block_shadow="0 1px 2px rgba(0,0,0,.04)",
    input_background_fill="#ffffff",
    input_border_color="#e2e8f0",
    input_border_color_focus="#2563eb",
    input_shadow_focus="0 0 0 3px rgba(37,99,235,.08)",
    button_primary_background_fill="#2563eb",
    button_primary_text_color="#ffffff",
    button_primary_background_fill_hover="#1d4ed8",
    button_primary_shadow="0 1px 2px rgba(37,99,235,.2)",
    button_secondary_background_fill="#ffffff",
    button_secondary_text_color="#475569",
    button_secondary_border_color="#e2e8f0",
)


# ─────────────────────────────────────────────────────────────────────────────
# App builder
# ─────────────────────────────────────────────────────────────────────────────
def build_gradio_app() -> gr.Blocks:
    with gr.Blocks(title="IMG Caption Platform") as demo:

        with gr.Tabs():

            # == PAGE 1 -- HOME ==
            with gr.Tab("Home"):
                gr.HTML(_hero_html())
                home_kpi = gr.HTML()

                gr.HTML('<div style="margin:1.5rem 0 .5rem;">'
                        + _sec_head("Pipeline", "Active", "#059669")
                        + "</div>")
                gr.HTML(_pipeline_html())

                with gr.Row():
                    gr.HTML('<div style="margin:1.5rem 0 .5rem;flex:1;">'
                            + _sec_head("Performance", "Live", "#2563eb")
                            + "</div>")
                    home_refresh = gr.Button(
                        "Refresh", variant="secondary", size="sm", scale=0)

                with gr.Row(equal_height=True):
                    home_tier_c = gr.Plot(label="")
                    home_quality_c = gr.Plot(label="")
                    home_cost_c = gr.Plot(label="")

            # == PAGE 2 -- CAPTION STUDIO ==
            with gr.Tab("Caption Studio"):
                gr.HTML(
                    '<div style="margin-bottom:1.2rem;">'
                    + _sec_head("Caption Generation")
                    + '<p style="font-size:.86rem;color:var(--text-secondary);'
                    'margin-top:-.5rem;line-height:1.7;">'
                    'Upload an image, select a style, and generate a '
                    'self-evaluated caption.</p></div>')

                with gr.Row(equal_height=False):
                    with gr.Column(scale=5, min_width=320):
                        cap_image = gr.Image(
                            label="Upload Image", type="numpy", height=340)
                        cap_style = gr.Dropdown(
                            choices=AVAILABLE_STYLES, value="descriptive",
                            label="Caption Style")
                        cap_lang = gr.Dropdown(
                            choices=settings.available_languages,
                            value=settings.default_language,
                            label="Output Language")
                        cap_btn = gr.Button(
                            "Generate Caption", variant="primary", size="lg")
                        cmp_btn = gr.Button(
                            "Compare All 5 Styles", variant="secondary")

                    with gr.Column(scale=7, min_width=440):
                        cap_out = gr.Textbox(
                            label="Generated Caption", lines=4,
                            interactive=False,
                            placeholder="Caption will appear here...")
                        meta_out = gr.HTML()
                        with gr.Row(equal_height=True):
                            metrics_out = gr.HTML(_EMPTY_METRICS)
                            log_out = gr.HTML(_agent_log_html([]))
                        variations_out = gr.HTML()
                        with gr.Row(equal_height=True):
                            refinements_out = gr.HTML()
                            translation_out = gr.HTML()

                cap_btn.click(
                    fn=generate_caption,
                    inputs=[cap_image, cap_style, cap_lang],
                    outputs=[cap_out, meta_out, metrics_out, log_out,
                             refinements_out, translation_out],
                )
                cmp_btn.click(
                    fn=compare_all_styles,
                    inputs=[cap_image],
                    outputs=[variations_out],
                )

            # == PAGE 3 -- VISUAL QA ==
            with gr.Tab("Visual QA"):
                gr.HTML(
                    '<div style="margin-bottom:1.2rem;">'
                    + _sec_head("Visual Q&A", "GPT-4o-mini", "#7c3aed")
                    + '<p style="font-size:.86rem;color:var(--text-secondary);'
                    'margin-top:-.5rem;line-height:1.7;">'
                    'Multi-turn conversational visual analysis. '
                    'Ask anything about your image.</p></div>')

                vqa_session = gr.State(value=str(uuid.uuid4()))

                with gr.Row(equal_height=False):
                    with gr.Column(scale=1, min_width=280):
                        vqa_image = gr.Image(
                            label="Upload Image", type="numpy", height=300)
                        vqa_clear = gr.Button(
                            "New Session", variant="secondary")
                        gr.HTML(
                            '<div style="margin-top:.5rem;text-align:center;'
                            'font-size:.7rem;color:var(--text-muted);">'
                            'Multi-turn &bull; Image-grounded &bull; '
                            'Session-aware</div>')

                    with gr.Column(scale=2, min_width=440):
                        vqa_bot = gr.Chatbot(
                            label="Conversation", height=380)
                        with gr.Row():
                            vqa_q = gr.Textbox(
                                placeholder="Ask anything about the image...",
                                show_label=False, scale=5, lines=1)
                            vqa_btn = gr.Button(
                                "Ask", variant="primary", scale=1)

                vqa_btn.click(
                    fn=vqa_chat,
                    inputs=[vqa_image, vqa_q, vqa_bot, vqa_session],
                    outputs=[vqa_bot, vqa_q, vqa_session],
                )
                vqa_q.submit(
                    fn=vqa_chat,
                    inputs=[vqa_image, vqa_q, vqa_bot, vqa_session],
                    outputs=[vqa_bot, vqa_q, vqa_session],
                )
                vqa_clear.click(
                    fn=new_vqa_session,
                    inputs=[vqa_session],
                    outputs=[vqa_bot, vqa_q, vqa_session],
                )

            # == PAGE 4 -- ANALYTICS ==
            with gr.Tab("Analytics"):
                with gr.Row():
                    gr.HTML(
                        '<div style="margin-bottom:1.2rem;flex:1;">'
                        + _sec_head("Analytics", "Live", "#059669")
                        + '<p style="font-size:.86rem;color:var(--text-secondary);'
                        'margin-top:-.5rem;line-height:1.7;">'
                        'Model usage, quality scores, cost tracking, '
                        'and latency analysis.</p></div>')
                    dash_refresh = gr.Button(
                        "Refresh", variant="secondary", size="sm", scale=0)

                dash_kpi = gr.HTML()

                with gr.Row(equal_height=True):
                    dash_tier_c = gr.Plot(label="")
                    dash_style_c = gr.Plot(label="")

                with gr.Row(equal_height=True):
                    dash_qual_c = gr.Plot(label="")
                    dash_lat_c = gr.Plot(label="")

                dash_refresh.click(
                    fn=refresh_dashboard,
                    outputs=[dash_kpi, dash_tier_c, dash_style_c,
                             dash_qual_c, dash_lat_c],
                )

            # == PAGE 5 -- ABOUT ==
            with gr.Tab("About"):
                gr.HTML(_about_html())

        demo.load(
            fn=refresh_home,
            outputs=[home_kpi, home_tier_c, home_quality_c, home_cost_c])
        demo.load(
            fn=refresh_dashboard,
            outputs=[dash_kpi, dash_tier_c, dash_style_c,
                     dash_qual_c, dash_lat_c])
        home_refresh.click(
            fn=refresh_home,
            outputs=[home_kpi, home_tier_c, home_quality_c, home_cost_c])

    return demo
