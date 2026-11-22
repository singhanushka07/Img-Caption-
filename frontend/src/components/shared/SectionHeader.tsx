import StatusBadge from './StatusBadge'

interface SectionHeaderProps {
  title: string
  badge?: string
  badgeColor?: string
}

export default function SectionHeader({ title, badge, badgeColor }: SectionHeaderProps) {
  return (
    <div className="flex items-center gap-3 mb-4">
      <h2 className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
        {title}
      </h2>
      {badge && badgeColor && <StatusBadge label={badge} color={badgeColor} />}
    </div>
  )
}
