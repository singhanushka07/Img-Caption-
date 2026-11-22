import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
  ResponsiveContainer,
  LabelList,
} from 'recharts'
import { STYLE_COLORS } from '@/lib/constants'

interface Props {
  styleUsage: Record<string, number>
}

export default function StyleUsage({ styleUsage }: Props) {
  const total = Object.values(styleUsage).reduce((sum, v) => sum + v, 0)

  const data = Object.entries(styleUsage)
    .map(([name, value]) => ({
      name,
      value,
      pct: total > 0 ? ((value / total) * 100).toFixed(0) : '0',
    }))
    .sort((a, b) => a.value - b.value)

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5">
      <h3 className="mb-3 text-sm font-semibold text-gray-700">Style Usage</h3>

      {total === 0 ? (
        <div className="flex h-[280px] items-center justify-center text-sm text-gray-400">
          No data yet
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={280}>
          <BarChart
            data={data}
            layout="vertical"
            margin={{ top: 5, right: 60, left: 10, bottom: 5 }}
          >
            <XAxis
              type="number"
              tick={{ fontSize: 11, fill: '#64748b' }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              type="category"
              dataKey="name"
              tick={{ fontSize: 11, fill: '#64748b' }}
              axisLine={false}
              tickLine={false}
              width={85}
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
              formatter={(value: number) => [value, 'Runs']}
            />
            <Bar dataKey="value" radius={[0, 4, 4, 0]} maxBarSize={28}>
              {data.map((entry) => (
                <Cell
                  key={entry.name}
                  fill={STYLE_COLORS[entry.name] ?? '#94a3b8'}
                />
              ))}
              <LabelList
                dataKey="value"
                position="right"
                formatter={(v: number) => {
                  const item = data.find((d) => d.value === v)
                  return `${v} (${item?.pct ?? 0}%)`
                }}
                style={{ fontSize: 10, fill: '#64748b' }}
              />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}
