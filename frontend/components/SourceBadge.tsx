'use client'

import React from 'react'

interface SourceBadgeProps {
  source: string
}

export default function SourceBadge({ source }: SourceBadgeProps) {
  // Clean up filename for display
  const displayName = source.split('/').pop() || source
  
  return (
    <span className="inline-block bg-slate-700 text-slate-100 px-3 py-1 rounded-full text-xs font-medium mr-2 mt-2 border border-slate-600 hover:border-blue-400 transition-colors">
      [{displayName}]
    </span>
  )
}
