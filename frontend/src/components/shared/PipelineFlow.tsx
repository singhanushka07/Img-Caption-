import { PIPELINE_NODES } from '@/lib/constants'
import { rgba } from '@/lib/utils'

export default function PipelineFlow() {
  return (
    <div className="flex flex-wrap items-center gap-1.5">
      {PIPELINE_NODES.map((node, i) => (
        <div key={i} className="flex items-center gap-1.5">
          <span
            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md font-mono text-[10px] font-medium"
            style={{
              color: node.color,
              backgroundColor: rgba(node.color, 0.06),
            }}
          >
            <span
              className="w-1.5 h-1.5 rounded-full"
              style={{ backgroundColor: node.color }}
            />
            {node.name}
          </span>

          {i < PIPELINE_NODES.length - 1 && (
            <svg
              className="w-3 h-3 text-slate-300 flex-shrink-0"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
            </svg>
          )}
        </div>
      ))}
    </div>
  )
}
