import os
import sys
import json
from http.server import BaseHTTPRequestHandler
import urllib.parse

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_agent.arbo_agent import ArboDentalAgent
from data_preparation.knowledge_base import ArboDentalKnowledgeBase

# Global agent instance (will be initialized on first request)
agent = None

def initialize_agent():
    """Initialize the knowledge base and AI agent"""
    global agent
    if agent is None:
        try:
            kb = ArboDentalKnowledgeBase()
            agent = ArboDentalAgent(kb)
        except Exception as e:
            print(f"Error initializing agent: {e}")
            agent = None
    return agent

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST requests to /api/chat"""
        try:
            # Initialize agent if not already done
            agent = initialize_agent()
            if agent is None:
                self.send_error_response(500, 'AI agent is not available. Please check configuration.')
                return
            
            # Parse request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            user_message = data.get('message', '').strip()
            if not user_message:
                self.send_error_response(400, 'Message is required')
                return
            
            # Process the query
            result = agent.process_query(user_message)
            
            # Send response
            response_data = {
                'response': result['response'],
                'confidence': result.get('confidence', 0.0),
                'sources': result.get('sources', []),
                'timestamp': result.get('timestamp', ''),
                'debug_info': result.get('debug_info', {})
            }
            
            self.send_json_response(200, response_data)
            
        except Exception as e:
            self.send_error_response(500, f'An error occurred: {str(e)}')
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/api/chat':
            self.send_error_response(405, 'Method not allowed. Use POST.')
        else:
            self.send_error_response(404, 'Not found')
    
    def send_json_response(self, status_code, data):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def send_error_response(self, status_code, message):
        """Send error response"""
        self.send_json_response(status_code, {'error': message})
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
