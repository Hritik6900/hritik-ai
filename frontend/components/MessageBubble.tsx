'use client'

import React from 'react'
import SourceBadge from './SourceBadge'

export interface Message {
  id: string
  sender: 'user' | 'ai'
  text: string
  sources?: string[]
  timestamp: Date
}

interface MessageBubbleProps {
  message: Message
  isTyping?: boolean
}

export default function MessageBubble({ message, isTyping }: MessageBubbleProps) {
  const isUser = message.sender === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} animate-message`}>
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-white text-xs font-bold mr-2 mt-1 shrink-0 shadow-sm">
          H
        </div>
      )}

      <div className={`max-w-xs lg:max-w-md xl:max-w-lg flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
        <div
          className={`px-4 py-3 rounded-2xl text-sm leading-relaxed shadow-sm ${
            isUser
              ? 'bg-indigo-600 text-white rounded-tr-sm'
              : 'bg-white text-gray-800 rounded-tl-sm border border-gray-100'
          }`}
        >
          {isTyping ? (
            <div className="flex space-x-1.5 py-1">
              <div className="typing-dot w-2 h-2 bg-gray-400 rounded-full"></div>
              <div className="typing-dot w-2 h-2 bg-gray-400 rounded-full"></div>
              <div className="typing-dot w-2 h-2 bg-gray-400 rounded-full"></div>
            </div>
          ) : (
            <div className="whitespace-pre-wrap break-words">{message.text}</div>
          )}
        </div>

        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-1.5 ml-1">
            {message.sources.map((source, idx) => (
              <SourceBadge key={idx} source={source} />
            ))}
          </div>
        )}

        <div className={`text-xs mt-1 text-gray-400 ${isUser ? 'mr-1' : 'ml-1'}`}>
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>

      {isUser && (
        <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center text-gray-600 text-xs font-bold ml-2 mt-1 shrink-0">
          U
        </div>
      )}
    </div>
  )
}
