# ai_service.py

import os
from typing import List, Dict, Optional
import google.generativeai as genai
from dotenv import load_dotenv

from prompts import (
    SYSTEM_PROMPT,
    RAG_PROMPT_TEMPLATE,
    SUMMARIZATION_PROMPT_TEMPLATE,
    CONTEXT_VALIDATION_PROMPT_TEMPLATE  # Import the new prompt
)
from faq_service import faq_service

# Load environment variables from .env file
load_dotenv()

# Configure the Gemini API client
try:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    llm = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')
except KeyError:
    print("Error: GEMINI_API_KEY not found in environment variables.")
    llm = None
except Exception as e:
    print(f"An error occurred during Gemini configuration: {e}")
    llm = None

# Define conversational fillers and their responses
CONVERSATIONAL_RESPONSES = {
    "thank you": "You're welcome! Is there anything else I can help with?",
    "thanks": "You're welcome! Let me know if you need anything else.",
    "hello": "Hello! How can I help you today?",
    "hi": "Hi there! What can I assist you with?",
    "hey": "Hey! How can I help?",
    "bye": "Goodbye! Have a great day.",
    "ok": "Great. Do you have any other questions?"
}

class AIResponse:
    """A data class to structure the response from the AI service."""
    def __init__(self, content: str, is_escalated: bool, summary: Optional[str] = None):
        self.content = content
        self.is_escalated = is_escalated
        self.summary = summary


def _format_history(history: List[Dict]) -> str:
    """Formats the conversation history into a readable string for the LLM."""
    if not history:
        return "No conversation history yet."
    return "\n".join([f"{msg['role'].title()}: {msg['content']}" for msg in history])


async def get_ai_decision(history: List[Dict], user_message: str) -> AIResponse:
    """
    The main function to get a response from the AI.
    It performs a RAG search and decides whether to answer or escalate.
    """
    # --- Stage 1: Filter for Edge Cases and Conversational Filler ---
    cleaned_message = user_message.strip().lower()

    if not cleaned_message:
        summary = "User sent an empty message. No specific issue identified."
        escalation_message = (
            "It seems your message was empty. "
            "I am escalating this to a human agent to see if you need help."
        )
        return AIResponse(
            content=escalation_message,
            is_escalated=True,
            summary=summary
        )

    for trigger, response in CONVERSATIONAL_RESPONSES.items():
        if trigger in cleaned_message:
            return AIResponse(content=response, is_escalated=False)
    
    if not llm:
        return AIResponse(
            content="Our AI service is currently unavailable. A human agent will be with you shortly.",
            is_escalated=True,
            summary="AI service is offline."
        )

    # --- Stage 2: Search Knowledge Base and Validate Context ---
    context = faq_service.search_faqs(user_message)
    chat_history_str = _format_history(history)

    if context:
        # --- NEW: Use LLM to validate if the found context is truly relevant ---
        validation_prompt = CONTEXT_VALIDATION_PROMPT_TEMPLATE.format(
            question=user_message,
            context=context
        )
        try:
            validation_response = await llm.generate_content_async(validation_prompt)
            is_relevant = "yes" in validation_response.text.lower()
        except Exception as e:
            print(f"Error during context validation: {e}")
            is_relevant = False # Default to not relevant on error
        
        if is_relevant:
            # If context is validated, proceed with generating the answer
            prompt = RAG_PROMPT_TEMPLATE.format(
                system_prompt=SYSTEM_PROMPT,
                chat_history=chat_history_str,
                context=context,
                question=user_message
            )
            try:
                response = await llm.generate_content_async(prompt)
                return AIResponse(content=response.text, is_escalated=False)
            except Exception as e:
                print(f"Error generating content with RAG: {e}")
                return AIResponse(
                    content="I encountered an error trying to process your request. Please try again.",
                    is_escalated=False
                )
        # If context is found but deemed NOT relevant, we fall through to the escalation logic.

    # --- Stage 3: Escalate to Human Agent ---
    # This logic is now reached if no context is found OR if the found context is irrelevant.
    summary = await summarize_conversation(history, user_message)
    escalation_message = (
        "I couldn't find an answer to your question in my knowledge base. "
        "I am escalating this conversation to a human agent who can better assist you. "
        f"Here is a summary of your issue for the agent: '{summary}'"
    )
    return AIResponse(
        content=escalation_message,
        is_escalated=True,
        summary=summary
    )


async def summarize_conversation(history: List[Dict], latest_message: str) -> str:
    """
    Generates a concise summary of the conversation for a human agent.
    """
    if not llm:
        return "Could not generate summary because AI service is offline."

    full_history = history + [{"role": "user", "content": latest_message}]
    chat_history_str = _format_history(full_history)

    prompt = SUMMARIZATION_PROMPT_TEMPLATE.format(chat_history=chat_history_str)
    try:
        response = await llm.generate_content_async(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error during summarization: {e}")
        return "Could not generate a summary due to an error."

