"""
Comprehensive test suite for Customer Support API
Tests all functionality including edge cases and error handling
"""
import requests
import json
import time
from uuid import UUID, uuid4

BASE_URL = "http://localhost:8000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name):
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}Test: {name}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")

def print_pass(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_fail(message):
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.YELLOW}ℹ {message}{Colors.END}")

# Test 1: Health Check
def test_health_check():
    print_test("Health Check")
    response = requests.get(f"{BASE_URL}/health")
    data = response.json()
    
    print_info(f"Status Code: {response.status_code}")
    print_info(f"Response: {json.dumps(data, indent=2)}")
    
    assert response.status_code == 200, "Status code should be 200"
    assert "status" in data, "Response should contain 'status'"
    assert "database" in data, "Response should contain 'database'"
    assert data["database"] == "connected", "Database should be connected"
    assert data["status"] == "healthy", "Status should be healthy"
    
    print_pass("Health check passed")
    return True

# Test 2: Root Endpoint
def test_root_endpoint():
    print_test("Root Endpoint")
    response = requests.get(f"{BASE_URL}/")
    data = response.json()
    
    print_info(f"Status Code: {response.status_code}")
    
    assert response.status_code == 200, "Status code should be 200"
    assert "message" in data, "Should have message"
    assert "endpoints" in data, "Should list endpoints"
    
    print_pass("Root endpoint passed")
    return True

# Test 3: Create New Chat (No Session ID)
def test_create_new_chat():
    print_test("Create New Chat (No Session ID)")
    payload = {"user_message": "What are your business hours?"}
    response = requests.post(f"{BASE_URL}/api/chat", json=payload)
    data = response.json()
    
    print_info(f"Status Code: {response.status_code}")
    print_info(f"Session ID: {data.get('session_id')}")
    print_info(f"Response: {data.get('response')[:100]}...")
    
    assert response.status_code == 200, "Status code should be 200"
    assert "session_id" in data, "Should return session_id"
    assert "response" in data, "Should return AI response"
    assert "is_escalated" in data, "Should indicate escalation status"
    assert data["is_escalated"] == False, "Should not be escalated"
    
    print_pass("New chat creation passed")
    return data["session_id"]

# Test 4: Continue Existing Chat
def test_continue_chat(session_id):
    print_test("Continue Existing Chat")
    payload = {
        "session_id": session_id,
        "user_message": "What about your pricing?"
    }
    response = requests.post(f"{BASE_URL}/api/chat", json=payload)
    data = response.json()
    
    print_info(f"Status Code: {response.status_code}")
    print_info(f"Session ID matches: {data['session_id'] == session_id}")
    
    assert response.status_code == 200, "Status code should be 200"
    assert data["session_id"] == session_id, "Session ID should match"
    assert len(data["response"]) > 0, "Should have a response"
    
    print_pass("Continue chat passed")
    return True

# Test 5: Multiple Messages in Conversation
def test_multiple_messages(session_id):
    print_test("Multiple Messages in Same Conversation")
    messages = [
        "How can I contact you?",
        "Do you offer refunds?",
        "What payment methods do you accept?"
    ]
    
    for i, msg in enumerate(messages, 1):
        payload = {"session_id": session_id, "user_message": msg}
        response = requests.post(f"{BASE_URL}/api/chat", json=payload)
        data = response.json()
        
        assert response.status_code == 200, f"Message {i} should succeed"
        print_info(f"Message {i}/{len(messages)} sent successfully")
    
    print_pass("Multiple messages passed")
    return True

# Test 6: Get Conversation History
def test_get_conversation_history(session_id):
    print_test("Get Conversation History")
    response = requests.get(f"{BASE_URL}/api/conversations/{session_id}")
    data = response.json()
    
    print_info(f"Status Code: {response.status_code}")
    print_info(f"Message Count: {data['message_count']}")
    print_info(f"Status: {data['status']}")
    
    assert response.status_code == 200, "Status code should be 200"
    assert data["session_id"] == session_id, "Session ID should match"
    assert "history" in data, "Should have history"
    assert data["message_count"] >= 8, f"Should have at least 8 messages (4 exchanges), got {data['message_count']}"
    
    # Verify message structure
    history = data["history"]
    for msg in history:
        assert "role" in msg, "Message should have role"
        assert "content" in msg, "Message should have content"
        assert "timestamp" in msg, "Message should have timestamp"
        assert msg["role"] in ["user", "assistant", "system"], "Role should be valid"
    
    # Verify alternating roles
    user_messages = [m for m in history if m["role"] == "user"]
    assistant_messages = [m for m in history if m["role"] == "assistant"]
    
    print_info(f"User messages: {len(user_messages)}")
    print_info(f"Assistant messages: {len(assistant_messages)}")
    
    assert len(user_messages) == len(assistant_messages), "Should have equal user and assistant messages"
    
    print_pass("Conversation history retrieval passed")
    return True

