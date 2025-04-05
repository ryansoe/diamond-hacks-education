from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class UserLogin(BaseModel):
    """User login model"""
    username: str
    password: str


class Token(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token data model"""
    username: Optional[str] = None


class DeadlineCreate(BaseModel):
    """Model for creating a new deadline from the bot"""
    course: str
    title: str
    description: Optional[str] = None
    due_date: datetime
    link: Optional[str] = None
    category: Optional[str] = "assignment"
    source: Optional[str] = "discord_bot"


class DeadlineResponse(BaseModel):
    """Deadline response model"""
    id: str
    title: str
    date_str: str
    raw_content: str
    channel_name: str
    guild_name: str
    message_id: int
    author_id: int
    author_name: str
    timestamp: datetime
    source_link: str


class DeadlineList(BaseModel):
    """Deadline list response model"""
    deadlines: List[Dict[str, Any]]
    total: int
    skip: int
    limit: int


class UserBase(BaseModel):
    """Base user model"""
    username: str
    email: str
    full_name: Optional[str] = None
    is_admin: bool = False


class UserCreate(UserBase):
    """User creation model"""
    password: str


class User(UserBase):
    """User response model"""
    id: str

    class Config:
        orm_mode = True 