"""
Pydantic schemas for FastAPI request/response validation.
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class ReviewCommentSchema(BaseModel):
    """Review comment in API responses."""
    id: UUID
    file: str
    line: int
    category: str
    severity: str
    explanation: str
    suggested_fix: Optional[str] = None
    
    class Config:
        from_attributes = True


class ReviewSchema(BaseModel):
    """Review in API responses."""
    id: UUID
    repo: str
    pr_number: int
    verdict: str
    critical_count: int
    warning_count: int
    suggestion_count: int
    llm_cost_usd: Optional[float] = None
    latency_seconds: Optional[float] = None
    created_at: datetime
    comments: List[ReviewCommentSchema] = []
    
    class Config:
        from_attributes = True


class ReviewIngestSchema(BaseModel):
    """Schema for ingesting review results from the agent."""
    pr_number: int
    repo: str
    summary: dict  # {verdict, critical_count, warning_count, suggestion_count}
    comments: List[dict]  # List of comment dicts
    llm_cost_usd: Optional[float] = None
    latency_seconds: Optional[float] = None


class RuleSchema(BaseModel):
    """A single rule in the ruleset."""
    match: str
    category: str
    checks: List[str]


class RuleSetSchema(BaseModel):
    """The complete ruleset for the dashboard UI."""
    version: int
    general_instructions: str
    rules: List[RuleSchema]
    severity_guidance: Optional[dict] = None


class AnalyticsSummarySchema(BaseModel):
    """Aggregated analytics summary."""
    total_reviews: int
    avg_latency_seconds: Optional[float]
    avg_cost_usd: Optional[float]
    issues_by_category: dict  # {category: count}
    issues_by_severity: dict  # {severity: count}


class LoginSchema(BaseModel):
    """Login request."""
    email: EmailStr
    password: str


class TokenSchema(BaseModel):
    """Login response with JWT token."""
    access_token: str
    token_type: str = "bearer"
