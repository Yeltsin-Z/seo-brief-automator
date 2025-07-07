import logging
import json
from typing import Dict, Any, List
from datetime import datetime
import openai

from config.config import Config
from src.utils import Utils
from src.serp_scraper import SERPScraper
from src.content_analyzer import ContentAnalyzer
from src.ugc_researcher import UGCResearcher

logger = logging.getLogger(__name__)

class BriefGenerator:
    """Main class for generating comprehensive SEO briefs"""
    
    def __init__(self, api_increment_callback=None):
        self.content_analyzer = ContentAnalyzer(api_increment_callback=api_increment_callback)
        self.ugc_researcher = UGCResearcher(api_increment_callback=api_increment_callback)
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        self.api_increment_callback = api_increment_callback
    
    def generate_brief(self, focus_keyword: str, topic_theme: str, 
                      buyer_persona: str, content_id: str, custom_prompt: str = None) -> Dict[str, Any]:
        """Generate a comprehensive SEO brief for the given parameters"""
        try:
            logger.info(f"Starting brief generation for focus keyword: {focus_keyword}")
            
            brief_data = {
                'focus_keyword': focus_keyword,
                'topic_theme': topic_theme,
                'buyer_persona': buyer_persona,
                'content_id': content_id,
                'custom_prompt': custom_prompt,
                'generated_at': datetime.now().isoformat(),
                'status': 'processing'
            }
            
            # Step 1: Scrape top SERP results
            logger.info("Step 1: Scraping top SERP results...")
            scraper = SERPScraper()
            articles = scraper.scrape_top_articles(focus_keyword)
            
            brief_data['serp_analysis'] = {
                'articles_found': len(articles),
                'articles': articles
            }
            
            # Step 2: Analyze content from top articles
            logger.info("Step 2: Analyzing content from top articles...")
            content_analysis = self.content_analyzer.analyze_articles(articles)
            brief_data['content_analysis'] = content_analysis
            
            # Step 3: Research UGC platforms
            logger.info("Step 3: Researching UGC platforms...")
            ugc_data = self.ugc_researcher.research_ugc(focus_keyword, topic_theme, buyer_persona, custom_prompt)
            brief_data['ugc_research'] = ugc_data
            
            # Step 4: Generate comprehensive brief
            logger.info("Step 4: Generating comprehensive brief...")
            brief_content = self.create_comprehensive_brief(brief_data)
            brief_data['brief_content'] = brief_content
            
            # Step 5: Save brief
            logger.info("Step 5: Saving brief...")
            filename = self.save_brief(brief_data)
            brief_data['filename'] = filename
            
            brief_data['status'] = 'completed'
            logger.info(f"Brief generation completed successfully: {filename}")
            
            return brief_data
            
        except Exception as e:
            logger.error(f"Error generating brief: {e}")
            return {
                'error': str(e),
                'status': 'error'
            }
    
    def create_comprehensive_brief(self, brief_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive brief content using AI"""
        try:
            # Check API request limit before making the call
            if self.api_increment_callback:
                limit_reached = self.api_increment_callback()
                if limit_reached:
                    logger.error("API request limit reached during brief generation")
                    raise Exception("API request limit reached (200 requests). Please try again later.")
            
            # Prepare context for AI
            context = self.prepare_brief_context(brief_data)
            
            # Generate brief using AI
            prompt = self.create_brief_prompt(context, brief_data)
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert SEO content strategist and content brief writer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=3000,
                temperature=0.3
            )
            
            brief_text = response.choices[0].message.content
            
            # Parse and structure the brief
            structured_brief = self.parse_brief_response(brief_text, brief_data)
            
            return structured_brief
            
        except Exception as e:
            logger.error(f"Error creating comprehensive brief: {e}")
            return self.create_fallback_brief(brief_data)
    
    def prepare_brief_context(self, brief_data: Dict[str, Any]) -> str:
        """Prepare context for brief generation"""
        focus_keyword = brief_data['focus_keyword']
        topic_theme = brief_data['topic_theme']
        buyer_persona = brief_data['buyer_persona']
        
        # SERP Analysis Summary
        serp_analysis = brief_data.get('serp_analysis', {})
        articles = serp_analysis.get('articles', [])
        
        serp_summary = f"Found {len(articles)} top-ranking articles for '{focus_keyword}':\n"
        for i, article in enumerate(articles[:5], 1):
            serp_summary += f"{i}. {article.get('title', 'No title')} (from {article.get('domain', 'Unknown')})\n"
        
        # Content Analysis Summary
        content_analysis = brief_data.get('content_analysis', {})
        key_themes = content_analysis.get('key_themes', [])
        key_points = content_analysis.get('key_points', [])
        gaps = content_analysis.get('gaps', [])
        
        content_summary = f"\nKey themes found: {', '.join(key_themes[:5])}\n"
        content_summary += f"Key points covered: {len(key_points)} points identified\n"
        content_summary += f"Content gaps: {', '.join(gaps[:3])}\n"
        
        # UGC Research Summary
        ugc_research = brief_data.get('ugc_research', {})
        questions = ugc_research.get('questions', [])
        concerns = ugc_research.get('concerns', [])
        themes = ugc_research.get('themes', [])
        
        # AI Deep Research Summary
        ai_research = ugc_research.get('ai_deep_research', {})
        ai_themes = ai_research.get('themes', [])
        top_questions = ai_research.get('top_questions', [])
        key_concerns = ai_research.get('key_concerns', [])
        platform_insights = ai_research.get('platform_insights', {})
        
        ugc_summary = f"\nUser questions found: {len(questions)} questions\n"
        ugc_summary += f"User concerns: {len(concerns)} concerns identified\n"
        ugc_summary += f"AI-identified themes: {len(ai_themes)} themes\n"
        ugc_summary += f"Top questions from AI research: {len(top_questions)} questions\n"
        ugc_summary += f"Key concerns from AI research: {len(key_concerns)} concerns\n"
        
        # Platform insights
        for platform, insight in platform_insights.items():
            if insight:
                ugc_summary += f"{platform.capitalize()} insights: {insight[:100]}...\n"
        
        return f"""
        Focus Keyword: {focus_keyword}
        Topic/Theme: {topic_theme}
        Buyer Persona: {buyer_persona}
        
        {serp_summary}
        {content_summary}
        {ugc_summary}
        """
    
    def create_brief_prompt(self, context: str, brief_data: Dict[str, Any]) -> str:
        """Create AI prompt for brief generation with enhanced content intelligence"""
        
        # Get UGC research data
        ugc_research = brief_data.get('ugc_research', {})
        ai_research = ugc_research.get('ai_deep_research', {})
        
        # Extract AI research insights
        themes = ai_research.get('themes', [])
        top_questions = ai_research.get('top_questions', [])
        key_concerns = ai_research.get('key_concerns', [])
        platform_insights = ai_research.get('platform_insights', {})
        recommendations = ai_research.get('recommendations', [])
        
        # Build themes section
        themes_section = ""
        if themes:
            themes_section = "\n\nAI-Identified Themes:\n"
            for theme in themes[:5]:  # Top 5 themes
                themes_section += f"- {theme.get('theme_name', 'Unknown')}: {theme.get('description', '')}\n"
                if theme.get('questions'):
                    themes_section += f"  Questions: {', '.join(theme['questions'][:3])}\n"
        
        # Build questions section
        questions_section = ""
        if top_questions:
            questions_section = f"\n\nTop Questions from AI Research:\n" + "\n".join([f"- {q}" for q in top_questions[:10]])
        
        # Build concerns section
        concerns_section = ""
        if key_concerns:
            concerns_section = f"\n\nKey Concerns from AI Research:\n" + "\n".join([f"- {c}" for c in key_concerns[:5]])
        
        # Build platform insights section
        platform_section = ""
        if platform_insights:
            platform_section = "\n\nPlatform-Specific Insights:\n"
            for platform, insight in platform_insights.items():
                if insight:
                    platform_section += f"- {platform.capitalize()}: {insight}\n"
        
        return f"""
        Based on the following comprehensive research data, create a detailed SEO content brief in JSON format:
        
        {context}
        
        {themes_section}
        {questions_section}
        {concerns_section}
        {platform_section}
        
        Please provide a detailed brief in the following JSON structure:
        {{
            "title_suggestions": ["suggestion1", "suggestion2", "suggestion3"],
            "meta_description": "compelling meta description",
            "target_keywords": ["primary", "secondary1", "secondary2", "secondary3"],
            "content_structure": [
                {{
                    "heading": "H1 heading",
                    "subheadings": ["H2 subheading 1", "H2 subheading 2"],
                    "key_points": ["point1", "point2", "point3"],
                    "word_count_target": 300
                }}
            ],
            "key_messages": ["message1", "message2", "message3"],
            "user_questions_to_answer": ["question1", "question2", "question3"],
            "content_gaps_to_fill": ["gap1", "gap2", "gap3"],
            "call_to_action": "specific call to action",
            "internal_linking_opportunities": ["opportunity1", "opportunity2"],
            "seo_recommendations": ["recommendation1", "recommendation2", "recommendation3"],
            "content_tone": "professional/informal/technical",
            "estimated_word_count": 1500,
            "target_reading_level": "beginner/intermediate/advanced",
            "ai_research_insights": {{
                "themes_to_cover": ["theme1", "theme2"],
                "questions_to_address": ["question1", "question2"],
                "concerns_to_address": ["concern1", "concern2"],
                "platform_specific_insights": {{
                    "linkedin": "insight for LinkedIn audience",
                    "reddit": "insight for Reddit audience",
                    "quora": "insight for Quora audience",
                    "substack": "insight for Substack audience"
                }}
            }}
        }}
        
        Focus on creating content that:
        1. Addresses the specific questions and concerns identified in AI research
        2. Covers the themes identified across platforms
        3. Fills content gaps in existing articles
        4. Provides unique value based on platform-specific insights
        5. Is optimized for SEO and matches the target audience
        6. Incorporates insights from LinkedIn, Reddit, Quora, and Substack research
        
        Return only valid JSON.
        """
    
    def parse_brief_response(self, response_text: str, brief_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI response into structured brief format"""
        try:
            import json
            
            # Try to extract JSON from response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = response_text[start_idx:end_idx]
                parsed_brief = json.loads(json_str)
                
                # Add additional context
                parsed_brief['research_summary'] = {
                    'articles_analyzed': len(brief_data.get('serp_analysis', {}).get('articles', [])),
                    'ugc_items_found': brief_data.get('ugc_research', {}).get('total_found', 0),
                    'questions_identified': len(brief_data.get('ugc_research', {}).get('questions', [])),
                    'concerns_identified': len(brief_data.get('ugc_research', {}).get('concerns', []))
                }
                
                return parsed_brief
            else:
                return self.create_fallback_brief(brief_data)
                
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON response, using fallback brief")
            return self.create_fallback_brief(brief_data)
    
    def create_fallback_brief(self, brief_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a fallback brief when AI parsing fails"""
        keyword = brief_data['focus_keyword']
        target_audience = brief_data['buyer_persona']
        
        # Extract data from research
        content_analysis = brief_data.get('content_analysis', {})
        ugc_research = brief_data.get('ugc_research', {})
        
        return {
            "title_suggestions": [
                f"Complete Guide to {keyword}",
                f"Everything You Need to Know About {keyword}",
                f"{keyword}: A Comprehensive Overview"
            ],
            "meta_description": f"Learn everything about {keyword} with our comprehensive guide. Discover key insights, best practices, and expert tips.",
            "target_keywords": [keyword, f"{keyword} guide", f"{keyword} tips"],
            "content_structure": [
                {
                    "heading": f"What is {keyword}?",
                    "subheadings": ["Definition", "Importance", "Benefits"],
                    "key_points": ["Define the concept", "Explain why it matters", "List key benefits"],
                    "word_count_target": 300
                },
                {
                    "heading": f"How to {keyword}",
                    "subheadings": ["Step-by-step guide", "Best practices", "Common mistakes"],
                    "key_points": ["Provide actionable steps", "Share expert tips", "Warn about pitfalls"],
                    "word_count_target": 500
                }
            ],
            "key_messages": [
                f"{keyword} is essential for success",
                "Follow best practices for optimal results",
                "Avoid common mistakes and pitfalls"
            ],
            "user_questions_to_answer": ugc_research.get('questions', [])[:5],
            "content_gaps_to_fill": content_analysis.get('gaps', [])[:3],
            "call_to_action": f"Start implementing {keyword} today for better results",
            "internal_linking_opportunities": ["related-topic-1", "related-topic-2"],
            "seo_recommendations": [
                "Use target keyword in H1 and first paragraph",
                "Include related keywords naturally",
                "Optimize meta description and title"
            ],
            "content_tone": "professional" if target_audience == "business" else "informal",
            "estimated_word_count": 1500,
            "target_reading_level": "intermediate",
            "research_summary": {
                'articles_analyzed': len(brief_data.get('serp_analysis', {}).get('articles', [])),
                'ugc_items_found': ugc_research.get('total_found', 0),
                'questions_identified': len(ugc_research.get('questions', [])),
                'concerns_identified': len(ugc_research.get('concerns', []))
            }
        }
    
    def save_brief(self, brief_data: Dict[str, Any]) -> str:
        """Save brief data to JSON and HTML files"""
        try:
            # Create filename using content_id
            content_id_safe = Utils.sanitize_filename(brief_data['content_id'])
            timestamp = Utils.format_timestamp()
            filename = f"brief_{content_id_safe}_{timestamp}.json"
            
            # Save JSON file
            json_content = json.dumps(brief_data, indent=2, ensure_ascii=False)
            Utils.save_to_file(json_content, filename)
            
            # Create and save HTML file
            html_content = self.create_html_brief(brief_data)
            html_filename = filename.replace('.json', '.html')
            Utils.save_to_file(html_content, html_filename)
            
            return filename
            
        except Exception as e:
            logger.error(f"Error saving brief: {e}")
            return f"brief_error_{Utils.format_timestamp()}.json"
    
    def create_html_brief(self, brief_data: Dict[str, Any]) -> str:
        """Create HTML version of the brief"""
        try:
            brief_content = brief_data.get('brief_content', {})
            
            html = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>SEO Brief: {brief_data['focus_keyword']}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 40px; }}
                    .header {{ background: #f4f4f4; padding: 20px; border-radius: 5px; margin-bottom: 30px; }}
                    .section {{ margin-bottom: 30px; }}
                    .section h2 {{ color: #333; border-bottom: 2px solid #007cba; padding-bottom: 10px; }}
                    .section h3 {{ color: #555; margin-top: 20px; }}
                    .list {{ background: #f9f9f9; padding: 15px; border-radius: 5px; }}
                    .list ul {{ margin: 0; padding-left: 20px; }}
                    .list li {{ margin-bottom: 8px; }}
                    .highlight {{ background: #fff3cd; padding: 10px; border-radius: 5px; margin: 10px 0; }}
                    .stats {{ display: flex; justify-content: space-around; text-align: center; margin: 20px 0; }}
                    .stat {{ background: #e3f2fd; padding: 15px; border-radius: 5px; flex: 1; margin: 0 10px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>SEO Content Brief</h1>
                    <p><strong>Keyword:</strong> {brief_data['focus_keyword']}</p>
                    <p><strong>Target Audience:</strong> {brief_data['buyer_persona']}</p>
                    <p><strong>Content Type:</strong> {brief_data['topic_theme']}</p>
                    <p><strong>Generated:</strong> {brief_data['generated_at']}</p>
                </div>
                
                <div class="stats">
                    <div class="stat">
                        <h3>Articles Analyzed</h3>
                        <p>{brief_data.get('serp_analysis', {}).get('articles_found', 0)}</p>
                    </div>
                    <div class="stat">
                        <h3>UGC Items Found</h3>
                        <p>{brief_data.get('ugc_research', {}).get('total_found', 0)}</p>
                    </div>
                    <div class="stat">
                        <h3>Questions Identified</h3>
                        <p>{len(brief_data.get('ugc_research', {}).get('questions', []))}</p>
                    </div>
                </div>
                
                <div class="section">
                    <h2>Title Suggestions</h2>
                    <div class="list">
                        <ul>
                            {''.join([f'<li>{title}</li>' for title in brief_content.get('title_suggestions', [])])}
                        </ul>
                    </div>
                </div>
                
                <div class="section">
                    <h2>Meta Description</h2>
                    <div class="highlight">
                        {brief_content.get('meta_description', 'No meta description provided')}
                    </div>
                </div>
                
                <div class="section">
                    <h2>Target Keywords</h2>
                    <div class="list">
                        <ul>
                            {''.join([f'<li>{keyword}</li>' for keyword in brief_content.get('target_keywords', [])])}
                        </ul>
                    </div>
                </div>
                
                <div class="section">
                    <h2>Content Structure</h2>
                    {''.join([f'''
                    <div class="list">
                        <h3>{section.get('heading', 'No heading')}</h3>
                        <p><strong>Subheadings:</strong></p>
                        <ul>
                            {''.join([f'<li>{subheading}</li>' for subheading in section.get('subheadings', [])])}
                        </ul>
                        <p><strong>Key Points:</strong></p>
                        <ul>
                            {''.join([f'<li>{point}</li>' for point in section.get('key_points', [])])}
                        </ul>
                        <p><strong>Target Word Count:</strong> {section.get('word_count_target', 0)}</p>
                    </div>
                    ''' for section in brief_content.get('content_structure', [])])}
                </div>
                
                <div class="section">
                    <h2>User Questions to Answer</h2>
                    <div class="list">
                        <ul>
                            {''.join([f'<li>{question}</li>' for question in brief_content.get('user_questions_to_answer', [])])}
                        </ul>
                    </div>
                </div>
                
                <div class="section">
                    <h2>Content Gaps to Fill</h2>
                    <div class="list">
                        <ul>
                            {''.join([f'<li>{gap}</li>' for gap in brief_content.get('content_gaps_to_fill', [])])}
                        </ul>
                    </div>
                </div>
                
                <div class="section">
                    <h2>SEO Recommendations</h2>
                    <div class="list">
                        <ul>
                            {''.join([f'<li>{rec}</li>' for rec in brief_content.get('seo_recommendations', [])])}
                        </ul>
                    </div>
                </div>
                
                <div class="section">
                    <h2>Content Specifications</h2>
                    <div class="list">
                        <p><strong>Tone:</strong> {brief_content.get('content_tone', 'Not specified')}</p>
                        <p><strong>Estimated Word Count:</strong> {brief_content.get('estimated_word_count', 0)}</p>
                        <p><strong>Target Reading Level:</strong> {brief_content.get('target_reading_level', 'Not specified')}</p>
                        <p><strong>Call to Action:</strong> {brief_content.get('call_to_action', 'Not specified')}</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return html
            
        except Exception as e:
            logger.error(f"Error creating HTML brief: {e}")
            return f"<html><body><h1>Error creating HTML brief: {e}</h1></body></html>"
    
    def get_brief_summary(self, brief_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get a summary of the generated brief"""
        return {
            'focus_keyword': brief_data['focus_keyword'],
            'topic_theme': brief_data['topic_theme'],
            'buyer_persona': brief_data['buyer_persona'],
            'content_id': brief_data['content_id'],
            'status': brief_data['status'],
            'generated_at': brief_data['generated_at'],
            'articles_analyzed': len(brief_data.get('serp_analysis', {}).get('articles', [])),
            'ugc_items_found': brief_data.get('ugc_research', {}).get('total_found', 0),
            'questions_identified': len(brief_data.get('ugc_research', {}).get('questions', [])),
            'filename': brief_data.get('filename', 'Not saved'),
            'estimated_word_count': brief_data.get('brief_content', {}).get('estimated_word_count', 0)
        }

if __name__ == "__main__":
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description="Generate an SEO brief for a keyword.")
    parser.add_argument('--keyword', type=str, required=True, help='Keyword to generate the brief for')
    parser.add_argument('--audience', type=str, default='general', help='Target audience (default: general)')
    parser.add_argument('--type', type=str, default='blog post', help='Content type (default: blog post)')
    args = parser.parse_args()

    try:
        Config.validate_config()
        generator = BriefGenerator()
        result = generator.generate_brief(args.keyword, args.audience, args.type)
        print(json.dumps(generator.get_brief_summary(result), indent=2, ensure_ascii=False))
        print(f"\nBrief saved as: {result.get('filename', 'N/A')}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1) 