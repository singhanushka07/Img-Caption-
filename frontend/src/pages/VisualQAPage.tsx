import { useState, useRef, useEffect, useCallback } from 'react'
import type { ChatMessage } from '@/lib/types'
import { askVQA } from '@/lib/api'
import ImageUploader from '@/components/shared/ImageUploader'

function generateId(): string {
  return crypto.randomUUID()
}

export default function VisualQAPage() {
  const [image, setImage] = useState<File | null>(null)
  const [preview, setPreview] = useState<string>()
  const [sessionId, setSessionId] = useState(generateId)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [question, setQuestion] = useState('')
  const [loading, setLoading] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  const handleSelectImage = useCallback((file: File) => {
    setImage(file)
    setPreview(URL.createObjectURL(file))
  }, [])

  const handleClear = useCallback(() => {
    setImage(null)
    setPreview(undefined)
  }, [])

  const handleNewSession = useCallback(() => {
    setMessages([])
    setSessionId(generateId())
    inputRef.current?.focus()
  }, [])

  const handleAsk = useCallback(async () => {
    if (!image || !question.trim() || loading) return

    const q = question.trim()
    setQuestion('')
    setMessages((prev) => [...prev, { role: 'user', content: q }])
    setLoading(true)

    try {
      const res = await askVQA(image, q, sessionId)
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: res.answer },
      ])
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `Error: ${err instanceof Error ? err.message : 'Request failed'}`,
        },
      ])
    } finally {
      setLoading(false)
    }
  }, [image, question, loading, sessionId])

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault()
        handleAsk()
      }
    },
    [handleAsk],
  )

  return (
    <div className="flex flex-col lg:flex-row gap-6">
      {/* Left column */}
      <div className="w-full lg:w-1/3 space-y-4 flex-shrink-0">
        <ImageUploader
          onSelect={handleSelectImage}
          preview={preview}
          onClear={handleClear}
          height={300}
        />

        <button
          onClick={handleNewSession}
          className="w-full px-4 py-2 text-sm font-medium rounded-lg border border-slate-200 text-slate-600 hover:text-slate-800 hover:border-slate-300 bg-white transition-colors"
        >
          New Session
        </button>

        <p className="text-[11px] text-slate-400 leading-relaxed">
          Upload an image and ask questions about it. The Visual QA agent uses
          GPT-4o-mini for multi-turn conversations grounded in your image.
          Each session maintains context so follow-up questions work naturally.
        </p>
      </div>

      {/* Right column */}
      <div className="w-full lg:w-2/3 flex flex-col bg-white rounded-xl border border-slate-200/60 shadow-sm overflow-hidden">
        {/* Chat messages */}
        <div
          ref={scrollRef}
          className="flex-1 overflow-y-auto p-4 space-y-3"
          style={{ maxHeight: 380, minHeight: 380 }}
        >
          {messages.length === 0 && (
            <div className="flex items-center justify-center h-full text-sm text-slate-300">
              Ask a question about your image
            </div>
          )}

          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[75%] px-3.5 py-2.5 rounded-xl text-sm leading-relaxed ${
                  msg.role === 'user'
                    ? 'bg-blue-600 text-white rounded-br-sm'
                    : 'bg-slate-100 text-slate-700 rounded-bl-sm'
                }`}
              >
                {msg.content}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div className="bg-slate-100 text-slate-400 px-3.5 py-2.5 rounded-xl rounded-bl-sm text-sm">
                <span className="inline-flex gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-slate-300 animate-bounce" style={{ animationDelay: '0ms' }} />
                  <span className="w-1.5 h-1.5 rounded-full bg-slate-300 animate-bounce" style={{ animationDelay: '150ms' }} />
                  <span className="w-1.5 h-1.5 rounded-full bg-slate-300 animate-bounce" style={{ animationDelay: '300ms' }} />
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Input row */}
        <div className="flex items-center gap-2 p-3 border-t border-slate-100">
          <input
            ref={inputRef}
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={image ? 'Ask about this image...' : 'Upload an image first'}
            disabled={!image || loading}
            className="flex-1 px-3.5 py-2 text-sm rounded-lg border border-slate-200 bg-slate-50 text-slate-800 placeholder:text-slate-300 focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-400/30 disabled:opacity-50 transition-colors"
          />
          <button
            onClick={handleAsk}
            disabled={!image || !question.trim() || loading}
            className="px-4 py-2 text-sm font-medium rounded-lg bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            Ask
          </button>
        </div>
      </div>
    </div>
  )
}
