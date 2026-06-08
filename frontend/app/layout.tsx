import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Hritik AI - AI Representative',
  description: 'AI-powered representative for Hritik Kumar',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body style={{background: '#f8f9fa', minHeight: '100vh'}}>
        {children}
      </body>
    </html>
  )
}
