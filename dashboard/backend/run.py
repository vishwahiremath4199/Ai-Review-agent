#!/usr/bin/env python
"""Backend startup script"""
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

# Set environment variables
os.environ.setdefault('DATABASE_URL', 'sqlite:///./reviewpilot.db')
os.environ.setdefault('JWT_SECRET', 'dev-secret-key-change-in-production')
os.environ.setdefault('CORS_ORIGINS', 'http://localhost:5173')
os.environ.setdefault('ENV', 'development')

if __name__ == "__main__":
    # Initialize database
    from app.database import init_db
    print("Initializing database...")
    try:
        init_db()
        print("✓ Database initialized\n")
    except Exception as e:
        print(f"Database init warning: {e}\n")
    
    # Start server
    import uvicorn
    print("Starting FastAPI server on http://0.0.0.0:8000")
    print("API Docs: http://localhost:8000/docs\n")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
