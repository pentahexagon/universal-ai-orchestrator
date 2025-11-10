'use client'

import { useState } from 'react'

interface Message {
  role: 'user' | 'assistant' | 'system'
  content: string
  agent?: string
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMessage: Message = { role: 'user', content: input }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: input }),
      })

      const data = await response.json()

      if (data.success) {
        // Add system message for processing
        setMessages(prev => [
          ...prev,
          { role: 'system', content: '3개 AI 에이전트가 분석 중...' }
        ])

        // Add individual agent responses
        if (data.responses) {
          Object.entries(data.responses).forEach(([agent, response]: [string, any]) => {
            if (response.success) {
              setMessages(prev => [
                ...prev.slice(0, -1), // Remove "processing" message
                {
                  role: 'assistant',
                  content: response.content,
                  agent: agent.toUpperCase()
                }
              ])
            }
          })
        }

        // Add synthesis
        if (data.synthesis) {
          setMessages(prev => [
            ...prev,
            {
              role: 'assistant',
              content: data.synthesis,
              agent: '통합 분석'
            }
          ])
        }
      } else {
        setMessages(prev => [
          ...prev,
          { role: 'system', content: `오류: ${data.error}` }
        ])
      }
    } catch (error) {
      setMessages(prev => [
        ...prev,
        { role: 'system', content: '네트워크 오류가 발생했습니다.' }
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="flex min-h-screen flex-col items-center p-4 md:p-24">
      <div className="w-full max-w-4xl">
        <h1 className="text-4xl font-bold mb-8 text-center">
          🤖 Universal AI Orchestrator
        </h1>
        <p className="text-center text-gray-600 mb-8">
          Gemini, ChatGPT, Claude가 협업하여 답변합니다
        </p>

        {/* Chat Messages */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-4 min-h-[500px] max-h-[600px] overflow-y-auto">
          {messages.length === 0 ? (
            <div className="text-center text-gray-400 mt-20">
              <p className="text-lg">질문을 입력하세요</p>
              <p className="text-sm mt-2">3개의 AI가 함께 답변합니다</p>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`p-4 rounded-lg ${
                    msg.role === 'user'
                      ? 'bg-blue-100 ml-auto max-w-[80%]'
                      : msg.role === 'system'
                      ? 'bg-gray-100 text-center text-sm text-gray-600'
                      : 'bg-green-50 mr-auto max-w-[80%]'
                  }`}
                >
                  {msg.agent && (
                    <div className="text-xs font-bold text-gray-600 mb-2">
                      {msg.agent}
                    </div>
                  )}
                  <div className="whitespace-pre-wrap">{msg.content}</div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="질문을 입력하세요..."
            disabled={loading}
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="px-6 py-3 bg-blue-500 text-white rounded-lg font-semibold hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition"
          >
            {loading ? '처리 중...' : '전송'}
          </button>
        </form>

        {/* Info */}
        <div className="mt-4 text-center text-sm text-gray-500">
          <p>
            💡 <strong>Gemini</strong> (정보수집) →{' '}
            <strong>ChatGPT</strong> (전략분석) →{' '}
            <strong>Claude</strong> (실행계획)
          </p>
        </div>
      </div>
    </main>
  )
}
