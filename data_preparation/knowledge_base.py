import json
import os
import chromadb
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Any
import re

class ArboDentalKnowledgeBase:
    def __init__(self, persist_directory="./chroma_db"):
        self.persist_directory = persist_directory
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="arbo_dental_knowledge",
            metadata={"hnsw:space": "cosine"}
        )
        
    def process_scraped_data(self, data_file: str) -> List[Dict[str, Any]]:
        """Process scraped data and prepare it for the knowledge base"""
        with open(data_file, 'r', encoding='utf-8') as f:
            scraped_data = json.load(f)
        
        processed_chunks = []
        
        for page in scraped_data:
            page_url = page.get('url', '')
            page_title = page.get('title', '')
            
            # Process main content
            for content_item in page.get('content', []):
                if isinstance(content_item, dict):
                    if content_item.get('type') in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li']:
                        text = content_item.get('text', '')
                        if text and len(text.strip()) > 20:
                            chunk = {
                                'text': text,
                                'metadata': {
                                    'source': page_url,
                                    'title': page_title,
                                    'content_type': content_item.get('type'),
                                    'chunk_type': 'content'
                                }
                            }
                            processed_chunks.append(chunk)
                    
                    elif content_item.get('type') == 'team_section':
                        for member in content_item.get('data', []):
                            member_text = f"Team Member: {member.get('name', '')}"
                            if member.get('bio'):
                                member_text += f" - {member.get('bio')}"
                            
                            chunk = {
                                'text': member_text,
                                'metadata': {
                                    'source': page_url,
                                    'title': page_title,
                                    'content_type': 'team_member',
                                    'chunk_type': 'team_info'
                                }
                            }
                            processed_chunks.append(chunk)
                    
                    elif content_item.get('type') == 'contact_info':
                        contact_data = content_item.get('data', {})
                        contact_text = "Contact Information: "
                        if contact_data.get('phone'):
                            contact_text += f"Phone: {contact_data['phone']} "
                        if contact_data.get('email'):
                            contact_text += f"Email: {contact_data['email']} "
                        if contact_data.get('address'):
                            contact_text += f"Address: {contact_data['address']}"
                        
                        chunk = {
                            'text': contact_text,
                            'metadata': {
                                'source': page_url,
                                'title': page_title,
                                'content_type': 'contact_info',
                                'chunk_type': 'contact'
                            }
                        }
                        processed_chunks.append(chunk)
                    
                    elif content_item.get('type') == 'services':
                        for service in content_item.get('data', []):
                            chunk = {
                                'text': f"Service: {service}",
                                'metadata': {
                                    'source': page_url,
                                    'title': page_title,
                                    'content_type': 'service',
                                    'chunk_type': 'service_info'
                                }
                            }
                            processed_chunks.append(chunk)
        
        return processed_chunks
    
    def add_to_knowledge_base(self, chunks: List[Dict[str, Any]]):
        """Add processed chunks to the knowledge base"""
        if not chunks:
            print("No chunks to add to knowledge base")
            return
        
        texts = [chunk['text'] for chunk in chunks]
        metadatas = [chunk['metadata'] for chunk in chunks]
        ids = [f"chunk_{i}_{hash(chunk['text'])}" for i, chunk in enumerate(chunks)]
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(texts)
        
        # Add to collection
        self.collection.add(
            embeddings=embeddings.tolist(),
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"Added {len(chunks)} chunks to knowledge base")
    
    def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search the knowledge base for relevant information"""
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])
        
        # Search collection
        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=n_results,
            include=['documents', 'metadatas', 'distances']
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results['documents'][0])):
            formatted_results.append({
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i]
            })
        
        return formatted_results
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the knowledge base collection"""
        count = self.collection.count()
        
        return {
            'total_chunks': count,
            'collection_name': self.collection.name,
            'persist_directory': self.persist_directory
        }
    
    def clear_knowledge_base(self):
        """Clear all data from the knowledge base"""
        self.client.delete_collection("arbo_dental_knowledge")
        self.collection = self.client.create_collection(
            name="arbo_dental_knowledge",
            metadata={"hnsw:space": "cosine"}
        )
        print("Knowledge base cleared")

def build_knowledge_base(data_file: str, persist_directory: str = "./chroma_db"):
    """Build the knowledge base from scraped data"""
    print("Building Arbo Dental Care knowledge base...")
    
    kb = ArboDentalKnowledgeBase(persist_directory)
    
    # Process scraped data
    chunks = kb.process_scraped_data(data_file)
    print(f"Processed {len(chunks)} chunks from scraped data")
    
    # Add to knowledge base
    kb.add_to_knowledge_base(chunks)
    
    # Get collection info
    info = kb.get_collection_info()
    print(f"Knowledge base built successfully!")
    print(f"Total chunks: {info['total_chunks']}")
    print(f"Collection: {info['collection_name']}")
    
    return kb

def main():
    """Main function to build knowledge base"""
    # Try augmented data first, then comprehensive, then original
    data_files = [
        "data/arbo_dental_data_augmented.json",
        "data/arbo_dental_data_comprehensive.json", 
        "data/arbo_dental_data.json"
    ]
    
    data_file = None
    for file_path in data_files:
        if os.path.exists(file_path):
            data_file = file_path
            break
    
    if not data_file:
        print(f"Data file not found. Please run the enhanced crawler first:")
        print("python data_preparation/enhanced_crawler.py")
        return
    
    print(f"Using data file: {data_file}")
    
    # Check if this is augmented data
    if "augmented" in data_file:
        print("🎉 Using augmented data with manual Q&A entries!")
    
    kb = build_knowledge_base(data_file)
    
    # Test search
    print("\n=== Testing Knowledge Base ===")
    test_queries = [
        "What is the address of Arbo Dental Care?",
        "Who are the team members?",
        "What services do you provide?",
        "What is the phone number?",
        "What are the office hours?",
        "What languages do you speak?",
        "How long has the practice been open?",
        "Do you accept insurance?",
        "What should I do if I have a dental emergency?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        results = kb.search(query, n_results=3)
        for i, result in enumerate(results):
            print(f"  {i+1}. {result['text'][:100]}...")
            print(f"     Source: {result['metadata']['source']}")
            print(f"     Confidence: {1 - result['distance']:.2f}")
    
    return kb

if __name__ == "__main__":
    main()
