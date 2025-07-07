#!/usr/bin/env python3
"""Test script to verify PDF generation functionality"""

import os
import sys
sys.path.append('src')

from src.pdf_generator import PDFGenerator

def test_pdf_generation():
    """Test PDF generation for each step"""
    
    # Ensure output directory exists
    os.makedirs('output', exist_ok=True)
    
    pdf_generator = PDFGenerator()
    
    # Test data
    test_ugc_brief = {
        'themes': [
            {
                'theme_name': 'Budget Planning',
                'description': 'Questions about annual budget planning processes',
                'questions': ['How to create a realistic budget?', 'What tools to use for budget planning?'],
                'common_answers': ['Use historical data', 'Involve stakeholders'],
                'key_insights': ['Budget planning is a collaborative process', 'Historical data is crucial']
            }
        ],
        'top_questions': ['How to improve budget accuracy?', 'What are best practices for budget planning?'],
        'key_concerns': ['Budget overruns', 'Lack of stakeholder buy-in'],
        'platform_insights': {
            'linkedin': 'Many discussions about budget planning tools and methodologies',
            'reddit': 'Questions about budget templates and software recommendations'
        },
        'recommendations': ['Use rolling forecasts', 'Implement regular budget reviews']
    }
    
    test_serp_brief = {
        'raw_response': 'Detailed analysis of top 10 SERP results for budget planning...'
    }
    
    test_serp_results = [
        {
            'title': 'How to Create a Business Budget in 8 Steps',
            'url': 'https://example.com/budget-guide',
            'snippet': 'Learn how to create a comprehensive business budget...'
        },
        {
            'title': 'Budget Planning Best Practices',
            'url': 'https://example.com/best-practices',
            'snippet': 'Discover the best practices for effective budget planning...'
        }
    ]
    
    test_combined_result = {
        'focus_keyword': 'budget planning',
        'topic_theme': 'Financial Planning',
        'buyer_persona': 'FP&A Professionals',
        'brief_content': {
            'title_suggestions': ['Complete Guide to Budget Planning', 'Budget Planning Best Practices'],
            'meta_description': 'Learn how to create effective budgets with our comprehensive guide...',
            'target_keywords': ['budget planning', 'financial planning', 'budget management'],
            'content_structure': [
                {
                    'heading': 'Introduction',
                    'subheadings': ['What is Budget Planning?', 'Why Budget Planning Matters'],
                    'key_points': ['Define budget planning', 'Explain its importance'],
                    'word_count_target': 500
                }
            ],
            'user_questions_to_answer': ['How to start budget planning?', 'What tools are needed?'],
            'content_gaps_to_fill': ['Practical examples', 'Step-by-step process'],
            'seo_recommendations': ['Use long-tail keywords', 'Include internal links'],
            'content_tone': 'Professional yet accessible',
            'estimated_word_count': 2500,
            'target_reading_level': 'Intermediate',
            'call_to_action': 'Download our budget planning template'
        },
        'ugc_research': test_ugc_brief,
        'serp_analysis': test_serp_brief
    }
    
    print("Testing PDF generation...")
    
    try:
        # Test Step 2 PDF
        print("Generating Step 2 PDF...")
        step2_filename = pdf_generator.generate_step2_pdf(
            test_ugc_brief, 'budget planning', 'Financial Planning', 'FP&A Professionals'
        )
        if step2_filename:
            print(f"✓ Step 2 PDF generated: {step2_filename}")
        else:
            print("✗ Step 2 PDF generation failed")
        
        # Test Step 3 PDF
        print("Generating Step 3 PDF...")
        step3_filename = pdf_generator.generate_step3_pdf(
            test_serp_brief, test_serp_results, 'budget planning'
        )
        if step3_filename:
            print(f"✓ Step 3 PDF generated: {step3_filename}")
        else:
            print("✗ Step 3 PDF generation failed")
        
        # Test Final PDF
        print("Generating Final PDF...")
        final_filename = pdf_generator.generate_final_pdf(test_combined_result)
        if final_filename:
            print(f"✓ Final PDF generated: {final_filename}")
        else:
            print("✗ Final PDF generation failed")
        
        print("\nPDF generation test completed!")
        
    except Exception as e:
        print(f"Error during PDF generation test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pdf_generation() 