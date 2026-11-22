import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ReferenceLine,
  Cell,
  ResponsiveContainer,
  LabelList,
} from 'recharts'
import { TIER_COLORS, CLIP_SCORE_THRESHOLD } from '@/lib/constants'
import type { RunRecord } from '@/lib/types'

interface Props {
  recentRuns: RunRecord[]
}

export default function QualityScores({ recentRuns }: Props) {
  const data = recentRuns.map((run, i) => ({
    name: `#${i + 1}`,
    clip_score: run.clip_score,
    tier: run.tier,
  }))

  const maxScore = Math.max(...data.map((d) => d.clip_score), 0)
  const yMax = Math.max(maxScore * 1.15, 1.05)

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5">
      <h3 className="mb-3 text-sm font-semibold text-gray-700">Quality Scores (CLIP)</h3>

      {recentRuns.length === 0 ? (
        <div className="flex h-[280px] items-center justify-center text-sm text-gray-400">
          No data yet
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={data} margin={{ top: 20, right: 10, left: 0, bottom: 5 }}>
            <XAxis
              dataKey="name"
              tick={{ fontSize: 11, fill: '#64748b' }}
              axisLine={{ stroke: '#e2e8f0' }}
              tickLine={false}
            />
            <YAxis
              domain={[0, yMax]}
              tick={{ fontSize: 11, fill: '#64748b' }}
              axisLine={false}
              tickLine={false}
              tickFormatter={(v: number) => v.toFixed(2)}
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
              formatter={(value: number) => [value.toFixed(3), 'CLIP Score']}
            />
            <ReferenceLine
              y={CLIP_SCORE_THRESHOLD}
              stroke="#dc2626"
              strokeDasharray="4 4"
              label={{
                value: `Threshold (${CLIP_SCORE_THRESHOLD})`,
                position: 'right',
                fill: '#dc2626',
                fontSize: 10,
              }}
            />
            <Bar dataKey="clip_score" radius={[4, 4, 0, 0]} maxBarSize={40}>
              {data.map((entry, index) => (
                <Cell key={index} fill={TIER_COLORS[entry.tier] ?? '#94a3b8'} />
              ))}
              <LabelList
                dataKey="clip_score"
                position="top"
                formatter={(v: number) => v.toFixed(2)}
                style={{ fontSize: 10, fill: '#64748b' }}
              />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}
