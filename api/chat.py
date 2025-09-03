import os
import sys
import json
from http.server import BaseHTTPRequestHandler
import urllib.parse

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Lightweight version without ChromaDB for Vercel deployment
class LightweightArboAgent:
    def __init__(self):
        import openai
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4')
        
        # Pre-defined knowledge base for Arbo Dental Care
        self.knowledge_base = {
            "address": "Arbo Dental Care is located at 123 Main Street, Bradford, Ontario, Canada",
            "phone": "Phone: (905) 775-7377",
            "hours": "Office Hours: Monday-Friday 9:00 AM - 5:00 PM, Saturday 9:00 AM - 2:00 PM",
            "services": "Services: General Dentistry, Cleanings, Fillings, Crowns, Root Canals, Extractions, Cosmetic Dentistry",
            "languages": "Languages: English, Portuguese, Spanish, Vietnamese",
            "established": "Established since 1995",
            "team": "Team includes Dr. Pham and experienced dental professionals",
            "insurance": "We accept most major insurance plans",
            "emergency": "For dental emergencies, please call (905) 775-7377"
        }
        
        self.system_prompt = """You are Arbo Dental Care's AI assistant named Arbot, a friendly and knowledgeable virtual receptionist. 
        
Your role is to help patients and potential patients with information about Arbo Dental Care, a family dentistry practice in Bradford, Ontario.

Key facts about Arbo Dental Care:
- Location: Bradford, Ontario
- Established: Since 1995
- Type: Family Dentistry
- Languages: English, Portuguese, Spanish, Vietnamese

Always be:
- Professional yet warm and welcoming
- Accurate with information
- Clear about what you can and cannot help with

You can help with:
- General information about the clinic
- Team member information
- Services offered
- Contact information
- Basic questions about dental care

You cannot:
- Make appointments
- Provide medical advice
- Give specific pricing information
- Diagnose dental problems

Avoid:
- Using bot-like language like "Based on the information provided"
- Referring to yourself as a bot. You can refer to yourself as Arbot however

Use the provided knowledge base information to answer questions accurately."""

    def search_knowledge(self, query: str) -> str:
        """Simple keyword-based search"""
        query_lower = query.lower()
        relevant_info = []
        
        for key, value in self.knowledge_base.items():
            if any(word in query_lower for word in key.split('_')):
                relevant_info.append(value)
        
        # Add general info if no specific match
        if not relevant_info:
            relevant_info = [
                self.knowledge_base["address"],
                self.knowledge_base["phone"],
                self.knowledge_base["services"]
            ]
        
        return " | ".join(relevant_info)

    def process_query(self, user_query: str) -> dict:
        """Process a user query and return a response"""
        try:
            # Search knowledge base
            context = self.search_knowledge(user_query)
            
            # Generate response using OpenAI
            response = self._generate_response(user_query, context)
            
            return {
                'query': user_query,
                'response': response,
                'sources': ['Arbo Dental Care Knowledge Base'],
                'confidence': 0.9,
                'debug_info': {
                    'search_results_count': 1,
                    'context_preview': context[:200] + '...' if len(context) > 200 else context
                }
            }
            
        except Exception as e:
            return {
                'query': user_query,
                'response': f"I apologize, but I encountered an error processing your request. Please contact Arbo Dental Care directly at (905) 775-7377 for assistance.",
                'error': str(e),
                'sources': [],
                'confidence': 0.0
            }
    
    def _generate_response(self, user_query: str, context: str) -> str:
        """Generate response using OpenAI"""
        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"""Based on the following information about Arbo Dental Care, please answer this question: {user_query}

Context information:
{context}

Please provide a helpful, accurate response based on the information above. If the information isn't sufficient to fully answer the question, acknowledge what you can answer and suggest they contact the office for more details."""}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"I apologize, but I'm having trouble generating a response right now. Please contact Arbo Dental Care directly at (905) 775-7377 for assistance. Error: {str(e)}"

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
