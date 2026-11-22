import { rgba } from '@/lib/utils'

interface KPICardProps {
  title: string
  value: string
  subtitle: string
  color: string
}

export default function KPICard({ title, value, subtitle, color }: KPICardProps) {
  return (
    <div
      className="bg-white rounded-xl border border-slate-200/60 p-5 shadow-sm"
      style={{ borderTop: `3px solid ${color}` }}
    >
      <p
        className="text-[10px] font-semibold uppercase tracking-wider mb-2"
        style={{ color }}
      >
        {title}
      </p>
      <p className="text-2xl font-bold text-slate-900 leading-none mb-1">
        {value}
      </p>
      <p className="text-xs text-slate-400">{subtitle}</p>
    </div>
  )
}
