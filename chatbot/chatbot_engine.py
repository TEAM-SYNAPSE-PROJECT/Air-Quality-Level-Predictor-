"""
Chatbot Interface & Session Manager.
Maintains chat conversation history and handles conversational queries.
"""
from typing import List, Dict, Any
from chatbot.response_generator import generate_chatbot_response

def process_chat_message(user_input: str, history: List[Dict[str, str]], live_context: Dict[str, Any]) -> str:
    """Processes user input, generates contextual response, and returns assistant text."""
    if not user_input.strip():
        return "Please enter an environmental or air quality question."
    return generate_chatbot_response(user_input, live_context)
