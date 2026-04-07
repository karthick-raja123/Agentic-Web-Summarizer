"""
FastAPI Backend for Enhanced Multi-Agent System with PDF Support
Wraps the LangGraph enhanced system with REST API endpoints
Supports web queries and PDF summarization
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import sys
import json
from datetime import datetime
from pathlib import Path
import PyPDF2
import tempfile
import logging
import uuid
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="QuickGlance API",
    description="Enhanced multi-agent summarization system with PDF support",
    version="1.0.0"
)

# Add CORS middleware for Streamlit and web access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import the enhanced system and metrics
sys.path.insert(0, str(Path(__file__).parent))
try:
    from langgraph_enhanced_multi_agent_system import create_graph
    GRAPH = create_graph()
    logger.info("✓ Enhanced LangGraph system loaded")
except Exception as e:
    logger.error(f"✗ Failed to load LangGraph: {e}")
    GRAPH = None

# Import metrics
try:
    from metrics import get_metrics_collector, TokenEstimator
    METRICS = get_metrics_collector()
    logger.info("✓ Metrics system initialized")
except Exception as e:
    logger.error(f"✗ Failed to load metrics: {e}")
    METRICS = None

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class LatencyMetricsResponse(BaseModel):
    """Response model for latency metrics"""
    search_time: float = 0.0
    scrape_time: float = 0.0
    rank_time: float = 0.0
    summarize_time: float = 0.0
    reflection_time: float = 0.0
    total_time: float = 0.0

class TokenMetricsResponse(BaseModel):
    """Response model for token usage metrics"""
    input_tokens: int = 0
    output_tokens: int = 0
    search_query_tokens: int = 0
    content_tokens: int = 0
    total_tokens: int = 0
    estimated_cost: float = 0.0

class SummarizeRequest(BaseModel):
    """Request model for web/text summarization"""
    query: str
    max_iterations: int = 2
    quality_threshold: float = 0.6

class SummarizeResponse(BaseModel):
    """Response model for summarization"""
    query: str
    summary: str
    bullet_points: List[str]
    quality_score: float
    sources_used: int
    processing_time: float
    status: str
    request_id: str
    latency_metrics: Optional[LatencyMetricsResponse] = None
    token_metrics: Optional[TokenMetricsResponse] = None

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    system: str
    version: str

class MetricsResponse(BaseModel):
    """Response model for metrics dashboard"""
    period_hours: int = 24
    total_requests: int = 0
    success_rate: float = 0.0
    avg_latency_seconds: float = 0.0
    median_latency_seconds: float = 0.0
    avg_search_time: float = 0.0
    avg_scrape_time: float = 0.0
    avg_summarize_time: float = 0.0
    avg_tokens: int = 0
    total_tokens: int = 0
    avg_quality_score: float = 0.0
    request_types: Dict[str, int] = {}
    status_distribution: Dict[str, int] = {}

class PDFSummarizeResponse(BaseModel):
    """Response model for PDF summarization"""
    filename: str
    original_length: int
    extracted_text_length: int
    summary: str
    bullet_points: List[str]
    processing_time: float
    status: str
    request_id: str = ""
    latency_metrics: Optional[LatencyMetricsResponse] = None
    token_metrics: Optional[TokenMetricsResponse] = None

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from PDF file
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        Extracted text from PDF
    """
    try:
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            logger.info(f"PDF has {len(pdf_reader.pages)} pages")
            
            for page_num, page in enumerate(pdf_reader.pages[:10], 1):  # Limit to first 10 pages
                try:
                    page_text = page.extract_text()
                    text += page_text + "\n"
                    logger.info(f"Extracted page {page_num}")
                except Exception as e:
                    logger.warning(f"Error extracting page {page_num}: {e}")
        
        return text
    except Exception as e:
        logger.error(f"PDF extraction error: {e}")
        raise

