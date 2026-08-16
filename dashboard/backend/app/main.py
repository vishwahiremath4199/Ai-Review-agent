"""
FastAPI application for ReviewPilot dashboard backend.
"""

from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os

from .database import get_db, init_db
from .models import User
from .schemas import LoginSchema, TokenSchema
from .auth import verify_password, get_password_hash, create_access_token
from .routers import reviews, rules, analytics

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="ReviewPilot Dashboard API",
    description="API for AI Code Review agent results and rule management",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(reviews.router)
app.include_router(rules.router)
app.include_router(analytics.router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/auth/login", response_model=TokenSchema)
async def login(
    credentials: LoginSchema,
    db: Session = Depends(get_db),
):
    """
    Authenticate user and return JWT token.
    In production, use a proper auth flow (OAuth, OIDC, etc.)
    """
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create token
    access_token = create_access_token(data={"sub": user.email})
    
    return TokenSchema(access_token=access_token)


@app.post("/auth/register", response_model=TokenSchema, status_code=201)
async def register(
    credentials: LoginSchema,
    db: Session = Depends(get_db),
):
    """
    Register a new user (simplified - in production, add validation/verification).
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == credentials.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create new user
    user = User(
        email=credentials.email,
        password_hash=get_password_hash(credentials.password),
    )
    db.add(user)
    db.commit()
    
    # Return token for immediate login
    access_token = create_access_token(data={"sub": user.email})
    return TokenSchema(access_token=access_token)


@app.get("/")
async def root():
    """Root endpoint with API documentation."""
    return {
        "name": "ReviewPilot Dashboard API",
        "docs": "/docs",
        "openapi": "/openapi.json",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=os.environ.get("ENV") == "development",
    )
