'use client'

import React, { useState, useRef, useEffect } from 'react'
import MessageBubble, { Message } from './MessageBubble'

const GREETING_MESSAGE = `Hi! I'm Hritik's AI representative — built to answer your questions about his background, projects, and experience. Ask me anything, or book a call directly below! 🚀`

export default function ChatWindow() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '0',
      sender: 'ai',
      text: GREETING_MESSAGE,
      sources: [],
      timestamp: new Date(),
    },
  ])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId] = useState(() => `session-${Date.now()}`)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async (text: string) => {
    if (!text.trim()) return

    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      sender: 'user',
      text: text.trim(),
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    setMessages(prev => [...prev, {
      id: 'typing',
      sender: 'ai',
      text: '',
      timestamp: new Date(),
    }])

    try {
      const response = await fetch(`/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text.trim(), session_id: sessionId }),
      })

      if (!response.ok) throw new Error(`Chat failed`)

      const data = await response.json()

      setMessages(prev => [
        ...prev.filter(m => m.id !== 'typing'),
        {
          id: `msg-${Date.now()}`,
          sender: 'ai',
          text: data.response,
          sources: data.sources,
          timestamp: new Date(),
        },
      ])
    } catch (error) {
      setMessages(prev => [
        ...prev.filter(m => m.id !== 'typing'),
        {
          id: `msg-${Date.now()}`,
          sender: 'ai',
          text: 'Something went wrong. Please try again.',
          timestamp: new Date(),
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    sendMessage(inputValue)
  }

  const suggestedQuestions = [
    "Tell me about NavDrishti",
    "Why should we hire Hritik?",
    "Hackathon wins?",
    "What is Hritik's CGPA?",
  ]

  return (
    <div className="flex flex-col h-screen max-w-2xl mx-auto bg-white shadow-xl">

      {/* Header */}
      <div className="flex items-center gap-3 px-5 py-4 border-b border-gray-100 bg-white shadow-sm">
        <div className="relative">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-white font-bold text-base shadow-md">
            H
          </div>
          <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-green-400 rounded-full border-2 border-white"></div>
        </div>
        <div className="flex-1">
          <h1 className="text-gray-900 font-semibold text-base leading-none">Hritik AI</h1>
          <p className="text-indigo-500 text-xs mt-0.5">AI Representative • RAG-Powered</p>
        </div>
        <span className="text-xs text-gray-400 bg-gray-50 border border-gray-200 px-3 py-1 rounded-full">
          ⚡ Groq
        </span>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-5 space-y-3 bg-gray-100">
        {messages.map((message) => (
          <MessageBubble
            key={message.id}
            message={message}
            isTyping={message.id === 'typing'}
          />
        ))}

        {messages.length === 1 && (
          <div className="flex flex-wrap gap-2 mt-3 animate-message">
            {suggestedQuestions.map((q, i) => (
              <button
                key={i}
                onClick={() => sendMessage(q)}
                className="text-xs px-3 py-2 rounded-full bg-white border border-gray-200 text-gray-600 hover:border-indigo-300 hover:text-indigo-600 hover:bg-indigo-50 transition-all shadow-sm"
              >
                {q}
              </button>
            ))}
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="px-4 py-4 bg-white border-t border-gray-100 shadow-sm">
        <form onSubmit={handleSubmit} className="flex gap-2 items-center">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Ask about Hritik's projects, skills..."
            disabled={isLoading}
            className="flex-1 px-4 py-3 rounded-full text-sm text-gray-800 placeholder-gray-400 bg-gray-50 border border-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-300 focus:border-transparent disabled:opacity-50 transition-all"
          />

          

          <button
            type="submit"
            disabled={isLoading || !inputValue.trim()}
            className="w-10 h-10 rounded-full bg-indigo-600 text-white flex items-center justify-center disabled:opacity-30 disabled:cursor-not-allowed hover:bg-indigo-700 transition-all shadow-md"
          >
            {isLoading ? (
              <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
              </svg>
            ) : (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
              </svg>
            )}
          </button>
        </form>

        <div className="flex items-center justify-between mt-2 px-1">
          <p className="text-gray-400 text-xs">RAG-grounded • No hallucinations</p>
          <button className="text-xs text-indigo-500 hover:text-indigo-700 transition-colors font-medium">
            📞 Book a Call
          </button>
        </div>
      </div>
    </div>
  )
}
