"""
PDF Generation Module
Creates professional PDFs of summaries with clean formatting
"""

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from datetime import datetime
import io
from typing import BinaryIO


class PDFGenerator:
    """Generate professional PDFs for summaries"""
    
    if not REPORTLAB_AVAILABLE:
        def __init__(self):
            raise ImportError("reportlab is not installed. Install with: pip install reportlab")
    
    # Page configuration
    if REPORTLAB_AVAILABLE:
        PAGE_WIDTH, PAGE_HEIGHT = letter
        MARGIN = 0.75 * inch
        
        # Colors
        HEADER_COLOR = colors.HexColor('#1f77b4')
        ACCENT_COLOR = colors.HexColor('#ff7f0e')
        TEXT_COLOR = colors.HexColor('#333333')
    
    def __init__(self):
        """Initialize PDF generator"""
        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab is not installed. Install with: pip install reportlab")
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            textColor=self.HEADER_COLOR,
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.grey,
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Oblique'
        ))
        
        # Body text style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            leading=16,
            textColor=self.TEXT_COLOR,
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        ))
        
        # Bullet style
        self.styles.add(ParagraphStyle(
            name='CustomBullet',
            parent=self.styles['BodyText'],
            fontSize=11,
            leading=14,
            leftIndent=20,
            textColor=self.TEXT_COLOR,
            spaceAfter=8,
            fontName='Helvetica'
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='CustomSectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=self.ACCENT_COLOR,
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
    
    def _parse_summary_text(self, text: str) -> list:
        """
        Parse summary text and convert to formatted elements
        Handles bullet points (with • or -, or starting lines)
        """
        elements = []
        
        if not text or not text.strip():
            return elements
        
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            
            if not line:
                # Empty line = spacer
                elements.append(('spacer', 8))
                continue
            
            # Detect bullet points
            if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                # Remove bullet character and clean
                clean_text = line.lstrip('•-* ').strip()
                if clean_text:
                    elements.append(('bullet', clean_text))
            
            # Detect headers (all caps or ends with colon)
            elif line.isupper() or line.endswith(':'):
                elements.append(('header', line))
            
            # Regular paragraph
            else:
                # Only add if has reasonable length
                if len(line) > 5:
                    elements.append(('paragraph', line))
        
        return elements
    
    def _build_story(self, title: str, summary: str, url: str = None) -> list:
        """
        Build the document story (list of flowable elements)
        
        Args:
            title: Document title
            summary: Summary text to include
            url: Optional source URL
        
        Returns:
            List of flowable elements for the document
        """
        story = []
        
        # Add title
        story.append(Paragraph(title, self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2 * inch))
        
        # Add metadata
        timestamp = datetime.now().strftime("%B %d, %Y at %H:%M")
        story.append(Paragraph(f"Generated on {timestamp}", self.styles['CustomSubtitle']))
        
        if url:
            # Truncate long URLs for display
            display_url = url[:60] + "..." if len(url) > 60 else url
            story.append(Paragraph(f"Source: {display_url}", self.styles['CustomSubtitle']))
        
        story.append(Spacer(1, 0.3 * inch))
        
        # Add horizontal line using a table (cleaner than alternatives)
        line_table = Table([['']],colWidths=[self.PAGE_WIDTH - 2*self.MARGIN])
        line_table.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (-1, -1), 1, self.ACCENT_COLOR),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(line_table)
        story.append(Spacer(1, 0.2 * inch))
        
        # Parse and format summary
        parsed_elements = self._parse_summary_text(summary)
        
        for element_type, content in parsed_elements:
            try:
                if element_type == 'spacer':
                    story.append(Spacer(1, content / 72))  # Convert points to inches
                
                elif element_type == 'header':
                    # Remove trailing colon from headers
                    header_text = content.rstrip(':')
                    story.append(Paragraph(header_text, self.styles['CustomSectionHeader']))
                
                elif element_type == 'bullet':
                    # Format as bullet point
                    bullet_text = f"<b>•</b> {content}"
                    story.append(Paragraph(bullet_text, self.styles['CustomBullet']))
                
                elif element_type == 'paragraph':
                    story.append(Paragraph(content, self.styles['CustomBody']))
            
            except Exception as e:
                print(f"Warning: Could not add element: {e}")
                continue
        
        # Add footer
        story.append(Spacer(1, 0.3 * inch))
        story.append(Paragraph(
            "<i>Generated by QuickGlance - AI-Powered Content Summarization</i>",
            self.styles['CustomSubtitle']
        ))
        
        return story
    
    def generate_pdf(self, 
                     summary_text: str,
                     title: str = "QuickGlance Summary",
                     url: str = None,
                     filename: str = None) -> BinaryIO:
        """
        Generate PDF from summary text
        
        Args:
            summary_text: The summary content
            title: PDF title (default: "QuickGlance Summary")
            url: Optional source URL
            filename: Optional filename (for saving)
        
        Returns:
            BytesIO object containing the PDF (ready for download)
        
        Raises:
            ValueError: If summary text is empty
        """
        
        if not summary_text or not summary_text.strip():
            raise ValueError("Summary text cannot be empty")
        
        # Create in-memory PDF
        pdf_buffer = io.BytesIO()
        
        # Create the PDF document
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=letter,
            rightMargin=self.MARGIN,
            leftMargin=self.MARGIN,
            topMargin=self.MARGIN,
            bottomMargin=self.MARGIN,
            title=title,
            author="QuickGlance"
        )
        
        # Build the story
        story = self._build_story(title, summary_text, url)
        
        # Build the PDF
        try:
            doc.build(
                story,
                onFirstPage=self._on_page,
                onLaterPages=self._on_page
            )
        except Exception as e:
            raise ValueError(f"Failed to generate PDF: {str(e)}")
        
        # Get bytes and return
        pdf_buffer.seek(0)
        return pdf_buffer
    
    def _on_page(self, canvas, doc):
        """
        Add headers/footers to each page
        
        Args:
            canvas: ReportLab canvas
            doc: Document object
        """
        canvas.saveState()
        
        # Page number and total pages
        page_info = f"Page {doc.page}"
        
        # Footer
        canvas.setFont("Helvetica", 9)
        canvas.setFillColor(colors.grey)
        canvas.drawString(
            self.MARGIN,
            0.3 * inch,
            page_info
        )
        
        canvas.restoreState()
    
    def generate_pdf_bytes(self, summary_text: str, title: str = "QuickGlance Summary", url: str = None) -> bytes:
        """
        Generate PDF and return as bytes (for download button)
        
        Args:
            summary_text: The summary content
            title: PDF title
            url: Optional source URL
        
        Returns:
            PDF as bytes
        """
        pdf_buffer = self.generate_pdf(summary_text, title, url)
        return pdf_buffer.getvalue()


def create_pdf_generator() -> PDFGenerator:
    """Factory function to create PDF generator instance"""
    return PDFGenerator()


# Convenience function for direct use
def generate_summary_pdf(summary_text: str, 
                        title: str = "QuickGlance Summary",
                        url: str = None) -> bytes:
    """
    Quick function to generate PDF from summary
    
    Args:
        summary_text: Summary content
        title: PDF title
        url: Optional source URL
    
    Returns:
        PDF as bytes (ready for download)
    
    Example:
        pdf_bytes = generate_summary_pdf(summary_text)
        # Use with st.download_button(data=pdf_bytes, ...)
    """
    generator = PDFGenerator()
    return generator.generate_pdf_bytes(summary_text, title, url)
