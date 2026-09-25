import type { Metadata } from 'next'
import { Providers } from './providers'
import './globals.css'

export const metadata: Metadata = {
  title: 'Academian Education Platform',
  description: 'AI-powered educational content development and workflow orchestration',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <style>{`
          :root {
            --blue-dark: #0F172A;
            --blue-light: #1E40AF;
            --blue-primary: #2563EB;
            --blue-secondary: #3B82F6;
            --white: #FFFFFF;
            --gray-light: #F8FAFC;
          }
        `}</style>
      </head>
      <body className="antialiased bg-white">
        <Providers>
          <main>{children}</main>
        </Providers>
      </body>
    </html>
  )
}
