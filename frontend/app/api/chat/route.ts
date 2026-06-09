import { NextRequest, NextResponse } from 'next/server'

export const runtime = 'nodejs'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL
    
    console.log(`[/api/chat] Forwarding to ${backendUrl}/chat`)
    
    const response = await fetch(`${backendUrl}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    })
    
    if (!response.ok) {
      console.error(`[/api/chat] Backend error: ${response.status} ${response.statusText}`)
      return NextResponse.json(
        { error: 'Backend error' },
        { status: response.status }
      )
    }
    
    const data = await response.json()
    console.log(`[/api/chat] ✅ Response received (latency: ${data.latency?.toFixed(2)}s)`)
    
    return NextResponse.json(data)
    
  } catch (error) {
    console.error('[/api/chat] Error:', error)
    return NextResponse.json(
      { error: 'Failed to process chat request' },
      { status: 500 }
    )
  }
}
