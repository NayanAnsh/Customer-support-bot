"""
Test script for the Customer Support API
Run this after starting the server to test all endpoints
"""
import requests
import json
from uuid import UUID

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test health check endpoint"""
    print("\n=== Testing Health Check ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✓ Health check passed")

def test_create_new_chat():
    """Test creating a new chat without session_id"""
    print("\n=== Testing New Chat Creation ===")
    payload = {
        "user_message": "What are your business hours?"
    }
    response = requests.post(f"{BASE_URL}/api/chat", json=payload)
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    assert response.status_code == 200
    assert "session_id" in data
    print("✓ New chat creation passed")
    return data["session_id"]

def test_continue_chat(session_id):
    """Test continuing an existing chat"""
    print("\n=== Testing Chat Continuation ===")
    payload = {
        "session_id": session_id,
        "user_message": "What about pricing?"
    }
    response = requests.post(f"{BASE_URL}/api/chat", json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✓ Chat continuation passed")

def test_get_conversation(session_id):
    """Test retrieving conversation history"""
    print("\n=== Testing Get Conversation ===")
    response = requests.get(f"{BASE_URL}/api/conversations/{session_id}")
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Message Count: {data['message_count']}")
    print(f"Status: {data['status']}")
    print(f"History: {json.dumps(data['history'], indent=2)}")
    assert response.status_code == 200
    assert data["message_count"] >= 2  # At least 2 exchanges
    print("✓ Get conversation passed")

def test_escalation():
    """Test escalation scenario"""
    print("\n=== Testing Escalation ===")
    payload = {
        "user_message": "This is urgent! I need to speak to a manager immediately!"
    }
    response = requests.post(f"{BASE_URL}/api/chat", json=payload)
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    assert response.status_code == 200
    assert data["is_escalated"] == True
    assert data["status"] == "escalated"
    print("✓ Escalation test passed")

def test_list_conversations():
    """Test listing conversations"""
    print("\n=== Testing List Conversations ===")
    response = requests.get(f"{BASE_URL}/api/conversations?limit=10")
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Number of conversations: {len(data)}")
    if data:
        print(f"First conversation: {json.dumps(data[0], indent=2, default=str)}")
    assert response.status_code == 200
    print("✓ List conversations passed")

def test_invalid_session():
    """Test with invalid session_id"""
    print("\n=== Testing Invalid Session ===")
    payload = {
        "session_id": "00000000-0000-0000-0000-000000000000",
        "user_message": "Hello"
    }
    response = requests.post(f"{BASE_URL}/api/chat", json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 404
    print("✓ Invalid session test passed")

def run_all_tests():
    """Run all API tests"""
    print("=" * 50)
    print("Starting API Tests")
    print("=" * 50)
    
    try:
        # Test health check
        test_health_check()
        
        # Test chat flow
        session_id = test_create_new_chat()
        test_continue_chat(session_id)
        test_get_conversation(session_id)
        
        # Test escalation
        test_escalation()
        
        # Test listing
        test_list_conversations()
        
        # Test error handling
        test_invalid_session()
        
        print("\n" + "=" * 50)
        print("✓ All tests passed successfully!")
        print("=" * 50)
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
    except requests.exceptions.ConnectionError:
        print("\n✗ Could not connect to API. Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")

if __name__ == "__main__":
    run_all_tests()