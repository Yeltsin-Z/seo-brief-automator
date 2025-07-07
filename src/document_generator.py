import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List
from jinja2 import Template
import markdown
from weasyprint import HTML, CSS
from config.config import Config
from src.utils import Utils

logger = logging.getLogger(__name__)

class DocumentGenerator:
    """Generates beautiful, professional documents from SEO brief data"""
    
    def __init__(self):
        self.templates_dir = 'templates'
        self.output_dir = Config.OUTPUT_DIR
        
    def generate_documents(self, brief_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate multiple document formats from brief data"""
        try:
            documents = {}
            
            # Generate HTML document
            html_content = self.generate_html_document(brief_data)
            html_filename = self.save_html_document(html_content, brief_data['keyword'])
            documents['html'] = html_filename
            
            # Generate PDF document
            pdf_filename = self.generate_pdf_document(html_content, brief_data['keyword'])
            documents['pdf'] = pdf_filename
            
            # Generate Markdown document
            markdown_content = self.generate_markdown_document(brief_data)
            md_filename = self.save_markdown_document(markdown_content, brief_data['keyword'])
            documents['markdown'] = md_filename
            
            # Generate Executive Summary
            summary_content = self.generate_executive_summary(brief_data)
            summary_filename = self.save_executive_summary(summary_content, brief_data['keyword'])
            documents['summary'] = summary_filename
            
            logger.info(f"Generated documents: {list(documents.keys())}")
            return documents
            
        except Exception as e:
            logger.error(f"Error generating documents: {e}")
            return {}
    
    def generate_html_document(self, brief_data: Dict[str, Any]) -> str:
        """Generate a beautiful HTML document"""
        template = self.get_html_template()
        
        # Prepare data for template
        template_data = self.prepare_template_data(brief_data)
        
        return template.render(**template_data)
    
    def get_html_template(self) -> Template:
        """Get the HTML template"""
        template_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SEO Content Brief: {{ keyword }}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f8f9fa;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 10px;
        }
        
        .header .subtitle {
            font-size: 1.2rem;
            opacity: 0.9;
            margin-bottom: 20px;
        }
        
        .meta-info {
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
            gap: 20px;
            margin-top: 30px;
        }
        
        .meta-item {
            text-align: center;
        }
        
        .meta-item .value {
            font-size: 1.5rem;
            font-weight: 600;
            display: block;
        }
        
        .meta-item .label {
            font-size: 0.9rem;
            opacity: 0.8;
        }
        
        .content {
            padding: 40px;
        }
        
        .section {
            margin-bottom: 40px;
        }
        
        .section h2 {
            font-size: 1.8rem;
            font-weight: 600;
            color: #2c3e50;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        
        .section h3 {
            font-size: 1.3rem;
            font-weight: 500;
            color: #34495e;
            margin: 25px 0 15px 0;
        }
        
        .card {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 25px;
            margin: 15px 0;
            border-left: 4px solid #667eea;
        }
        
        .highlight-box {
            background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
            border: 1px solid #fdcb6e;
            border-radius: 8px;
            padding: 20px;
            margin: 15px 0;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        
        .stat-card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-top: 3px solid #667eea;
        }
        
        .stat-card .number {
            font-size: 2rem;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 5px;
        }
        
        .stat-card .label {
            font-size: 0.9rem;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .list-item {
            background: white;
            border-radius: 6px;
            padding: 15px;
            margin: 10px 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border-left: 3px solid #667eea;
        }
        
        .list-item:hover {
            transform: translateX(5px);
            transition: transform 0.2s ease;
        }
        
        .tag {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            margin: 2px;
        }
        
        .content-structure {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin: 15px 0;
        }
        
        .content-section {
            background: white;
            border-radius: 6px;
            padding: 15px;
            margin: 10px 0;
            border-left: 3px solid #27ae60;
        }
        
        .footer {
            background: #2c3e50;
            color: white;
            text-align: center;
            padding: 30px;
            margin-top: 40px;
        }
        
        .footer p {
            opacity: 0.8;
        }
        
        @media print {
            body { background: white; }
            .container { box-shadow: none; }
            .header { break-inside: avoid; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>SEO Content Brief</h1>
            <div class="subtitle">Comprehensive Content Strategy Report</div>
            <div class="meta-info">
                <div class="meta-item">
                    <span class="value">{{ keyword }}</span>
                    <span class="label">Target Keyword</span>
                </div>
                <div class="meta-item">
                    <span class="value">{{ target_audience }}</span>
                    <span class="label">Target Audience</span>
                </div>
                <div class="meta-item">
                    <span class="value">{{ content_type }}</span>
                    <span class="label">Content Type</span>
                </div>
                <div class="meta-item">
                    <span class="value">{{ generated_date }}</span>
                    <span class="label">Generated</span>
                </div>
            </div>
        </div>
        
        <div class="content">
            <!-- Executive Summary -->
            <div class="section">
                <h2>📊 Executive Summary</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="number">{{ articles_analyzed }}</div>
                        <div class="label">Articles Analyzed</div>
                    </div>
                    <div class="stat-card">
                        <div class="number">{{ ugc_items_found }}</div>
                        <div class="label">UGC Items Found</div>
                    </div>
                    <div class="stat-card">
                        <div class="number">{{ questions_identified }}</div>
                        <div class="label">User Questions</div>
                    </div>
                    <div class="stat-card">
                        <div class="number">{{ estimated_word_count }}</div>
                        <div class="label">Target Word Count</div>
                    </div>
                </div>
            </div>
            
            <!-- Title Suggestions -->
            {% if title_suggestions %}
            <div class="section">
                <h2>🎯 Title Suggestions</h2>
                {% for title in title_suggestions %}
                <div class="list-item">
                    <strong>{{ title }}</strong>
                </div>
                {% endfor %}
            </div>
            {% endif %}
            
            <!-- Meta Description -->
            {% if meta_description %}
            <div class="section">
                <h2>📝 Meta Description</h2>
                <div class="highlight-box">
                    <strong>Recommended Meta Description:</strong><br>
                    {{ meta_description }}
                </div>
            </div>
            {% endif %}
            
            <!-- Target Keywords -->
            {% if target_keywords %}
            <div class="section">
                <h2>🔑 Target Keywords</h2>
                <div class="card">
                    {% for keyword in target_keywords %}
                    <span class="tag">{{ keyword }}</span>
                    {% endfor %}
                </div>
            </div>
            {% endif %}
            
            <!-- Content Structure -->
            {% if content_structure %}
            <div class="section">
                <h2>📋 Content Structure</h2>
                <div class="content-structure">
                    {% for section in content_structure %}
                    <div class="content-section">
                        <h3>{{ section.heading }}</h3>
                        {% if section.subheadings %}
                        <p><strong>Subheadings:</strong></p>
                        <ul>
                            {% for subheading in section.subheadings %}
                            <li>{{ subheading }}</li>
                            {% endfor %}
                        </ul>
                        {% endif %}
                        {% if section.key_points %}
                        <p><strong>Key Points:</strong></p>
                        <ul>
                            {% for point in section.key_points %}
                            <li>{{ point }}</li>
                            {% endfor %}
                        </ul>
                        {% endif %}
                        <p><strong>Target Word Count:</strong> {{ section.word_count_target }}</p>
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}
            
            <!-- User Questions -->
            {% if user_questions %}
            <div class="section">
                <h2>❓ User Questions to Answer</h2>
                {% for question in user_questions %}
                <div class="list-item">
                    {{ question }}
                </div>
                {% endfor %}
            </div>
            {% endif %}
            
            <!-- Content Gaps -->
            {% if content_gaps %}
            <div class="section">
                <h2>🕳️ Content Gaps to Fill</h2>
                {% for gap in content_gaps %}
                <div class="list-item">
                    {{ gap }}
                </div>
                {% endfor %}
            </div>
            {% endif %}
            
            <!-- SEO Recommendations -->
            {% if seo_recommendations %}
            <div class="section">
                <h2>🚀 SEO Recommendations</h2>
                {% for rec in seo_recommendations %}
                <div class="list-item">
                    {{ rec }}
                </div>
                {% endfor %}
            </div>
            {% endif %}
            
            <!-- Content Specifications -->
            <div class="section">
                <h2>⚙️ Content Specifications</h2>
                <div class="card">
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="number">{{ content_tone }}</div>
                            <div class="label">Content Tone</div>
                        </div>
                        <div class="stat-card">
                            <div class="number">{{ target_reading_level }}</div>
                            <div class="label">Reading Level</div>
                        </div>
                        <div class="stat-card">
                            <div class="number">{{ estimated_word_count }}</div>
                            <div class="label">Word Count</div>
                        </div>
                    </div>
                    {% if call_to_action %}
                    <div class="highlight-box">
                        <strong>Call to Action:</strong><br>
                        {{ call_to_action }}
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Generated by SEO Brief Generator | {{ generated_date }}</p>
            <p>This document contains AI-generated insights and recommendations for content creation.</p>
        </div>
    </div>
</body>
</html>
        """
        return Template(template_content)
    
    def prepare_template_data(self, brief_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for template rendering"""
        brief_content = brief_data.get('brief_content', {})
        
        return {
            'keyword': brief_data.get('keyword', ''),
            'target_audience': brief_data.get('target_audience', 'general'),
            'content_type': brief_data.get('content_type', 'blog post'),
            'generated_date': brief_data.get('generated_at', ''),
            'articles_analyzed': len(brief_data.get('serp_analysis', {}).get('articles', [])),
            'ugc_items_found': brief_data.get('ugc_research', {}).get('total_found', 0),
            'questions_identified': len(brief_data.get('ugc_research', {}).get('questions', [])),
            'estimated_word_count': brief_content.get('estimated_word_count', 1500),
            'title_suggestions': brief_content.get('title_suggestions', []),
            'meta_description': brief_content.get('meta_description', ''),
            'target_keywords': brief_content.get('target_keywords', []),
            'content_structure': brief_content.get('content_structure', []),
            'user_questions': brief_content.get('user_questions_to_answer', []),
            'content_gaps': brief_content.get('content_gaps_to_fill', []),
            'seo_recommendations': brief_content.get('seo_recommendations', []),
            'content_tone': brief_content.get('content_tone', 'professional'),
            'target_reading_level': brief_content.get('target_reading_level', 'intermediate'),
            'call_to_action': brief_content.get('call_to_action', '')
        }
    
    def save_html_document(self, html_content: str, keyword: str) -> str:
        """Save HTML document to file"""
        filename = f"brief_{Utils.sanitize_filename(keyword)}_{Utils.format_timestamp()}.html"
        filepath = Utils.save_to_file(html_content, filename)
        return filename
    
    def generate_pdf_document(self, html_content: str, keyword: str) -> str:
        """Generate PDF from HTML content"""
        try:
            filename = f"brief_{Utils.sanitize_filename(keyword)}_{Utils.format_timestamp()}.pdf"
            filepath = os.path.join(self.output_dir, filename)
            
            # Generate PDF using WeasyPrint
            HTML(string=html_content).write_pdf(filepath)
            
            logger.info(f"PDF generated: {filepath}")
            return filename
            
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            return ""
    
    def generate_markdown_document(self, brief_data: Dict[str, Any]) -> str:
        """Generate Markdown document"""
        brief_content = brief_data.get('brief_content', {})
        
        md_content = f"""# SEO Content Brief: {brief_data.get('keyword', '')}

**Generated:** {brief_data.get('generated_at', '')}  
**Target Audience:** {brief_data.get('target_audience', 'general')}  
**Content Type:** {brief_data.get('content_type', 'blog post')}

## 📊 Executive Summary

- **Articles Analyzed:** {len(brief_data.get('serp_analysis', {}).get('articles', []))}
- **UGC Items Found:** {brief_data.get('ugc_research', {}).get('total_found', 0)}
- **User Questions Identified:** {len(brief_data.get('ugc_research', {}).get('questions', []))}
- **Estimated Word Count:** {brief_content.get('estimated_word_count', 1500)}

## 🎯 Title Suggestions

"""
        
        for title in brief_content.get('title_suggestions', []):
            md_content += f"- {title}\n"
        
        md_content += f"""
## 📝 Meta Description

{brief_content.get('meta_description', 'No meta description provided')}

## 🔑 Target Keywords

"""
        
        for keyword in brief_content.get('target_keywords', []):
            md_content += f"- `{keyword}`\n"
        
        md_content += """
## 📋 Content Structure

"""
        
        for section in brief_content.get('content_structure', []):
            md_content += f"### {section.get('heading', 'No heading')}\n\n"
            
            if section.get('subheadings'):
                md_content += "**Subheadings:**\n"
                for subheading in section.get('subheadings', []):
                    md_content += f"- {subheading}\n"
                md_content += "\n"
            
            if section.get('key_points'):
                md_content += "**Key Points:**\n"
                for point in section.get('key_points', []):
                    md_content += f"- {point}\n"
                md_content += "\n"
            
            md_content += f"**Target Word Count:** {section.get('word_count_target', 0)}\n\n"
        
        md_content += "## ❓ User Questions to Answer\n\n"
        
        for question in brief_content.get('user_questions_to_answer', []):
            md_content += f"- {question}\n"
        
        md_content += "\n## 🕳️ Content Gaps to Fill\n\n"
        
        for gap in brief_content.get('content_gaps_to_fill', []):
            md_content += f"- {gap}\n"
        
        md_content += "\n## 🚀 SEO Recommendations\n\n"
        
        for rec in brief_content.get('seo_recommendations', []):
            md_content += f"- {rec}\n"
        
        md_content += f"""
## ⚙️ Content Specifications

- **Content Tone:** {brief_content.get('content_tone', 'professional')}
- **Target Reading Level:** {brief_content.get('target_reading_level', 'intermediate')}
- **Estimated Word Count:** {brief_content.get('estimated_word_count', 1500)}
- **Call to Action:** {brief_content.get('call_to_action', 'Not specified')}

---
*Generated by SEO Brief Generator*
"""
        
        return md_content
    
    def save_markdown_document(self, markdown_content: str, keyword: str) -> str:
        """Save Markdown document to file"""
        filename = f"brief_{Utils.sanitize_filename(keyword)}_{Utils.format_timestamp()}.md"
        filepath = Utils.save_to_file(markdown_content, filename)
        return filename
    
    def generate_executive_summary(self, brief_data: Dict[str, Any]) -> str:
        """Generate a concise executive summary"""
        brief_content = brief_data.get('brief_content', {})
        
        summary = f"""# Executive Summary: {brief_data.get('keyword', '')}

## Quick Overview
- **Keyword:** {brief_data.get('keyword', '')}
- **Target Audience:** {brief_data.get('target_audience', 'general')}
- **Content Type:** {brief_data.get('content_type', 'blog post')}
- **Generated:** {brief_data.get('generated_at', '')}

## Key Metrics
- Articles Analyzed: {len(brief_data.get('serp_analysis', {}).get('articles', []))}
- UGC Items Found: {brief_data.get('ugc_research', {}).get('total_found', 0)}
- User Questions: {len(brief_data.get('ugc_research', {}).get('questions', []))}
- Target Word Count: {brief_content.get('estimated_word_count', 1500)}

## Top Title Suggestion
{brief_content.get('title_suggestions', ['No title suggestions'])[0] if brief_content.get('title_suggestions') else 'No title suggestions'}

## Primary Keywords
{', '.join(brief_content.get('target_keywords', [])[:3])}

## Content Focus
- **Tone:** {brief_content.get('content_tone', 'professional')}
- **Reading Level:** {brief_content.get('target_reading_level', 'intermediate')}
- **Main CTA:** {brief_content.get('call_to_action', 'Not specified')}

## Key User Questions (Top 3)
"""
        
        for i, question in enumerate(brief_content.get('user_questions_to_answer', [])[:3], 1):
            summary += f"{i}. {question}\n"
        
        summary += f"""
## Content Gaps to Address
"""
        
        for i, gap in enumerate(brief_content.get('content_gaps_to_fill', [])[:3], 1):
            summary += f"{i}. {gap}\n"
        
        summary += """
---
*This summary provides the essential information needed to start content creation.*
"""
        
        return summary
    
    def save_executive_summary(self, summary_content: str, keyword: str) -> str:
        """Save executive summary to file"""
        filename = f"summary_{Utils.sanitize_filename(keyword)}_{Utils.format_timestamp()}.md"
        filepath = Utils.save_to_file(summary_content, filename)
        return filename 