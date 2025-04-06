import os
import sys
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status, Body
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Add parent directory to path to import database module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.mongodb_client import MongoDBClient
from backend.models import DeadlineResponse, DeadlineList, UserLogin, Token, DeadlineCreate
from backend.auth import create_access_token, get_current_user

# Load environment variables
load_dotenv()

# Get API configuration from environment variables
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', '8000'))
CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
BOT_API_KEY = os.getenv('BOT_API_KEY', 'your_bot_api_key_here')

# Create FastAPI app
app = FastAPI(
    title="Eventory API",
    description="API for accessing and managing events from Discord",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MongoDB client
db_client = MongoDBClient()


@app.get("/")
async def root():
    """Root endpoint to check if the API is running"""
    return {"message": "Eventory API is running"}


# Add a public endpoint for deadlines that doesn't require authentication
@app.get("/public/deadlines", response_model=DeadlineList)
async def get_public_deadlines(
    skip: int = 0,
    limit: int = 10,
):
    """Get a list of deadlines without authentication
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
    
    Returns:
        List of deadlines
    """
    deadlines = db_client.get_deadlines(limit=limit, skip=skip)
    
    # Convert MongoDB documents to API models
    deadline_list = []
    for d in deadlines:
        # Convert MongoDB _id to string
        d["id"] = str(d.pop("_id"))
        deadline_list.append(d)
    
    return {
        "deadlines": deadline_list,
        "total": len(deadline_list),
        "skip": skip,
        "limit": limit
    }


@app.get("/deadlines", response_model=DeadlineList)
async def get_deadlines(
    skip: int = 0,
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """Get a list of deadlines
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        current_user: Current authenticated user
    
    Returns:
        List of deadlines
    """
    deadlines = db_client.get_deadlines(limit=limit, skip=skip)
    
    # Convert MongoDB documents to API models
    deadline_list = []
    for d in deadlines:
        # Convert MongoDB _id to string
        d["id"] = str(d.pop("_id"))
        deadline_list.append(d)
    
    return {
        "deadlines": deadline_list,
        "total": len(deadline_list),
        "skip": skip,
        "limit": limit
    }


# Add a public endpoint for a single deadline that doesn't require authentication
@app.get("/public/deadlines/{deadline_id}", response_model=DeadlineResponse)
async def get_public_deadline(
    deadline_id: str,
):
    """Get a specific deadline by ID without authentication
    
    Args:
        deadline_id: ID of the deadline to retrieve
    
    Returns:
        Deadline details
    """
    deadline = db_client.get_deadline_by_id(deadline_id)
    
    if not deadline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deadline not found"
        )
    
    # Convert MongoDB _id to string
    deadline["id"] = str(deadline.pop("_id"))
    
    return deadline


@app.get("/deadlines/{deadline_id}", response_model=DeadlineResponse)
async def get_deadline(
    deadline_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific deadline by ID
    
    Args:
        deadline_id: ID of the deadline to retrieve
        current_user: Current authenticated user
    
    Returns:
        Deadline details
    """
    deadline = db_client.get_deadline_by_id(deadline_id)
    
    if not deadline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deadline not found"
        )
    
    # Convert MongoDB _id to string
    deadline["id"] = str(deadline.pop("_id"))
    
    return deadline


@app.post("/bot/deadlines", status_code=status.HTTP_201_CREATED)
async def create_deadline(
    deadline: DeadlineCreate = Body(...),
    api_key: str = Body(...)
):
    """Create a new deadline from the Discord bot
    
    Args:
        deadline: Deadline information
        api_key: API key for authorization
    
    Returns:
        Created deadline ID
    """
    # Validate API key
    if api_key != BOT_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    # Convert to dict for MongoDB
    deadline_data = deadline.dict()
    
    # Save to database
    deadline_id = db_client.save_deadline(deadline_data)
    
    if not deadline_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save deadline"
        )
    
    return {"id": deadline_id, "message": "Deadline created successfully"}


@app.post("/token", response_model=Token)
async def login_for_access_token(user: UserLogin):
    """Login endpoint to get JWT token
    
    Args:
        user: User login credentials
    
    Returns:
        JWT access token
    """
    # This is a placeholder - in a real app, you would validate against a user database
    if user.username != "admin" or user.password != "password":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username})
    
    return {"access_token": access_token, "token_type": "bearer"}


# Endpoint to get a guest token for demo purposes
@app.get("/guest-token", response_model=Token)
async def get_guest_token():
    """Get a guest access token for demo purposes
    
    Returns:
        JWT access token for guest access
    """
    access_token = create_access_token(data={"sub": "guest"})
    
    return {"access_token": access_token, "token_type": "bearer"}


def main():
    """Run the FastAPI application with Uvicorn"""
    uvicorn.run(
        "backend.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=True
    )


if __name__ == "__main__":
    main() 