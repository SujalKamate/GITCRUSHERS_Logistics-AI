import { Truck, MapPin, Activity, AlertTriangle } from 'lucide-react'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Truck className="h-8 w-8 text-primary-600" />
              <h1 className="ml-3 text-xl font-semibold text-gray-900">
                Logistics AI Dashboard
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-500">
                Agentic Control System
              </span>
              <div className="h-2 w-2 bg-success-500 rounded-full animate-pulse"></div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Welcome to Logistics AI Control System
          </h2>
          <p className="text-lg text-gray-600 max-w-3xl">
            Continuous decision-making for road logistics. Our agentic AI system 
            observes, reasons, plans, and acts to optimize your fleet operations in real-time.
          </p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="card">
            <div className="flex items-center">
              <div className="p-2 bg-primary-100 rounded-lg">
                <Truck className="h-6 w-6 text-primary-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Active Trucks</p>
                <p className="text-2xl font-semibold text-gray-900">12</p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center">
              <div className="p-2 bg-success-100 rounded-lg">
                <MapPin className="h-6 w-6 text-success-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">En Route</p>
                <p className="text-2xl font-semibold text-gray-900">8</p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center">
              <div className="p-2 bg-warning-100 rounded-lg">
                <Activity className="h-6 w-6 text-warning-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Active Loads</p>
                <p className="text-2xl font-semibold text-gray-900">15</p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center">
              <div className="p-2 bg-danger-100 rounded-lg">
                <AlertTriangle className="h-6 w-6 text-danger-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Issues</p>
                <p className="text-2xl font-semibold text-gray-900">2</p>
              </div>
            </div>
          </div>
        </div>

        {/* Control Loop Status */}
        <div className="card mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            AI Control Loop Status
          </h3>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-6">
              <div className="flex items-center">
                <div className="h-3 w-3 bg-success-500 rounded-full animate-pulse mr-2"></div>
                <span className="text-sm text-gray-600">Observing</span>
              </div>
              <div className="flex items-center">
                <div className="h-3 w-3 bg-primary-500 rounded-full mr-2"></div>
                <span className="text-sm text-gray-600">Reasoning</span>
              </div>
              <div className="flex items-center">
                <div className="h-3 w-3 bg-warning-500 rounded-full mr-2"></div>
                <span className="text-sm text-gray-600">Planning</span>
              </div>
              <div className="flex items-center">
                <div className="h-3 w-3 bg-gray-300 rounded-full mr-2"></div>
                <span className="text-sm text-gray-600">Acting</span>
              </div>
            </div>
            <div className="text-sm text-gray-500">
              Cycle #1,247 • Last update: 2 seconds ago
            </div>
          </div>
        </div>

        {/* Coming Soon Features */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              🗺️ Real-time Fleet Map
            </h3>
            <p className="text-gray-600 mb-4">
              Interactive map showing live truck positions, routes, and traffic conditions.
            </p>
            <div className="bg-gray-100 rounded-lg h-32 flex items-center justify-center">
              <span className="text-gray-500">Map component loading...</span>
            </div>
          </div>

          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              🤖 AI Decision Center
            </h3>
            <p className="text-gray-600 mb-4">
              Review and approve AI-generated decisions for route optimization and load assignment.
            </p>
            <div className="bg-gray-100 rounded-lg h-32 flex items-center justify-center">
              <span className="text-gray-500">Decision interface loading...</span>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}