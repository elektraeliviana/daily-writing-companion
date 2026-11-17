"""
AI Writing Partner Service using Google Gemini API (`google-genai`).
Handles dynamic prompt generation and constructive writing critique.
"""

import os
from typing import Optional, Tuple
from config.settings import GEMINI_API_KEY


class AIService:
    """Service for interacting with Google Gemini API."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", GEMINI_API_KEY)
        self._client = None

    def _get_client(self):
        """Initializes and returns the Gemini client if API key is present."""
        if not self.api_key:
            return None

        if self._client is None:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"Error initializing Gemini client: {e}")
                return None
        return self._client

    def set_api_key(self, api_key: str) -> None:
        """Updates the API key and resets the client."""
        self.api_key = api_key.strip()
        self._client = None

    def test_connection(self) -> Tuple[bool, str]:
        """Tests if the configured API key is valid."""
        if not self.api_key:
            return False, "API key is missing. Please enter a valid Gemini API key."

        client = self._get_client()
        if not client:
            return False, "Failed to initialize Gemini client."

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents="Hello, reply with the word 'Connected' if you can read this.",
            )
            if response and response.text:
                return True, "Successfully connected to Gemini API!"
            return False, "Empty response received from Gemini."
        except Exception as e:
            return False, f"Connection error: {str(e)}"

    def generate_prompt(self, category: str = "journal", mood: Optional[str] = None) -> Tuple[bool, str]:
        """
        Generates an inspiring writing prompt based on category and mood.
        """
        client = self._get_client()
        if not client:
            return False, "Gemini API key is not configured. Please add it in Settings."

        mood_context = f" The writer is currently feeling: {mood}." if mood else ""
        system_instruction = (
            "You are an empathetic, imaginative writing mentor. "
            "Generate exactly ONE compelling, thought-provoking writing prompt (1 to 2 sentences max). "
            "Do not include quotes, preamble, or explanations—just the prompt text."
        )

        user_prompt = f"Category: {category}.{mood_context} Give me a fresh, creative writing prompt."

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"{system_instruction}\n\n{user_prompt}",
            )
            text = response.text.strip().strip('"')
            return True, text
        except Exception as e:
            return False, f"Failed to generate prompt: {str(e)}"

    def get_writing_feedback(self, text: str, category: str = "journal", prompt_used: str = "") -> Tuple[bool, str]:
        """
        Provides constructive, encouraging feedback and reflection questions on the user's writing.
        """
        client = self._get_client()
        if not client:
            return False, "Gemini API key is not configured. Please add it in Settings."

        if not text or len(text.strip().split()) < 3:
            return False, "Please write at least a few sentences before asking for feedback."

        prompt_context = f"The prompt was: '{prompt_used}'\n" if prompt_used else ""

        system_instruction = (
            "You are a supportive, insightful writing mentor. "
            "Analyze the user's short writing piece. "
            "Provide encouraging feedback in 3 concise sections:\n"
            "1. 🌟 **What Shines**: Highlight a vivid image, emotional truth, or strong sentence.\n"
            "2. 💡 **Gentle Suggestions**: A vocabulary or stylistic thought to consider.\n"
            "3. 🤔 **Reflection Question**: One deep question to inspire deeper thought or further writing.\n"
            "Keep the entire feedback warm, supportive, and under 150 words."
        )

        user_content = f"{prompt_context}Writing genre: {category}\nUser's writing:\n{text}"

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"{system_instruction}\n\n{user_content}",
            )
            return True, response.text.strip()
        except Exception as e:
            return False, f"Failed to get AI feedback: {str(e)}"
