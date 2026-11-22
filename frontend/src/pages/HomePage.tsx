import { useState, useEffect, useCallback } from 'react'
import type { HealthResponse, StatsResponse } from '@/lib/types'
import { getHealth, getStats } from '@/lib/api'
import StatusBadge from '@/components/shared/StatusBadge'
import KPICard from '@/components/shared/KPICard'
import SectionHeader from '@/components/shared/SectionHeader'
import PipelineFlow from '@/components/shared/PipelineFlow'
import TierDistribution from '@/components/charts/TierDistribution'
import QualityScores from '@/components/charts/QualityScores'
import CumulativeCost from '@/components/charts/CumulativeCost'

const TECH_BADGES = [
  { label: 'LangGraph', color: '#2563eb' },
  { label: 'FAISS+SBERT', color: '#7c3aed' },
  { label: 'CLIP Score', color: '#059669' },
  { label: 'YOLOv8', color: '#dc2626' },
  { label: 'FastAPI', color: '#d97706' },
]

export default function HomePage() {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [stats, setStats] = useState<StatsResponse | null>(null)

  const fetchData = useCallback(async () => {
    try {
      const [h, s] = await Promise.all([getHealth(), getStats()])
      setHealth(h)
      setStats(s)
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
      {/* Hero Section */}
      <section className="space-y-5">
        {/* Status badges */}
        <div className="flex flex-wrap items-center gap-2">
          <StatusBadge
            label={health?.has_openai ? 'Online' : 'Offline'}
            color={health?.has_openai ? '#059669' : '#dc2626'}
            dot
          />
          <StatusBadge
            label="BLIP Ready"
            color={health?.blip_ready ? '#059669' : '#64748b'}
            dot
          />
          <StatusBadge
            label="FAISS Memory"
            color={health?.faiss_memory ? '#7c3aed' : '#64748b'}
            dot
          />
          {health?.version && (
            <StatusBadge label={health.version} color="#2563eb" />
          )}
        </div>

        {/* Subtitle */}
        <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
          Multi-Agent Vision Platform
        </p>

        {/* Heading */}
        <h1 className="text-4xl sm:text-5xl font-extrabold leading-tight text-slate-900">
          Agentic{' '}
          <span className="text-blue-600">Image</span>{' '}
          Intelligence
        </h1>

        {/* Description */}
        <p className="max-w-2xl text-base text-slate-500 leading-relaxed">
          A multi-agent image captioning platform powered by LangGraph
          orchestration. Three-tier routing from local BLIP to GPT-4o, dual
          quality gates with CLIP and LLM-as-Judge, FAISS RAG memory, five
          caption styles, visual QA, and intelligent object-aware captioning.
        </p>

        {/* Tech badges */}
        <div className="flex flex-wrap items-center gap-2">
          {TECH_BADGES.map((b) => (
            <StatusBadge key={b.label} label={b.label} color={b.color} />
          ))}
        </div>
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

      {/* Pipeline Section */}
      <section>
        <SectionHeader title="Pipeline" badge="Active" badgeColor="#059669" />
        <PipelineFlow />
      </section>

      {/* Performance Section */}
      <section>
        <div className="flex items-center gap-4 mb-4">
          <SectionHeader title="Performance" badge="Live" badgeColor="#2563eb" />
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

        {stats && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            <TierDistribution tierUsage={stats.tier_usage} />
            <QualityScores recentRuns={stats.recent_runs} />
            <CumulativeCost recentRuns={stats.recent_runs} />
          </div>
        )}
      </section>
    </div>
  )
}
