import logging
from typing import List, Dict, Any
import openai
from config.config import Config
from src.utils import Utils

logger = logging.getLogger(__name__)

class ContentAnalyzer:
    """Analyzes content using OpenAI's GPT models"""
    
    def __init__(self, api_increment_callback=None):
        # Validate OpenAI API key
        if not Config.OPENAI_API_KEY:
            logger.error("OPENAI_API_KEY is not set in environment variables")
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        logger.info(f"Initializing ContentAnalyzer with OpenAI API key: {Config.OPENAI_API_KEY[:10]}...")
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        self.api_increment_callback = api_increment_callback
    
    def analyze_articles(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze multiple articles and extract key insights"""
        try:
            logger.info(f"Analyzing {len(articles)} articles")
            
            # Combine all content for analysis
            combined_content = self.combine_article_content(articles)
            
            # Analyze content in chunks if too long
            if len(combined_content) > Config.MAX_TOKENS_PER_REQUEST:
                chunks = Utils.chunk_text(combined_content, Config.MAX_TOKENS_PER_REQUEST // 2)
                analysis_results = []
                
                for chunk in chunks:
                    chunk_analysis = self.analyze_content_chunk(chunk)
                    analysis_results.append(chunk_analysis)
                
                # Combine chunk analyses
                final_analysis = self.combine_analyses(analysis_results)
            else:
                final_analysis = self.analyze_content_chunk(combined_content)
            
            # Add article metadata
            final_analysis['article_count'] = len(articles)
            final_analysis['total_word_count'] = sum(article.get('word_count', 0) for article in articles)
            final_analysis['domains_analyzed'] = list(set(article.get('domain', '') for article in articles))
            
            logger.info("Content analysis completed successfully")
            return final_analysis
            
        except Exception as e:
            logger.error(f"Error in analyze_articles: {e}")
            return {
                'error': str(e),
                'article_count': len(articles),
                'total_word_count': 0
            }
    
    def combine_article_content(self, articles: List[Dict[str, Any]]) -> str:
        """Combine content from multiple articles"""
        combined = []
        
        for i, article in enumerate(articles, 1):
            title = article.get('title', f'Article {i}')
            content = article.get('content', '')
            domain = article.get('domain', 'Unknown')
            
            combined.append(f"=== ARTICLE {i}: {title} (from {domain}) ===\n{content}\n")
        
        return "\n".join(combined)
    
    def analyze_content_chunk(self, content: str) -> Dict[str, Any]:
        """Analyze a single chunk of content using AI"""
        try:
            # Check API limit before making request
            if self.api_increment_callback:
                limit_reached = self.api_increment_callback()
                if limit_reached:
                    logger.error("API request limit reached during content analysis")
                    raise Exception("API request limit reached (200 requests). Please try again later.")
            
            prompt = self.create_analysis_prompt(content)
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert content analyst specializing in SEO and content strategy."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            analysis_text = response.choices[0].message.content
            
            # Parse the analysis into structured format
            structured_analysis = self.parse_analysis_response(analysis_text)
            
            return structured_analysis
            
        except Exception as e:
            logger.error(f"Error in analyze_content_chunk: {e}")
            return {
                'error': str(e),
                'summary': 'Analysis failed',
                'key_themes': [],
                'key_points': [],
                'gaps': []
            }
    
    def create_analysis_prompt(self, content: str) -> str:
        """Create prompt for content analysis"""
        return f"""
        Analyze the following content and provide a comprehensive analysis in the following JSON format:
        
        {{
            "summary": "Brief summary of the main content",
            "key_themes": ["theme1", "theme2", "theme3"],
            "key_points": ["point1", "point2", "point3", "point4", "point5"],
            "gaps": ["gap1", "gap2", "gap3"],
            "tone": "professional/informal/technical/etc",
            "target_audience": "who this content is for",
            "content_quality": "high/medium/low",
            "seo_opportunities": ["opportunity1", "opportunity2"]
        }}
        
        Content to analyze:
        {content[:Config.MAX_TOKENS_PER_REQUEST]}
        
        Please provide the analysis in valid JSON format only.
        """
    
    def parse_analysis_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response into structured format"""
        try:
            import json
            
            # Try to extract JSON from response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # Fallback parsing
                return self.fallback_parsing(response_text)
                
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON response, using fallback parsing")
            return self.fallback_parsing(response_text)
    
    def fallback_parsing(self, response_text: str) -> Dict[str, Any]:
        """Fallback parsing when JSON parsing fails"""
        analysis = {
            'summary': 'Analysis completed',
            'key_themes': [],
            'key_points': [],
            'gaps': [],
            'tone': 'professional',
            'target_audience': 'general',
            'content_quality': 'medium',
            'seo_opportunities': []
        }
        
        # Extract key points using simple text parsing
        lines = response_text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('-') or line.startswith('•'):
                point = line[1:].strip()
                if point:
                    analysis['key_points'].append(point)
        
        return analysis
    
    def combine_analyses(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combine multiple chunk analyses into one"""
        combined = {
            'summary': '',
            'key_themes': [],
            'key_points': [],
            'gaps': [],
            'tone': 'professional',
            'target_audience': 'general',
            'content_quality': 'medium',
            'seo_opportunities': []
        }
        
        # Combine summaries
        summaries = [a.get('summary', '') for a in analyses if a.get('summary')]
        combined['summary'] = ' '.join(summaries)
        
        # Combine lists
        for analysis in analyses:
            combined['key_themes'].extend(analysis.get('key_themes', []))
            combined['key_points'].extend(analysis.get('key_points', []))
            combined['gaps'].extend(analysis.get('gaps', []))
            combined['seo_opportunities'].extend(analysis.get('seo_opportunities', []))
        
        # Remove duplicates
        combined['key_themes'] = list(set(combined['key_themes']))
        combined['key_points'] = list(set(combined['key_points']))
        combined['gaps'] = list(set(combined['gaps']))
        combined['seo_opportunities'] = list(set(combined['seo_opportunities']))
        
        return combined
    
    def extract_keywords(self, content: str) -> List[str]:
        """Extract keywords from content using AI"""
        try:
            # Check API request limit before making the call
            if self.api_increment_callback:
                limit_reached = self.api_increment_callback()
                if limit_reached:
                    logger.error("API request limit reached during keyword extraction")
                    raise Exception("API request limit reached (200 requests). Please try again later.")
            
            prompt = f"""
            Extract the top 10 most important keywords from the following content. 
            Focus on terms that would be valuable for SEO purposes.
            Return only the keywords separated by commas:
            
            {content[:1000]}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an SEO expert. Extract only the most relevant keywords."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.1
            )
            
            keywords_text = response.choices[0].message.content
            keywords = [kw.strip() for kw in keywords_text.split(',') if kw.strip()]
            
            return keywords[:10]
            
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return Utils.extract_keywords(content)
    
    def analyze_content_gaps(self, articles: List[Dict[str, Any]], target_keyword: str) -> List[str]:
        """Identify content gaps in existing articles"""
        try:
            # Create a summary of what's already covered
            covered_topics = []
            for article in articles:
                if article.get('content'):
                    topics = self.extract_topics_from_content(article['content'])
                    covered_topics.extend(topics)
            
            # Remove duplicates
            covered_topics = list(set(covered_topics))
            
            # Check API request limit before making the call
            if self.api_increment_callback:
                limit_reached = self.api_increment_callback()
                if limit_reached:
                    logger.error("API request limit reached during content gap analysis")
                    raise Exception("API request limit reached (200 requests). Please try again later.")
            
            # Use AI to identify gaps
            prompt = f"""
            Based on the keyword "{target_keyword}" and the following covered topics, 
            identify 5 important topics that are missing or could be covered better:
            
            Covered topics: {', '.join(covered_topics[:20])}
            
            Return only the missing topics, one per line.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a content strategist identifying content gaps."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            gaps_text = response.choices[0].message.content
            gaps = [gap.strip() for gap in gaps_text.split('\n') if gap.strip()]
            
            return gaps[:5]
            
        except Exception as e:
            logger.error(f"Error analyzing content gaps: {e}")
            return []
    
    def extract_topics_from_content(self, content: str) -> List[str]:
        """Extract main topics from content"""
        try:
            prompt = f"""
            Extract the main topics discussed in this content. Return only the topics separated by commas:
            
            {content[:500]}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Extract main topics from content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.1
            )
            
            topics_text = response.choices[0].message.content
            topics = [topic.strip() for topic in topics_text.split(',') if topic.strip()]
            
            return topics
            
        except Exception as e:
            logger.error(f"Error extracting topics: {e}")
            return [] 