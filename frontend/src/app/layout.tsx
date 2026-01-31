import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Logistics AI Dashboard',
  description: 'Agentic AI Control System for Road Logistics',
  icons: {
    icon: [
      { url: '/favicon.svg', type: 'image/svg+xml' },
      { url: '/icon', type: 'image/png', sizes: '32x32' },
    ],
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}