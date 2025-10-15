from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from models import Conversation
from datetime import datetime
import uuid
from typing import Optional, Dict, List

def create_conversation(db: Session, session_id: Optional[uuid.UUID] = None) -> Conversation:
    """
    Create a new conversation in the database.
    
    Args:
        db: Database session
        session_id: Optional UUID for the session. If not provided, a new one is generated.
    
    Returns:
        Conversation object
    """
    if session_id is None:
        session_id = uuid.uuid4()
    
    conversation = Conversation(
        session_id=session_id,
        history=[],
        status="active"
    )
    
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    
    return conversation

def get_conversation(db: Session, session_id: uuid.UUID) -> Optional[Conversation]:
    """
    Retrieve a conversation by session_id.
    
    Args:
        db: Database session
        session_id: UUID of the session
    
    Returns:
        Conversation object or None if not found
    """
    return db.query(Conversation).filter(
        Conversation.session_id == session_id
    ).first()

def update_conversation(
    db: Session,
    session_id: uuid.UUID,
    new_message: Dict,
    status: Optional[str] = None
) -> Optional[Conversation]:
    """
    Update conversation history with a new message.
    
    Args:
        db: Database session
        session_id: UUID of the session
        new_message: Dictionary containing message data (role, content, timestamp)
        status: Optional status update (active, escalated, resolved)
    
    Returns:
        Updated Conversation object or None if not found
    """
    conversation = get_conversation(db, session_id)
    
    if not conversation:
        return None
    
    # Add timestamp to message if not present
    if "timestamp" not in new_message:
        new_message["timestamp"] = datetime.utcnow().isoformat()
    
    # Get current history and append new message
    history = list(conversation.history) if conversation.history else []
    history.append(new_message)
    
    # Update the conversation with new history
    conversation.history = history
    conversation.updated_at = datetime.utcnow()
    
    # Update status if provided
    if status:
        conversation.status = status
    
    # Mark the history column as modified (important for JSONB updates)
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(conversation, "history")
    
    db.commit()
    db.refresh(conversation)
    
    return conversation

def get_conversation_history(db: Session, session_id: uuid.UUID) -> Optional[List[Dict]]:
    """
    Get the full history of a conversation.
    
    Args:
        db: Database session
        session_id: UUID of the session
    
    Returns:
        List of message dictionaries or None if conversation not found
    """
    conversation = get_conversation(db, session_id)
    
    if not conversation:
        return None
    
    return conversation.history

def delete_conversation(db: Session, session_id: uuid.UUID) -> bool:
    """
    Delete a conversation from the database.
    
    Args:
        db: Database session
        session_id: UUID of the session
    
    Returns:
        True if deleted, False if not found
    """
    conversation = get_conversation(db, session_id)
    
    if not conversation:
        return False
    
    db.delete(conversation)
    db.commit()
    
    return True

def list_conversations(
    db: Session,
    limit: int = 50,
    offset: int = 0,
    status: Optional[str] = None
) -> List[Conversation]:
    """
    List conversations with pagination and optional status filter.
    
    Args:
        db: Database session
        limit: Maximum number of conversations to return
        offset: Number of conversations to skip
        status: Optional status filter
    
    Returns:
        List of Conversation objects
    """
    query = db.query(Conversation)
    
    if status:
        query = query.filter(Conversation.status == status)
    
    return query.order_by(
        Conversation.updated_at.desc()
    ).limit(limit).offset(offset).all()