# Test 7: Escalation Detection
def test_escalation():
    print_test("Escalation Detection")
    escalation_messages = [
        "This is urgent! I need help now!",
        "I want to speak to your manager immediately!",
        "This is an emergency situation!",
        "I'm going to file a complaint!"
    ]
    
    for msg in escalation_messages:
        payload = {"user_message": msg}
        response = requests.post(f"{BASE_URL}/api/chat", json=payload)
        data = response.json()
        
        print_info(f"Testing: '{msg[:50]}...'")
        assert response.status_code == 200, "Status code should be 200"
        assert data["is_escalated"] == True, f"Should be escalated for: {msg}"
        assert data["status"] == "escalated", "Status should be 'escalated'"
    
    print_pass("Escalation detection passed")
    return True

# Test 8: Non-Escalation Messages
def test_non_escalation():
    print_test("Non-Escalation Messages")
    normal_messages = [
        "Thank you for your help",
        "What are your opening hours?",
        "I have a question about your product"
    ]
    
    for msg in normal_messages:
        payload = {"user_message": msg}
        response = requests.post(f"{BASE_URL}/api/chat", json=payload)
        data = response.json()
        
        assert response.status_code == 200, "Status code should be 200"
        assert data["is_escalated"] == False, f"Should NOT be escalated for: {msg}"
    
    print_pass("Non-escalation detection passed")
    return True

# Test 9: Invalid Session ID
def test_invalid_session():
    print_test("Invalid Session ID")
    fake_uuid = str(uuid4())
    payload = {
        "session_id": fake_uuid,
        "user_message": "Hello"
    }
    response = requests.post(f"{BASE_URL}/api/chat", json=payload)
    
    print_info(f"Status Code: {response.status_code}")
    
    assert response.status_code == 404, "Should return 404 for invalid session"
    
    print_pass("Invalid session handling passed")
    return True

# Test 10: Empty Message
def test_empty_message():
    print_test("Empty Message Validation")
    payload = {"user_message": ""}
    response = requests.post(f"{BASE_URL}/api/chat", json=payload)
    
    print_info(f"Status Code: {response.status_code}")
    
    assert response.status_code == 422, "Should return 422 for empty message"
    
    print_pass("Empty message validation passed")
    return True

# Test 11: List Conversations
def test_list_conversations():
    print_test("List All Conversations")
    response = requests.get(f"{BASE_URL}/api/conversations?limit=10")
    data = response.json()
    
    print_info(f"Status Code: {response.status_code}")
    print_info(f"Number of conversations: {len(data)}")
    
    assert response.status_code == 200, "Status code should be 200"
    assert isinstance(data, list), "Should return a list"
    assert len(data) > 0, "Should have at least one conversation"
    
    # Check structure of first conversation
    if data:
        conv = data[0]
        assert "session_id" in conv, "Should have session_id"
        assert "created_at" in conv, "Should have created_at"
        assert "message_count" in conv, "Should have message_count"
        assert "status" in conv, "Should have status"
    
    print_pass("List conversations passed")
    return True

# Test 12: Pagination
def test_pagination():
    print_test("Conversation Pagination")
    
    # Get first page
    response1 = requests.get(f"{BASE_URL}/api/conversations?limit=2&offset=0")
    data1 = response1.json()
    
    # Get second page
    response2 = requests.get(f"{BASE_URL}/api/conversations?limit=2&offset=2")
    data2 = response2.json()
    
    print_info(f"First page: {len(data1)} conversations")
    print_info(f"Second page: {len(data2)} conversations")
    
    assert response1.status_code == 200, "First page should succeed"
    assert response2.status_code == 200, "Second page should succeed"
    
    # Ensure pages are different (if there are enough conversations)
    if len(data1) > 0 and len(data2) > 0:
        assert data1[0]["session_id"] != data2[0]["session_id"], "Pages should have different content"
    
    print_pass("Pagination passed")
    return True

# Test 13: Status Filter
def test_status_filter():
    print_test("Status Filtering")
    
    # Filter by active status
    response = requests.get(f"{BASE_URL}/api/conversations?status=active&limit=10")
    data = response.json()
    
    print_info(f"Active conversations: {len(data)}")
    
    assert response.status_code == 200, "Status code should be 200"
    
    # Verify all returned conversations have active status
    for conv in data:
        assert conv["status"] == "active", "All conversations should have 'active' status"
    
    print_pass("Status filtering passed")
    return True

# Test 14: Concurrent Sessions
def test_concurrent_sessions():
    print_test("Concurrent Sessions")
    
    # Create multiple sessions simultaneously
    sessions = []
    for i in range(3):
        payload = {"user_message": f"Hello from session {i+1}"}
        response = requests.post(f"{BASE_URL}/api/chat", json=payload)
        data = response.json()
        
        assert response.status_code == 200, f"Session {i+1} creation should succeed"
        sessions.append(data["session_id"])
    
    print_info(f"Created {len(sessions)} concurrent sessions")
    
    # Verify all sessions are unique
    assert len(sessions) == len(set(sessions)), "All session IDs should be unique"
    
    print_pass("Concurrent sessions passed")
    return sessions

