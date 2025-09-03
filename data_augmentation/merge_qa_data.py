#!/usr/bin/env python3
"""
Script to merge CSV Q&A data with the existing Arbo Dental Care comprehensive JSON file
"""

import csv
import json
import os
from pathlib import Path

def load_csv_qa_data(csv_file_path):
    """Load Q&A data from CSV file"""
    qa_data = []
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                qa_data.append({
                    'question': row['question'].strip(),
                    'answer': row['answer'].strip(),
                    'category': row['category'].strip(),
                    'source': row['source'].strip(),
                    'priority': row['priority'].strip()
                })
        
        print(f"✅ Loaded {len(qa_data)} Q&A pairs from CSV")
        return qa_data
        
    except Exception as e:
        print(f"❌ Error loading CSV file: {e}")
        return []

def load_existing_json(json_file_path):
    """Load existing comprehensive JSON data"""
    try:
        with open(json_file_path, 'r', encoding='utf-8') as jsonfile:
            data = json.load(jsonfile)
        print(f"✅ Loaded existing JSON with {len(data)} pages")
        return data
    except Exception as e:
        print(f"❌ Error loading JSON file: {e}")
        return []

def create_qa_page(qa_item):
    """Create a page structure for Q&A items"""
    return {
        'url': f"manual_qa_{qa_item['category']}_{qa_item['priority']}",
        'title': f"Q&A: {qa_item['question'][:50]}...",
        'content': [
            {
                'type': 'h2',
                'text': qa_item['question']
            },
            {
                'type': 'p',
                'text': qa_item['answer']
            },
            {
                'type': 'div',
                'text': f"Category: {qa_item['category']} | Priority: {qa_item['priority']} | Source: {qa_item['source']}"
            }
        ],
        'metadata': {
            'description': f"Answer to: {qa_item['question']}",
            'language': 'en',
            'qa_category': qa_item['category'],
            'qa_priority': qa_item['priority'],
            'qa_source': qa_item['source']
        },
        'links_found': [],
        'qa_data': qa_item  # Store original Q&A data for reference
    }

def merge_data(existing_data, qa_data):
    """Merge existing data with new Q&A data"""
    merged_data = existing_data.copy()
    
    # Add Q&A pages
    for qa_item in qa_data:
        qa_page = create_qa_page(qa_item)
        merged_data.append(qa_page)
    
    print(f"✅ Merged {len(qa_data)} Q&A items into existing data")
    return merged_data

def save_merged_data(merged_data, output_file_path):
    """Save merged data to new JSON file"""
    try:
        with open(output_file_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(merged_data, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"💾 Merged data saved to: {output_file_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error saving merged data: {e}")
        return False

def analyze_merged_data(merged_data):
    """Analyze the merged dataset"""
    total_pages = len(merged_data)
    qa_pages = sum(1 for page in merged_data if 'qa_data' in page)
    website_pages = total_pages - qa_pages
    
    # Count Q&A by category
    categories = {}
    priorities = {}
    
    for page in merged_data:
        if 'qa_data' in page:
            qa = page['qa_data']
            categories[qa['category']] = categories.get(qa['category'], 0) + 1
            priorities[qa['priority']] = priorities.get(qa['priority'], 0) + 1
    
    print(f"\n📊 MERGED DATA ANALYSIS")
    print(f"=" * 40)
    print(f"Total pages: {total_pages}")
    print(f"Website pages: {website_pages}")
    print(f"Q&A pages: {qa_pages}")
    
    print(f"\n📋 Q&A by Category:")
    for category, count in sorted(categories.items()):
        print(f"  {category.capitalize()}: {count}")
    
    print(f"\n⭐ Q&A by Priority:")
    for priority, count in sorted(priorities.items()):
        print(f"  {priority.capitalize()}: {count}")
    
    return {
        'total_pages': total_pages,
        'website_pages': website_pages,
        'qa_pages': qa_pages,
        'categories': categories,
        'priorities': priorities
    }

def main():
    """Main function to merge Q&A data"""
    print("🦷 Arbo Dental Care Q&A Data Merger")
    print("=" * 50)
    
    # File paths
    csv_file = "data_augmentation/dental_qa_template.csv"
    json_file = "data/arbo_dental_data_comprehensive.json"
    output_file = "data/arbo_dental_data_augmented.json"
    
    # Check if files exist
    if not os.path.exists(csv_file):
        print(f"❌ CSV file not found: {csv_file}")
        print("Please fill in the dental_qa_template.csv file first.")
        return False
    
    if not os.path.exists(json_file):
        print(f"❌ JSON file not found: {json_file}")
        print("Please run the enhanced crawler first to generate comprehensive data.")
        return False
    
    # Load data
    print("\n📥 Loading data...")
    qa_data = load_csv_qa_data(csv_file)
    if not qa_data:
        return False
    
    existing_data = load_existing_json(json_file)
    if not existing_data:
        return False
    
    # Merge data
    print("\n🔄 Merging data...")
    merged_data = merge_data(existing_data, qa_data)
    
    # Save merged data
    print("\n💾 Saving merged data...")
    if not save_merged_data(merged_data, output_file):
        return False
    
    # Analyze results
    print("\n📊 Analyzing merged data...")
    analysis = analyze_merged_data(merged_data)
    
    print(f"\n" + "=" * 50)
    print("🎉 Q&A Data Merging Complete!")
    print("=" * 50)
    print(f"\n📋 Summary:")
    print(f"✅ Original data: {analysis['website_pages']} website pages")
    print(f"✅ Added Q&A: {analysis['qa_pages']} Q&A items")
    print(f"✅ Total: {analysis['total_pages']} pages")
    
    print(f"\n🚀 Next steps:")
    print(f"1. Review the augmented data file: {output_file}")
    print(f"2. Rebuild knowledge base: python data_preparation/knowledge_base.py")
    print(f"3. Test enhanced AI responses with new Q&A data")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        exit(1)


