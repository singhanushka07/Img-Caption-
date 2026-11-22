import type { CaptionResponse, CompareResponse, VQAResponse, StatsResponse, HealthResponse } from './types'

async function fetchJSON<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, init)
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText)
    throw new Error(`${res.status}: ${text}`)
  }
  return res.json()
}

export async function getHealth(): Promise<HealthResponse> {
  return fetchJSON('/health')
}

export async function getStats(): Promise<StatsResponse> {
  return fetchJSON('/stats')
}

export async function getStyles(): Promise<string[]> {
  const data = await fetchJSON<{ styles: string[] }>('/styles')
  return data.styles
}

export async function getLanguages(): Promise<string[]> {
  const data = await fetchJSON<{ languages: string[] }>('/languages')
  return data.languages
}

export async function generateCaption(image: File, style: string, language: string): Promise<CaptionResponse> {
  const form = new FormData()
  form.append('image', image)
  form.append('style', style)
  form.append('language', language)
  return fetchJSON('/caption', { method: 'POST', body: form })
}

export async function compareStyles(image: File): Promise<CompareResponse> {
  const form = new FormData()
  form.append('image', image)
  return fetchJSON('/caption/compare', { method: 'POST', body: form })
}

export async function askVQA(image: File, question: string, sessionId: string): Promise<VQAResponse> {
  const form = new FormData()
  form.append('image', image)
  form.append('question', question)
  form.append('session_id', sessionId)
  return fetchJSON('/vqa', { method: 'POST', body: form })
}
