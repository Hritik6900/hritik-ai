import { NextRequest, NextResponse } from 'next/server'

export const runtime = 'nodejs'

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000'
    
    console.log(`[/api/transcribe] Forwarding to ${backendUrl}/transcribe`)
    
    const response = await fetch(`${backendUrl}/transcribe`, {
      method: 'POST',
      body: formData,
    })
    
    if (!response.ok) {
      console.error(`[/api/transcribe] Backend error: ${response.status} ${response.statusText}`)
      return NextResponse.json(
        { error: 'Backend error' },
        { status: response.status }
      )
    }
    
    const data = await response.json()
    console.log(`[/api/transcribe] ✅ Transcription complete (latency: ${data.latency?.toFixed(2)}s)`)
    
    return NextResponse.json(data)
    
  } catch (error) {
    console.error('[/api/transcribe] Error:', error)
    return NextResponse.json(
      { error: 'Failed to process transcription request' },
      { status: 500 }
    )
  }
}
