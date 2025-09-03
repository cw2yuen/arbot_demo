import os
import sys
import json
from http.server import BaseHTTPRequestHandler

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the lightweight agent from chat.py
from api.chat import LightweightArboAgent

# Global agent instance
agent = None

def initialize_agent():
    """Initialize the lightweight AI agent"""
    global agent
    if agent is None:
        try:
            agent = LightweightArboAgent()
        except Exception as e:
            print(f"Error initializing agent: {e}")
            agent = None
    return agent

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests to /api/agent-info"""
        try:
            agent = initialize_agent()
            if agent is None:
                self.send_error_response(500, 'Agent not available')
                return
            
            info = {
                'agent_type': 'Arbo Dental Care AI Assistant (Lightweight)',
                'model': agent.model,
                'knowledge_base_chunks': len(agent.knowledge_base),
                'capabilities': [
                    'Answer questions about Arbo Dental Care',
                    'Provide team member information',
                    'List services offered',
                    'Share contact information',
                    'Direct to office for appointments'
                ],
                'limitations': [
                    'Cannot make appointments',
                    'Cannot provide medical advice',
                    'Cannot give specific pricing',
                    'Cannot diagnose dental problems'
                ]
            }
            self.send_json_response(200, info)
            
        except Exception as e:
            self.send_error_response(500, f'Error getting agent info: {str(e)}')
    
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
