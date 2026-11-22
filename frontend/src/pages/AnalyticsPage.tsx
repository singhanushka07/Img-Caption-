import { useState, useEffect, useCallback } from 'react'
import type { StatsResponse } from '@/lib/types'
import { getStats } from '@/lib/api'
import KPICard from '@/components/shared/KPICard'
import SectionHeader from '@/components/shared/SectionHeader'
import TierDistribution from '@/components/charts/TierDistribution'
import QualityScores from '@/components/charts/QualityScores'
import StyleUsage from '@/components/charts/StyleUsage'
import LatencyChart from '@/components/charts/LatencyChart'

export default function AnalyticsPage() {
  const [stats, setStats] = useState<StatsResponse | null>(null)

  const fetchData = useCallback(async () => {
    try {
      setStats(await getStats())
    } catch {
      /* silently handle */
    }
  }, [])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  const tier1Pct =
    stats && stats.total_runs > 0
      ? Math.round(
          ((stats.tier_usage['1'] ?? 0) / stats.total_runs) * 100,
        )
      : 0

  return (
    <div className="space-y-10">
      {/* Header */}
      <section>
        <div className="flex items-center gap-4 mb-2">
          <SectionHeader title="Analytics" badge="Live" badgeColor="#2563eb" />
          <button
            onClick={fetchData}
            className="ml-auto inline-flex items-center gap-1.5 px-3 py-1.5 text-[11px] font-medium rounded-lg border border-slate-200 text-slate-500 hover:text-slate-700 hover:border-slate-300 bg-white transition-colors"
          >
            <svg
              className="w-3.5 h-3.5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              />
            </svg>
            Refresh
          </button>
        </div>
        <p className="text-sm text-slate-500 leading-relaxed max-w-xl">
          Real-time performance metrics, tier distribution, quality scores, and
          cost analytics across all captioning runs.
        </p>
      </section>

      {/* KPI Cards */}
      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Images"
          value={String(stats?.total_runs ?? 0)}
          subtitle="Total captions generated"
          color="#2563eb"
        />
        <KPICard
          title="Quality"
          value={(stats?.avg_clip_score ?? 0).toFixed(3)}
          subtitle="Average CLIP score"
          color="#7c3aed"
        />
        <KPICard
          title="Cost"
          value={`$${(stats?.total_cost ?? 0).toFixed(4)}`}
          subtitle="Total API spend"
          color="#dc2626"
        />
        <KPICard
          title="Local"
          value={`${tier1Pct}%`}
          subtitle="Tier 1 (BLIP) runs"
          color="#059669"
        />
      </section>

      {/* Row 1: Tier Distribution + Style Usage */}
      {stats && (
        <section className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <TierDistribution tierUsage={stats.tier_usage} />
          <StyleUsage styleUsage={stats.style_usage} />
        </section>
      )}

      {/* Row 2: Quality Scores + Latency */}
      {stats && (
        <section className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <QualityScores recentRuns={stats.recent_runs} />
          <LatencyChart recentRuns={stats.recent_runs} />
        </section>
      )}
    </div>
  )
}
