'use client'

import React, { useState, useRef, useEffect } from 'react'
import MessageBubble, { Message } from './MessageBubble'
import VoiceInput from './VoiceInput'

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

      if (!response.ok) throw new Error(`Chat failed: ${response.statusText}`)

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
          text: 'Something went wrong. Please try again in a moment.',
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

  const handleTranscript = (transcript: string) => {
    setInputValue(transcript)
  }

  const suggestedQuestions = [
    "Tell me about NavDrishti",
    "Why should we hire Hritik?",
    "How many hackathons has Hritik won?",
  ]

  return (
    <div className="flex flex-col h-screen max-w-3xl mx-auto" style={{background: 'linear-gradient(135deg, #0a0a0f 0%, #0f0f1a 50%, #0a0a0f 100%)'}}>
      
      <div className="glass border-b border-white/5 px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold text-lg">
              H
            </div>
            <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-green-400 rounded-full border-2 border-[#0a0a0f]"></div>
          </div>
          <div>
            <h1 className="text-white font-bold text-lg leading-none">Hritik AI</h1>
            <p className="text-indigo-400 text-xs mt-0.5">AI Representative • RAG-Powered • Online</p>
          </div>
          <div className="ml-auto">
            <span className="text-xs text-white/30 glass px-3 py-1 rounded-full">
              ⚡ Powered by Groq
            </span>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-2">
        {messages.map((message) => (
          <MessageBubble
            key={message.id}
            message={message}
            isTyping={message.id === 'typing'}
          />
        ))}

        {messages.length === 1 && (
          <div className="flex flex-wrap gap-2 mt-4 animate-message">
            {suggestedQuestions.map((q, i) => (
              <button
                key={i}
                onClick={() => sendMessage(q)}
                className="text-xs px-3 py-2 rounded-full border border-indigo-500/30 text-indigo-300 hover:bg-indigo-500/10 transition-all"
              >
                {q}
              </button>
            ))}
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="glass border-t border-white/5 px-4 py-4">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Ask about Hritik's projects, skills, experience..."
            disabled={isLoading}
            className="flex-1 px-4 py-3 rounded-xl text-sm text-white placeholder-white/25 disabled:opacity-50 transition-all outline-none focus:ring-1 focus:ring-indigo-500/50"
            style={{background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.08)'}}
          />

          <VoiceInput onTranscript={handleTranscript} isDisabled={isLoading} />

          <button
            type="submit"
            disabled={isLoading || !inputValue.trim()}
            className="px-4 py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 text-white disabled:opacity-30 disabled:cursor-not-allowed transition-all hover:from-indigo-500 hover:to-purple-500"
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

        <div className="flex items-center justify-between mt-3">
          <p className="text-white/20 text-xs">RAG-grounded • No hallucinations</p>
          <button className="text-xs text-indigo-400 hover:text-indigo-300 transition-colors">
            📞 Book a Call with Hritik
          </button>
        </div>
      </div>
    </div>
  )
}
