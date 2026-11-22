import { rgba } from '@/lib/utils'

interface StatusBadgeProps {
  label: string
  color: string
  dot?: boolean
}

export default function StatusBadge({ label, color, dot }: StatusBadgeProps) {
  return (
    <span
      className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full font-mono text-[10px] font-medium leading-none"
      style={{
        color,
        backgroundColor: rgba(color, 0.08),
        border: `1px solid ${rgba(color, 0.18)}`,
      }}
    >
      {dot && (
        <span
          className="w-1.5 h-1.5 rounded-full"
          style={{ backgroundColor: color }}
        />
      )}
      {label}
    </span>
  )
}
