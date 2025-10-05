"""
Research model - Database schema
"""
from sqlalchemy import Column, String, DateTime, JSON, Float, Text
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Research(Base):
    """Research query and results"""
    __tablename__ = "research"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    query = Column(Text, nullable=False)
    status = Column(String, nullable=False, default="pending")  # pending, processing, completed, failed
    sources = Column(JSON, default=list)
    results = Column(JSON, default=list)
    synthesis = Column(Text, nullable=True)
    credibility_score = Column(Float, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<Research(id={self.id}, query={self.query[:50]}...)>"