def summarize_text(text: str, custom_query: str = None) -> dict:
    """
    Summarize text using the enhanced system
    
    Args:
        text: Text to summarize
        custom_query: Optional custom query for summarization
        
    Returns:
        Summarization result
    """
    if not GRAPH:
        raise HTTPException(status_code=500, detail="LangGraph system not initialized")
    
    query = custom_query or "Please summarize this content"
    
    # Prepare initial state
    initial_state = {
        "query": query,
        "user_intent": "Summarize the provided text",
        "query_expansion": {"original_query": "", "expanded_queries": [], "angles": []},
        "expanded_queries": [],
        "plan": [],
        "plan_iterations": 0,
        "search_queries": [],
        "search_results": [],
        "urls": [],
        "backup_urls": [],
        "failed_urls": [],
        "scraped_content": [],
        "scraping_iterations": 0,
        "ranked_content": [],
        "content_rankings": {},
        "deduplicated_content": [],
        "duplicate_groups": {},
        "content_chunks": [],
        "chunk_summaries": [],
        "evaluations": [],
        "valid_content": [],
        "raw_summary": "",
        "summary": "",
        "summary_bullets": [],
        "reflection_score": 0.0,
        "reflection_notes": "",
        "needs_improvement": False,
        "iterations": 0,
        "max_iterations": 1,
        "timestamps": {},
        "messages": [],
        "current_agent": "start",
        "next_agent": "expansion",
        "error": None,
        "performance_metrics": {}
    }
    
    # Pre-populate with text for direct summarization (skip search)
    # Create a fake "scraped content" entry
    initial_state["scraped_content"] = [{
        "url": "internal://input",
        "title": "User Provided Text",
        "content": text[:5000],  # Limit to 5000 chars
        "length": len(text),
        "quality_score": 0.9,
        "source_type": "internal",
        "relevance_score": 1.0,
        "combined_rank": 0.95,
        "rank_position": 1,
        "is_duplicate": False,
        "chunk_count": max(1, len(text) // 1000)
    }]
    
    # Skip expansion and search, go directly to ranking
    initial_state["next_agent"] = "ranker"
    
    try:
        start_time = datetime.now()
        result = GRAPH.invoke(initial_state)
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        return {
            "summary": result.get("summary", "No summary generated"),
            "bullet_points": result.get("summary_bullets", []),
            "quality_score": result.get("reflection_score", 0.0),
            "sources_used": len(result.get("valid_content", [])),
            "processing_time": processing_time,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Summarization error: {e}")
        raise HTTPException(status_code=500, detail=f"Summarization error: {str(e)}")

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """
    Health check endpoint
    
    Returns system status and version information
    """
    return HealthResponse(
        status="healthy" if GRAPH else "degraded",
        timestamp=datetime.now().isoformat(),
        system="QuickGlance Enhanced API",
        version="1.0.0"
    )

@app.get("/metrics", response_model=MetricsResponse, tags=["Metrics"])
async def get_metrics(hours: int = 24):
    """
    Get metrics dashboard data
    
    Args:
        hours: Time period for metrics (default 24 hours)
        
    Returns:
        Performance metrics and statistics
    """
    if not METRICS:
        raise HTTPException(status_code=500, detail="Metrics system not initialized")
    
    try:
        summary = METRICS.get_performance_summary(hours=hours)
        return MetricsResponse(**summary)
    except Exception as e:
        logger.error(f"Metrics retrieval error: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving metrics: {str(e)}")

@app.post("/summarize", response_model=SummarizeResponse, tags=["Summarization"])
async def summarize_web(request: SummarizeRequest):
    """
    Summarize web query using enhanced multi-agent system
    
    Args:
        query: Topic to search and summarize
        max_iterations: Maximum retry iterations (1-3)
        quality_threshold: Quality score threshold (0.0-1.0)
        
    Returns:
        Summarization result with metrics
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    if not GRAPH:
        raise HTTPException(status_code=500, detail="System not initialized")
    
    # Generate unique request ID for tracking
    request_id = str(uuid.uuid4())
    
    # Start metrics tracking
    if METRICS:
        METRICS.start_request(request_id, request.query, "web")
    
    try:
        start_time = datetime.now()
        
        # Prepare initial state for web query
        initial_state = {
            "query": request.query,
            "user_intent": f"Find and summarize information about: {request.query}",
            "query_expansion": {"original_query": "", "expanded_queries": [], "angles": []},
            "expanded_queries": [],
            "plan": [],
            "plan_iterations": 0,
            "search_queries": [],
            "search_results": [],
            "urls": [],
            "backup_urls": [],
            "failed_urls": [],
            "scraped_content": [],
            "scraping_iterations": 0,
            "ranked_content": [],
            "content_rankings": {},
            "deduplicated_content": [],
            "duplicate_groups": {},
            "content_chunks": [],
            "chunk_summaries": [],
            "evaluations": [],
            "valid_content": [],
            "raw_summary": "",
            "summary": "",
            "summary_bullets": [],
            "reflection_score": 0.0,
            "reflection_notes": "",
            "needs_improvement": False,
            "iterations": 0,
            "max_iterations": min(3, max(1, request.max_iterations)),
            "timestamps": {},
            "messages": [],
            "current_agent": "start",
            "next_agent": "expansion",
            "error": None,
            "performance_metrics": {}
        }
        
        # Run the enhanced system
        result = GRAPH.invoke(initial_state)
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        quality_score = result.get("reflection_score", 0.0)
        sources_used = len(result.get("valid_content", []))
        summary_text = result.get("summary", "No summary generated")
        bullet_points = result.get("summary_bullets", [])
        
        # Estimate tokens
        input_tokens = TokenEstimator.estimate_tokens(request.query)
        output_tokens = TokenEstimator.estimate_output_tokens(summary_text, bullet_points)
        content_tokens = TokenEstimator.estimate_content_tokens(result.get("valid_content", []))
        
        # Record metrics
        if METRICS:
            METRICS.record_token_usage(request_id, input_tokens, output_tokens, content_tokens=content_tokens)
            METRICS.record_total_time(request_id, processing_time)
            METRICS.record_success(request_id, quality_score, sources_used)
        
        # Build latency and token response objects
        latency_metrics = LatencyMetricsResponse(total_time=processing_time)
        token_metrics = TokenMetricsResponse(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            content_tokens=content_tokens,
            total_tokens=input_tokens + output_tokens + content_tokens
        )
        
        return SummarizeResponse(
            request_id=request_id,
            query=request.query,
            summary=summary_text,
            bullet_points=bullet_points,
            quality_score=quality_score,
            sources_used=sources_used,
            processing_time=processing_time,
            status="success",
            latency_metrics=latency_metrics,
            token_metrics=token_metrics
        )
        
    except Exception as e:
        logger.error(f"Summarization endpoint error: {e}")
        if METRICS:
            METRICS.record_failure(request_id, str(e))
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/summarize/pdf", response_model=PDFSummarizeResponse, tags=["Summarization"])
async def summarize_pdf(file: UploadFile = File(...)):
    """
    Summarize uploaded PDF file
    
    Args:
        file: PDF file to upload and summarize
        
    Returns:
        PDF summarization result with metrics
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    if file.size and file.size > 50 * 1024 * 1024:  # 50MB limit
        raise HTTPException(status_code=413, detail="File too large (max 50MB)")
    
    # Generate unique request ID
    request_id = str(uuid.uuid4())
    
    # Start metrics tracking
    if METRICS:
        METRICS.start_request(request_id, f"PDF: {file.filename}", "pdf")
    
    temp_file = None
    try:
        start_time = datetime.now()
        
        # Save uploaded file temporarily
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        content = await file.read()
        temp_file.write(content)
        temp_file.close()
        
        # Extract text from PDF
        logger.info(f"Extracting text from PDF: {file.filename}")
        pdf_text = extract_text_from_pdf(temp_file.name)
        
        if not pdf_text.strip():
            raise HTTPException(status_code=422, detail="No text could be extracted from PDF")
        
        original_length = len(content)
        extracted_length = len(pdf_text)
        
        logger.info(f"Extracted {extracted_length} characters from {file.filename}")
        
        # Summarize extracted text
        logger.info("Summarizing PDF text...")
        summary_result = summarize_text(
            pdf_text,
            custom_query=f"Summarize the key points from this document: {file.filename}"
        )
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        quality_score = summary_result.get("quality_score", 0.0)
        sources_used = summary_result.get("sources_used", 0)
        summary_text = summary_result.get("summary", "")
        bullet_points = summary_result.get("bullet_points", [])
        
        # Estimate tokens
        input_tokens = TokenEstimator.estimate_tokens(pdf_text)
        output_tokens = TokenEstimator.estimate_output_tokens(summary_text, bullet_points)
        
        # Record metrics
        if METRICS:
            METRICS.record_token_usage(request_id, input_tokens, output_tokens)
            METRICS.record_total_time(request_id, processing_time)
            METRICS.record_success(request_id, quality_score, sources_used)
        
        # Build latency and token response objects
        latency_metrics = LatencyMetricsResponse(total_time=processing_time)
        token_metrics = TokenMetricsResponse(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens
        )
        
        return PDFSummarizeResponse(
            request_id=request_id,
            filename=file.filename,
            original_length=original_length,
            extracted_text_length=extracted_length,
            summary=summary_text,
            bullet_points=bullet_points,
            processing_time=processing_time,
            status="success",
            latency_metrics=latency_metrics,
            token_metrics=token_metrics
        )
        
    except HTTPException:
        if METRICS:
            METRICS.record_failure(request_id, "HTTP Exception")
        raise
    except Exception as e:
        logger.error(f"PDF summarization error: {e}")
        if METRICS:
            METRICS.record_failure(request_id, str(e))
        raise HTTPException(status_code=500, detail=f"PDF processing error: {str(e)}")
    finally:
        # Cleanup temp file
        if temp_file and os.path.exists(temp_file.name):
            try:
                os.unlink(temp_file.name)
                logger.info("Temporary file cleaned up")
            except Exception as e:
                logger.warning(f"Could not delete temp file: {e}")

@app.get("/docs", tags=["Documentation"])
async def api_docs():
    """
    API documentation endpoint
    Redirects to interactive Swagger UI
    """
    return {"message": "Visit /docs for interactive API documentation"}

# ============================================================================
# BACKGROUND TASKS
# ============================================================================

@app.post("/summarize/pdf/async", tags=["Summarization"])
async def summarize_pdf_async(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    """
    Async PDF summarization with background processing
    
    Args:
        file: PDF file to upload
        background_tasks: FastAPI background tasks
        
    Returns:
        Job status with task ID
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    # In production, save to database and return task ID
    return {
        "status": "processing",
        "task_id": "task_" + datetime.now().isoformat().replace(":", "_"),
        "filename": file.filename,
        "message": "PDF is being processed. Check back later with task_id."
    }

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions gracefully"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }
    )

# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/", tags=["Info"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "QuickGlance Enhanced Summarization API",
        "version": "1.0.0",
        "description": "Multi-agent enhanced summarization with PDF support",
        "endpoints": {
            "health": "/health",
            "web_summarization": "/summarize",
            "pdf_summarization": "/summarize/pdf",
            "documentation": "/docs"
        },
        "status": "healthy" if GRAPH else "degraded"
    }

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    logger.info(f"🚀 Starting FastAPI server on {host}:{port}")
    logger.info("📚 API docs available at http://localhost:8000/docs")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )
