#!/usr/bin/env python3
"""
Script to rebuild the Arbo Dental Care knowledge base with comprehensive website data
"""

import os
import sys
import time

def main():
    """Main function to rebuild knowledge base"""
    print("🦷 Arbo Dental Care Knowledge Base Rebuilder")
    print("=" * 60)
    
    # Step 1: Run enhanced crawler
    print("\n🚀 Step 1: Running Enhanced Website Crawler")
    print("-" * 40)
    
    try:
        from data_preparation.enhanced_crawler import EnhancedArboDentalCrawler
        
        # Create and run crawler
        crawler = EnhancedArboDentalCrawler(max_pages=50)
        data = crawler.crawl_site()
        
        # Save comprehensive data
        data_file = crawler.save_data()
        
        # Print summary
        summary = crawler.get_crawl_summary()
        print(f"\n✅ Crawling completed successfully!")
        print(f"📊 Total pages scraped: {summary['total_pages_scraped']}")
        print(f"🔗 Total URLs discovered: {summary['total_urls_discovered']}")
        print(f"🗺️ Sitemaps found: {summary['sitemaps_found']}")
        
        print("\n📄 Pages by category:")
        for category, count in summary['pages_by_type'].items():
            print(f"  {category.capitalize()}: {count}")
            
    except Exception as e:
        print(f"❌ Error during crawling: {e}")
        print("Falling back to original data file...")
        data_file = "data/arbo_dental_data.json"
    
    # Step 2: Rebuild knowledge base
    print("\n🧠 Step 2: Rebuilding Knowledge Base")
    print("-" * 40)
    
    try:
        from data_preparation.knowledge_base import build_knowledge_base
        
        print(f"Building knowledge base from: {data_file}")
        kb = build_knowledge_base(data_file)
        
        # Get collection info
        info = kb.get_collection_info()
        print(f"\n✅ Knowledge base rebuilt successfully!")
        print(f"📚 Total chunks: {info['total_chunks']}")
        print(f"🗂️ Collection: {info['collection_name']}")
        
    except Exception as e:
        print(f"❌ Error rebuilding knowledge base: {e}")
        return False
    
    # Step 3: Test the knowledge base
    print("\n🧪 Step 3: Testing Knowledge Base")
    print("-" * 40)
    
    try:
        test_queries = [
            "What is the address of Arbo Dental Care?",
            "Who are the team members?",
            "What services do you provide?",
            "What are the office hours?",
            "What languages do you speak?"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Testing: {query}")
            results = kb.search(query, n_results=2)
            
            if results:
                for i, result in enumerate(results, 1):
                    confidence = 1 - result['distance']
                    print(f"  {i}. Confidence: {confidence:.2f} | {result['text'][:80]}...")
                    print(f"     Source: {result['metadata']['source']}")
            else:
                print("  No results found")
                
    except Exception as e:
        print(f"❌ Error during testing: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Knowledge Base Rebuild Complete!")
    print("=" * 60)
    print("\n📋 Summary:")
    print(f"✅ Website crawled: {data_file}")
    print(f"✅ Knowledge base rebuilt with {info['total_chunks']} chunks")
    print(f"✅ System ready for enhanced AI responses")
    
    print("\n🚀 Next steps:")
    print("1. Restart your chatbot: python chatbot_interface/app.py")
    print("2. Test with more comprehensive questions")
    print("3. Enable debug mode to see detailed search results")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)


