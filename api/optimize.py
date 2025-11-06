"""
API endpoint for task optimization using 0/1 Knapsack or Fractional Knapsack DP algorithm.
"""
from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.optimizer import optimize_tasks
from backend.fractional_optimize import optimize_tasks_fractional

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST request for task optimization"""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            if not data:
                self.send_error_response(400, "No data provided")
                return
            
            tasks = data.get("tasks", [])
            available_time = data.get("available_time", 480)  # Default 8 hours
            method = data.get("method", "0/1")  # Default to 0/1 Knapsack
            
            if not tasks:
                self.send_error_response(400, "No tasks provided")
                return
            
            if available_time <= 0:
                self.send_error_response(400, "Available time must be positive")
                return
            
            # Validate task structure
            for task in tasks:
                required_fields = ["name", "duration", "priority", "category"]
                for field in required_fields:
                    if field not in task:
                        self.send_error_response(400, f"Task missing required field: {field}")
                        return
                
                if task["duration"] <= 0:
                    self.send_error_response(400, "Task duration must be positive")
                    return
                
                if not 1 <= task["priority"] <= 5:
                    self.send_error_response(400, "Task priority must be between 1 and 5")
                    return
                
                if task["category"] not in ["work", "health", "learning", "chore", "relaxation"]:
                    self.send_error_response(400, "Invalid task category")
                    return
            
            if method == "fractional":
                result = optimize_tasks_fractional(tasks, available_time)
            else:
                result = optimize_tasks(tasks, available_time)
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
            
        except Exception as e:
            print(f"Error in optimize endpoint: {str(e)}")
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
