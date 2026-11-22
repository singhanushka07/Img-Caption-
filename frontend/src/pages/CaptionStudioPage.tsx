import { useState, useEffect, useCallback } from 'react'
import type { CaptionResponse, CompareResponse } from '@/lib/types'
import { getStyles, getLanguages, generateCaption, compareStyles } from '@/lib/api'
import { TIER_COLORS, TIER_NAMES, STYLE_COLORS, CLIP_SCORE_THRESHOLD } from '@/lib/constants'
import { rgba } from '@/lib/utils'
import ImageUploader from '@/components/shared/ImageUploader'
import MetricsTable from '@/components/shared/MetricsTable'
import AgentLog from '@/components/shared/AgentLog'
import CopyButton from '@/components/shared/CopyButton'

function buildAgentLog(result: CaptionResponse, style: string): string[] {
  const lines: string[] = []
  lines.push(`Complexity: ${result.complexity_label}`)
  if (result.detected_objects.length > 0) {
    lines.push(
      `YOLO: Detected ${result.detected_objects.map((o) => o.label).join(', ')}`,
    )
  }
  result.history.forEach((h, i) => {
    lines.push(`Tier ${h.tier} (${h.model}): Generated caption`)
    if (i === result.history.length - 1) {
      const status =
        result.clip_score >= CLIP_SCORE_THRESHOLD ? 'PASSED' : 'FAILED'
      lines.push(
        `Critic (Tier ${h.tier}): Score ${result.clip_score.toFixed(3)} -- ${status}`,
      )
    } else {
      lines.push(`Critic (Tier ${h.tier}): Score below threshold -- escalating`)
    }
  })
  lines.push(`Decision: Accepted Tier ${result.tier} caption`)
  lines.push(`Style: Caption generated in '${style}' mode`)
  lines.push(`Confidence: ${result.confidence_score.toFixed(0)}/100`)
  return lines
}

