#!/usr/bin/env python3
"""
Simple HTTP server for the customer-facing delivery request app.
"""

import http.server
import socketserver
import os
from pathlib import Path

PORT = 3001
DIRECTORY = Path(__file__).parent

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def main():
    """Start the customer app server."""
    print("🚀 Starting Customer Delivery Request App")
    print("="*50)
    print(f"📱 Customer App: http://localhost:{PORT}")
    print(f"📊 Dashboard: http://localhost:3000/requests")
    print(f"🔧 API Server: http://localhost:8000")
    print()
    print("💡 How it works:")
    print("1. Customers use the mobile app to request deliveries")
    print("2. Requests appear in the dashboard as 'Pending'")
    print("3. AI processes and allocates trucks automatically")
    print("4. Customers get updates via SMS/email")
    print()
    print("Press Ctrl+C to stop the server")
    print("="*50)
    
    with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Customer app server stopped")

if __name__ == "__main__":
    main()