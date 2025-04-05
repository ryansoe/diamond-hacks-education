import os
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from dotenv import load_dotenv

from backend.models import TokenData

# Load environment variables
load_dotenv()

# Get JWT settings from environment variables
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key_for_jwt_here")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# Set up OAuth2 password bearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a new JWT access token
    
    Args:
        data: Data to encode in the token
        expires_delta: Token expiration time delta
    
    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get the current user from the JWT token
    
    Args:
        token: JWT token
    
    Returns:
        dict: User information
    
    Raises:
        HTTPException: If the token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            raise credentials_exception
        
        token_data = TokenData(username=username)
    
    except JWTError:
        raise credentials_exception
    
    # In a real application, you would look up the user in your database
    # For now, we'll just return a simple user object
    user = {
        "username": token_data.username,
        "is_admin": token_data.username == "admin"
    }
    
    return user


async def get_admin_user(current_user: dict = Depends(get_current_user)):
    """Check if the current user is an admin
    
    Args:
        current_user: Current user information
    
    Returns:
        dict: User information if admin
    
    Raises:
        HTTPException: If the user is not an admin
    """
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return current_user 