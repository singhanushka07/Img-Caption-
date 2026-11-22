import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
  ResponsiveContainer,
} from 'recharts'
import type { RunRecord } from '@/lib/types'

interface Props {
  recentRuns: RunRecord[]
}

function getLatencyColor(ms: number): string {
  if (ms < 1000) return '#059669'
  if (ms < 3000) return '#d97706'
  return '#dc2626'
}

export default function LatencyChart({ recentRuns }: Props) {
  const data = recentRuns.map((run, i) => ({
    name: `#${i + 1}`,
    latency_ms: run.latency_ms,
    cost_usd: run.cost_usd,
  }))

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5">
      <h3 className="mb-3 text-sm font-semibold text-gray-700">Latency</h3>

      {recentRuns.length === 0 ? (
        <div className="flex h-[280px] items-center justify-center text-sm text-gray-400">
          No data yet
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={data} margin={{ top: 10, right: 10, left: 5, bottom: 5 }}>
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
              tickFormatter={(v: number) => `${v}ms`}
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
              formatter={(value: number, name: string) => {
                if (name === 'latency_ms') return [`${value.toFixed(0)} ms`, 'Latency']
                if (name === 'cost_usd') return [`$${value.toFixed(6)}`, 'Cost']
                return [value, name]
              }}
            />
            <Bar dataKey="latency_ms" radius={[4, 4, 0, 0]} maxBarSize={40}>
              {data.map((entry, index) => (
                <Cell key={index} fill={getLatencyColor(entry.latency_ms)} />
              ))}
            </Bar>
            {/* Hidden bar so cost shows in tooltip */}
            <Bar dataKey="cost_usd" hide />
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}
