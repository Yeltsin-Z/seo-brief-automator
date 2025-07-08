import time
import logging
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote_plus
import re
import openai
from datetime import datetime
import markdown2

from config.config import Config
from src.utils import Utils

logger = logging.getLogger(__name__)

class UGCResearcher:
    """Researches user-generated content from various platforms with AI-powered deep research"""
    
    def __init__(self, api_increment_callback=None):
        try:
            logger.info("Initializing UGCResearcher...")
            logger.info("Creating requests session...")
            self.session = requests.Session()
            logger.info("Setting session headers...")
            self.session.headers.update({
                'User-Agent': Utils.get_random_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            })
            
            # Validate OpenAI API key
            logger.info("Validating OpenAI API key...")
            if not Config.OPENAI_API_KEY:
                logger.error("OPENAI_API_KEY is not set in environment variables")
                raise ValueError("OPENAI_API_KEY environment variable is required")
            
            logger.info(f"Initializing OpenAI client with API key: {Config.OPENAI_API_KEY[:10]}...")
            try:
                self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
                logger.info("OpenAI client created successfully")
            except Exception as openai_error:
                logger.error(f"Error creating OpenAI client: {openai_error}")
                raise
            
            self.api_increment_callback = api_increment_callback
            logger.info("UGCResearcher initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing UGCResearcher: {e}")
            raise
    
    def research_ugc_basic(self, focus_keyword: str, topic_theme: str, buyer_persona: str, custom_prompt: str = None) -> Dict[str, Any]:
        """Enhanced UGC research using ChatGPT with real-time data gathering and analysis"""
        try:
            logger.info(f"Performing enhanced ChatGPT UGC research for focus keyword: {focus_keyword}")
            
            # Step 1: Initial research prompt to gather comprehensive data
            if custom_prompt:
                research_prompt = custom_prompt.strip()
            else:
                research_prompt = f"""
You are an expert content researcher specializing in finance and business topics. I need you to conduct comprehensive research on "{focus_keyword}" for a blog about "{topic_theme}" targeting "{buyer_persona}".

Please research the following aspects and provide detailed findings:

1. **Platform Research**: Search across LinkedIn, Reddit (r/finance, r/FPandA, r/CFO), Quora, and Substack for recent discussions about {focus_keyword}
2. **Question Analysis**: Identify specific questions that finance professionals are asking
3. **Pain Points**: Find common challenges and concerns
4. **Trending Topics**: Discover emerging themes and hot topics
5. **Industry Insights**: Gather insights from recent articles, discussions, and expert opinions

Please provide your findings in this structured format:

## Key Questions Identified
[List 8-12 specific questions that finance professionals are asking about {focus_keyword}]

## Common Concerns & Challenges  
[List 6-8 main concerns or pain points related to {focus_keyword}]

## Trending Topics & Themes
[List 5-7 trending topics or themes in the {focus_keyword} space]

## Industry Insights & Expert Opinions
[Share 4-6 key insights from industry experts and recent discussions]

## Content Opportunities
[Identify 3-5 specific content opportunities based on your research]

## Recent Developments
[Note any recent changes, updates, or new developments related to {focus_keyword}]

Use clear, professional language and focus on actionable insights. Base your research on real discussions and current trends.
"""
            
            # Call OpenAI ChatGPT for comprehensive research
            if self.api_increment_callback:
                limit_reached = self.api_increment_callback()
                if limit_reached:
                    raise Exception("API request limit reached (200 requests). Please try again later.")
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert content researcher with deep knowledge of finance, FP&A, CFO concerns, and industry trends. You have access to current information and can provide real-time insights."},
                    {"role": "user", "content": research_prompt}
                ],
                max_tokens=2500,
                temperature=0.7
            )
            
            initial_research = response.choices[0].message.content.strip()
            
            # Step 2: Follow-up analysis to extract actionable insights
            analysis_prompt = f"""
Based on the research findings below, please provide a comprehensive analysis and actionable recommendations for content creation:

{initial_research}

Please analyze this research and provide:

## Executive Summary
[A 2-3 sentence overview of the key findings]

## Content Strategy Recommendations
[3-4 specific recommendations for content creation]

## Target Audience Insights
[Detailed insights about what {buyer_persona} specifically needs]

## Competitive Analysis
[What gaps exist in current content about {focus_keyword}]

## SEO Opportunities
[Specific keywords and topics to target]

## Content Format Suggestions
[Recommended content formats (guides, case studies, etc.)]

Format your response in clear markdown with proper headings and bullet points.
"""
            
            # Call ChatGPT for analysis
            if self.api_increment_callback:
                limit_reached = self.api_increment_callback()
                if limit_reached:
                    raise Exception("API request limit reached (200 requests). Please try again later.")
            
            analysis_response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a content strategy expert specializing in SEO and content marketing for finance professionals."},
                    {"role": "user", "content": analysis_prompt}
                ],
                max_tokens=2000,
                temperature=0.6
            )
            
            analysis_content = analysis_response.choices[0].message.content.strip()
            
            # Combine research and analysis
            combined_content = f"""
# UGC Research Report: {focus_keyword}

## Research Findings
{initial_research}

---

## Strategic Analysis
{analysis_content}

---
*Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}*
"""
            
            # Convert to HTML with advanced markdown features
            html_output = markdown2.markdown(combined_content, extras=["fenced-code-blocks", "tables", "strike", "cuddled-lists", "metadata", "numbering", "task_list"])
            # Post-process for better indentation and bulleting
            html_output = html_output.replace('<ul>', '<ul class="custom-list">').replace('<ol>', '<ol class="custom-list-ol">').replace('<li>', '<li class="custom-list-item">')
            
            return {
                'focus_keyword': focus_keyword,
                'topic_theme': topic_theme,
                'buyer_persona': buyer_persona,
                'custom_prompt': custom_prompt,
                'html_output': html_output,
                'raw_markdown': combined_content,
                'raw_response': initial_research,
                'analysis_response': analysis_content,
                'research_method': 'enhanced_chatgpt',
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in enhanced ChatGPT UGC research: {e}")
            return {
                'focus_keyword': focus_keyword,
                'topic_theme': topic_theme,
                'buyer_persona': buyer_persona,
                'custom_prompt': custom_prompt,
                'error': str(e),
                'html_output': f'<p>Error: {str(e)}</p>',
                'research_method': 'enhanced_chatgpt',
                'generated_at': datetime.now().isoformat()
            }
    
    def research_ugc(self, focus_keyword: str, topic_theme: str, buyer_persona: str, custom_prompt: str = None) -> Dict[str, Any]:
        """Main method to research UGC across multiple platforms with AI deep research"""
        try:
            logger.info(f"Researching UGC for focus keyword: {focus_keyword}")
            
            ugc_data = {
                'focus_keyword': focus_keyword,
                'topic_theme': topic_theme,
                'buyer_persona': buyer_persona,
                'custom_prompt': custom_prompt,
                'serp_snapshot': [],
                'reddit_data': [],
                'quora_data': [],
                'linkedin_data': [],
                'substack_data': [],
                'ai_deep_research': {},
                'questions': [],
                'concerns': [],
                'trends': [],
                'themes': [],
                'total_found': 0
            }
            
            # Step 1: SERP Snapshot - Top 10 ranking articles
            try:
                serp_data = self.get_serp_snapshot(focus_keyword)
                ugc_data['serp_snapshot'] = serp_data
                ugc_data['total_found'] += len(serp_data)
            except Exception as e:
                logger.warning(f"SERP snapshot failed: {e}")
            
            # Step 2: Platform-specific research
            try:
                reddit_data = self.research_reddit(focus_keyword)
                ugc_data['reddit_data'] = reddit_data
                ugc_data['total_found'] += len(reddit_data)
            except Exception as e:
                logger.warning(f"Reddit research failed: {e}")
            
            try:
                quora_data = self.research_quora(focus_keyword)
                ugc_data['quora_data'] = quora_data
                ugc_data['total_found'] += len(quora_data)
            except Exception as e:
                logger.warning(f"Quora research failed: {e}")
            
            try:
                linkedin_data = self.research_linkedin(focus_keyword)
                ugc_data['linkedin_data'] = linkedin_data
                ugc_data['total_found'] += len(linkedin_data)
            except Exception as e:
                logger.warning(f"LinkedIn research failed: {e}")
            
            try:
                substack_data = self.research_substack(focus_keyword)
                ugc_data['substack_data'] = substack_data
                ugc_data['total_found'] += len(substack_data)
            except Exception as e:
                logger.warning(f"Substack research failed: {e}")
            
            # Step 3: AI Deep Research using ChatGPT
            try:
                ai_research = self.perform_ai_deep_research(focus_keyword, topic_theme, buyer_persona, custom_prompt)
                ugc_data['ai_deep_research'] = ai_research
            except Exception as e:
                logger.warning(f"AI deep research failed: {e}")
            
            # Step 4: SERP Analysis using ChatGPT
            try:
                serp_analysis = self.perform_serp_analysis(ugc_data['serp_snapshot'], focus_keyword, None)  # Always use default prompt for initial analysis
                ugc_data['serp_analysis'] = serp_analysis
            except Exception as e:
                logger.warning(f"SERP analysis failed: {e}")
                ugc_data['serp_analysis'] = {
                    'error': str(e),
                    'raw_response': 'SERP analysis failed during initial generation',
                    'focus_keyword': focus_keyword,
                    'articles_analyzed': 0
                }
            
            # Step 5: Extract insights
            ugc_data['questions'] = self.extract_questions(ugc_data)
            ugc_data['concerns'] = self.extract_concerns(ugc_data)
            ugc_data['trends'] = self.identify_trends(ugc_data)
            ugc_data['themes'] = self.identify_themes(ugc_data)
            
            logger.info(f"UGC research completed. Found {ugc_data['total_found']} items")
            return ugc_data
            
        except Exception as e:
            logger.error(f"Error in UGC research: {e}")
            return {
                'focus_keyword': focus_keyword,
                'topic_theme': topic_theme,
                'buyer_persona': buyer_persona,
                'custom_prompt': custom_prompt,
                'error': str(e),
                'total_found': 0
            }
    
    def get_serp_snapshot(self, focus_keyword: str) -> List[Dict[str, Any]]:
        """Get top 10 ranking articles from Google Search for the focus keyword"""
        try:
            logger.info(f"Getting SERP snapshot for: {focus_keyword}")
            from src.serp_scraper import SERPScraper
            scraper = SERPScraper()
            results = scraper.search_google(focus_keyword)
            logger.info(f"Found {len(results)} SERP results")
            return results
        except Exception as e:
            logger.error(f"Error getting SERP snapshot: {e}")
            return []
    
    def perform_ai_deep_research(self, focus_keyword: str, topic_theme: str, buyer_persona: str, custom_prompt: str = None) -> Dict[str, Any]:
        """Perform AI-powered deep research using the specific ChatGPT prompt"""
        try:
            # Check API request limit before making the call
            if self.api_increment_callback:
                limit_reached = self.api_increment_callback()
                if limit_reached:
                    logger.error("API request limit reached during AI deep research")
                    raise Exception("API request limit reached (200 requests). Please try again later.")
            
            # Use custom prompt if provided, otherwise use default
            if custom_prompt:
                prompt = custom_prompt
            else:
                prompt = f"""
                Can you look at LinkedIn, Reddit, Quora, Substack and help me identify what questions finance people are asking about {focus_keyword}? 

                I'm writing a blog on {topic_theme} and trying to understand what's driving curiosity or challenges or concerns among {buyer_persona}. 

                Look at conversations, threads, and information from the past 6 months. Focus on questions asked by FP&A professionals and CFOs. The search should be industry-agnostic.

                Group your findings by common themes. Surface the common questions being asked and also summarise the answers and key insights.

                Please provide your analysis in the following JSON structure:
                {{
                    "themes": [
                        {{
                            "theme_name": "string",
                            "description": "string",
                            "questions": ["question1", "question2"],
                            "common_answers": ["answer1", "answer2"],
                            "key_insights": ["insight1", "insight2"],
                            "platforms_mentioned": ["linkedin", "reddit", "quora", "substack"]
                        }}
                    ],
                    "top_questions": ["question1", "question2", "question3"],
                    "key_concerns": ["concern1", "concern2", "concern3"],
                    "trending_topics": ["topic1", "topic2", "topic3"],
                    "platform_insights": {{
                        "linkedin": "string",
                        "reddit": "string", 
                        "quora": "string",
                        "substack": "string"
                    }},
                    "recommendations": ["recommendation1", "recommendation2", "recommendation3"]
                }}
                """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Changed from gpt-4 to gpt-3.5-turbo for compatibility
                messages=[
                    {"role": "system", "content": "You are an expert content researcher specializing in finance and business topics. You have deep knowledge of FP&A, CFO concerns, and industry trends."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4000,
                temperature=0.3
            )
            
            ai_response = response.choices[0].message.content
            
            # Try to parse JSON response
            try:
                import json
                parsed_response = json.loads(ai_response)
                return parsed_response
            except json.JSONDecodeError:
                # If JSON parsing fails, return structured text
                return {
                    'raw_response': ai_response,
                    'themes': [],
                    'top_questions': [],
                    'key_concerns': [],
                    'trending_topics': [],
                    'platform_insights': {},
                }
            
        except Exception as e:
            logger.error(f"Error in AI deep research: {e}")
            return {
                'error': str(e),
                'raw_response': 'AI deep research failed',
                'themes': [],
                'top_questions': [],
                'key_concerns': [],
                'trending_topics': [],
                'platform_insights': {},
                'recommendations': []
            }
    
    def perform_serp_analysis(self, serp_results: List[Dict[str, Any]], focus_keyword: str, custom_prompt: str = None) -> Dict[str, Any]:
        """Perform detailed SERP analysis using ChatGPT and return HTML output"""
        try:
            if self.api_increment_callback:
                limit_reached = self.api_increment_callback()
                if limit_reached:
                    logger.error("API request limit reached during SERP analysis")
                    raise Exception("API request limit reached (200 requests). Please try again later.")
            
            # Build the URLs list for the prompt
            urls_list = []
            count = 0
            for result in serp_results:
                title = result.get('title', '').strip()
                url = result.get('url', '').strip()
                if title and url and url.startswith('http'):
                    count += 1
                    urls_list.append(f"{count}. {title} - {url}")
                    if count == 10:
                        break
            urls_text = "\n".join(urls_list)
            
            if custom_prompt:
                prompt = custom_prompt + f"\n\nNow, analyze the following articles for the keyword \"{focus_keyword}\":\n\n{urls_text}\n\nPlease provide a comprehensive analysis for each article following the structure above. Format your response in markdown with headings, bullet points, and bold for key points."
            else:
                prompt = f"""You are an expert content strategist. I will give you a list of blog article URLs that rank on the first page of Google for a target keyword.

For each URL:
- Start with the blog title and URL in bold
- Then provide a structured analysis in bullet format under the following sections

Please follow this structure for each blog:
Blog Title: [Insert blog post title]  
URL: [Insert blog post URL]  
1. Summary of the Article  
   - Brief overview of what the article covers.
2. Search Intent Covered  
   - What is the primary search intent (Informational, Navigational, Transactional, Commercial)?
   - How well does it fulfill that intent?
3. Subtopics Covered  
   - Bullet list of all key sections or talking points.
4. Depth of Coverage  
   - Is the content shallow, moderate, or deep?
   - What's covered in detail vs only skimmed?
5. What's Missing  
   - Gaps in logic, unexplored ideas, missing data/examples/frameworks.
6. Tone & Point of View  
   - Describe the tone (e.g., expert, conversational, tactical).
   - Is there a distinct point of view or is it generic?
7. Structure  
   - Type of article (e.g., guide, listicle, editorial).
   - Include the full H1, and a list of H2s and H3s (if present).
8. SEO Signals  
   - Is the primary keyword used in title, H1, intro, and headers?
   - Mention 7-10 semantically related keywords used (if any).
   - Describe internal and external linking strategy.
9. Use of Visuals  
   - What types of visuals are used (if any)?
   - Are they helpful, decorative, or generic?
10. Unique Hooks or Contrarian Angles  
   - Any standout story, metaphor, framework, or angle?
11. Opportunities to Differentiate  
   - What can be improved — stronger POV, richer examples, deeper insights, visual storytelling, etc.?
12. Word Count  
   - Estimated total word count of the article.

Now, analyze the following articles for the keyword \"{focus_keyword}\":

{urls_text}

Please provide a comprehensive analysis for each article following the structure above. Format your response in markdown with headings, bullet points, and bold for key points."""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert content strategist and SEO analyst with deep knowledge of content analysis, search intent, and competitive research."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4000,
                temperature=0.3
            )
            markdown_text = response.choices[0].message.content.strip()
            html_output = markdown2.markdown(markdown_text, extras=["fenced-code-blocks", "tables", "strike", "cuddled-lists", "metadata", "numbering", "task_list"])
            html_output = html_output.replace('<ul>', '<ul class="custom-list">').replace('<ol>', '<ol class="custom-list-ol">').replace('<li>', '<li class="custom-list-item">')
            return {
                'html_output': html_output,
                'raw_markdown': markdown_text,
                'focus_keyword': focus_keyword,
                'articles_analyzed': len(serp_results[:10])
            }
        except Exception as e:
            logger.error(f"Error in SERP analysis: {e}")
            return {
                'error': str(e),
                'html_output': f'<p>Error: {str(e)}</p>',
                'focus_keyword': focus_keyword,
                'articles_analyzed': 0
            }

    def perform_serp_analysis_with_custom_prompt(self, serp_results: List[Dict[str, Any]], focus_keyword: str, custom_prompt: str) -> Dict[str, Any]:
        return self.perform_serp_analysis(serp_results, focus_keyword, custom_prompt)
    
    def research_reddit_basic(self, keyword: str) -> List[Dict[str, Any]]:
        """Basic Reddit research - simplified version"""
        try:
            logger.info(f"Basic Reddit research for: {keyword}")
            
            # Simplified search - just a few key subreddits
            subreddits = ['personalfinance', 'investing', 'financialindependence']
            results = []
            
            for subreddit in subreddits:
                try:
                    url = f"https://www.reddit.com/r/{subreddit}/search.json"
                    params = {
                        'q': keyword,
                        'restrict_sr': 'on',
                        'sort': 'relevance',
                        't': 'month',
                        'limit': 3  # Reduced limit for basic search
                    }
                    
                    response = self.session.get(url, params=params, timeout=5)  # Reduced timeout
                    if response.status_code == 200:
                        data = response.json()
                        if 'data' in data and 'children' in data['data']:
                            for post in data['data']['children'][:3]:  # Limit to 3 posts
                                post_data = post['data']
                                results.append({
                                    'platform': 'reddit',
                                    'subreddit': subreddit,
                                    'title': post_data.get('title', ''),
                                    'url': f"https://reddit.com{post_data.get('permalink', '')}",
                                    'score': post_data.get('score', 0),
                                    'comments': post_data.get('num_comments', 0),
                                    'content': post_data.get('selftext', '')[:200] + '...' if len(post_data.get('selftext', '')) > 200 else post_data.get('selftext', '')
                                })
                except Exception as e:
                    logger.warning(f"Error in basic Reddit research for {subreddit}: {e}")
                    continue
            
            logger.info(f"Basic Reddit research found {len(results)} posts")
            return results
            
        except Exception as e:
            logger.error(f"Error in basic Reddit research: {e}")
            return []
    
    def research_reddit(self, keyword: str) -> List[Dict[str, Any]]:
        """Research Reddit for discussions about the keyword"""
        try:
            # Use Reddit search API (simplified approach)
            search_url = f"https://www.reddit.com/search.json?q={quote_plus(keyword)}&sort=relevance&t=year"
            
            response = self.session.get(search_url, timeout=Config.REQUEST_TIMEOUT)
            response.raise_for_status()
            
            data = response.json()
            posts = []
            
            if 'data' in data and 'children' in data['data']:
                for child in data['data']['children'][:10]:  # Top 10 posts
                    post_data = child['data']
                    
                    posts.append({
                        'title': post_data.get('title', ''),
                        'content': post_data.get('selftext', ''),
                        'subreddit': post_data.get('subreddit', ''),
                        'score': post_data.get('score', 0),
                        'comments_count': post_data.get('num_comments', 0),
                        'url': f"https://reddit.com{post_data.get('permalink', '')}",
                        'created_utc': post_data.get('created_utc', 0),
                        'platform': 'reddit'
                    })
            
            return posts
            
        except Exception as e:
            logger.error(f"Error researching Reddit: {e}")
            return []
    
    def research_quora(self, keyword: str) -> List[Dict[str, Any]]:
        """Research Quora for questions about the keyword"""
        try:
            # Use Quora search (simplified approach)
            search_url = f"https://www.quora.com/search?q={quote_plus(keyword)}&type=question"
            
            response = self.session.get(search_url, timeout=Config.REQUEST_TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            questions = []
            
            # Look for question elements (this is a simplified approach)
            question_elements = soup.find_all('a', href=re.compile(r'/question/'))
            
            for element in question_elements[:10]:  # Top 10 questions
                title = element.get_text().strip()
                url = urljoin('https://www.quora.com', element.get('href', ''))
                
                if title and 'question' in url:
                    questions.append({
                        'title': title,
                        'url': url,
                        'platform': 'quora',
                        'type': 'question'
                    })
            
            return questions
            
        except Exception as e:
            logger.error(f"Error researching Quora: {e}")
            return []
    
    def research_stackoverflow(self, keyword: str) -> List[Dict[str, Any]]:
        """Research Stack Overflow for technical questions"""
        try:
            # Use Stack Overflow API
            api_url = f"https://api.stackexchange.com/2.3/search/advanced"
            params = {
                'order': 'desc',
                'sort': 'activity',
                'tagged': keyword.replace(' ', ';'),
                'site': 'stackoverflow',
                'pagesize': 10
            }
            
            response = self.session.get(api_url, params=params, timeout=Config.REQUEST_TIMEOUT)
            response.raise_for_status()
            
            data = response.json()
            questions = []
            
            if 'items' in data:
                for item in data['items']:
                    questions.append({
                        'title': item.get('title', ''),
                        'content': item.get('body', ''),
                        'score': item.get('score', 0),
                        'answers_count': item.get('answer_count', 0),
                        'url': item.get('link', ''),
                        'tags': item.get('tags', []),
                        'created_date': item.get('creation_date', 0),
                        'platform': 'stackoverflow',
                        'type': 'question'
                    })
            
            return questions
            
        except Exception as e:
            logger.error(f"Error researching Stack Overflow: {e}")
            return []
    
    def research_forums(self, keyword: str) -> List[Dict[str, Any]]:
        """Research general forums for discussions"""
        try:
            # Search for forum discussions (simplified approach)
            forum_data = []
            
            # Common forum search patterns
            forum_patterns = [
                f"site:forums.com {keyword}",
                f"site:community.com {keyword}",
                f"site:discussions.com {keyword}"
            ]
            
            for pattern in forum_patterns:
                try:
                    # This would typically use a search API
                    # For now, we'll simulate forum data
                    forum_data.append({
                        'title': f"Forum discussion about {keyword}",
                        'content': f"User discussion about {keyword} and related topics",
                        'url': f"https://example-forum.com/discussion/{keyword.replace(' ', '-')}",
                        'platform': 'forum',
                        'type': 'discussion'
                    })
                except Exception as e:
                    logger.warning(f"Forum pattern {pattern} failed: {e}")
                    continue
            
            return forum_data
            
        except Exception as e:
            logger.error(f"Error researching forums: {e}")
            return []
    
    def extract_questions(self, ugc_data: Dict[str, Any]) -> List[str]:
        """Extract questions from UGC data"""
        questions = []
        
        # Extract from Reddit posts
        for post in ugc_data.get('reddit_data', []):
            title = post.get('title', '')
            content = post.get('content', '')
            
            # Look for question patterns
            if '?' in title or any(word in title.lower() for word in ['how', 'what', 'why', 'when', 'where', 'which']):
                questions.append(title)
            
            # Extract questions from content
            content_questions = re.findall(r'[^.!?]*\?', content)
            questions.extend(content_questions[:3])  # Limit to 3 questions per post
        
        # Extract from Quora questions
        for question in ugc_data.get('quora_data', []):
            title = question.get('title', '')
            if title:
                questions.append(title)
        
        # Extract from Stack Overflow questions
        for question in ugc_data.get('stackoverflow_data', []):
            title = question.get('title', '')
            if title:
                questions.append(title)
        
        # Remove duplicates and clean
        unique_questions = list(set(questions))
        cleaned_questions = [q.strip() for q in unique_questions if len(q.strip()) > 10]
        
        return cleaned_questions[:20]  # Limit to 20 questions
    
    def extract_concerns(self, ugc_data: Dict[str, Any]) -> List[str]:
        """Extract user concerns from UGC data"""
        concerns = []
        
        # Common concern indicators
        concern_indicators = [
            'problem', 'issue', 'trouble', 'difficulty', 'challenge', 'struggle',
            'worried', 'concerned', 'frustrated', 'confused', 'help', 'advice',
            'error', 'bug', 'broken', 'not working', 'failed', 'stuck'
        ]
        
        # Extract from all platforms
        for platform_data in [ugc_data.get('reddit_data', []), 
                             ugc_data.get('stackoverflow_data', []),
                             ugc_data.get('forums_data', [])]:
            
            for item in platform_data:
                title = item.get('title', '').lower()
                content = item.get('content', '').lower()
                
                # Check for concern indicators
                for indicator in concern_indicators:
                    if indicator in title or indicator in content:
                        concern_text = item.get('title', '')[:100]  # First 100 chars of title
                        if concern_text and concern_text not in concerns:
                            concerns.append(concern_text)
        
        return concerns[:15]  # Limit to 15 concerns
    
    def identify_trends(self, ugc_data: Dict[str, Any]) -> List[str]:
        """Identify trends in UGC data"""
        trends = []
        
        # Analyze common themes across platforms
        all_text = ""
        
        for platform_data in [ugc_data.get('reddit_data', []), 
                             ugc_data.get('quora_data', []),
                             ugc_data.get('stackoverflow_data', []),
                             ugc_data.get('forums_data', [])]:
            
            for item in platform_data:
                all_text += " " + item.get('title', '') + " " + item.get('content', '')
        
        # Extract keywords to identify trends
        keywords = Utils.extract_keywords(all_text, max_keywords=20)
        
        # Look for trending terms
        trending_terms = []
        for keyword in keywords:
            if len(keyword) > 3:  # Filter out short words
                trending_terms.append(keyword)
        
        return trending_terms[:10]  # Top 10 trends
    
    def get_popular_questions(self, keyword: str) -> List[str]:
        """Get the most popular questions for a keyword"""
        try:
            # This would typically use Google's "People also ask" or similar
            # For now, we'll generate some common question patterns
            
            question_templates = [
                f"What is {keyword}?",
                f"How to {keyword}?",
                f"Why is {keyword} important?",
                f"When should I use {keyword}?",
                f"Best practices for {keyword}",
                f"Common problems with {keyword}",
                f"How to improve {keyword}?",
                f"Tips for {keyword}",
                f"Guide to {keyword}",
                f"Everything you need to know about {keyword}"
            ]
            
            return question_templates
            
        except Exception as e:
            logger.error(f"Error getting popular questions: {e}")
            return []
    
    def analyze_sentiment(self, ugc_data: Dict[str, Any]) -> Dict[str, float]:
        """Analyze sentiment of UGC data"""
        try:
            from textblob import TextBlob
            
            positive_count = 0
            negative_count = 0
            neutral_count = 0
            total_items = 0
            
            # Analyze sentiment across all platforms
            for platform_data in [ugc_data.get('reddit_data', []), 
                                 ugc_data.get('quora_data', []),
                                 ugc_data.get('stackoverflow_data', []),
                                 ugc_data.get('forums_data', [])]:
                
                for item in platform_data:
                    text = item.get('title', '') + ' ' + item.get('content', '')
                    if text.strip():
                        blob = TextBlob(text)
                        sentiment = blob.sentiment.polarity
                        
                        if sentiment > 0.1:
                            positive_count += 1
                        elif sentiment < -0.1:
                            negative_count += 1
                        else:
                            neutral_count += 1
                        
                        total_items += 1
            
            if total_items > 0:
                return {
                    'positive': positive_count / total_items,
                    'negative': negative_count / total_items,
                    'neutral': neutral_count / total_items,
                    'total_items': total_items
                }
            else:
                return {
                    'positive': 0.0,
                    'negative': 0.0,
                    'neutral': 1.0,
                    'total_items': 0
                }
                
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {
                'positive': 0.0,
                'negative': 0.0,
                'neutral': 1.0,
                'total_items': 0
            }
    
    def research_linkedin(self, keyword: str) -> List[Dict[str, Any]]:
        """Research LinkedIn for discussions about the keyword"""
        try:
            # LinkedIn research (simplified approach)
            # In a real implementation, this would use LinkedIn's API or scraping
            logger.info(f"Researching LinkedIn for: {keyword}")
            
            # Placeholder for LinkedIn research
            # Note: LinkedIn requires authentication and has strict terms of service
            return [
                {
                    'title': f'LinkedIn discussion about {keyword}',
                    'content': f'Professional discussion on {keyword}',
                    'author': 'Finance Professional',
                    'engagement': 'High',
                    'url': f'https://linkedin.com/posts/{keyword.replace(" ", "-")}',
                    'platform': 'linkedin',
                    'type': 'post'
                }
            ]
            
        except Exception as e:
            logger.error(f"Error researching LinkedIn: {e}")
            return []
    
    def research_substack(self, keyword: str) -> List[Dict[str, Any]]:
        """Research Substack for articles about the keyword"""
        try:
            # Substack research (simplified approach)
            logger.info(f"Researching Substack for: {keyword}")
            
            # Placeholder for Substack research
            return [
                {
                    'title': f'Substack article about {keyword}',
                    'content': f'In-depth analysis of {keyword}',
                    'author': 'Finance Newsletter',
                    'subscribers': '5000+',
                    'url': f'https://substack.com/posts/{keyword.replace(" ", "-")}',
                    'platform': 'substack',
                    'type': 'article'
                }
            ]
            
        except Exception as e:
            logger.error(f"Error researching Substack: {e}")
            return []
    
    def identify_themes(self, ugc_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify common themes from UGC data and AI research"""
        try:
            themes = []
            
            # Extract themes from AI deep research
            ai_research = ugc_data.get('ai_deep_research', {})
            if 'themes' in ai_research:
                themes.extend(ai_research['themes'])
            
            # Extract themes from platform data
            platform_themes = {}
            
            # Reddit themes
            for post in ugc_data.get('reddit_data', []):
                title = post.get('title', '').lower()
                if 'budget' in title:
                    platform_themes['Budget Planning'] = platform_themes.get('Budget Planning', 0) + 1
                if 'forecast' in title:
                    platform_themes['Forecasting'] = platform_themes.get('Forecasting', 0) + 1
                if 'analysis' in title:
                    platform_themes['Financial Analysis'] = platform_themes.get('Financial Analysis', 0) + 1
            
            # Convert platform themes to structured format
            for theme_name, count in platform_themes.items():
                themes.append({
                    'theme_name': theme_name,
                    'description': f'Common theme found in {count} discussions',
                    'questions': [],
                    'common_answers': [],
                    'key_insights': [],
                    'platforms_mentioned': ['reddit', 'quora', 'linkedin', 'substack']
                })
            
            return themes
            
        except Exception as e:
            logger.error(f"Error identifying themes: {e}")
            return []
    
    # Basic research methods
    def research_quora_basic(self, keyword: str) -> List[Dict[str, Any]]:
        """Basic Quora research - simplified version"""
        try:
            logger.info(f"Basic Quora research for: {keyword}")
            
            # Simplified Quora search
            search_url = f"https://www.quora.com/search?q={quote_plus(keyword)}&type=question"
            
            response = self.session.get(search_url, timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                questions = []
                
                # Look for question elements (simplified)
                question_elements = soup.find_all('a', href=re.compile(r'/question/'))
                
                for element in question_elements[:5]:  # Limit to 5 questions
                    title = element.get_text().strip()
                    url = urljoin('https://www.quora.com', element.get('href', ''))
                    
                    if title and 'question' in url:
                        questions.append({
                            'platform': 'quora',
                            'title': title,
                            'url': url,
                            'type': 'question'
                        })
                
                logger.info(f"Basic Quora research found {len(questions)} questions")
                return questions
            
            return []
            
        except Exception as e:
            logger.error(f"Error in basic Quora research: {e}")
            return []
    
    def research_linkedin_basic(self, keyword: str) -> List[Dict[str, Any]]:
        """Basic LinkedIn research - simplified version"""
        try:
            logger.info(f"Basic LinkedIn research for: {keyword}")
            
            # Simplified LinkedIn search (simulation)
            # Note: LinkedIn has strict anti-scraping measures
            linkedin_data = [
                {
                    'platform': 'linkedin',
                    'title': f"Discussion about {keyword} in finance industry",
                    'content': f"Professional discussion about {keyword} and its impact on business",
                    'url': f"https://linkedin.com/posts/discussion-{keyword.replace(' ', '-')}",
                    'type': 'post'
                },
                {
                    'platform': 'linkedin',
                    'title': f"{keyword} trends in 2024",
                    'content': f"Industry insights on {keyword} and future trends",
                    'url': f"https://linkedin.com/posts/trends-{keyword.replace(' ', '-')}",
                    'type': 'article'
                }
            ]
            
            logger.info(f"Basic LinkedIn research found {len(linkedin_data)} items")
            return linkedin_data
            
        except Exception as e:
            logger.error(f"Error in basic LinkedIn research: {e}")
            return []
    
    def research_substack_basic(self, keyword: str) -> List[Dict[str, Any]]:
        """Basic Substack research - simplified version"""
        try:
            logger.info(f"Basic Substack research for: {keyword}")
            
            # Simplified Substack search (simulation)
            substack_data = [
                {
                    'platform': 'substack',
                    'title': f"Understanding {keyword} for finance professionals",
                    'content': f"Comprehensive guide on {keyword} and its applications",
                    'url': f"https://substack.com/posts/{keyword.replace(' ', '-')}",
                    'type': 'newsletter'
                },
                {
                    'platform': 'substack',
                    'title': f"{keyword} analysis and insights",
                    'content': f"Deep dive into {keyword} with expert analysis",
                    'url': f"https://substack.com/posts/analysis-{keyword.replace(' ', '-')}",
                    'type': 'article'
                }
            ]
            
            logger.info(f"Basic Substack research found {len(substack_data)} items")
            return substack_data
            
        except Exception as e:
            logger.error(f"Error in basic Substack research: {e}")
            return []
    
    # Basic insight extraction methods
    def extract_questions_basic(self, ugc_data: Dict[str, Any]) -> List[str]:
        """Extract questions from basic UGC data"""
        questions = []
        
        # Extract from Reddit posts
        for post in ugc_data.get('reddit_data', []):
            title = post.get('title', '')
            if '?' in title or any(word in title.lower() for word in ['how', 'what', 'why', 'when', 'where', 'which']):
                questions.append(title)
        
        # Extract from Quora questions
        for question in ugc_data.get('quora_data', []):
            title = question.get('title', '')
            if title:
                questions.append(title)
        
        # Remove duplicates and clean
        unique_questions = list(set(questions))
        cleaned_questions = [q.strip() for q in unique_questions if len(q.strip()) > 10]
        
        return cleaned_questions[:10]  # Limit to 10 questions
    
    def extract_concerns_basic(self, ugc_data: Dict[str, Any]) -> List[str]:
        """Extract user concerns from basic UGC data"""
        concerns = []
        
        # Common concern indicators
        concern_indicators = [
            'problem', 'issue', 'trouble', 'difficulty', 'challenge', 'struggle',
            'worried', 'concerned', 'frustrated', 'confused', 'help', 'advice'
        ]
        
        # Extract from all platforms
        for platform_data in [ugc_data.get('reddit_data', []), 
                             ugc_data.get('quora_data', []),
                             ugc_data.get('linkedin_data', []),
                             ugc_data.get('substack_data', [])]:
            
            for item in platform_data:
                title = item.get('title', '').lower()
                content = item.get('content', '').lower()
                
                for indicator in concern_indicators:
                    if indicator in title or indicator in content:
                        concerns.append(item.get('title', ''))
                        break
        
        # Remove duplicates and clean
        unique_concerns = list(set(concerns))
        cleaned_concerns = [c.strip() for c in unique_concerns if len(c.strip()) > 10]
        
        return cleaned_concerns[:10]  # Limit to 10 concerns
    
    def identify_themes_basic(self, ugc_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify basic themes from UGC data"""
        themes = []
        
        # Simple theme extraction
        all_text = ""
        
        # Combine all text from different platforms
        for platform_data in [ugc_data.get('reddit_data', []), 
                             ugc_data.get('quora_data', []),
                             ugc_data.get('linkedin_data', []),
                             ugc_data.get('substack_data', [])]:
            
            for item in platform_data:
                title = item.get('title', '')
                content = item.get('content', '')
                all_text += f" {title} {content}"
        
        # Basic theme categories
        basic_themes = {
            'finance': ['money', 'finance', 'financial', 'budget', 'invest'],
            'business': ['business', 'company', 'strategy', 'management'],
            'technology': ['tech', 'software', 'digital', 'automation'],
            'planning': ['plan', 'strategy', 'goal', 'objective'],
            'analysis': ['analysis', 'data', 'metrics', 'report']
        }
        
        theme_scores = {}
        
        for theme, keywords in basic_themes.items():
            score = 0
            for keyword in keywords:
                score += all_text.lower().count(keyword.lower())
            if score > 0:
                theme_scores[theme] = score
        
        # Create theme objects
        for theme, score in sorted(theme_scores.items(), key=lambda x: x[1], reverse=True)[:3]:
            themes.append({
                'theme_name': theme.title(),
                'description': f"Discussions related to {theme}",
                'frequency': score
            })
        
        return themes
    
    def generate_ugc_html(self, ugc_data: Dict[str, Any]) -> str:
        """Generate HTML output for UGC research results"""
        try:
            focus_keyword = ugc_data.get('focus_keyword', '')
            topic_theme = ugc_data.get('topic_theme', '')
            buyer_persona = ugc_data.get('buyer_persona', '')
            
            html = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>UGC Research Results - {focus_keyword}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
                    .header {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
                    .section {{ margin-bottom: 30px; }}
                    .section h2 {{ color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
                    .platform {{ background: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin-bottom: 15px; }}
                    .platform h3 {{ color: #007bff; margin-top: 0; }}
                    .item {{ margin-bottom: 15px; padding: 10px; background: #f8f9fa; border-radius: 5px; }}
                    .item h4 {{ margin: 0 0 10px 0; color: #333; }}
                    .item a {{ color: #007bff; text-decoration: none; }}
                    .item a:hover {{ text-decoration: underline; }}
                    .stats {{ display: flex; gap: 20px; margin-bottom: 20px; }}
                    .stat {{ text-align: center; padding: 15px; background: #e9ecef; border-radius: 8px; flex: 1; }}
                    .stat h3 {{ margin: 0; color: #007bff; font-size: 24px; }}
                    .stat p {{ margin: 5px 0 0 0; color: #666; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>UGC Research Results</h1>
                    <p><strong>Focus Keyword:</strong> {focus_keyword}</p>
                    <p><strong>Topic/Theme:</strong> {topic_theme}</p>
                    <p><strong>Buyer Persona:</strong> {buyer_persona}</p>
                    <p><strong>Generated:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                </div>
                
                <div class="stats">
                    <div class="stat">
                        <h3>{len(ugc_data.get('reddit_data', []))}</h3>
                        <p>Reddit Posts</p>
                    </div>
                    <div class="stat">
                        <h3>{len(ugc_data.get('quora_data', []))}</h3>
                        <p>Quora Questions</p>
                    </div>
                    <div class="stat">
                        <h3>{len(ugc_data.get('linkedin_data', []))}</h3>
                        <p>LinkedIn Posts</p>
                    </div>
                    <div class="stat">
                        <h3>{len(ugc_data.get('substack_data', []))}</h3>
                        <p>Substack Articles</p>
                    </div>
                </div>
            """
            
            # Reddit Section
            reddit_data = ugc_data.get('reddit_data', [])
            if reddit_data:
                html += """
                <div class="section">
                    <h2>Reddit Discussions</h2>
                """
                for post in reddit_data:
                    html += f"""
                    <div class="item">
                        <h4><a href="{post.get('url', '#')}" target="_blank">{post.get('title', 'No title')}</a></h4>
                        <p><strong>Subreddit:</strong> r/{post.get('subreddit', 'unknown')}</p>
                        <p><strong>Score:</strong> {post.get('score', 0)} | <strong>Comments:</strong> {post.get('comments', 0)}</p>
                        <p>{post.get('content', 'No content available')}</p>
                    </div>
                    """
                html += "</div>"
            
            # Quora Section
            quora_data = ugc_data.get('quora_data', [])
            if quora_data:
                html += """
                <div class="section">
                    <h2>Quora Questions</h2>
                """
                for question in quora_data:
                    html += f"""
                    <div class="item">
                        <h4><a href="{question.get('url', '#')}" target="_blank">{question.get('title', 'No title')}</a></h4>
                    </div>
                    """
                html += "</div>"
            
            # LinkedIn Section
            linkedin_data = ugc_data.get('linkedin_data', [])
            if linkedin_data:
                html += """
                <div class="section">
                    <h2>LinkedIn Content</h2>
                """
                for post in linkedin_data:
                    html += f"""
                    <div class="item">
                        <h4><a href="{post.get('url', '#')}" target="_blank">{post.get('title', 'No title')}</a></h4>
                        <p>{post.get('content', 'No content available')}</p>
                    </div>
                    """
                html += "</div>"
            
            # Substack Section
            substack_data = ugc_data.get('substack_data', [])
            if substack_data:
                html += """
                <div class="section">
                    <h2>Substack Articles</h2>
                """
                for article in substack_data:
                    html += f"""
                    <div class="item">
                        <h4><a href="{article.get('url', '#')}" target="_blank">{article.get('title', 'No title')}</a></h4>
                        <p>{article.get('content', 'No content available')}</p>
                    </div>
                    """
                html += "</div>"
            
            # Questions Section
            questions = ugc_data.get('questions', [])
            if questions:
                html += """
                <div class="section">
                    <h2>Key Questions Identified</h2>
                    <ul>
                """
                for question in questions:
                    html += f"<li>{question}</li>"
                html += "</ul></div>"
            
            # Concerns Section
            concerns = ugc_data.get('concerns', [])
            if concerns:
                html += """
                <div class="section">
                    <h2>User Concerns</h2>
                    <ul>
                """
                for concern in concerns:
                    html += f"<li>{concern}</li>"
                html += "</ul></div>"
            
            # Themes Section
            themes = ugc_data.get('themes', [])
            if themes:
                html += """
                <div class="section">
                    <h2>Identified Themes</h2>
                """
                for theme in themes:
                    html += f"""
                    <div class="item">
                        <h4>{theme.get('theme_name', 'Unknown Theme')}</h4>
                        <p>{theme.get('description', 'No description')}</p>
                        <p><strong>Frequency:</strong> {theme.get('frequency', 0)} mentions</p>
                    </div>
                    """
                html += "</div>"
            
            html += """
            </body>
            </html>
            """
            
            return html
            
        except Exception as e:
            logger.error(f"Error generating UGC HTML: {e}")
            return f"<p>Error generating HTML: {str(e)}</p>" 