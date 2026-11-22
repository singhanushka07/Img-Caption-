import { TIER_COLORS, TIER_NAMES, CLIP_SCORE_THRESHOLD } from '@/lib/constants'
import { rgba } from '@/lib/utils'
import ConfidenceBar from './ConfidenceBar'

interface MetricsTableProps {
  clipScore: number
  judgeScore: number
  judgeReason: string
  passes: boolean
  tier: number
  model: string
  cost: number
  latencyMs: number
  caption: string
  confidenceScore: number
  confidenceExplanation: string
}

export default function MetricsTable({
  clipScore,
  judgeScore,
  judgeReason,
  passes,
  tier,
  model,
  cost,
  latencyMs,
  caption,
  confidenceScore,
  confidenceExplanation,
}: MetricsTableProps) {
  const tierColor = TIER_COLORS[tier] ?? '#64748b'
  const tierName = TIER_NAMES[tier] ?? `Tier ${tier}`
  const combined =
    (Math.min(clipScore / CLIP_SCORE_THRESHOLD, 1.0) + judgeScore / 10) / 2

  const rows: [string, React.ReactNode][] = [
    ['Combined Score', combined.toFixed(3)],
    ['CLIP Score', clipScore.toFixed(4)],
    ['LLM Judge', `${judgeScore}/10`],
    [
      'Verdict',
      <span
        key="verdict"
        className="font-semibold"
        style={{ color: passes ? '#059669' : '#d97706' }}
      >
        {passes ? 'Accepted' : 'Escalated'}
      </span>,
    ],
  ]

  return (
    <div
      className="bg-white rounded-xl border border-slate-200/60 shadow-sm overflow-hidden"
      style={{ borderTop: `3px solid ${tierColor}` }}
    >
      {/* Header */}
      <div className="px-5 pt-4 pb-3">
        <h3 className="text-sm font-bold text-slate-800">
          Tier {tier} &mdash;{' '}
          <span style={{ color: tierColor }}>{tierName}</span>
        </h3>
      </div>

      <div className="px-5 pb-4 space-y-4">
        {/* Confidence */}
        {confidenceScore > 0 && (
          <ConfidenceBar
            score={confidenceScore}
            explanation={confidenceExplanation}
          />
        )}

        {/* Caption */}
        <div
          className="pl-3 py-2 text-[13px] text-slate-700 leading-relaxed rounded"
          style={{
            borderLeft: `3px solid ${tierColor}`,
            backgroundColor: rgba(tierColor, 0.04),
          }}
        >
          {caption}
        </div>

        {/* Metrics rows */}
        <table className="w-full text-[12px]">
          <tbody>
            {rows.map(([label, value]) => (
              <tr key={label} className="border-t border-slate-100">
                <td className="py-1.5 text-slate-400 font-medium">{label}</td>
                <td className="py-1.5 text-right text-slate-700 font-mono">
                  {value}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {/* Judge reason */}
        {judgeReason && (
          <p className="text-[11px] text-slate-400 leading-snug italic">
            {judgeReason}
          </p>
        )}

        {/* Footer */}
        <div className="flex items-center gap-4 pt-2 border-t border-slate-100 text-[11px] text-slate-400 font-mono">
          <span>Model: {model}</span>
          <span>Cost: ${cost.toFixed(4)}</span>
          <span>Time: {latencyMs}ms</span>
        </div>
      </div>
    </div>
  )
}
