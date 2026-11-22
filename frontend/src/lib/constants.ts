export const TIER_COLORS: Record<number, string> = { 1: '#059669', 2: '#2563eb', 3: '#7c3aed' }
export const TIER_NAMES: Record<number, string> = { 1: 'BLIP-L1', 2: 'GPT-Mini', 3: 'GPT-4O' }

export const STYLE_COLORS: Record<string, string> = {
  descriptive: '#7c3aed',
  creative: '#dc2626',
  technical: '#2563eb',
  concise: '#059669',
  social_media: '#d97706',
}

export const PIPELINE_NODES = [
  { name: 'INPUT', color: '#2563eb' },
  { name: 'RAG+CLIP', color: '#7c3aed' },
  { name: 'COMPLEXITY', color: '#d97706' },
  { name: 'YOLO', color: '#dc2626' },
  { name: 'BLIP-L1', color: '#059669' },
  { name: 'CRITIC', color: '#d97706' },
  { name: 'GPT-MINI', color: '#2563eb' },
  { name: 'CRITIC', color: '#d97706' },
  { name: 'GPT-4O', color: '#7c3aed' },
  { name: 'REFINE', color: '#059669' },
]

export const CLIP_SCORE_THRESHOLD = 0.25
