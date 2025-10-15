AI Customer Support BotThis project is a sophisticated, AI-powered customer support chatbot designed to handle user queries efficiently. It leverages a Retrieval-Augmented Generation (RAG) system to answer questions based on a knowledge base, maintains conversational context, and intelligently escalates to human agents when necessary.🎯 Key FeaturesIntelligent Responses: Uses Google's Gemini Pro model to understand and respond to user queries.Session Management: Maintains conversation history and context for each user session.Knowledge Base Integration (RAG): Answers questions by retrieving relevant information from a predefined FAQ dataset.Smart Escalation: Automatically escalates conversations to a human agent when a query cannot be resolved, providing a concise summary of the issue.Robust Backend: Built with Python and FastAPI for high performance and scalability.Containerized: Fully containerized with Docker and Docker Compose for easy setup and deployment.🏗️ Project Structure/
├── server/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI application and endpoints
│   │   ├── models.py           # SQLAlchemy database models
│   │   ├── schemas.py          # Pydantic models for API validation
│   │   ├── database.py         # Database configuration and session management
│   │   ├── db_operations.py    # Database CRUD (Create, Read, Update) functions
│   │   ├── ai_service.py       # Core AI logic and LLM interaction
│   │   ├── faq_service.py      # Logic for searching the FAQ knowledge base
│   │   └── prompts.py          # Central repository for all LLM prompts
│   ├── data/
│   │   └── faqs.json           # The FAQ knowledge base
│   ├── tests/
│   │   └── test_api_phase3.py  # Automated API tests
│   ├── .env                    # Environment variables (API keys, DB URL)
│   └── requirements.txt        # Python dependencies
├── client/                     # (Optional Frontend)
├── docker-compose.yml          # Docker Compose configuration
└── README.md                   # This file
🚀 Getting StartedThe easiest way to run this project is with Docker.PrerequisitesDockerDocker ComposeRunning the ApplicationClone the repository:git clone <your-repo-url>
cd <repository-folder>/server
Configure Environment Variables:Create a file named .env in the server/ directory and add your API key:GEMINI_API_KEY="YOUR_GOOGLE_AI_API_KEY"
Build and Run with Docker Compose:From the root directory of the project, run:docker-compose up --build
This command will build the Docker images for the FastAPI application and a PostgreSQL database, and then start both services. The API will be available at http://localhost:8000.🤖 Prompt Engineering StrategyA key component of this project is its sophisticated, multi-stage approach to handling user queries. This ensures both accuracy and efficiency.The Three-Stage Triage SystemStage 1: Small Talk Filtering: The bot first checks if a user's message is a common conversational filler (e.g., "hello", "thank you"). If so, it provides a predefined response without calling the LLM, making the interaction fast and efficient.Stage 2: RAG with LLM Validation: If the message is a real query, the system searches the faqs.json knowledge base for relevant context.If potential context is found, we perform a crucial validation step. We ask the LLM a simple Yes/No question to confirm if the found context can truly answer the user's specific question. This prevents the bot from giving generic answers to specific problems.If the context is validated as relevant, it's passed to the main RAG prompt to generate a final answer.Stage 3: Intelligent Escalation: Escalation occurs if no context is found in the knowledge base, or if the LLM validation in Stage 2 fails. The bot then uses a summarization prompt to create a concise summary for the human agent, ensuring a seamless handover.Core PromptsContext Validation Prompt: This is the first check, used to prevent incorrect answers.CONTEXT_VALIDATION_PROMPT_TEMPLATE = """
You are an AI assistant that determines if a provided context is relevant for answering a user's question.

User Question: "{question}"
Provided Context: "{context}"

Does the provided context contain enough information to directly answer the user's question?
Respond with only "YES" or "NO".
"""
Retrieval-Augmented Generation (RAG) Prompt: This prompt is used when the context is validated. It combines the system's persona, conversation history, and the verified knowledge base context to generate an accurate answer.RAG_PROMPT_TEMPLATE = """
{system_prompt}

Based on the following conversation history and the provided context from our knowledge base, please answer the user's question.

**Conversation History:**
{chat_history}

**Knowledge Base Context:**
{context}

**User's Question:**
{question}

**Your Answer:**
"""
Summarization Prompt: Used during escalation to provide a clear and concise summary for the human agent.SUMMARIZATION_PROMPT_TEMPLATE = """
Based on the following conversation history, please provide a concise, one-sentence summary of the user's issue for a human agent.

**Conversation History:**
{chat_history}

**Summary:**
"""
🧪 TestingThe project includes an automated test suite using pytest. To run the tests, ensure the Docker containers are running and then execute:pytest -v -s server/tests/test_api_phase3.py
