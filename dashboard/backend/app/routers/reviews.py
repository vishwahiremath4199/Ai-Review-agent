"""
Reviews API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from uuid import UUID
from datetime import datetime

from ..database import get_db
from ..models import Review, ReviewComment
from ..schemas import ReviewSchema, ReviewIngestSchema, ReviewCommentSchema
from ..auth import verify_token

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("", status_code=201)
async def ingest_review(
    review_data: ReviewIngestSchema,
    db: Session = Depends(get_db),
):
    """
    Ingest a new review result from the agent.
    Called by review-agent after posting to GitHub.
    """
    # Create Review record
    review = Review(
        repo=review_data.repo,
        pr_number=review_data.pr_number,
        verdict=review_data.summary.get("verdict", ""),
        critical_count=review_data.summary.get("critical_count", 0),
        warning_count=review_data.summary.get("warning_count", 0),
        suggestion_count=review_data.summary.get("suggestion_count", 0),
        llm_cost_usd=review_data.llm_cost_usd,
        latency_seconds=review_data.latency_seconds,
    )
    
    # Create ReviewComment records
    for comment_data in review_data.comments:
        comment = ReviewComment(
            review=review,
            file=comment_data.get("file", ""),
            line=comment_data.get("line", 0),
            category=comment_data.get("category", ""),
            severity=comment_data.get("severity", ""),
            explanation=comment_data.get("explanation", ""),
            suggested_fix=comment_data.get("suggested_fix"),
        )
        db.add(comment)
    
    db.add(review)
    db.commit()
    db.refresh(review)
    
    return {"id": review.id, "status": "stored"}


@router.get("", response_model=List[ReviewSchema])
async def list_reviews(
    repo: str = Query(None, description="Filter by repository"),
    severity: str = Query(None, description="Filter by minimum severity"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token),
):
    """
    List reviews, paginated and filterable.
    """
    query = db.query(Review)
    
    if repo:
        query = query.filter(Review.repo.ilike(f"%{repo}%"))
    
    if severity == "critical":
        query = query.filter(Review.critical_count > 0)
    elif severity == "warning":
        query = query.filter(Review.warning_count > 0)
    
    reviews = query.order_by(desc(Review.created_at)).offset(skip).limit(limit).all()
    return reviews


@router.get("/{review_id}", response_model=ReviewSchema)
async def get_review(
    review_id: UUID,
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token),
):
    """Get full detail of a specific review."""
    review = db.query(Review).filter(Review.id == review_id).first()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    return review


@router.delete("/{review_id}", status_code=204)
async def delete_review(
    review_id: UUID,
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token),
):
    """Delete a review and its comments."""
    review = db.query(Review).filter(Review.id == review_id).first()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    db.delete(review)
    db.commit()
