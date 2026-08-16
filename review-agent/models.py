"""
Pydantic models for ReviewPilot review results and data structures.
"""

from pydantic import BaseModel
from typing import Optional, Literal


class ReviewComment(BaseModel):
    """A single review comment on a specific file/line."""
    file: str
    line: int
    category: Literal[
        "security", "bug-risk", "code-quality", "testing", "style", "database", "frontend"
    ]
    severity: Literal["critical", "warning", "suggestion"]
    explanation: str
    suggested_fix: Optional[str] = None


class ReviewSummary(BaseModel):
    """Overall summary of a review."""
    verdict: str
    critical_count: int
    warning_count: int
    suggestion_count: int


class ReviewResult(BaseModel):
    """Complete review result for a PR."""
    pr_number: int
    repo: str
    summary: ReviewSummary
    comments: list[ReviewComment]
    llm_cost_usd: Optional[float] = None
    latency_seconds: Optional[float] = None


class Rule(BaseModel):
    """A single rule block from review-rules.yaml."""
    match: str
    category: str
    checks: list[str]


class RuleSet(BaseModel):
    """The complete set of review rules."""
    version: int
    general_instructions: str
    rules: list[Rule]
    severity_guidance: Optional[dict[str, str]] = None
