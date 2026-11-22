interface ConfidenceBarProps {
  score: number
  explanation: string
}

function scoreInfo(score: number) {
  if (score >= 80) return { label: 'High', color: '#059669' }
  if (score >= 50) return { label: 'Moderate', color: '#d97706' }
  return { label: 'Low', color: '#dc2626' }
}

export default function ConfidenceBar({ score, explanation }: ConfidenceBarProps) {
  const { label, color } = scoreInfo(score)

  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between">
        <span className="text-[11px] font-medium text-slate-500">
          Confidence:&nbsp;
          <span style={{ color }} className="font-semibold">
            {score}/100 ({label})
          </span>
        </span>
      </div>

      <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-500 ease-out"
          style={{ width: `${Math.min(score, 100)}%`, backgroundColor: color }}
        />
      </div>

      {explanation && (
        <p className="text-[11px] text-slate-400 leading-snug">{explanation}</p>
      )}
    </div>
  )
}
