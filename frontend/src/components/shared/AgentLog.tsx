import { useRef, useEffect } from 'react'

interface AgentLogProps {
  lines: string[]
}

function lineColor(line: string): string {
  if (/PASSED|Accepted|Stored|Memory/i.test(line)) return '#059669'
  if (/FAILED|Escalat|escalating/i.test(line)) return '#d97706'
  if (/Error/i.test(line)) return '#dc2626'
  if (/RAG|retrieved|Retrieved/i.test(line)) return '#2563eb'
  if (/Tier|tier/i.test(line)) return '#7c3aed'
  if (/Confidence/i.test(line)) return '#059669'
  if (/YOLO|Complexity/i.test(line)) return '#d97706'
  return '#64748b'
}

export default function AgentLog({ lines }: AgentLogProps) {
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [lines])

  return (
    <div className="bg-white rounded-xl border border-slate-200/60 shadow-sm overflow-hidden">
      {/* Header */}
      <div className="flex items-center gap-2.5 px-4 py-2.5 border-b border-slate-100">
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
          <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
        </span>
        <span className="text-xs font-semibold text-slate-700">Agent Log</span>
        <span className="ml-auto text-[10px] font-mono font-medium text-emerald-600 tracking-wide">
          LIVE
        </span>
      </div>

      {/* Log body */}
      <div
        ref={scrollRef}
        className="overflow-y-auto bg-slate-50/80"
        style={{ maxHeight: 340 }}
      >
        <pre className="p-3 text-[11px] leading-relaxed font-mono">
          {lines.map((line, i) => (
            <div
              key={i}
              className="whitespace-pre-wrap"
              style={{
                color: lineColor(line),
                animation: `fadeIn 0.25s ease-out ${i * 0.07}s both`,
              }}
            >
              <span className="inline-block w-6 text-right mr-2 text-slate-300 select-none">
                {String(i + 1).padStart(2, '0')}
              </span>
              {line}
            </div>
          ))}
        </pre>
      </div>

      {/* Inline keyframes */}
      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(4px); }
          to   { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  )
}
