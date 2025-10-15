import requests
import pytest
import uuid
import time
import threading
import concurrent.futures

# --- Test Configuration ---
BASE_URL = "http://localhost:8000/api"

@pytest.fixture
def api_url():
    """Provides the base URL for the API endpoints."""
    return BASE_URL

def test_health_check(api_url):
    """Tests if the health check endpoint is working."""
    response = requests.get(f"{api_url.replace('/api', '')}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"

def test_chat_rag_success_with_faq_question(api_url):
    """
    Tests the RAG functionality.
    Sends a question that exists in the faqs.json file and expects a direct answer.
    """
    print("\n--- Running Test: RAG Success ---")
    payload = {
        "user_message": "How do I update my account information?"
    }
    response = requests.post(f"{api_url}/chat", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    print(f"Response Body: {data}")
    
    assert "session_id" in data
    assert data["is_escalated"] is False
    assert data["status"] == "active"
    assert "summary" not in data or data["summary"] is None
    assert "profile" in data["response"].lower() or "dashboard" in data["response"].lower()

def test_chat_escalation_with_unknown_question(api_url):
    """
    Tests the escalation functionality.
    Sends a question that is NOT in faqs.json and expects an escalation.
    """
    print("\n--- Running Test: Escalation and Summarization ---")
    payload = {
        "user_message": "What are the key principles of quantum physics?"
    }
    response = requests.post(f"{api_url}/chat", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    print(f"Response Body: {data}")
    
    assert "session_id" in data
    assert data["is_escalated"] is True
    assert data["status"] == "escalated"
    assert "summary" in data and data["summary"] is not None
    assert "escalating" in data["response"].lower() or "human agent" in data["response"].lower()
    assert "quantum" in data["summary"].lower()

def test_chat_conversation_continuity_and_escalation(api_url):
    """
    Tests a multi-turn conversation that starts with a FAQ and then escalates correctly.
    """
    print("\n--- Running Test: Conversation Continuity ---")
    
    first_payload = {"user_message": "Do you offer refunds?"}
    first_response = requests.post(f"{api_url}/chat", json=first_payload)
    assert first_response.status_code == 200
    first_data = first_response.json()
    print(f"First Response Body: {first_data}")
    
    assert first_data["is_escalated"] is False
    session_id = first_data["session_id"]
    
    second_payload = {
        "session_id": session_id,
        "user_message": "My refund hasn't arrived and I'm very frustrated."
    }
    second_response = requests.post(f"{api_url}/chat", json=second_payload)
    assert second_response.status_code == 200
    second_data = second_response.json()
    print(f"Second Response Body: {second_data}")
    
    assert second_data["is_escalated"] is True
    assert second_data["status"] == "escalated"
    assert "summary" in second_data and second_data["summary"] is not None
    
    summary = second_data["summary"].lower()
    print(f"Generated Summary: {summary}")
    assert "refund" in summary
    assert "frustrated" in summary or "hasn't arrived" in summary

def test_invalid_session_id_returns_404(api_url):
    """Tests that providing a non-existent session_id returns a 404 error."""
    print("\n--- Running Test: Invalid Session ID ---")
    invalid_session_id = str(uuid.uuid4())
    payload = {"session_id": invalid_session_id, "user_message": "This should fail."}
    response = requests.post(f"{api_url}/chat", json=payload)
    
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()

def test_empty_user_message_escalates(api_url):
    """
    Tests that sending an empty or whitespace-only message is handled gracefully
    and results in a deterministic escalation.
    """
    print("\n--- Running Test: Empty User Message ---")
    payloads = [{"user_message": ""}, {"user_message": "   "}]
    for payload in payloads:
        response = requests.post(f"{api_url}/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        print(f"Response for payload '{payload}': {data}")
        assert data["is_escalated"] is True
        assert "summary" in data and "user sent an empty message" in data["summary"].lower()

def test_get_conversation_history_endpoint(api_url):
    """
    Tests that the GET /conversations/{session_id} endpoint returns the correct history.
    """
    print("\n--- Running Test: Get Conversation History ---")
    turn1_payload = {"user_message": "How can I track my order?"}
    response1 = requests.post(f"{api_url}/chat", json=turn1_payload)
    data1 = response1.json()
    session_id = data1["session_id"]
    
    time.sleep(1)

    turn2_payload = {"session_id": session_id, "user_message": "Okay, thank you!"}
    requests.post(f"{api_url}/chat", json=turn2_payload)

    history_response = requests.get(f"{api_url}/conversations/{session_id}")
    assert history_response.status_code == 200
    history_data = history_response.json()
    print(f"History Response: {history_data}")

    assert history_data["session_id"] == session_id
    assert history_data["message_count"] == 4
    assert len(history_data["history"]) == 4
    assert history_data["history"][0]["content"] == "How can I track my order?"
    assert history_data["history"][3]["role"] == "assistant"

def test_list_conversations_with_filtering_and_pagination(api_url):
    """
    Tests the GET /conversations endpoint with status filtering and pagination.
    """
    print("\n--- Running Test: List Conversations with Filters ---")
    requests.post(f"{api_url}/chat", json={"user_message": "Test for active conversation."})
    requests.post(f"{api_url}/chat", json={"user_message": "Test for escalation conversation."})
    time.sleep(1)

    escalated_list_res = requests.get(f"{api_url}/conversations?status=escalated&limit=5")
    assert escalated_list_res.status_code == 200
    escalated_list_data = escalated_list_res.json()
    assert len(escalated_list_data) >= 1
    assert all(conv["status"] == "escalated" for conv in escalated_list_data)

    active_list_res = requests.get(f"{api_url}/conversations?status=active&limit=5")
    assert active_list_res.status_code == 200
    active_list_data = active_list_res.json()
    assert len(active_list_data) >= 1
    assert all(conv["status"] == "active" for conv in active_list_data)

    paginated_res = requests.get(f"{api_url}/conversations?limit=1")
    assert paginated_res.status_code == 200
    assert len(paginated_res.json()) == 1

# --- NEW, More Extensive Tests ---

def test_small_talk_non_escalation(api_url):
    """
    Tests that common conversational fillers receive a direct response and do not escalate.
    """
    print("\n--- Running Test: Small Talk Handling ---")
    small_talk = ["hello", "hi", "thanks", "thank you", "ok", "bye"]
    for message in small_talk:
        response = requests.post(f"{api_url}/chat", json={"user_message": message})
        assert response.status_code == 200
        data = response.json()
        print(f"Input: '{message}', Response: '{data['response']}', Escalated: {data['is_escalated']}")
        assert data["is_escalated"] is False
        assert data["status"] == "active"

def test_input_with_leading_trailing_whitespace(api_url):
    """
    Ensures that whitespace is trimmed and does not affect RAG or small talk logic.
    """
    print("\n--- Running Test: Whitespace Trimming ---")
    payload = {"user_message": "  How can I reset my password?   "}
    response = requests.post(f"{api_url}/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_escalated"] is False
    assert "reset" in data["response"].lower()

def test_case_insensitivity_of_small_talk(api_url):
    """
    Ensures that small talk keywords are matched regardless of case.
    """
    print("\n--- Running Test: Case Insensitivity ---")
    payload = {"user_message": "THANK YOU VERY MUCH"}
    response = requests.post(f"{api_url}/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_escalated"] is False
    assert "welcome" in data["response"].lower()


def test_input_with_special_characters_escalates(api_url):
    """
    Tests that a message with only special characters or emojis escalates gracefully.
    """
    print("\n--- Running Test: Special Character Handling ---")
    payload = {"user_message": "🤔 emojis are great 👍"}
    response = requests.post(f"{api_url}/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_escalated"] is True
    assert "summary" in data and "emojis" in data["summary"].lower()


