"""
Unit tests for database operations
Run with: pytest test_unit.py -v
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid

from models import Base, Conversation
from db_operations import (
    create_conversation,
    get_conversation,
    update_conversation,
    get_conversation_history,
    list_conversations
)

# Test database URL (use in-memory SQLite for tests)
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture
def db_session():
    """Create a test database session"""
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(engine)

def test_create_conversation(db_session):
    """Test creating a new conversation"""
    conversation = create_conversation(db_session)
    
    assert conversation is not None
    assert conversation.session_id is not None
    assert isinstance(conversation.session_id, uuid.UUID)
    assert conversation.status == "active"
    assert conversation.history == []
    assert conversation.created_at is not None

def test_create_conversation_with_custom_id(db_session):
    """Test creating conversation with custom UUID"""
    custom_id = uuid.uuid4()
    conversation = create_conversation(db_session, session_id=custom_id)
    
    assert conversation.session_id == custom_id

def test_get_conversation(db_session):
    """Test retrieving a conversation"""
    # Create a conversation
    created = create_conversation(db_session)
    
    # Retrieve it
    retrieved = get_conversation(db_session, created.session_id)
    
    assert retrieved is not None
    assert retrieved.session_id == created.session_id

def test_get_nonexistent_conversation(db_session):
    """Test retrieving a conversation that doesn't exist"""
    fake_id = uuid.uuid4()
    result = get_conversation(db_session, fake_id)
    
    assert result is None

def test_update_conversation(db_session):
    """Test updating conversation with messages"""
    # Create conversation
    conversation = create_conversation(db_session)
    
    # Add first message
    msg1 = {
        "role": "user",
        "content": "Hello",
        "timestamp": datetime.utcnow().isoformat()
    }
    updated = update_conversation(db_session, conversation.session_id, msg1)
    
    assert updated is not None
    assert len(updated.history) == 1
    assert updated.history[0]["content"] == "Hello"
    
    # Add second message
    msg2 = {
        "role": "assistant",
        "content": "Hi there!",
        "timestamp": datetime.utcnow().isoformat()
    }
    updated = update_conversation(db_session, conversation.session_id, msg2)
    
    assert len(updated.history) == 2
    assert updated.history[1]["content"] == "Hi there!"

def test_update_conversation_with_status(db_session):
    """Test updating conversation status"""
    conversation = create_conversation(db_session)
    
    msg = {"role": "user", "content": "Urgent!"}
    updated = update_conversation(
        db_session,
        conversation.session_id,
        msg,
        status="escalated"
    )
    
    assert updated.status == "escalated"

def test_get_conversation_history(db_session):
    """Test retrieving conversation history"""
    conversation = create_conversation(db_session)
    
    # Add messages
    messages = [
        {"role": "user", "content": "Message 1"},
        {"role": "assistant", "content": "Response 1"},
        {"role": "user", "content": "Message 2"}
    ]
    
    for msg in messages:
        update_conversation(db_session, conversation.session_id, msg)
    
    # Get history
    history = get_conversation_history(db_session, conversation.session_id)
    
    assert history is not None
    assert len(history) == 3
    assert history[0]["content"] == "Message 1"
    assert history[2]["content"] == "Message 2"

def test_list_conversations(db_session):
    """Test listing conversations"""
    # Create multiple conversations
    conv1 = create_conversation(db_session)
    conv2 = create_conversation(db_session)
    conv3 = create_conversation(db_session)
    
    # List all
    conversations = list_conversations(db_session, limit=10)
    
    assert len(conversations) == 3

def test_list_conversations_pagination(db_session):
    """Test conversation pagination"""
    # Create 5 conversations
    for _ in range(5):
        create_conversation(db_session)
    
    # Get first page
    page1 = list_conversations(db_session, limit=2, offset=0)
    assert len(page1) == 2
    
    # Get second page
    page2 = list_conversations(db_session, limit=2, offset=2)
    assert len(page2) == 2
    
    # Ensure different conversations
    assert page1[0].session_id != page2[0].session_id

def test_list_conversations_by_status(db_session):
    """Test filtering conversations by status"""
    # Create conversations with different statuses
    conv1 = create_conversation(db_session)
    update_conversation(db_session, conv1.session_id, {"role": "user", "content": "test"}, status="active")
    
    conv2 = create_conversation(db_session)
    update_conversation(db_session, conv2.session_id, {"role": "user", "content": "urgent"}, status="escalated")
    
    # Filter by active
    active = list_conversations(db_session, status="active")
    assert len(active) >= 1
    assert all(c.status == "active" for c in active)
    
    # Filter by escalated
    escalated = list_conversations(db_session, status="escalated")
    assert len(escalated) >= 1
    assert all(c.status == "escalated" for c in escalated)

def test_message_timestamps(db_session):
    """Test that messages have timestamps"""
    conversation = create_conversation(db_session)
    
    # Add message without timestamp
    msg = {"role": "user", "content": "Test"}
    updated = update_conversation(db_session, conversation.session_id, msg)
    
    # Should automatically add timestamp
    assert "timestamp" in updated.history[0]
    assert updated.history[0]["timestamp"] is not None

def test_conversation_updated_at(db_session):
    """Test that updated_at changes when conversation is updated"""
    conversation = create_conversation