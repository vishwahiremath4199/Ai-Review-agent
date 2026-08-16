"""
SQLAlchemy database models for ReviewPilot dashboard.
"""

from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

Base = declarative_base()


class Review(Base):
    """Stores aggregated review results for a PR."""
    __tablename__ = "reviews"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    repo = Column(String(255), nullable=False, index=True)
    pr_number = Column(Integer, nullable=False)
    verdict = Column(String(1000), nullable=False)
    critical_count = Column(Integer, default=0)
    warning_count = Column(Integer, default=0)
    suggestion_count = Column(Integer, default=0)
    llm_cost_usd = Column(Float, nullable=True)
    latency_seconds = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    comments = relationship("ReviewComment", back_populates="review", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Review(repo={self.repo}, pr={self.pr_number}, created={self.created_at})>"


class ReviewComment(Base):
    """Individual review comments on specific files/lines."""
    __tablename__ = "review_comments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    review_id = Column(UUID(as_uuid=True), ForeignKey("reviews.id"), nullable=False)
    file = Column(String(500), nullable=False)
    line = Column(Integer, nullable=False)
    category = Column(String(50), nullable=False)  # security, bug-risk, code-quality, etc.
    severity = Column(String(20), nullable=False)  # critical, warning, suggestion
    explanation = Column(Text, nullable=False)
    suggested_fix = Column(Text, nullable=True)
    
    # Relationships
    review = relationship("Review", back_populates="comments")
    
    def __repr__(self):
        return f"<ReviewComment(file={self.file}, line={self.line}, severity={self.severity})>"


class User(Base):
    """Simple user model for JWT authentication."""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<User(email={self.email})>"
