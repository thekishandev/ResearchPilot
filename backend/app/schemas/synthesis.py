"""
Structured output schemas for Cerebras synthesis
Using Pydantic for type-safe JSON schema generation
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class ConfidenceLevel(str, Enum):
    """Confidence level enum"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SourceCitation(BaseModel):
    """Individual source citation with metadata"""
    source_name: str = Field(..., description="Name of the source (e.g., 'ArXiv', 'Web Search')")
    title: Optional[str] = Field(None, description="Title of the specific result")
    url: Optional[str] = Field(None, description="URL of the source")
    confidence: float = Field(..., description="Confidence score 0-1")
    relevance: str = Field(..., description="Why this source is relevant")


class KeyFinding(BaseModel):
    """Individual key finding from research"""
    finding: str = Field(..., description="Concise finding statement")
    supporting_sources: List[str] = Field(..., description="List of source names that support this finding")
    importance: str = Field(..., description="Why this finding is important")


class ResearchSynthesis(BaseModel):
    """Structured synthesis response from Cerebras"""
    
    # Executive Summary
    summary: str = Field(
        ...,
        description="2-3 sentence executive summary of key findings"
    )
    
    # Key Findings
    key_findings: List[KeyFinding] = Field(
        ...,
        description="3-5 most important findings from research"
    )
    
    # Detailed Analysis
    detailed_analysis: str = Field(
        ...,
        description="Comprehensive analysis with full context and explanations"
    )
    
    # Source Citations
    sources: List[SourceCitation] = Field(
        ...,
        description="List of all sources used with citations"
    )
    
    # Credibility Assessment
    credibility_score: float = Field(
        ...,
        description="Overall credibility score from 0.0 to 1.0 based on source quality"
    )
    
    confidence_level: ConfidenceLevel = Field(
        ...,
        description="Overall confidence in the research findings"
    )
    
    # Follow-up Suggestions
    follow_up_questions: List[str] = Field(
        ...,
        description="3-5 suggested follow-up questions to explore further"
    )
    
    # Caveats & Limitations
    limitations: Optional[str] = Field(
        None,
        description="Any limitations or caveats about the research"
    )


def get_synthesis_schema() -> dict:
    """
    Get JSON schema for ResearchSynthesis model
    Compatible with Cerebras structured outputs API
    """
    schema = ResearchSynthesis.model_json_schema()
    
    # Ensure required properties for Cerebras strict mode
    schema["additionalProperties"] = False
    
    return schema


# Export schema dictionary for easy use in Cerebras API
SYNTHESIS_JSON_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "research_synthesis",
        "strict": True,
        "schema": get_synthesis_schema()
    }
}
