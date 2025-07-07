import logging
from typing import Dict, Any, List
from datetime import datetime
import os

from src.utils import Utils

# Conditional imports for PDF generation
try:
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("WeasyPrint not available")

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("ReportLab not available")

logger = logging.getLogger(__name__)

class PDFGenerator:
    """Generate well-formatted PDFs for each step of the SEO brief workflow"""
    
    def __init__(self):
        if WEASYPRINT_AVAILABLE:
            try:
                self.font_config = FontConfiguration()
                self.use_weasyprint = True
            except Exception as e:
                logger.warning(f"WeasyPrint initialization failed: {e}")
                self.use_weasyprint = False
        else:
            self.use_weasyprint = False
        
        if REPORTLAB_AVAILABLE and not self.use_weasyprint:
            self.reportlab_imports = {
                'letter': letter, 'A4': A4, 'SimpleDocTemplate': SimpleDocTemplate,
                'Paragraph': Paragraph, 'Spacer': Spacer, 'Table': Table, 'TableStyle': TableStyle,
                'getSampleStyleSheet': getSampleStyleSheet, 'ParagraphStyle': ParagraphStyle,
                'inch': inch, 'colors': colors
            }
        else:
            self.reportlab_imports = None
        
        if not self.use_weasyprint and not self.reportlab_imports:
            logger.error("No PDF generation method available")
    
    def generate_step2_pdf(self, ugc_brief: Dict[str, Any], focus_keyword: str, topic_theme: str, buyer_persona: str) -> str:
        """Generate PDF for Step 2 UGC Brief"""
        try:
            if self.use_weasyprint:
                return self._generate_step2_pdf_weasyprint(ugc_brief, focus_keyword, topic_theme, buyer_persona)
            elif self.reportlab_imports:
                return self._generate_step2_pdf_reportlab(ugc_brief, focus_keyword, topic_theme, buyer_persona)
            else:
                logger.error("No PDF generation method available")
                return None
        except Exception as e:
            logger.error(f"Error generating Step 2 PDF: {e}")
            return None
    
    def generate_step3_pdf(self, serp_brief: Dict[str, Any], serp_results: List[Dict], focus_keyword: str) -> str:
        """Generate PDF for Step 3 SERP Analysis Brief"""
        try:
            if self.use_weasyprint:
                return self._generate_step3_pdf_weasyprint(serp_brief, serp_results, focus_keyword)
            elif self.reportlab_imports:
                return self._generate_step3_pdf_reportlab(serp_brief, serp_results, focus_keyword)
            else:
                logger.error("No PDF generation method available")
                return None
        except Exception as e:
            logger.error(f"Error generating Step 3 PDF: {e}")
            return None
    
    def generate_final_pdf(self, combined_result: Dict[str, Any]) -> str:
        """Generate comprehensive PDF for final brief"""
        try:
            if self.use_weasyprint:
                return self._generate_final_pdf_weasyprint(combined_result)
            elif self.reportlab_imports:
                return self._generate_final_pdf_reportlab(combined_result)
            else:
                logger.error("No PDF generation method available")
                return None
        except Exception as e:
            logger.error(f"Error generating final PDF: {e}")
            return None
    
    def _generate_step2_pdf_weasyprint(self, ugc_brief: Dict[str, Any], focus_keyword: str, topic_theme: str, buyer_persona: str) -> str:
        """Generate Step 2 PDF using WeasyPrint"""
        html_content = self._create_ugc_html(ugc_brief, focus_keyword, topic_theme, buyer_persona)
        timestamp = Utils.format_timestamp()
        filename = f"ugc_brief_{Utils.sanitize_filename(focus_keyword)}_{timestamp}.pdf"
        filepath = os.path.join('output', filename)
        
        HTML(string=html_content).write_pdf(
            filepath,
            font_config=self.font_config,
            stylesheets=[CSS(string=self._get_css_styles())]
        )
        
        logger.info(f"Step 2 PDF generated: {filepath}")
        return filename
    
    def _generate_step2_pdf_reportlab(self, ugc_brief: Dict[str, Any], focus_keyword: str, topic_theme: str, buyer_persona: str) -> str:
        """Generate Step 2 PDF using ReportLab"""
        # Implementation using ReportLab
        timestamp = Utils.format_timestamp()
        filename = f"ugc_brief_{Utils.sanitize_filename(focus_keyword)}_{timestamp}.pdf"
        filepath = os.path.join('output', filename)
        
        doc = self.reportlab_imports['SimpleDocTemplate'](filepath, pagesize=self.reportlab_imports['A4'])
        styles = self.reportlab_imports['getSampleStyleSheet']()
        story = []
        
        # Title
        title_style = self.reportlab_imports['ParagraphStyle'](
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Center
        )
        story.append(self.reportlab_imports['Paragraph']("User-Generated Content Research Brief", title_style))
        story.append(self.reportlab_imports['Spacer'](1, 20))
        
        # Brief info
        info_data = [
            ['Focus Keyword:', focus_keyword],
            ['Topic/Theme:', topic_theme],
            ['Buyer Persona:', buyer_persona],
            ['Generated:', datetime.now().strftime('%B %d, %Y at %I:%M %p')]
        ]
        
        info_table = self.reportlab_imports['Table'](info_data, colWidths=[2*self.reportlab_imports['inch'], 4*self.reportlab_imports['inch']])
        info_table.setStyle(self.reportlab_imports['TableStyle']([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        story.append(info_table)
        story.append(self.reportlab_imports['Spacer'](1, 20))
        
        # Content sections
        if ugc_brief.get('themes'):
            story.append(self.reportlab_imports['Paragraph']("Thematic Analysis", styles['Heading2']))
            for theme in ugc_brief['themes']:
                story.append(self.reportlab_imports['Paragraph'](f"<b>{theme.get('theme_name', 'Unnamed Theme')}</b>", styles['Normal']))
                story.append(self.reportlab_imports['Paragraph'](theme.get('description', 'No description'), styles['Normal']))
                story.append(self.reportlab_imports['Spacer'](1, 10))
        
        if ugc_brief.get('top_questions'):
            story.append(self.reportlab_imports['Paragraph']("Top Questions", styles['Heading2']))
            for i, question in enumerate(ugc_brief['top_questions'], 1):
                story.append(self.reportlab_imports['Paragraph'](f"{i}. {question}", styles['Normal']))
            story.append(self.reportlab_imports['Spacer'](1, 10))
        
        doc.build(story)
        logger.info(f"Step 2 PDF generated (ReportLab): {filepath}")
        return filename
    
    def _generate_step3_pdf_weasyprint(self, serp_brief: Dict[str, Any], serp_results: List[Dict], focus_keyword: str) -> str:
        """Generate Step 3 PDF using WeasyPrint"""
        html_content = self._create_serp_html(serp_brief, serp_results, focus_keyword)
        timestamp = Utils.format_timestamp()
        filename = f"serp_analysis_{Utils.sanitize_filename(focus_keyword)}_{timestamp}.pdf"
        filepath = os.path.join('output', filename)
        
        HTML(string=html_content).write_pdf(
            filepath,
            font_config=self.font_config,
            stylesheets=[CSS(string=self._get_css_styles())]
        )
        
        logger.info(f"Step 3 PDF generated: {filepath}")
        return filename
    
    def _generate_step3_pdf_reportlab(self, serp_brief: Dict[str, Any], serp_results: List[Dict], focus_keyword: str) -> str:
        """Generate Step 3 PDF using ReportLab"""
        timestamp = Utils.format_timestamp()
        filename = f"serp_analysis_{Utils.sanitize_filename(focus_keyword)}_{timestamp}.pdf"
        filepath = os.path.join('output', filename)
        
        doc = self.reportlab_imports['SimpleDocTemplate'](filepath, pagesize=self.reportlab_imports['A4'])
        styles = self.reportlab_imports['getSampleStyleSheet']()
        story = []
        
        # Title
        title_style = self.reportlab_imports['ParagraphStyle'](
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1
        )
        story.append(self.reportlab_imports['Paragraph']("SERP Analysis Brief", title_style))
        story.append(self.reportlab_imports['Spacer'](1, 20))
        
        # SERP Results
        story.append(self.reportlab_imports['Paragraph']("Top 10 Google Search Results", styles['Heading2']))
        for i, result in enumerate(serp_results, 1):
            story.append(self.reportlab_imports['Paragraph'](f"{i}. {result.get('title', 'No title')}", styles['Normal']))
            story.append(self.reportlab_imports['Paragraph'](result.get('url', 'No URL'), styles['Normal']))
            story.append(self.reportlab_imports['Paragraph'](result.get('snippet', 'No snippet'), styles['Normal']))
            story.append(self.reportlab_imports['Spacer'](1, 10))
        
        # SERP Analysis
        story.append(self.reportlab_imports['Paragraph']("Detailed SERP Analysis", styles['Heading2']))
        story.append(self.reportlab_imports['Paragraph'](serp_brief.get('raw_response', 'No analysis available'), styles['Normal']))
        
        doc.build(story)
        logger.info(f"Step 3 PDF generated (ReportLab): {filepath}")
        return filename
    
    def _generate_final_pdf_weasyprint(self, combined_result: Dict[str, Any]) -> str:
        """Generate Final PDF using WeasyPrint"""
        html_content = self._create_final_html(combined_result)
        timestamp = Utils.format_timestamp()
        filename = f"final_brief_{Utils.sanitize_filename(combined_result['focus_keyword'])}_{timestamp}.pdf"
        filepath = os.path.join('output', filename)
        
        HTML(string=html_content).write_pdf(
            filepath,
            font_config=self.font_config,
            stylesheets=[CSS(string=self._get_css_styles())]
        )
        
        logger.info(f"Final PDF generated: {filepath}")
        return filename
    
    def _generate_final_pdf_reportlab(self, combined_result: Dict[str, Any]) -> str:
        """Generate Final PDF using ReportLab"""
        timestamp = Utils.format_timestamp()
        filename = f"final_brief_{Utils.sanitize_filename(combined_result['focus_keyword'])}_{timestamp}.pdf"
        filepath = os.path.join('output', filename)
        
        doc = self.reportlab_imports['SimpleDocTemplate'](filepath, pagesize=self.reportlab_imports['A4'])
        styles = self.reportlab_imports['getSampleStyleSheet']()
        story = []
        
        # Title
        title_style = self.reportlab_imports['ParagraphStyle'](
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1
        )
        story.append(self.reportlab_imports['Paragraph']("Comprehensive SEO Content Brief", title_style))
        story.append(self.reportlab_imports['Spacer'](1, 20))
        
        # Brief info
        info_data = [
            ['Focus Keyword:', combined_result['focus_keyword']],
            ['Topic/Theme:', combined_result['topic_theme']],
            ['Buyer Persona:', combined_result['buyer_persona']],
            ['Generated:', datetime.now().strftime('%B %d, %Y at %I:%M %p')]
        ]
        
        info_table = self.reportlab_imports['Table'](info_data, colWidths=[2*self.reportlab_imports['inch'], 4*self.reportlab_imports['inch']])
        info_table.setStyle(self.reportlab_imports['TableStyle']([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        story.append(info_table)
        story.append(self.reportlab_imports['Spacer'](1, 20))
        
        # Content sections
        brief_content = combined_result.get('brief_content', {})
        
        if brief_content.get('title_suggestions'):
            story.append(self.reportlab_imports['Paragraph']("Title Suggestions", styles['Heading2']))
            for i, title in enumerate(brief_content['title_suggestions'], 1):
                story.append(self.reportlab_imports['Paragraph'](f"{i}. {title}", styles['Normal']))
            story.append(self.reportlab_imports['Spacer'](1, 10))
        
        if brief_content.get('meta_description'):
            story.append(self.reportlab_imports['Paragraph']("Meta Description", styles['Heading2']))
            story.append(self.reportlab_imports['Paragraph'](brief_content['meta_description'], styles['Normal']))
            story.append(self.reportlab_imports['Spacer'](1, 10))
        
        if brief_content.get('target_keywords'):
            story.append(self.reportlab_imports['Paragraph']("Target Keywords", styles['Heading2']))
            keywords_text = ", ".join(brief_content['target_keywords'])
            story.append(self.reportlab_imports['Paragraph'](keywords_text, styles['Normal']))
            story.append(self.reportlab_imports['Spacer'](1, 10))
        
        doc.build(story)
        logger.info(f"Final PDF generated (ReportLab): {filepath}")
        return filename
    
    def _create_ugc_html(self, ugc_brief: Dict[str, Any], focus_keyword: str, topic_theme: str, buyer_persona: str) -> str:
        """Create HTML content for UGC brief"""
        
        # Extract data from UGC brief
        themes = ugc_brief.get('themes', [])
        top_questions = ugc_brief.get('top_questions', [])
        key_concerns = ugc_brief.get('key_concerns', [])
        platform_insights = ugc_brief.get('platform_insights', {})
        recommendations = ugc_brief.get('recommendations', [])
        
        # Create themes HTML
        themes_html = ""
        if themes:
            for theme in themes:
                themes_html += f"""
                <div class="theme-section">
                    <h3>{theme.get('theme_name', 'Unnamed Theme')}</h3>
                    <p><strong>Description:</strong> {theme.get('description', 'No description available')}</p>
                    <div class="theme-details">
                        <h4>Questions:</h4>
                        <ul>
                            {''.join([f'<li>{q}</li>' for q in theme.get('questions', [])])}
                        </ul>
                        <h4>Common Answers:</h4>
                        <ul>
                            {''.join([f'<li>{a}</li>' for a in theme.get('common_answers', [])])}
                        </ul>
                        <h4>Key Insights:</h4>
                        <ul>
                            {''.join([f'<li>{i}</li>' for i in theme.get('key_insights', [])])}
                        </ul>
                    </div>
                </div>
                """
        
        # Create platform insights HTML
        platform_html = ""
        for platform, insight in platform_insights.items():
            if insight:
                platform_html += f"""
                <div class="platform-section">
                    <h3>{platform.capitalize()}</h3>
                    <p>{insight}</p>
                </div>
                """
        
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>UGC Research Brief - {focus_keyword}</title>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>User-Generated Content Research Brief</h1>
                    <div class="brief-info">
                        <p><strong>Focus Keyword:</strong> {focus_keyword}</p>
                        <p><strong>Topic/Theme:</strong> {topic_theme}</p>
                        <p><strong>Buyer Persona:</strong> {buyer_persona}</p>
                        <p><strong>Generated:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                    </div>
                </div>
                
                <div class="summary-section">
                    <h2>Executive Summary</h2>
                    <div class="summary-stats">
                        <div class="stat">
                            <h3>{len(themes)}</h3>
                            <p>Themes Identified</p>
                        </div>
                        <div class="stat">
                            <h3>{len(top_questions)}</h3>
                            <p>Top Questions</p>
                        </div>
                        <div class="stat">
                            <h3>{len(key_concerns)}</h3>
                            <p>Key Concerns</p>
                        </div>
                        <div class="stat">
                            <h3>{len(recommendations)}</h3>
                            <p>Recommendations</p>
                        </div>
                    </div>
                </div>
                
                <div class="content-section">
                    <h2>Top Questions Identified</h2>
                    <div class="questions-list">
                        {''.join([f'<div class="question-item"><span class="number">{i+1}.</span> {q}</div>' for i, q in enumerate(top_questions)])}
                    </div>
                </div>
                
                <div class="content-section">
                    <h2>Key Concerns</h2>
                    <div class="concerns-list">
                        {''.join([f'<div class="concern-item"><span class="bullet">•</span> {c}</div>' for c in key_concerns])}
                    </div>
                </div>
                
                <div class="content-section">
                    <h2>Thematic Analysis</h2>
                    {themes_html}
                </div>
                
                <div class="content-section">
                    <h2>Platform Insights</h2>
                    {platform_html}
                </div>
                
                <div class="content-section">
                    <h2>Strategic Recommendations</h2>
                    <div class="recommendations-list">
                        {''.join([f'<div class="recommendation-item"><span class="bullet">•</span> {r}</div>' for r in recommendations])}
                    </div>
                </div>
                
                <div class="footer">
                    <p>Generated by SEO Brief Automator | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _create_serp_html(self, serp_brief: Dict[str, Any], serp_results: List[Dict], focus_keyword: str) -> str:
        """Create HTML content for SERP analysis brief"""
        
        # Create SERP results HTML
        serp_results_html = ""
        for i, result in enumerate(serp_results, 1):
            serp_results_html += f"""
            <div class="serp-result">
                <h3>{i}. {result.get('title', 'No title')}</h3>
                <p class="url">{result.get('url', 'No URL')}</p>
                <p class="snippet">{result.get('snippet', 'No snippet available')}</p>
            </div>
            """
        
        # Get SERP analysis content
        serp_analysis = serp_brief.get('raw_response', 'No SERP analysis available')
        
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>SERP Analysis Brief - {focus_keyword}</title>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>SERP Analysis Brief</h1>
                    <div class="brief-info">
                        <p><strong>Focus Keyword:</strong> {focus_keyword}</p>
                        <p><strong>Articles Analyzed:</strong> {len(serp_results)}</p>
                        <p><strong>Generated:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                    </div>
                </div>
                
                <div class="content-section">
                    <h2>Top 10 Google Search Results</h2>
                    <div class="serp-results">
                        {serp_results_html}
                    </div>
                </div>
                
                <div class="content-section">
                    <h2>Detailed SERP Analysis</h2>
                    <div class="serp-analysis">
                        <pre class="analysis-content">{serp_analysis}</pre>
                    </div>
                </div>
                
                <div class="footer">
                    <p>Generated by SEO Brief Automator | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _create_final_html(self, combined_result: Dict[str, Any]) -> str:
        """Create comprehensive HTML content for final brief"""
        
        focus_keyword = combined_result['focus_keyword']
        topic_theme = combined_result['topic_theme']
        buyer_persona = combined_result['buyer_persona']
        brief_content = combined_result.get('brief_content', {})
        ugc_research = combined_result.get('ugc_research', {})
        serp_analysis = combined_result.get('serp_analysis', {})
        
        # Extract brief content sections
        title_suggestions = brief_content.get('title_suggestions', [])
        meta_description = brief_content.get('meta_description', '')
        target_keywords = brief_content.get('target_keywords', [])
        content_structure = brief_content.get('content_structure', [])
        user_questions = brief_content.get('user_questions_to_answer', [])
        content_gaps = brief_content.get('content_gaps_to_fill', [])
        seo_recommendations = brief_content.get('seo_recommendations', [])
        
        # Create content structure HTML
        structure_html = ""
        for section in content_structure:
            structure_html += f"""
            <div class="structure-section">
                <h3>{section.get('heading', 'No heading')}</h3>
                <div class="section-details">
                    <h4>Subheadings:</h4>
                    <ul>
                        {''.join([f'<li>{sub}</li>' for sub in section.get('subheadings', [])])}
                    </ul>
                    <h4>Key Points:</h4>
                    <ul>
                        {''.join([f'<li>{point}</li>' for point in section.get('key_points', [])])}
                    </ul>
                    <p><strong>Target Word Count:</strong> {section.get('word_count_target', 0)}</p>
                </div>
            </div>
            """
        
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Comprehensive SEO Brief - {focus_keyword}</title>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Comprehensive SEO Content Brief</h1>
                    <div class="brief-info">
                        <p><strong>Focus Keyword:</strong> {focus_keyword}</p>
                        <p><strong>Topic/Theme:</strong> {topic_theme}</p>
                        <p><strong>Buyer Persona:</strong> {buyer_persona}</p>
                        <p><strong>Generated:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                    </div>
                </div>
                
                <div class="summary-section">
                    <h2>Executive Summary</h2>
                    <div class="summary-stats">
                        <div class="stat">
                            <h3>{serp_analysis.get('articles_found', 0)}</h3>
                            <p>SERP Articles</p>
                        </div>
                        <div class="stat">
                            <h3>{len(ugc_research.get('themes', []))}</h3>
                            <p>UGC Themes</p>
                        </div>
                        <div class="stat">
                            <h3>{len(user_questions)}</h3>
                            <p>User Questions</p>
                        </div>
                        <div class="stat">
                            <h3>{brief_content.get('estimated_word_count', 0)}</h3>
                            <p>Target Words</p>
                        </div>
                    </div>
                </div>
                
                <div class="content-section">
                    <h2>Title Suggestions</h2>
                    <div class="title-suggestions">
                        {''.join([f'<div class="title-item"><span class="number">{i+1}.</span> {title}</div>' for i, title in enumerate(title_suggestions)])}
                    </div>
                </div>
                
                <div class="content-section">
                    <h2>Meta Description</h2>
                    <div class="meta-description">
                        <p>{meta_description}</p>
                    </div>
                </div>
                
                <div class="content-section">
                    <h2>Target Keywords</h2>
                    <div class="keywords-list">
                        {''.join([f'<span class="keyword">{keyword}</span>' for keyword in target_keywords])}
                    </div>
                </div>
                
                <div class="content-section">
                    <h2>Content Structure</h2>
                    <div class="content-structure">
                        {structure_html}
                    </div>
                </div>
                
                <div class="content-section">
                    <h2>User Questions to Answer</h2>
                    <div class="questions-list">
                        {''.join([f'<div class="question-item"><span class="bullet">•</span> {q}</div>' for q in user_questions])}
                    </div>
                </div>
                
                <div class="content-section">
                    <h2>Content Gaps to Fill</h2>
                    <div class="gaps-list">
                        {''.join([f'<div class="gap-item"><span class="bullet">•</span> {gap}</div>' for gap in content_gaps])}
                    </div>
                </div>
                
                <div class="content-section">
                    <h2>SEO Recommendations</h2>
                    <div class="seo-recommendations">
                        {''.join([f'<div class="seo-item"><span class="bullet">•</span> {rec}</div>' for rec in seo_recommendations])}
                    </div>
                </div>
                
                <div class="content-section">
                    <h2>Content Specifications</h2>
                    <div class="specifications">
                        <div class="spec-item">
                            <strong>Tone:</strong> {brief_content.get('content_tone', 'Not specified')}
                        </div>
                        <div class="spec-item">
                            <strong>Estimated Word Count:</strong> {brief_content.get('estimated_word_count', 0)}
                        </div>
                        <div class="spec-item">
                            <strong>Target Reading Level:</strong> {brief_content.get('target_reading_level', 'Not specified')}
                        </div>
                        <div class="spec-item">
                            <strong>Call to Action:</strong> {brief_content.get('call_to_action', 'Not specified')}
                        </div>
                    </div>
                </div>
                
                <div class="footer">
                    <p>Generated by SEO Brief Automator | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _get_css_styles(self) -> str:
        """Get CSS styles for PDF formatting"""
        return """
        @page {
            size: A4;
            margin: 2cm;
            @top-center {
                content: "SEO Brief Automator";
                font-size: 10pt;
                color: #666;
            }
            @bottom-center {
                content: "Page " counter(page) " of " counter(pages);
                font-size: 10pt;
                color: #666;
            }
        }
        
        body {
            font-family: 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
        }
        
        .container {
            max-width: 100%;
            margin: 0 auto;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            margin-bottom: 2rem;
            border-radius: 8px;
        }
        
        .header h1 {
            margin: 0 0 1rem 0;
            font-size: 2rem;
            font-weight: 700;
        }
        
        .brief-info {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
        }
        
        .brief-info p {
            margin: 0.5rem 0;
            font-size: 0.95rem;
        }
        
        .summary-section {
            margin-bottom: 2rem;
        }
        
        .summary-stats {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1rem;
            margin-top: 1rem;
        }
        
        .stat {
            background: #f8f9fa;
            padding: 1.5rem;
            text-align: center;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        
        .stat h3 {
            margin: 0 0 0.5rem 0;
            font-size: 2rem;
            color: #667eea;
            font-weight: 700;
        }
        
        .stat p {
            margin: 0;
            color: #666;
            font-size: 0.9rem;
        }
        
        .content-section {
            margin-bottom: 2rem;
            page-break-inside: avoid;
        }
        
        .content-section h2 {
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 0.5rem;
            margin-bottom: 1rem;
            font-size: 1.5rem;
        }
        
        .content-section h3 {
            color: #555;
            margin-top: 1.5rem;
            margin-bottom: 1rem;
            font-size: 1.2rem;
        }
        
        .content-section h4 {
            color: #666;
            margin-top: 1rem;
            margin-bottom: 0.5rem;
            font-size: 1rem;
        }
        
        .questions-list, .concerns-list, .recommendations-list, .gaps-list, .seo-recommendations {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
        }
        
        .question-item, .concern-item, .recommendation-item, .gap-item, .seo-item {
            margin-bottom: 0.75rem;
            padding-left: 1rem;
        }
        
        .title-item {
            background: #e3f2fd;
            padding: 1rem;
            margin-bottom: 0.75rem;
            border-radius: 6px;
            border-left: 4px solid #2196f3;
        }
        
        .number {
            font-weight: 700;
            color: #667eea;
            margin-right: 0.5rem;
        }
        
        .bullet {
            color: #667eea;
            font-weight: 700;
            margin-right: 0.5rem;
        }
        
        .theme-section {
            background: #f8f9fa;
            padding: 1.5rem;
            margin-bottom: 1rem;
            border-radius: 8px;
            border-left: 4px solid #28a745;
        }
        
        .theme-details {
            margin-top: 1rem;
        }
        
        .theme-details ul {
            margin: 0.5rem 0;
            padding-left: 1.5rem;
        }
        
        .platform-section {
            background: #fff3cd;
            padding: 1rem;
            margin-bottom: 1rem;
            border-radius: 6px;
            border-left: 4px solid #ffc107;
        }
        
        .serp-results {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
        }
        
        .serp-result {
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid #dee2e6;
        }
        
        .serp-result:last-child {
            border-bottom: none;
        }
        
        .serp-result h3 {
            color: #1a0dab;
            margin-bottom: 0.5rem;
            font-size: 1.1rem;
        }
        
        .url {
            color: #006621;
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
        }
        
        .snippet {
            color: #545454;
            font-size: 0.9rem;
            line-height: 1.4;
        }
        
        .serp-analysis {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
        }
        
        .analysis-content {
            white-space: pre-wrap;
            font-family: 'Courier New', monospace;
            font-size: 0.85rem;
            line-height: 1.5;
            margin: 0;
        }
        
        .meta-description {
            background: #e8f5e8;
            padding: 1rem;
            border-radius: 6px;
            border-left: 4px solid #28a745;
        }
        
        .keywords-list {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }
        
        .keyword {
            background: #667eea;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 500;
        }
        
        .content-structure {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
        }
        
        .structure-section {
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid #dee2e6;
        }
        
        .structure-section:last-child {
            border-bottom: none;
        }
        
        .section-details ul {
            margin: 0.5rem 0;
            padding-left: 1.5rem;
        }
        
        .specifications {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
        }
        
        .spec-item {
            margin-bottom: 0.75rem;
            padding: 0.5rem;
            background: white;
            border-radius: 4px;
        }
        
        .footer {
            margin-top: 3rem;
            padding-top: 1rem;
            border-top: 1px solid #dee2e6;
            text-align: center;
            color: #666;
            font-size: 0.9rem;
        }
        
        ul {
            margin: 0.5rem 0;
            padding-left: 1.5rem;
        }
        
        li {
            margin-bottom: 0.5rem;
        }
        
        p {
            margin: 0.5rem 0;
        }
        """ 