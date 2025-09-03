import json
import os
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests to /api/diagnostic"""
        try:
            # Check environment variables
            openai_key = os.getenv('OPENAI_API_KEY')
            openai_model = os.getenv('OPENAI_MODEL', 'gpt-4')
            
            # Check if we can import required modules
            import_status = {}
            try:
                import openai
                import_status['openai'] = 'OK'
            except ImportError as e:
                import_status['openai'] = f'ERROR: {str(e)}'
            
            try:
                import numpy
                import_status['numpy'] = 'OK'
            except ImportError as e:
                import_status['numpy'] = f'ERROR: {str(e)}'
            
            diagnostic_data = {
                'status': 'success',
                'environment': {
                    'OPENAI_API_KEY': 'SET' if openai_key else 'NOT SET',
                    'OPENAI_MODEL': openai_model,
                    'PYTHON_VERSION': os.sys.version,
                },
                'imports': import_status,
                'endpoint': '/api/diagnostic',
                'message': 'Diagnostic endpoint working'
            }
            
            self.send_json_response(200, diagnostic_data)
            
        except Exception as e:
            error_data = {
                'status': 'error',
                'error': str(e),
                'endpoint': '/api/diagnostic'
            }
            self.send_json_response(500, error_data)
    
    def send_json_response(self, status_code, data):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
