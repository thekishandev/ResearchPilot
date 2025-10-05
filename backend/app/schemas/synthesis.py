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
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")
    relevance: str = Field(..., description="Why this source is relevant")
    
    class Config:
        json_schema_extra = {
            "example": {
                "source_name": "ArXiv",
                "title": "Quantum Computing Advances in 2024",
                "url": "https://arxiv.org/abs/2024.12345",
                "confidence": 0.95,
                "relevance": "Directly discusses recent quantum computing breakthroughs"
            }
        }


class KeyFinding(BaseModel):
    """Individual key finding from research"""
    finding: str = Field(..., description="Concise finding statement")
    supporting_sources: List[str] = Field(..., description="List of source names that support this finding")
    importance: str = Field(..., description="Why this finding is important")
    
    class Config:
        json_schema_extra = {
            "example": {
                "finding": "Quantum error correction rates improved by 10x in 2024",
                "supporting_sources": ["ArXiv", "Nature", "Web Search"],
                "importance": "Makes practical quantum computing more feasible"
            }
        }


class ResearchSynthesis(BaseModel):
    """Structured synthesis response from Cerebras"""
    
    # Executive Summary
    summary: str = Field(
        ...,
        description="2-3 sentence executive summary of key findings",
        min_length=50,
        max_length=500
    )
    
    # Key Findings
    key_findings: List[KeyFinding] = Field(
        ...,
        description="3-5 most important findings from research",
        min_length=3,
        max_length=7
    )
    
    # Detailed Analysis
    detailed_analysis: str = Field(
        ...,
        description="Comprehensive analysis with full context and explanations",
        min_length=200
    )
    
    # Source Citations
    sources: List[SourceCitation] = Field(
        ...,
        description="List of all sources used with citations",
        min_length=1
    )
    
    # Credibility Assessment
    credibility_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Overall credibility score based on source quality"
    )
    
    confidence_level: ConfidenceLevel = Field(
        ...,
        description="Overall confidence in the research findings"
    )
    
    # Follow-up Suggestions
    follow_up_questions: List[str] = Field(
        ...,
        description="3-5 suggested follow-up questions to explore further",
        min_length=3,
        max_length=5
    )
    
    # Caveats & Limitations
    limitations: Optional[str] = Field(
        None,
        description="Any limitations or caveats about the research"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "summary": "Quantum computing saw significant advances in 2024, with error correction rates improving 10x and new algorithms demonstrating quantum advantage in drug discovery.",
                "key_findings": [
                    {
                        "finding": "Error correction improved 10x",
                        "supporting_sources": ["ArXiv", "Nature"],
                        "importance": "Critical for practical quantum computers"
                    }
                ],
                "detailed_analysis": "The field of quantum computing...",
                "sources": [
                    {
                        "source_name": "ArXiv",
                        "title": "Quantum Error Correction 2024",
                        "url": "https://arxiv.org/...",
                        "confidence": 0.95,
                        "relevance": "Primary source for error correction advances"
                    }
                ],
                "credibility_score": 0.92,
                "confidence_level": "high",
                "follow_up_questions": [
                    "What are the specific algorithms that improved?",
                    "Which companies are leading quantum hardware development?",
                    "What are the timeline estimates for practical quantum computers?"
                ],
                "limitations": "Most findings are from academic papers; commercial applications may differ"
            }
        }


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
