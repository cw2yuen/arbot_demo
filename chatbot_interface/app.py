from flask import Flask, render_template, request, jsonify
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_agent.arbo_agent import ArboDentalAgent
from data_preparation.knowledge_base import ArboDentalKnowledgeBase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize knowledge base and agent
def initialize_agent():
    """Initialize the knowledge base and AI agent"""
    try:
        kb = ArboDentalKnowledgeBase()
        agent = ArboDentalAgent(kb)
        return agent
    except Exception as e:
        print(f"Error initializing agent: {e}")
        return None

# Global agent instance
agent = None

@app.route('/')
def index():
    """Main chat interface"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    global agent
    
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Initialize agent if not already done
        if agent is None:
            agent = initialize_agent()
            if agent is None:
                return jsonify({'error': 'AI agent is not available. Please check configuration.'}), 500
        
        # Process the query
        result = agent.process_query(user_message)
        
        return jsonify({
            'response': result['response'],
            'confidence': result.get('confidence', 0.0),
            'sources': result.get('sources', []),
            'timestamp': result.get('timestamp', ''),
            'debug_info': result.get('debug_info', {})
        })
        
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/api/agent-info')
def agent_info():
    """Get information about the AI agent"""
    global agent
    
    if agent is None:
        agent = initialize_agent()
    
    if agent is None:
        return jsonify({'error': 'Agent not available'}), 500
    
    try:
        info = agent.get_agent_info()
        return jsonify(info)
    except Exception as e:
        return jsonify({'error': f'Error getting agent info: {str(e)}'}), 500

@app.route('/api/test-queries')
def test_queries():
    """Test the agent with common queries"""
    global agent
    
    if agent is None:
        agent = initialize_agent()
    
    if agent is None:
        return jsonify({'error': 'Agent not available'}), 500
    
    try:
        results = agent.test_common_queries()
        return jsonify({'test_results': results})
    except Exception as e:
        return jsonify({'error': f'Error running test queries: {str(e)}'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'Arbo Dental Care AI Chatbot'})

@app.route('/api/debug-test')
def debug_test():
    """Test endpoint to verify debug information is working"""
    global agent
    
    if agent is None:
        agent = initialize_agent()
    
    if agent is None:
        return jsonify({'error': 'Agent not available'}), 500
    
    try:
        # Test with a simple query
        result = agent.process_query("What is the address of Arbo Dental Care?")
        return jsonify({
            'test_query': "What is the address of Arbo Dental Care?",
            'full_result': result,
            'has_debug_info': 'debug_info' in result,
            'debug_info_keys': list(result.get('debug_info', {}).keys()) if 'debug_info' in result else []
        })
    except Exception as e:
        return jsonify({'error': f'Error testing debug: {str(e)}'}), 500

if __name__ == '__main__':
    # Check if required environment variables are set
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        print("Warning: OPENAI_API_KEY not set. The AI agent will not function properly.")
        print("Please set your OpenAI API key in the .env file.")
    
    # Initialize agent on startup
    agent = initialize_agent()
    
    if agent:
        print("AI Agent initialized successfully!")
        info = agent.get_agent_info()
        print(f"Agent type: {info['agent_type']}")
        print(f"Knowledge base chunks: {info['knowledge_base_chunks']}")
    else:
        print("Failed to initialize AI Agent. Check configuration and try again.")
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5001)