# Test 15: Session Isolation
def test_session_isolation(sessions):
    print_test("Session Isolation")
    
    # Send different messages to each session
    for i, session_id in enumerate(sessions):
        payload = {
            "session_id": session_id,
            "user_message": f"Unique message for session {i+1}"
        }
        response = requests.post(f"{BASE_URL}/api/chat", json=payload)
        assert response.status_code == 200, f"Message to session {i+1} should succeed"
    
    # Verify each session has its own history
    for i, session_id in enumerate(sessions):
        response = requests.get(f"{BASE_URL}/api/conversations/{session_id}")
        data = response.json()
        
        user_messages = [m for m in data["history"] if m["role"] == "user"]
        assert any(f"session {i+1}" in m["content"] for m in user_messages), \
            f"Session {i+1} should have its unique message"
    
    print_pass("Session isolation passed")
    return True

# Test 16: Performance Test
def test_performance():
    print_test("Performance Test (10 rapid requests)")
    
    session_id = None
    start_time = time.time()
    
    for i in range(10):
        payload = {"user_message": f"Performance test message {i+1}"}
        if session_id:
            payload["session_id"] = session_id
        
        response = requests.post(f"{BASE_URL}/api/chat", json=payload)
        data = response.json()
        
        if not session_id:
            session_id = data["session_id"]
        
        assert response.status_code == 200, f"Request {i+1} should succeed"
    
    end_time = time.time()
    duration = end_time - start_time
    avg_time = duration / 10
    
    print_info(f"Total time: {duration:.2f} seconds")
    print_info(f"Average time per request: {avg_time:.3f} seconds")
    
    assert avg_time < 1.0, f"Average response time should be under 1 second, got {avg_time:.3f}s"
    
    print_pass("Performance test passed")
    return True

# Run all tests
def run_all_tests():
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}AI Customer Support Bot - Comprehensive Test Suite{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    
    tests = []
    failures = []
    
    try:
        # Basic tests
        tests.append(("Health Check", test_health_check))
        tests.append(("Root Endpoint", test_root_endpoint))
        
        # Chat functionality
        session_id = None
        test_name = "Create New Chat"
        try:
            session_id = test_create_new_chat()
            print_pass(f"{test_name} completed")
        except AssertionError as e:
            failures.append((test_name, str(e)))
            print_fail(f"{test_name} failed: {e}")
        
        if session_id:
            tests.append(("Continue Chat", lambda: test_continue_chat(session_id)))
            tests.append(("Multiple Messages", lambda: test_multiple_messages(session_id)))
            tests.append(("Get History", lambda: test_get_conversation_history(session_id)))
        
        # Escalation tests
        tests.append(("Escalation Detection", test_escalation))
        tests.append(("Non-Escalation", test_non_escalation))
        
        # Error handling
        tests.append(("Invalid Session", test_invalid_session))
        tests.append(("Empty Message", test_empty_message))
        
        # List and filter
        tests.append(("List Conversations", test_list_conversations))
        tests.append(("Pagination", test_pagination))
        tests.append(("Status Filter", test_status_filter))
        
        # Advanced tests
        concurrent_sessions = None
        test_name = "Concurrent Sessions"
        try:
            concurrent_sessions = test_concurrent_sessions()
            print_pass(f"{test_name} completed")
        except AssertionError as e:
            failures.append((test_name, str(e)))
            print_fail(f"{test_name} failed: {e}")
        
        if concurrent_sessions:
            tests.append(("Session Isolation", lambda: test_session_isolation(concurrent_sessions)))
        
        tests.append(("Performance Test", test_performance))
        
        # Run remaining tests
        for test_name, test_func in tests:
            try:
                test_func()
                print_pass(f"{test_name} completed")
            except AssertionError as e:
                failures.append((test_name, str(e)))
                print_fail(f"{test_name} failed: {e}")
            except Exception as e:
                failures.append((test_name, f"Unexpected error: {e}"))
                print_fail(f"{test_name} failed with error: {e}")
        
        # Summary
        print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
        print(f"{Colors.BLUE}Test Summary{Colors.END}")
        print(f"{Colors.BLUE}{'='*60}{Colors.END}")
        
        total_tests = len(tests) + 2  # +2 for manual tests
        passed_tests = total_tests - len(failures)
        
        print_info(f"Total Tests: {total_tests}")
        print_pass(f"Passed: {passed_tests}")
        
        if failures:
            print_fail(f"Failed: {len(failures)}")
            print(f"\n{Colors.RED}Failed Tests:{Colors.END}")
            for test_name, error in failures:
                print(f"  {Colors.RED}✗ {test_name}: {error}{Colors.END}")
        else:
            print(f"\n{Colors.GREEN}🎉 All tests passed!{Colors.END}")
        
        print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
        
        return len(failures) == 0
        
    except requests.exceptions.ConnectionError:
        print_fail("Could not connect to API. Make sure server is running on http://localhost:8000")
        return False
    except Exception as e:
        print_fail(f"Unexpected error during test execution: {e}")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)