"""
Research schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class ResearchQuery(BaseModel):
    """Request schema for research query"""
    query: str = Field(..., min_length=10, max_length=1000, description="Research query")
    sources: Optional[List[str]] = Field(
        default=None,
        description="Specific sources to use (web-search, arxiv, github, news, database, filesystem)"
    )
    max_sources: Optional[int] = Field(default=6, ge=1, le=6, description="Maximum number of sources")
    include_credibility: Optional[bool] = Field(default=True, description="Include credibility scoring")
    parent_research_id: Optional[str] = Field(default=None, description="Parent research ID for follow-up queries")
    use_tool_calling: Optional[bool] = Field(default=False, description="Use AI to intelligently select sources")


class ResearchResponse(BaseModel):
    """Response schema for research query submission"""
    id: str = Field(..., description="Research ID for tracking")
    status: str = Field(..., description="Current status")
    message: str = Field(..., description="Status message")


class SourceResult(BaseModel):
    """Result from a single source"""
    source: str
    status: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    response_time: Optional[float] = None


class ResearchStatus(BaseModel):
    """Complete research status and results"""
    id: str
    status: str
    query: str
    sources: List[str]
    results: Optional[List[SourceResult]] = None
    synthesis: Optional[str] = None
    credibility_score: Optional[float] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    
    class Config:
        from_attributes = True
