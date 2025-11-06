"""
API endpoint for saving tasks to Firebase using username-based storage.
"""
from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.firebase_connect import save_user_tasks

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST request for saving tasks"""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            if not data:
                self.send_error_response(400, "No data provided")
                return
            
            username = data.get("username")
            tasks = data.get("tasks", [])
            
            if not username:
                self.send_error_response(400, "Username required")
                return
            
            if not tasks:
                self.send_error_response(400, "No tasks to save")
                return
            
            # Save to Firebase using username
            result = save_user_tasks(username, tasks)
            
            if result.get("success"):
                response_data = {
                    "success": True,
                    "message": "Tasks saved successfully",
                    "task_count": len(tasks)
                }
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode('utf-8'))
            else:
                self.send_error_response(500, "Failed to save tasks")
            
        except Exception as e:
            print(f"Error in save endpoint: {str(e)}")
            self.send_error_response(500, "Internal server error")
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def send_error_response(self, code, message):
        """Send error response"""
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode('utf-8'))
