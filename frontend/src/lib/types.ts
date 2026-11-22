export interface CaptionResponse {
  caption: string
  model_used: string
  tier: number
  clip_score: number
  judge_score: number
  latency_ms: number
  cost_usd: number
  escalation_count: number
  history: Array<{ tier: number; model: string }>
  refinements: { alt_text?: string; seo?: string }
  language: string
  translated_caption: string
  confidence_score: number
  confidence_explanation: string
  complexity_label: string
  detected_objects: Array<{ label: string; confidence: number; bbox: number[] }>
}

export interface CompareResponse {
  styles: Record<string, {
    caption: string
    model_used: string
    clip_score: number
    judge_score: number
    cost_usd: number
    latency_ms: number
  }>
}

export interface VQAResponse {
  answer: string
  tokens_used: number
  history_length: number
}

export interface RunRecord {
  ts: string
  model: string
  style: string
  tier: number
  clip_score: number
  judge_score: number
  latency_ms: number
  cost_usd: number
  escalations: number
  caption_len: number
  img_hash: string
}

export interface StatsResponse {
  total_runs: number
  avg_cost: number
  avg_latency: number
  avg_clip_score: number
  avg_judge_score: number
  total_cost: number
  avg_escalations: number
  model_usage: Record<string, number>
  style_usage: Record<string, number>
  tier_usage: Record<string, number>
  recent_runs: RunRecord[]
}

export interface HealthResponse {
  has_openai: boolean
  blip_ready: boolean
  faiss_memory: boolean
  version: string
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}
