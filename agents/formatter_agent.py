"""
Formatter Agent - Converts summaries to multiple formats.
Handles CSV export and audio generation.
"""

import csv
import tempfile
import json
from typing import Dict, List, Optional
from datetime import datetime
from utils.logging_config import get_logger

logger = get_logger(__name__)


class FormatterAgent:
    """Agent that formats output in various formats."""
    
    def __init__(self):
        """Initialize Formatter Agent."""
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info("Formatter Agent initialized")
    
    def execute(self, query: str, summary: str, urls: List[str] = None) -> dict:
        """
        Format results into multiple output formats.
        
        Args:
            query: Original search query
            summary: Generated summary
            urls: List of source URLs
            
        Returns:
            Dictionary with formatted outputs
        """
        logger.info(f"FormatterAgent processing summary ({len(summary)} chars)")
        
        try:
            results = {
                "status": "success",
                "query": query,
                "timestamp": self.timestamp,
                "formats": {}
            }
            
            # Text format
            text_output = self._format_text(query, summary, urls)
            results["formats"]["text"] = {
                "content": text_output,
                "file": self._save_text(text_output),
                "mime_type": "text/plain"
            }
            
            # CSV format
            csv_output = self._format_csv(query, summary, urls)
            results["formats"]["csv"] = {
                "content": csv_output,
                "file": csv_output,  # Already a file path
                "mime_type": "text/csv"
            }
            
            # JSON format
            json_output = self._format_json(query, summary, urls)
            results["formats"]["json"] = {
                "content": json.dumps(json_output, indent=2),
                "file": self._save_json(json_output),
                "mime_type": "application/json"
            }
            
            # Markdown format
            md_output = self._format_markdown(query, summary, urls)
            results["formats"]["markdown"] = {
                "content": md_output,
                "file": self._save_markdown(md_output),
                "mime_type": "text/markdown"
            }
            
            logger.info(f"FormatterAgent generated formats: {list(results['formats'].keys())}")
            return results
            
        except Exception as e:
            logger.error(f"FormatterAgent failed: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "formats": {}
            }
    
    def _format_text(self, query: str, summary: str, urls: List[str] = None) -> str:
        """Format as plain text."""
        output = []
        output.append("=" * 60)
        output.append("SEARCH RESULTS")
        output.append("=" * 60)
        output.append(f"\nQuery: {query}")
        output.append(f"Generated: {self.timestamp}\n")
        
        output.append("SUMMARY:")
        output.append("-" * 60)
        output.append(summary)
        
        if urls:
            output.append("\n\nSOURCES:")
            output.append("-" * 60)
            for i, url in enumerate(urls, 1):
                output.append(f"{i}. {url}")
        
        output.append("\n" + "=" * 60)
        return "\n".join(output)
    
    def _format_csv(self, query: str, summary: str, urls: List[str] = None) -> str:
        """Format as CSV and return file path."""
        try:
            tmp = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".csv",
                mode="w",
                newline='',
                encoding="utf-8"
            )
            
            writer = csv.writer(tmp)
            
            # Header
            writer.writerow(["QuickGlance Search Results"])
            writer.writerow([])
            
            # Metadata
            writer.writerow(["Query", query])
            writer.writerow(["Generated", self.timestamp])
            writer.writerow([])
            
            # Summary
            writer.writerow(["Summary"])
            writer.writerow([summary])
            writer.writerow([])
            
            # Bullet points from summary
            if summary:
                writer.writerow(["Bullet Points"])
                for line in summary.split("\n"):
                    if line.strip():
                        writer.writerow([line.strip()])
                writer.writerow([])
            
            # Sources
            if urls:
                writer.writerow(["Sources"])
                writer.writerow([])
                for i, url in enumerate(urls, 1):
                    writer.writerow([f"{i}. {url}"])
            
            tmp.close()
            logger.info(f"CSV file created: {tmp.name}")
            return tmp.name
            
        except Exception as e:
            logger.error(f"CSV formatting failed: {str(e)}")
            raise
    
    def _format_json(self, query: str, summary: str, urls: List[str] = None) -> dict:
        """Format as JSON."""
        return {
            "metadata": {
                "query": query,
                "generated": self.timestamp,
                "format": "json"
            },
            "results": {
                "summary": summary,
                "sources": urls or [],
                "summary_lines": [s.strip() for s in summary.split("\n") if s.strip()]
            }
        }
    
    def _format_markdown(self, query: str, summary: str, urls: List[str] = None) -> str:
        """Format as Markdown."""
        output = []
        output.append("# Search Results\n")
        output.append(f"**Query:** {query}\n")
        output.append(f"**Generated:** {self.timestamp}\n")
        
        output.append("## Summary\n")
        output.append(summary)
        
        if urls:
            output.append("\n## Sources\n")
            for i, url in enumerate(urls, 1):
                output.append(f"{i}. [{url}]({url})")
        
        return "\n".join(output)
    
    def _save_text(self, content: str) -> str:
        """Save text to temporary file."""
        try:
            tmp = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".txt",
                mode="w",
                encoding="utf-8"
            )
            tmp.write(content)
            tmp.close()
            logger.info(f"Text file created: {tmp.name}")
            return tmp.name
        except Exception as e:
            logger.error(f"Text file creation failed: {str(e)}")
            raise
    
    def _save_json(self, data: dict) -> str:
        """Save JSON to temporary file."""
        try:
            tmp = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".json",
                mode="w",
                encoding="utf-8"
            )
            json.dump(data, tmp, indent=2)
            tmp.close()
            logger.info(f"JSON file created: {tmp.name}")
            return tmp.name
        except Exception as e:
            logger.error(f"JSON file creation failed: {str(e)}")
            raise
    
    def _save_markdown(self, content: str) -> str:
        """Save Markdown to temporary file."""
        try:
            tmp = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".md",
                mode="w",
                encoding="utf-8"
            )
            tmp.write(content)
            tmp.close()
            logger.info(f"Markdown file created: {tmp.name}")
            return tmp.name
        except Exception as e:
            logger.error(f"Markdown file creation failed: {str(e)}")
            raise
    
    def generate_audio(self, text: str, output_path: str = None) -> dict:
        """
        Generate audio from text using gTTS (optional).
        
        Args:
            text: Text to convert to speech
            output_path: Where to save audio file
            
        Returns:
            Dictionary with audio info
        """
        try:
            from gtts import gTTS
            
            logger.info(f"Generating audio for {len(text)} characters")
            
            # Truncate if too long
            if len(text) > 500:
                text = text[:500] + "..."
            
            # Generate audio
            tts = gTTS(text, lang='en', slow=False)
            
            # Save to file
            if not output_path:
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                output_path = tmp.name
            
            tts.save(output_path)
            
            logger.info(f"Audio file created: {output_path}")
            
            return {
                "status": "success",
                "file": output_path,
                "mime_type": "audio/mpeg"
            }
            
        except ImportError:
            logger.warning("gTTS not installed - audio generation skipped")
            return {
                "status": "skipped",
                "error": "gTTS library not installed"
            }
        except Exception as e:
            logger.error(f"Audio generation failed: {str(e)}")
            return {
                "status": "failed",
                "error": str(e)
            }
