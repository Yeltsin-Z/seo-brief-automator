#!/usr/bin/env python3

import sys
import os
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from document_generator import DocumentGenerator

def test_document_generator():
    """Test the document generator with sample data"""
    
    # Sample brief data
    sample_brief_data = {
        'keyword': 'Python Tutorial',
        'target_audience': 'beginners',
        'content_type': 'tutorial',
        'generated_at': '2025-06-25T16:50:00',
        'serp_analysis': {
            'articles': [
                {'title': 'Sample Article 1', 'domain': 'example.com'},
                {'title': 'Sample Article 2', 'domain': 'example.org'}
            ]
        },
        'ugc_research': {
            'total_found': 5,
            'questions': ['How to start?', 'What is Python?', 'Best practices?']
        },
        'brief_content': {
            'title_suggestions': ['Complete Python Tutorial', 'Python for Beginners'],
            'meta_description': 'Learn Python with our comprehensive tutorial',
            'target_keywords': ['python', 'tutorial', 'beginners'],
            'content_structure': [
                {
                    'heading': 'Introduction to Python',
                    'subheadings': ['What is Python?', 'Why Learn Python?'],
                    'key_points': ['Python is easy to learn', 'Python is versatile'],
                    'word_count_target': 300
                }
            ],
            'user_questions_to_answer': ['How to install Python?', 'What can I build?'],
            'content_gaps_to_fill': ['Advanced topics', 'Real-world projects'],
            'seo_recommendations': ['Use keywords naturally', 'Include internal links'],
            'content_tone': 'friendly',
            'target_reading_level': 'beginner',
            'estimated_word_count': 1500,
            'call_to_action': 'Start learning Python today!'
        }
    }
    
    try:
        # Initialize document generator
        doc_gen = DocumentGenerator()
        
        # Generate documents
        print("Generating documents...")
        documents = doc_gen.generate_documents(sample_brief_data)
        
        print(f"Generated documents: {documents}")
        
        # Check if files were created
        for doc_type, filename in documents.items():
            if filename:
                filepath = os.path.join('seo-brief-automator/output', filename)
                if os.path.exists(filepath):
                    print(f"✓ {doc_type}: {filename} created successfully")
                else:
                    print(f"✗ {doc_type}: {filename} not found")
            else:
                print(f"✗ {doc_type}: No filename returned")
                
    except Exception as e:
        print(f"Error testing document generator: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_document_generator() 