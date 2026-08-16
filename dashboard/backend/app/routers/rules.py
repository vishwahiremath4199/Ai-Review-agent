"""
Rules API endpoints for viewing and editing review rules.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import yaml
import json
from pathlib import Path

from ..database import get_db
from ..schemas import RuleSetSchema
from ..auth import verify_token

router = APIRouter(prefix="/rules", tags=["rules"])

# Path to the rules file in the repo root
# When deployed, this should be configurable or fetched from GitHub
RULES_FILE_PATH = Path("review-rules.yaml")


@router.get("", response_model=RuleSetSchema)
async def get_rules(
    current_user: str = Depends(verify_token),
):
    """
    Get the current review rules as JSON.
    Reads from review-rules.yaml in the repository root.
    """
    if not RULES_FILE_PATH.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="review-rules.yaml not found"
        )
    
    with open(RULES_FILE_PATH, "r") as f:
        data = yaml.safe_load(f)
    
    return RuleSetSchema(**data)


@router.put("", response_model=RuleSetSchema)
async def update_rules(
    ruleset: RuleSetSchema,
    current_user: str = Depends(verify_token),
):
    """
    Update the review rules.
    Writes back to review-rules.yaml and optionally commits to repo.
    """
    # Convert Pydantic model to dict for YAML
    data = ruleset.model_dump(exclude_none=True)
    
    # Write to file
    with open(RULES_FILE_PATH, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    
    # Note: In production, you might want to:
    # 1. Commit this change to the repo via GitHub API
    # 2. Create a PR or direct commit
    # 3. Store edit history in the database
    
    return ruleset


@router.post("/validate", status_code=200)
async def validate_rules(
    ruleset: RuleSetSchema,
    current_user: str = Depends(verify_token),
):
    """Validate that a ruleset is well-formed."""
    # Basic validation - Pydantic handles most of this
    # Additional custom validation could go here
    
    return {
        "valid": True,
        "rules_count": len(ruleset.rules),
        "message": "Ruleset is valid"
    }
