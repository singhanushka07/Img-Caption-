import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import type { RunRecord } from '@/lib/types'

interface Props {
  recentRuns: RunRecord[]
}

export default function CumulativeCost({ recentRuns }: Props) {
  let cumulative = 0
  const data = recentRuns.map((run, i) => {
    cumulative += run.cost_usd
    return {
      name: `#${i + 1}`,
      cost: Number(cumulative.toFixed(6)),
    }
  })

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5">
      <h3 className="mb-3 text-sm font-semibold text-gray-700">Cumulative Cost</h3>

      {recentRuns.length === 0 ? (
        <div className="flex h-[280px] items-center justify-center text-sm text-gray-400">
          No data yet
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={280}>
          <AreaChart data={data} margin={{ top: 10, right: 10, left: 5, bottom: 5 }}>
            <defs>
              <linearGradient id="costGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#2563eb" stopOpacity={0.1} />
                <stop offset="100%" stopColor="#2563eb" stopOpacity={0.02} />
              </linearGradient>
            </defs>
            <XAxis
              dataKey="name"
              tick={{ fontSize: 11, fill: '#64748b' }}
              axisLine={{ stroke: '#e2e8f0' }}
              tickLine={false}
            />
            <YAxis
              tick={{ fontSize: 11, fill: '#64748b' }}
              axisLine={false}
              tickLine={false}
              tickFormatter={(v: number) => `$${v.toFixed(4)}`}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1e293b',
                border: 'none',
                borderRadius: '6px',
                color: '#fff',
                fontSize: '12px',
              }}
              itemStyle={{ color: '#fff' }}
              formatter={(value: number) => [`$${value.toFixed(6)}`, 'Cumulative Cost']}
            />
            <Area
              type="monotone"
              dataKey="cost"
              stroke="#2563eb"
              strokeWidth={2}
              fill="url(#costGradient)"
              dot={{ r: 3, fill: '#2563eb', stroke: '#fff', strokeWidth: 2 }}
              activeDot={{ r: 5, fill: '#2563eb', stroke: '#fff', strokeWidth: 2 }}
            />
          </AreaChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}
