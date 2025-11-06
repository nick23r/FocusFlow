"""
API endpoint for loading tasks from Firebase using username-based storage.
"""
from http.server import BaseHTTPRequestHandler
import json
import sys
import os
from urllib.parse import urlparse, parse_qs

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.firebase_connect import load_user_tasks

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET request for loading tasks"""
        try:
            # Parse query parameters
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            
            username = query_params.get('username', [None])[0]
            
            if not username:
                self.send_error_response(400, "Username required")
                return
            
            # Load from Firebase using username
            result = load_user_tasks(username)
            
            if result.get("success"):
                response_data = {
                    "success": True,
                    "tasks": result.get("tasks", []),
                    "task_count": len(result.get("tasks", []))
                }
            else:
                response_data = {
                    "success": False,
                    "tasks": [],
                    "message": "No tasks found"
                }
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
            
        except Exception as e:
            print(f"Error in load endpoint: {str(e)}")
            self.send_error_response(500, "Internal server error")
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def send_error_response(self, code, message):
        """Send error response"""
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode('utf-8'))
