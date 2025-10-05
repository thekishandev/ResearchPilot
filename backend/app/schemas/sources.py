"""
Source schemas for MCP source management
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SourceStatus(BaseModel):
    """Status of a single MCP source"""
    name: str = Field(..., description="Source name")
    status: str = Field(..., description="Status (healthy, unhealthy, degraded)")
    response_time: Optional[float] = Field(None, description="Response time in seconds")
    last_check: Optional[datetime] = Field(None, description="Last health check timestamp")
    error: Optional[str] = Field(None, description="Error message if unhealthy")


class SourceHealth(BaseModel):
    """Overall health summary of all sources"""
    total_sources: int = Field(..., description="Total number of sources")
    healthy_sources: int = Field(..., description="Number of healthy sources")
    unhealthy_sources: int = Field(..., description="Number of unhealthy sources")
    health_percentage: float = Field(..., description="Percentage of healthy sources")
