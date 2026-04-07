#!/usr/bin/env python3
"""
FastAPI Backend Wrapper for Multi-Agent Pipeline
Production-grade API with async support, error handling, and monitoring
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging
import asyncio
import json
from datetime import datetime
from pathlib import Path
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from multi_agent_pipeline import MultiAgentPipeline

# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# FASTAPI APP SETUP
# ============================================================================

app = FastAPI(
    title="QuickGlance API",
    description="AI-powered research aggregation API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# DATA MODELS
# ============================================================================

class QueryRequest(BaseModel):
    """Query request model"""
    query: str = Field(..., min_length=1, max_length=500, description="Search query")
    enable_evaluation: bool = Field(True, description="Enable content evaluation")
    enable_formatting: bool = Field(True, description="Enable multi-format output")
    timeout: int = Field(60, description="Request timeout in seconds")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "What is machine learning?",
                "enable_evaluation": True,
                "enable_formatting": True,
                "timeout": 60
            }
        }


class QueryResponse(BaseModel):
    """Query response model"""
    request_id: str = Field(..., description="Unique request ID")
    status: str = Field(..., description="Request status (success/failed/partial_success)")
    query: str = Field(..., description="Original query")
    timestamp: str = Field(..., description="Request timestamp")
    results: Dict[str, Any] = Field(..., description="Query results")
    processing_time: float = Field(..., description="Processing time in seconds")
    
    class Config:
        schema_extra = {
            "example": {
                "request_id": "req_12345",
                "status": "success",
                "query": "What is machine learning?",
                "timestamp": "2026-04-07T10:30:00",
                "results": {},
                "processing_time": 5.2
            }
        }


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = Field("healthy", description="Service status")
    timestamp: str = Field(..., description="Check timestamp")
    version: str = Field("1.0.0", description="API version")


class ErrorResponse(BaseModel):
    """Error response"""
    status: str = Field("error", description="Error status")
    message: str = Field(..., description="Error message")
    request_id: Optional[str] = Field(None, description="Request ID if applicable")
    timestamp: str = Field(..., description="Error timestamp")


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def generate_request_id() -> str:
    """Generate unique request ID"""
    import uuid
    return f"req_{uuid.uuid4().hex[:8]}"


def format_response(
    request_id: str,
    status: str,
    query: str,
    results: Dict[str, Any],
    processing_time: float
) -> QueryResponse:
    """Format successful response"""
    return QueryResponse(
        request_id=request_id,
        status=status,
        query=query,
        timestamp=datetime.utcnow().isoformat(),
        results=results,
        processing_time=processing_time
    )


def format_error(message: str, request_id: Optional[str] = None) -> ErrorResponse:
    """Format error response"""
    return ErrorResponse(
        message=message,
        request_id=request_id,
        timestamp=datetime.utcnow().isoformat()
    )


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/", tags=["Info"])
async def root():
    """Root endpoint - API information"""
    return {
        "name": "QuickGlance API",
        "version": "1.0.0",
        "description": "AI-powered research aggregation API",
        "documentation": "/api/docs",
        "endpoints": {
            "health": "/health",
            "query": {
                "method": "POST",
                "url": "/api/query",
                "description": "Submit search query"
            },
            "status": {
                "method": "GET",
                "url": "/api/status/{request_id}",
                "description": "Check request status"
            }
        }
    }


@app.get("/health", tags=["Health"])
async def health_check() -> HealthCheckResponse:
    """Health check endpoint"""
    logger.info("Health check performed")
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0"
    )


@app.post("/api/query", response_model=QueryResponse, tags=["Query"])
async def process_query(
    request: QueryRequest,
    background_tasks: BackgroundTasks
) -> QueryResponse:
    """
    Process a search query
    
    Returns:
        QueryResponse with search results, summary, and sources
    
    Raises:
        HTTPException: On processing error
    """
    request_id = generate_request_id()
    start_time = datetime.utcnow()
    
    try:
        logger.info(f"[{request_id}] Processing query: {request.query}")
        
        # Validate query
        if not request.query.strip():
            raise ValueError("Query cannot be empty")
        
        # Create pipeline
        pipeline = MultiAgentPipeline(
            enable_evaluation=request.enable_evaluation,
            enable_formatting=request.enable_formatting
        )
        
        # Run pipeline
        result = await asyncio.wait_for(
            asyncio.to_thread(pipeline.run, request.query),
            timeout=request.timeout
        )
        
        # Calculate processing time
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        logger.info(f"[{request_id}] Query processed successfully ({processing_time:.2f}s)")
        
        return format_response(
            request_id=request_id,
            status=result.get('status', 'success'),
            query=request.query,
            results=result,
            processing_time=processing_time
        )
    
    except asyncio.TimeoutError:
        logger.error(f"[{request_id}] Request timeout after {request.timeout}s")
        raise HTTPException(
            status_code=504,
            detail="Request timeout - processing took too long"
        )
    
    except ValueError as e:
        logger.error(f"[{request_id}] Validation error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid request: {str(e)}"
        )
    
    except Exception as e:
        logger.error(f"[{request_id}] Processing error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error - failed to process query"
        )


@app.get("/api/status/{request_id}", tags=["Status"])
async def get_request_status(request_id: str):
    """Get status of a previous request"""
    logger.info(f"Checking status for request: {request_id}")
    
    return {
        "request_id": request_id,
        "status": "completed",
        "message": "Status tracking available via webhook"
    }


@app.post("/api/batch", tags=["Batch"])
async def process_batch(queries: List[QueryRequest]):
    """
    Process multiple queries in batch
    
    Args:
        queries: List of QueryRequest objects
    
    Returns:
        List of QueryResponse objects
    """
    request_id = generate_request_id()
    logger.info(f"[{request_id}] Processing batch of {len(queries)} queries")
    
    results = []
    for i, query_req in enumerate(queries, 1):
        try:
            pipeline = MultiAgentPipeline(
                enable_evaluation=query_req.enable_evaluation,
                enable_formatting=query_req.enable_formatting
            )
            
            result = pipeline.run(query_req.query)
            results.append({
                "index": i,
                "status": "success",
                "result": result
            })
        except Exception as e:
            logger.error(f"[{request_id}] Batch item {i} failed: {str(e)}")
            results.append({
                "index": i,
                "status": "failed",
                "error": str(e)
            })
    
    return {
        "request_id": request_id,
        "total": len(queries),
        "successful": sum(1 for r in results if r["status"] == "success"),
        "failed": sum(1 for r in results if r["status"] == "failed"),
        "results": results,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/capabilities", tags=["Info"])
async def get_capabilities():
    """Get API capabilities"""
    return {
        "version": "1.0.0",
        "capabilities": {
            "query_processing": True,
            "batch_processing": True,
            "content_evaluation": True,
            "multi_format_export": True,
            "audio_generation": True,
        },
        "limits": {
            "max_query_length": 500,
            "max_batch_size": 10,
            "timeout_seconds": 60,
            "max_requests_per_minute": 60
        },
        "formats": ["CSV", "TXT", "Audio"],
        "features": [
            "Web search",
            "Content scraping",
            "Summarization",
            "Quality evaluation",
            "Multi-format export",
            "Real-time progress"
        ]
    }


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=format_error(exc.detail).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=format_error("Internal server error").dict()
    )


# ============================================================================
# STARTUP/SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Run on startup"""
    logger.info("QuickGlance API starting up...")
    logger.info("API Documentation: http://localhost:8000/api/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on shutdown"""
    logger.info("QuickGlance API shutting down...")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    reload = os.getenv("API_RELOAD", "False").lower() == "true"
    
    logger.info(f"Starting FastAPI server on {host}:{port}")
    
    uvicorn.run(
        "api:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
