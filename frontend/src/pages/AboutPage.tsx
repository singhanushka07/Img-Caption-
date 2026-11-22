import SectionHeader from '@/components/shared/SectionHeader'
import { rgba } from '@/lib/utils'

const FEATURES = [
  {
    num: '01',
    title: '3-Tier Routing',
    desc: 'BLIP → GPT-4o-mini → GPT-4o with auto-escalation',
    color: '#2563eb',
  },
  {
    num: '02',
    title: 'Dual Quality Gates',
    desc: 'CLIPScore + LLM-as-Judge (threshold gated)',
    color: '#7c3aed',
  },
  {
    num: '03',
    title: 'FAISS RAG Memory',
    desc: 'SentenceTransformer + CLIP dual-index retrieval',
    color: '#059669',
  },
  {
    num: '04',
    title: '5 Caption Styles',
    desc: 'Descriptive, Creative, Technical, Concise, Social',
    color: '#d97706',
  },
  {
    num: '05',
    title: 'Visual QA',
    desc: 'Multi-turn GPT-4o-mini conversation on images',
    color: '#dc2626',
  },
  {
    num: '06',
    title: 'Smart Routing',
    desc: 'OpenCV complexity analysis for intelligent tier selection',
    color: '#2563eb',
  },
  {
    num: '07',
    title: 'Object Detection',
    desc: 'YOLOv8n pre-pass for scene-aware captioning',
    color: '#7c3aed',
  },
  {
    num: '08',
    title: 'Caption Refinement',
    desc: 'Alt-text + SEO variants, multi-language output',
    color: '#059669',
  },
]

const FLOW_TEXT = `INPUT (image + style + language)
  │
  ├─ RAG Retrieval (FAISS + CLIP dual-index)
  ├─ Complexity Analysis (OpenCV metrics)
  ├─ Object Detection (YOLOv8n)
  │
  ├─ Tier 1: BLIP-L1 (local, free)
  │   └─ Critic: CLIPScore + LLM Judge
  │       ├─ PASS → Refine + Output
  │       └─ FAIL → Escalate
  │
  ├─ Tier 2: GPT-4o-mini (fast, cheap)
  │   └─ Critic: CLIPScore + LLM Judge
  │       ├─ PASS → Refine + Output
  │       └─ FAIL → Escalate
  │
  └─ Tier 3: GPT-4o (premium, best)
      └─ Critic: CLIPScore + LLM Judge
          └─ Always Accept → Refine + Output

REFINE: alt-text + SEO + translation + FAISS store`

export default function AboutPage() {
  return (
    <div className="space-y-10">
      {/* Header */}
      <SectionHeader title="Documentation" badge="v2.0" badgeColor="#2563eb" />

      {/* Architecture heading */}
      <section className="space-y-3">
        <h2 className="text-2xl font-bold text-slate-900">
          Platform Architecture
        </h2>
        <p className="max-w-3xl text-sm text-slate-500 leading-relaxed">
          The IMG Caption platform uses a multi-agent LangGraph architecture
          with three-tier model routing, dual quality gates, FAISS-backed RAG
          memory, and intelligent complexity-based escalation. Below is an
          overview of the core capabilities and the decision flow.
        </p>
      </section>

      {/* Feature cards grid */}
      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {FEATURES.map((f) => (
          <div
            key={f.num}
            className="bg-white rounded-xl border border-slate-200/60 shadow-sm p-5"
            style={{ borderTop: `3px solid ${f.color}` }}
          >
            <span
              className="inline-block font-mono text-[10px] font-bold mb-2 tracking-wider"
              style={{ color: f.color }}
            >
              [{f.num}]
            </span>
            <h3 className="text-sm font-bold text-slate-800 mb-1">
              {f.title}
            </h3>
            <p className="text-xs text-slate-400 leading-relaxed">{f.desc}</p>
          </div>
        ))}
      </section>

      {/* LangGraph Decision Flow */}
      <section>
        <h3 className="text-sm font-bold text-slate-800 mb-3">
          LangGraph Decision Flow
        </h3>
        <div
          className="bg-white rounded-xl border border-slate-200/60 shadow-sm overflow-hidden"
          style={{ borderLeft: `3px solid #2563eb` }}
        >
          <div
            className="px-5 py-4"
            style={{ backgroundColor: rgba('#2563eb', 0.03) }}
          >
            <pre className="text-[12px] font-mono text-slate-600 leading-relaxed whitespace-pre overflow-x-auto">
              {FLOW_TEXT}
            </pre>
          </div>
        </div>
      </section>
    </div>
  )
}
