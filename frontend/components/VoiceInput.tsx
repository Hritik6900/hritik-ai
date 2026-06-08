'use client'

import React, { useRef, useState } from 'react'

interface VoiceInputProps {
  onTranscript: (transcript: string) => void
  isDisabled?: boolean
}

export default function VoiceInput({ onTranscript, isDisabled }: VoiceInputProps) {
  const [isRecording, setIsRecording] = useState(false)
  const [isTranscribing, setIsTranscribing] = useState(false)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm',
      })
      
      mediaRecorderRef.current = mediaRecorder
      chunksRef.current = []
      
      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data)
        }
      }
      
      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm' })
        await transcribeAudio(audioBlob)
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop())
      }
      
      mediaRecorder.start()
      setIsRecording(true)
      console.log('🎤 Recording started')
    } catch (error) {
      console.error('❌ Microphone access denied:', error)
      alert('Unable to access microphone. Please check permissions.')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      console.log('🎤 Recording stopped')
    }
  }

  const transcribeAudio = async (audioBlob: Blob) => {
    setIsTranscribing(true)
    console.log('📤 Sending audio to backend for transcription...')
    
    try {
      const formData = new FormData()
      formData.append('file', audioBlob, 'audio.webm')
      
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
      
      const response = await fetch(`${backendUrl}/transcribe`, {
        method: 'POST',
        body: formData,
      })
      
      if (!response.ok) {
        throw new Error(`Transcription failed: ${response.statusText}`)
      }
      
      const data = await response.json()
      console.log(`✅ Transcription complete: "${data.transcript}"`)
      onTranscript(data.transcript)
      
    } catch (error) {
      console.error('❌ Transcription error:', error)
      alert('Transcription failed. Please try again.')
    } finally {
      setIsTranscribing(false)
    }
  }

  const handleToggle = () => {
    if (isRecording) {
      stopRecording()
    } else {
      startRecording()
    }
  }

  return (
    <button
      onClick={handleToggle}
      disabled={isDisabled || isTranscribing}
      className={`p-3 rounded-full transition-all ${
        isRecording
          ? 'bg-red-600 hover:bg-red-700 animate-recording-pulse'
          : isTranscribing
          ? 'bg-yellow-600 cursor-wait'
          : 'bg-blue-600 hover:bg-blue-700'
      } text-white disabled:opacity-50 disabled:cursor-not-allowed`}
      title={
        isRecording
          ? 'Stop recording'
          : isTranscribing
          ? 'Transcribing...'
          : 'Start recording'
      }
    >
      {isTranscribing ? (
        <span className="text-lg">⏳</span>
      ) : isRecording ? (
        <span className="text-lg">🔴</span>
      ) : (
        <span className="text-lg">🎤</span>
      )}
    </button>
  )
}
