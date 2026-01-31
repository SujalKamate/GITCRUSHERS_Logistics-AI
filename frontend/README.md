# Logistics AI Dashboard

A Next.js web application for the Agentic Logistics Control System.

## Features

- Real-time fleet tracking and monitoring
- AI-powered decision recommendations
- Interactive maps and data visualization
- Responsive design for desktop and mobile
- WebSocket integration for live updates

## Tech Stack

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety and better DX
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Beautiful icons
- **Socket.io** - Real-time communication (coming soon)
- **Leaflet** - Interactive maps (coming soon)
- **Chart.js** - Data visualization (coming soon)

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Run the development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
src/
├── app/                 # Next.js App Router
│   ├── globals.css     # Global styles
│   ├── layout.tsx      # Root layout
│   └── page.tsx        # Home page
├── components/         # Reusable components (coming soon)
├── lib/               # Utilities and helpers (coming soon)
└── types/             # TypeScript type definitions (coming soon)
```

## Development

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## Backend Integration

The frontend is configured to proxy API requests to the Python backend running on `http://localhost:8000`.