export default function CaptionStudioPage() {
  const [image, setImage] = useState<File | null>(null)
  const [preview, setPreview] = useState<string>()
  const [styles, setStyles] = useState<string[]>([])
  const [languages, setLanguages] = useState<string[]>([])
  const [style, setStyle] = useState('')
  const [language, setLanguage] = useState('')
  const [captionResult, setCaptionResult] = useState<CaptionResponse | null>(
    null,
  )
  const [compareResult, setCompareResult] = useState<CompareResponse | null>(
    null,
  )
  const [generating, setGenerating] = useState(false)
  const [comparing, setComparing] = useState(false)

  useEffect(() => {
    async function init() {
      try {
        const [s, l] = await Promise.all([getStyles(), getLanguages()])
        setStyles(s)
        setLanguages(l)
        if (s.length > 0) setStyle(s[0])
        if (l.length > 0) setLanguage(l[0])
      } catch {
        /* silently handle */
      }
    }
    init()
  }, [])

  const handleSelectImage = useCallback((file: File) => {
    setImage(file)
    setPreview(URL.createObjectURL(file))
    setCaptionResult(null)
    setCompareResult(null)
  }, [])

  const handleClear = useCallback(() => {
    setImage(null)
    setPreview(undefined)
    setCaptionResult(null)
    setCompareResult(null)
  }, [])

  const handleGenerate = useCallback(async () => {
    if (!image || generating) return
    setGenerating(true)
    setCompareResult(null)
    try {
      const res = await generateCaption(image, style, language)
      setCaptionResult(res)
    } catch {
      /* silently handle */
    } finally {
      setGenerating(false)
    }
  }, [image, style, language, generating])

  const handleCompare = useCallback(async () => {
    if (!image || comparing) return
    setComparing(true)
    try {
      const res = await compareStyles(image)
      setCompareResult(res)
    } catch {
      /* silently handle */
    } finally {
      setComparing(false)
    }
  }, [image, comparing])

  const tierColor = captionResult
    ? (TIER_COLORS[captionResult.tier] ?? '#64748b')
    : '#64748b'
  const tierName = captionResult
    ? (TIER_NAMES[captionResult.tier] ?? `Tier ${captionResult.tier}`)
    : ''

  return (
    <div className="flex flex-col lg:flex-row gap-6">
      {/* Left column */}
      <div className="w-full lg:w-5/12 space-y-4 flex-shrink-0">
        <ImageUploader
          onSelect={handleSelectImage}
          preview={preview}
          onClear={handleClear}
          height={340}
        />

        {/* Style select */}
        <select
          value={style}
          onChange={(e) => setStyle(e.target.value)}
          className="w-full px-3.5 py-2.5 text-sm rounded-lg border border-slate-200 bg-white text-slate-700 focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-400/30 transition-colors appearance-none bg-[url('data:image/svg+xml;charset=UTF-8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2212%22%20height%3D%2212%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%2394a3b8%22%20stroke-width%3D%222%22%3E%3Cpath%20d%3D%22M6%209l6%206%206-6%22%2F%3E%3C%2Fsvg%3E')] bg-[length:16px] bg-[right_12px_center] bg-no-repeat"
        >
          {styles.map((s) => (
            <option key={s} value={s}>
              {s.charAt(0).toUpperCase() + s.slice(1).replace('_', ' ')}
            </option>
          ))}
        </select>

        {/* Language select */}
        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          className="w-full px-3.5 py-2.5 text-sm rounded-lg border border-slate-200 bg-white text-slate-700 focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-400/30 transition-colors appearance-none bg-[url('data:image/svg+xml;charset=UTF-8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2212%22%20height%3D%2212%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%2394a3b8%22%20stroke-width%3D%222%22%3E%3Cpath%20d%3D%22M6%209l6%206%206-6%22%2F%3E%3C%2Fsvg%3E')] bg-[length:16px] bg-[right_12px_center] bg-no-repeat"
        >
          {languages.map((l) => (
            <option key={l} value={l}>
              {l.charAt(0).toUpperCase() + l.slice(1)}
            </option>
          ))}
        </select>

        {/* Generate button */}
        <button
          onClick={handleGenerate}
          disabled={!image || generating}
          className="w-full px-4 py-2.5 text-sm font-medium rounded-lg bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          {generating ? (
            <span className="inline-flex items-center gap-2">
              <svg
                className="w-4 h-4 animate-spin"
                viewBox="0 0 24 24"
                fill="none"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                />
              </svg>
              Generating...
            </span>
          ) : (
            'Generate Caption'
          )}
        </button>

        {/* Compare button */}
        <button
          onClick={handleCompare}
          disabled={!image || comparing}
          className="w-full px-4 py-2.5 text-sm font-medium rounded-lg border border-slate-200 text-slate-600 hover:text-slate-800 hover:border-slate-300 bg-white disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          {comparing ? (
            <span className="inline-flex items-center gap-2">
              <svg
                className="w-4 h-4 animate-spin"
                viewBox="0 0 24 24"
                fill="none"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                />
              </svg>
              Comparing...
            </span>
          ) : (
            'Compare All 5 Styles'
          )}
        </button>
      </div>

      {/* Right column */}
      <div className="w-full lg:w-7/12 space-y-5">
        {/* Caption output */}
        <div className="relative">
          {generating && !captionResult && (
            <div className="h-28 rounded-xl border border-slate-200/60 bg-white overflow-hidden">
              <div className="animate-pulse space-y-2.5 p-4">
                <div className="h-3 bg-slate-100 rounded w-full" />
                <div className="h-3 bg-slate-100 rounded w-5/6" />
                <div className="h-3 bg-slate-100 rounded w-4/6" />
                <div className="h-3 bg-slate-100 rounded w-3/6" />
              </div>
            </div>
          )}

          {!generating && (
            <div
              className="min-h-[7rem] rounded-xl border border-slate-200/60 bg-white p-4 text-sm text-slate-700 leading-relaxed"
              style={
                captionResult
                  ? { borderLeft: `3px solid ${tierColor}` }
                  : undefined
              }
            >
              {captionResult ? (
                <div className="flex items-start gap-2">
                  <p className="flex-1">{captionResult.caption}</p>
                  <CopyButton text={captionResult.caption} />
                </div>
              ) : (
                <p className="text-slate-300">
                  Generated caption will appear here...
                </p>
              )}
            </div>
          )}
        </div>

        {/* Meta chips */}
        {captionResult && (
          <div className="flex flex-wrap items-center gap-2">
            <span
              className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md font-mono text-[11px] font-medium"
              style={{
                color: tierColor,
                backgroundColor: rgba(tierColor, 0.08),
                border: `1px solid ${rgba(tierColor, 0.18)}`,
              }}
            >
              Tier {captionResult.tier} &mdash; {tierName}
            </span>
            <span className="inline-flex items-center px-2.5 py-1 rounded-md font-mono text-[11px] font-medium text-slate-500 bg-slate-50 border border-slate-200/60">
              {(captionResult.latency_ms / 1000).toFixed(1)}s
            </span>
            <span className="inline-flex items-center px-2.5 py-1 rounded-md font-mono text-[11px] font-medium text-slate-500 bg-slate-50 border border-slate-200/60">
              ${captionResult.cost_usd.toFixed(4)}
            </span>
          </div>
        )}

        {/* Metrics + Agent Log */}
        {captionResult && (
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
            <MetricsTable
              clipScore={captionResult.clip_score}
              judgeScore={captionResult.judge_score}
              judgeReason=""
              passes={captionResult.clip_score >= CLIP_SCORE_THRESHOLD}
              tier={captionResult.tier}
              model={captionResult.model_used}
              cost={captionResult.cost_usd}
              latencyMs={captionResult.latency_ms}
              caption={captionResult.caption}
              confidenceScore={captionResult.confidence_score}
              confidenceExplanation={captionResult.confidence_explanation}
            />
            <AgentLog lines={buildAgentLog(captionResult, style)} />
          </div>
        )}

        {/* Style variations (compare) */}
        {compareResult && (
          <div className="space-y-3">
            <h3 className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
              Style Variations
            </h3>
            <div className="space-y-2">
              {Object.entries(compareResult.styles).map(([name, data]) => {
                const sColor = STYLE_COLORS[name] ?? '#64748b'
                return (
                  <div
                    key={name}
                    className="bg-white rounded-xl border border-slate-200/60 shadow-sm p-4"
                    style={{ borderLeft: `3px solid ${sColor}` }}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1.5">
                          <span
                            className="text-[11px] font-bold uppercase tracking-wider"
                            style={{ color: sColor }}
                          >
                            {name.replace('_', ' ')}
                          </span>
                          <span className="text-[10px] font-mono text-slate-400">
                            CLIP {data.clip_score.toFixed(3)} | ${data.cost_usd.toFixed(4)} |{' '}
                            {(data.latency_ms / 1000).toFixed(1)}s
                          </span>
                        </div>
                        <p className="text-sm text-slate-600 leading-relaxed">
                          {data.caption}
                        </p>
                      </div>
                      <CopyButton text={data.caption} />
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* Comparing shimmer */}
        {comparing && !compareResult && (
          <div className="space-y-3">
            <h3 className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
              Style Variations
            </h3>
            {[1, 2, 3, 4, 5].map((n) => (
              <div
                key={n}
                className="animate-pulse bg-white rounded-xl border border-slate-200/60 p-4"
              >
                <div className="h-3 bg-slate-100 rounded w-24 mb-2" />
                <div className="h-3 bg-slate-100 rounded w-full mb-1.5" />
                <div className="h-3 bg-slate-100 rounded w-4/5" />
              </div>
            ))}
          </div>
        )}

        {/* Refinements */}
        {captionResult &&
          (captionResult.refinements.alt_text ||
            captionResult.refinements.seo) && (
            <div className="space-y-3">
              <h3 className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                Refinements
              </h3>
              <div className="space-y-2">
                {captionResult.refinements.alt_text && (
                  <div className="bg-white rounded-xl border border-slate-200/60 shadow-sm p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1 min-w-0">
                        <span className="text-[11px] font-bold uppercase tracking-wider text-blue-600 mb-1.5 block">
                          Alt Text
                        </span>
                        <p className="text-sm text-slate-600 leading-relaxed">
                          {captionResult.refinements.alt_text}
                        </p>
                      </div>
                      <CopyButton text={captionResult.refinements.alt_text} />
                    </div>
                  </div>
                )}
                {captionResult.refinements.seo && (
                  <div className="bg-white rounded-xl border border-slate-200/60 shadow-sm p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1 min-w-0">
                        <span className="text-[11px] font-bold uppercase tracking-wider text-purple-600 mb-1.5 block">
                          SEO
                        </span>
                        <p className="text-sm text-slate-600 leading-relaxed">
                          {captionResult.refinements.seo}
                        </p>
                      </div>
                      <CopyButton text={captionResult.refinements.seo} />
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

        {/* Translation */}
        {captionResult &&
          captionResult.language !== 'english' &&
          captionResult.translated_caption && (
            <div className="space-y-3">
              <h3 className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                Translation ({captionResult.language})
              </h3>
              <div className="bg-white rounded-xl border border-slate-200/60 shadow-sm p-4">
                <div className="flex items-start justify-between gap-3">
                  <p className="flex-1 text-sm text-slate-600 leading-relaxed">
                    {captionResult.translated_caption}
                  </p>
                  <CopyButton text={captionResult.translated_caption} />
                </div>
              </div>
            </div>
          )}
      </div>
    </div>
  )
}
