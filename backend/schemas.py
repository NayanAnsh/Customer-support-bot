from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    # session_id: Optional[uuid.UUID] = Field(None, description="Optional session ID. If not provided, a new session will be created.")
    # user_message: str = Field(..., min_length=1, description="User's message text")
    session_id: Optional[uuid.UUID] = None
    user_message: str
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_message": "What are your business hours?"
            }
        }

class Message(BaseModel):
    """Model for a single message in conversation history"""
    role: str = Field(..., description="Role of the message sender (user/assistant/system)")
    content: str = Field(..., description="Message content")
    timestamp: str = Field(..., description="ISO format timestamp")
    
class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    session_id: uuid.UUID = Field(..., description="Session ID for the conversation")
    response: str = Field(..., description="AI assistant's response")
    is_escalated: bool = Field(False, description="Whether the query was escalated")
    status: str = Field("active", description="Conversation status")
    summary: Optional[str] = None # <-- ADD THIS LINE

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "response": "Our business hours are Monday to Friday, 9 AM to 5 PM EST.",
                "is_escalated": False,
                "status": "active"
            }
        }

class ConversationHistory(BaseModel):
    """Model for full conversation history"""
    session_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    status: str
    history: List[Dict[str, Any]]
    message_count: int
    
    class Config:
        from_attributes = True

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    
class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    database: str