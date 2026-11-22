import { useState, useCallback, useRef, type DragEvent } from 'react'
import { cn } from '@/lib/utils'

interface ImageUploaderProps {
  onSelect: (file: File) => void
  preview?: string
  onClear?: () => void
  height?: number
}

export default function ImageUploader({
  onSelect,
  preview,
  onClear,
  height = 280,
}: ImageUploaderProps) {
  const [dragging, setDragging] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleDragOver = useCallback((e: DragEvent) => {
    e.preventDefault()
    setDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: DragEvent) => {
    e.preventDefault()
    setDragging(false)
  }, [])

  const handleDrop = useCallback(
    (e: DragEvent) => {
      e.preventDefault()
      setDragging(false)
      const file = e.dataTransfer.files?.[0]
      if (file && file.type.startsWith('image/')) {
        onSelect(file)
      }
    },
    [onSelect],
  )

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0]
      if (file) onSelect(file)
    },
    [onSelect],
  )

  if (preview) {
    return (
      <div
        className="relative rounded-xl overflow-hidden border border-slate-200/60 bg-slate-50 group"
        style={{ height }}
      >
        <img
          src={preview}
          alt="Upload preview"
          className="w-full h-full object-contain"
        />
        {onClear && (
          <button
            onClick={onClear}
            className="absolute top-2 right-2 w-7 h-7 rounded-full bg-black/50 text-white flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-150 hover:bg-black/70"
          >
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>
    )
  }

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={() => inputRef.current?.click()}
      className={cn(
        'flex flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed cursor-pointer transition-colors duration-150',
        dragging
          ? 'border-blue-400 bg-blue-50/50'
          : 'border-slate-200 bg-slate-50/50 hover:border-slate-300 hover:bg-slate-50',
      )}
      style={{ height }}
    >
      <svg
        className="w-10 h-10 text-slate-300"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        strokeWidth={1.5}
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"
        />
      </svg>
      <div className="text-center">
        <p className="text-sm font-medium text-slate-500">
          Drop image here or <span className="text-blue-600">browse</span>
        </p>
        <p className="text-[11px] text-slate-400 mt-0.5">
          PNG, JPG, WEBP up to 10MB
        </p>
      </div>
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={handleChange}
      />
    </div>
  )
}
