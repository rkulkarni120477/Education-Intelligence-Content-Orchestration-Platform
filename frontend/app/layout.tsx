import type { Metadata } from 'next'
import { Providers } from './providers'
import './globals.css'

export const metadata: Metadata = {
  title: 'Education Intelligence & Content Orchestration Platform',
  description: 'AI-powered educational content development and workflow orchestration',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="antialiased bg-page text-ink">
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
