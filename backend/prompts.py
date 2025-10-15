# prompts.py

SYSTEM_PROMPT = "You are a helpful and friendly AI customer support assistant. Your primary goal is to answer user questions based on the provided context. Be concise and clear in your responses."

RAG_PROMPT_TEMPLATE = """
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

SUMMARIZATION_PROMPT_TEMPLATE = """
Based on the following conversation history, please provide a concise, one-sentence summary of the user's issue for a human agent.

**Conversation History:**
{chat_history}

**Summary:**
"""

# --- NEW, STRICTER PROMPT FOR TRIAGE ---
CONTEXT_VALIDATION_PROMPT_TEMPLATE = """
You are a strict AI assistant. Your job is to determine if a general knowledge base article can solve a user's specific problem.

User's specific problem: "{question}"
General knowledge base article: "{context}"

Does the knowledge base article provide a direct solution to the user's specific problem?
- If the article is just a general policy and the user has a specific issue (like something is missing, broken, or not working), the answer is NO.
- If the article gives the exact steps to directly solve the user's problem, the answer is YES.

Respond with only "YES" or "NO".
"""

