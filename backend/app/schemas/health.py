"""
Health check schemas
"""
from pydantic import BaseModel, Field
from typing import Dict


class ComponentHealth(BaseModel):
    """Health status of a single component"""
    status: str = Field(..., description="Status (healthy, unhealthy, degraded, unconfigured)")
    message: str = Field(..., description="Status message")


class HealthCheck(BaseModel):
    """Overall system health check"""
    status: str = Field(..., description="Overall status")
    components: Dict[str, ComponentHealth] = Field(..., description="Component health statuses")
