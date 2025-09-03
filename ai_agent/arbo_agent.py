import os
import openai
from typing import List, Dict, Any
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ArboDentalAgent:
    def __init__(self, knowledge_base, openai_api_key: str = None):
        self.knowledge_base = knowledge_base
        
        # Initialize OpenAI
        api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        self.client = openai.OpenAI(api_key=api_key)
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4')
        
        # Agent personality and instructions
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
- Diagnose dental problems

Avoid:
- Using bot-like language like "Based on the information provided"
- Referring to yourself as a bot. You can refer to yourself as Arbot however

Use the provided knowledge base information to answer questions accurately."""

    def process_query(self, user_query: str) -> Dict[str, Any]:
        """Process a user query and return a response"""
        try:
            # Search knowledge base for relevant information
            search_results = self.knowledge_base.search(user_query, n_results=5)
            
            # Prepare context for the AI
            context = self._prepare_context(search_results)
            
            # Generate response using OpenAI
            response = self._generate_response(user_query, context)
            
            return {
                'query': user_query,
                'response': response,
                'sources': [result['metadata']['source'] for result in search_results],
                'confidence': self._calculate_confidence(search_results),
                'debug_info': {
                    'search_results_count': len(search_results),
                    'search_results': [
                        {
                            'text': result['text'][:200] + '...' if len(result['text']) > 200 else result['text'],
                            'metadata': result['metadata'],
                            'distance': result['distance'],
                            'text_length': len(result['text'])
                        }
                        for result in search_results
                    ],
                    'context_preview': self._prepare_context(search_results)[:500] + '...' if len(self._prepare_context(search_results)) > 500 else self._prepare_context(search_results)
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
    
    def _prepare_context(self, search_results: List[Dict[str, Any]]) -> str:
        """Prepare context from search results for the AI"""
        if not search_results:
            return "No specific information found in the knowledge base."
        
        context_parts = []
        for i, result in enumerate(search_results, 1):
            context_parts.append(f"Source {i}: {result['text']}")
        
        return "\n\n".join(context_parts)
    
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
    
    def _calculate_confidence(self, search_results: List[Dict[str, Any]]) -> float:
        """Calculate confidence score based on search results"""
        if not search_results:
            return 0.0
        
        # Calculate average distance (lower distance = higher confidence)
        distances = [result['distance'] for result in search_results]
        avg_distance = sum(distances) / len(distances)
        
        # Convert distance to confidence (0-1 scale)
        # Assuming cosine distance where 0 = perfect match, 2 = completely opposite
        confidence = max(0.0, 1.0 - (avg_distance / 2.0))
        
        return round(confidence, 2)
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the agent"""
        kb_info = self.knowledge_base.get_collection_info()
        
        return {
            'agent_type': 'Arbo Dental Care AI Assistant',
            'model': self.model,
            'knowledge_base_chunks': kb_info['total_chunks'],
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
    
    def test_common_queries(self) -> List[Dict[str, Any]]:
        """Test the agent with common queries"""
        test_queries = [
            "What is the address of Arbo Dental Care?",
            "What are the office hours?",
            "How many dentists work there?",
            "What services do you provide?",
            "Can I walk in for an emergency?",
            "What languages do you speak?",
            "How long has the practice been open?",
            "Who is Dr. Pham?"
        ]
        
        results = []
        for query in test_queries:
            result = self.process_query(query)
            results.append(result)
        
        return results

def main():
    """Test the Arbo Dental Agent"""
    # This would typically be called from the main application
    # For testing purposes, we'll show the structure
    print("Arbo Dental Care AI Agent")
    print("This agent processes queries about Arbo Dental Care")
    print("To use this agent, you need:")
    print("1. A built knowledge base")
    print("2. OpenAI API key")
    print("3. Integration with the chatbot interface")

if __name__ == "__main__":
    main()
