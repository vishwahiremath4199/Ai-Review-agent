"""
Analytics API endpoints.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Dict, List

from ..database import get_db
from ..models import Review, ReviewComment
from ..schemas import AnalyticsSummarySchema
from ..auth import verify_token

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummarySchema)
async def get_analytics_summary(
    days: int = Query(30, ge=1, le=365, description="Number of days to include"),
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token),
):
    """
    Get aggregated analytics summary for the last N days.
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Count total reviews
    total_reviews = db.query(func.count(Review.id)).filter(
        Review.created_at >= cutoff_date
    ).scalar()
    
    # Average latency and cost
    avg_result = db.query(
        func.avg(Review.latency_seconds),
        func.avg(Review.llm_cost_usd)
    ).filter(Review.created_at >= cutoff_date).first()
    
    avg_latency = avg_result[0]
    avg_cost = avg_result[1]
    
    # Count issues by category
    category_counts = db.query(
        ReviewComment.category,
        func.count(ReviewComment.id).label("count")
    ).join(Review).filter(
        Review.created_at >= cutoff_date
    ).group_by(ReviewComment.category).all()
    
    issues_by_category = {cat: count for cat, count in category_counts}
    
    # Count issues by severity
    severity_counts = db.query(
        ReviewComment.severity,
        func.count(ReviewComment.id).label("count")
    ).join(Review).filter(
        Review.created_at >= cutoff_date
    ).group_by(ReviewComment.severity).all()
    
    issues_by_severity = {sev: count for sev, count in severity_counts}
    
    return AnalyticsSummarySchema(
        total_reviews=total_reviews or 0,
        avg_latency_seconds=avg_latency,
        avg_cost_usd=avg_cost,
        issues_by_category=issues_by_category,
        issues_by_severity=issues_by_severity,
    )


@router.get("/timeline")
async def get_timeline(
    metric: str = Query("reviews", description="reviews | cost | latency"),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token),
):
    """
    Get daily timeline data for charts.
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    if metric == "reviews":
        data = db.query(
            func.date(Review.created_at).label("date"),
            func.count(Review.id).label("value")
        ).filter(Review.created_at >= cutoff_date).group_by(
            func.date(Review.created_at)
        ).all()
    
    elif metric == "cost":
        data = db.query(
            func.date(Review.created_at).label("date"),
            func.sum(Review.llm_cost_usd).label("value")
        ).filter(
            Review.created_at >= cutoff_date,
            Review.llm_cost_usd != None
        ).group_by(
            func.date(Review.created_at)
        ).all()
    
    elif metric == "latency":
        data = db.query(
            func.date(Review.created_at).label("date"),
            func.avg(Review.latency_seconds).label("value")
        ).filter(
            Review.created_at >= cutoff_date,
            Review.latency_seconds != None
        ).group_by(
            func.date(Review.created_at)
        ).all()
    else:
        return {"error": "Invalid metric"}
    
    return [{"date": str(row[0]), "value": float(row[1]) if row[1] else 0} for row in data]


@router.get("/top-issues")
async def get_top_issues(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token),
):
    """
    Get the most common issue explanations across all reviews.
    """
    top_issues = db.query(
        ReviewComment.explanation,
        func.count(ReviewComment.id).label("count")
    ).group_by(ReviewComment.explanation).order_by(
        func.count(ReviewComment.id).desc()
    ).limit(limit).all()
    
    return [{"explanation": exp, "count": cnt} for exp, cnt in top_issues]
