import { PieChart, Pie, Cell, Legend, Tooltip, ResponsiveContainer } from 'recharts'
import { TIER_COLORS, TIER_NAMES } from '@/lib/constants'

interface Props {
  tierUsage: Record<string, number>
}

const COLORS: Record<string, string> = {
  '1': TIER_COLORS[1],
  '2': TIER_COLORS[2],
  '3': TIER_COLORS[3],
}

export default function TierDistribution({ tierUsage }: Props) {
  const data = Object.entries(tierUsage).map(([key, value]) => ({
    name: TIER_NAMES[Number(key)] ?? `Tier ${key}`,
    value,
    key,
  }))

  const total = data.reduce((sum, d) => sum + d.value, 0)

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5">
      <h3 className="mb-3 text-sm font-semibold text-gray-700">Tier Distribution</h3>

      {total === 0 ? (
        <div className="flex h-[280px] items-center justify-center text-sm text-gray-400">
          No data yet
        </div>
      ) : (
        <div className="relative h-[280px]">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="45%"
                innerRadius={60}
                outerRadius={90}
                dataKey="value"
                stroke="none"
              >
                {data.map((entry) => (
                  <Cell key={entry.key} fill={COLORS[entry.key] ?? '#94a3b8'} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1e293b',
                  border: 'none',
                  borderRadius: '6px',
                  color: '#fff',
                  fontSize: '12px',
                }}
                itemStyle={{ color: '#fff' }}
              />
              <Legend
                verticalAlign="bottom"
                height={36}
                iconType="circle"
                iconSize={8}
                formatter={(value: string) => (
                  <span className="text-xs text-gray-600">{value}</span>
                )}
              />
            </PieChart>
          </ResponsiveContainer>

          {/* Center label */}
          <div className="pointer-events-none absolute inset-0 flex items-center justify-center" style={{ paddingBottom: 36 }}>
            <div className="flex flex-col items-center -mt-3">
              <span className="text-2xl font-bold text-gray-900">{total}</span>
              <span className="text-[10px] font-medium uppercase tracking-wider text-gray-400">
                Total
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
