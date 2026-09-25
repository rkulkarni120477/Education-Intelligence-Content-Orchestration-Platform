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
            --brown-dark: #6B4423;
            --brown-light: #8B5A3C;
            --tan: #D2B48C;
            --cream: #FFF8F0;
            --tan-dark: #A0826D;
            --brown-darker: #5A3A1F;
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
