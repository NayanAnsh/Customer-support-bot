# 🤖 AI Customer Support Bot

A **smart, AI-powered customer support chatbot** designed to efficiently handle user queries using **Retrieval-Augmented Generation (RAG)**. It maintains conversational context, retrieves relevant answers from a knowledge base, and intelligently escalates unresolved queries to human agents.

---

## 🌟 Features

* 🧠 **Intelligent Responses** – Powered by Google’s **Gemini Pro** model for accurate and natural language understanding.
* 💬 **Session Management** – Maintains chat history and user context throughout the conversation.
* 📚 **Knowledge Base Integration (RAG)** – Retrieves answers from a predefined FAQ dataset (`faqs.json`).
* 🚨 **Smart Escalation** – Escalates complex queries to human agents with a summarized conversation context.
* ⚙️ **Robust Backend** – Built with **Python** and **FastAPI** for speed and scalability.
* 🐳 **Dockerized** – Easy to deploy using **Docker** and **Docker Compose**.

---

## 📁 Project Structure

```
/
├── server/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI application and endpoints
│   │   ├── models.py           # SQLAlchemy database models
│   │   ├── schemas.py          # Pydantic validation models
│   │   ├── database.py         # DB config and session management
│   │   ├── db_operations.py    # Database CRUD operations
│   │   ├── ai_service.py       # Core AI logic and LLM interactions
│   │   ├── faq_service.py      # Knowledge base search logic
│   │   └── prompts.py          # Central LLM prompt templates
│   ├── data/
│   │   └── faqs.json           # FAQ knowledge base
│   ├── tests/
│   │   └── test_api_phase3.py  # Automated tests
│   ├── .env                    # Environment variables
│   └── requirements.txt        # Python dependencies
├── client/                     # (Optional frontend)
├── docker-compose.yml          # Docker Compose configuration
└── README.md                   # This file
```

---

## 🚀 Getting Started

### 🧩 Prerequisites

* [Docker](https://www.docker.com/get-started)
* [Docker Compose](https://docs.docker.com/compose/)

### 🛠️ Setup Instructions

1. **Clone the repository**

   ```bash
   git clone <your-repo-url>
   cd <repository-folder>/server
   ```

2. **Add environment variables**
   Create a `.env` file inside `server/` and add your Gemini API key:

   ```bash
   GEMINI_API_KEY="YOUR_GOOGLE_AI_API_KEY"
   ```

3. **Run with Docker Compose**
   From the root directory:

   ```bash
   docker-compose up --build
   ```

   The API will be live at **[http://localhost:8000](http://localhost:8000)**.

---

## 🧠 Prompt Engineering Strategy

This project uses a **three-stage triage system** to ensure fast, relevant, and accurate responses.

### 🔹 Stage 1 – Small Talk Filtering

Quickly detects and responds to casual messages (e.g., “Hi”, “Thanks”) without calling the LLM.

### 🔹 Stage 2 – RAG with LLM Validation

1. Searches `faqs.json` for related context.
2. Validates the relevance using a Yes/No LLM prompt.
3. If valid, uses the context to generate the final answer.

### 🔹 Stage 3 – Intelligent Escalation

If no suitable context is found, the bot creates a short summary and escalates to a human agent.

---

## 🧩 Core Prompt Templates

### ✅ Context Validation Prompt

```python
CONTEXT_VALIDATION_PROMPT_TEMPLATE = """
You are an AI assistant that determines if a provided context is relevant for answering a user's question.

User Question: "{question}"
Provided Context: "{context}"

Does the provided context contain enough information to directly answer the user's question?
Respond with only "YES" or "NO".
"""
```

### 📚 Retrieval-Augmented Generation (RAG) Prompt

```python
RAG_PROMPT_TEMPLATE = """
{system_prompt}

Based on the following conversation history and provided context, answer the user's question.

**Conversation History:**
{chat_history}

**Knowledge Base Context:**
{context}

**User's Question:**
{question}

**Your Answer:**
"""
```

### 🧾 Summarization Prompt

```python
SUMMARIZATION_PROMPT_TEMPLATE = """
Based on the following conversation history, provide a concise, one-sentence summary of the user's issue for a human agent.

**Conversation History:**
{chat_history}

**Summary:**
"""
```

---

## 🧪 Testing

This project includes automated tests using **pytest**.

Run tests using:

```bash
pytest -v -s server/tests/test_api_phase3.py
```

Ensure that all Docker containers are running before executing tests.

---

## 🧰 Tech Stack

* **Backend:** FastAPI (Python)
* **Database:** PostgreSQL (via SQLAlchemy)
* **AI Model:** Google Gemini Pro
* **Containerization:** Docker & Docker Compose
* **Testing:** pytest

---

## 📜 License

This project is licensed under the **MIT License**.

---

## 💡 Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

---

### ⭐ If you like this project, give it a star on GitHub!
