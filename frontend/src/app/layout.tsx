import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Logistics AI Dashboard',
  description: 'Agentic AI Control System for Road Logistics',
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