"""
Summarize Agent - Generates summaries using Gemini LLM.
Part of the LangGraph workflow.
"""

from typing import Optional
from services.llm_service import LLMService
from utils.cleaning import chunk_text
from utils.logging_config import get_logger

logger = get_logger(__name__)


class SummarizeAgent:
    """Agent responsible for summarizing content."""
    
    def __init__(self, summary_points: int = 5, use_chunks: bool = True):
        """
        Initialize Summarize Agent.
        
        Args:
            summary_points: Number of bullet points in summary
            use_chunks: Whether to chunk content before summarization
        """
        self.llm_service = LLMService()
        self.summary_points = summary_points
        self.use_chunks = use_chunks
        logger.info(
            f"Summarize Agent initialized (points: {summary_points}, "
            f"use_chunks: {use_chunks})"
        )
    
    def execute(self, content: str) -> dict:
        """
        Summarize content.
        
        Args:
            content: Content to summarize
            
        Returns:
            Dictionary with summary
        """
        logger.info(f"SummarizeAgent.execute() called for {len(content)} characters")
        
        if not content or len(content.strip()) == 0:
            logger.warning("Empty content provided to SummarizeAgent")
            return {
                "summary": "No content to summarize.",
                "status": "failed"
            }
        
        try:
            # Estimate tokens
            token_estimate = self.llm_service.estimate_tokens(content)
            logger.info(f"Estimated tokens: {token_estimate}")
            
            # Summarize
            summary = self.llm_service.summarize(
                content,
                max_length=self.summary_points
            )
            
            logger.info(f"SummarizeAgent successfully created summary")
            
            return {
                "summary": summary,
                "status": "success",
                "token_estimate": token_estimate
            }
            
        except Exception as e:
            logger.error(f"SummarizeAgent failed: {str(e)}")
            return {
                "summary": "",
                "status": "failed",
                "error": str(e)
            }
    
    def execute_with_chunking(self, content: str, chunk_size: int = 5000) -> dict:
        """
        Summarize with chunking for large content.
        Chunks content and creates summaries, then summarizes summaries.
        
        Args:
            content: Content to summarize
            chunk_size: Size of chunks
            
        Returns:
            Dictionary with hierarchical summary
        """
        logger.info(
            f"SummarizeAgent.execute_with_chunking() called for {len(content)} chars"
        )
        
        if not content or len(content.strip()) == 0:
            logger.warning("Empty content provided to SummarizeAgent chunking")
            return {"summary": "No content to summarize.", "status": "failed"}
        
        try:
            # Chunk content
            chunks = chunk_text(content, chunk_size=chunk_size)
            logger.info(f"Content chunked into {len(chunks)} pieces")
            
            # Summarize each chunk
            chunk_summaries = []
            for i, chunk in enumerate(chunks, 1):
                logger.debug(f"Summarizing chunk {i}/{len(chunks)}")
                chunk_result = self.execute(chunk)
                if chunk_result["status"] == "success":
                    chunk_summaries.append(chunk_result["summary"])
            
            # If multiple summaries, summarize them too (meta-summary)
            if len(chunk_summaries) > 1:
                combined_summaries = "\n".join(chunk_summaries)
                logger.info("Creating meta-summary from chunk summaries")
                final_summary = self.llm_service.summarize(
                    combined_summaries,
                    max_length=self.summary_points
                )
            else:
                final_summary = chunk_summaries[0] if chunk_summaries else ""
            
            logger.info("SummarizeAgent chunking completed successfully")
            
            return {
                "summary": final_summary,
                "chunk_count": len(chunks),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"SummarizeAgent chunking failed: {str(e)}")
            return {
                "summary": "",
                "status": "failed",
                "error": str(e)
            }
