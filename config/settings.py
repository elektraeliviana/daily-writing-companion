"""
Application Configuration and Settings.
Uses python-dotenv to securely load environment variables.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Base Directory: root of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file from project root if it exists
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# Database Configuration
DEFAULT_DB_PATH = BASE_DIR / "companion.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")

# Gemini AI API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# App Appearance & Defaults
APP_THEME = os.getenv("APP_THEME", "dark")  # "dark" or "light"
DEFAULT_DAILY_WORD_GOAL = int(os.getenv("DEFAULT_DAILY_WORD_GOAL", "200"))

# Default Prompts Dictionary (curated defaults)
DEFAULT_PROMPTS = {
    "story": [
        "Write about a door that only opens once a year.",
        "A character finds a letter addressed to them from ten years in the future.",
        "Someone discovers their reflection is one second behind them.",
        "Write the last five minutes before a goodbye that matters.",
        "A stranger sits down and says, 'You probably don't remember me.'",
    ],
    "poem": [
        "Write a poem about the sound a house makes when it's empty.",
        "Describe a color that doesn't exist using only things that do.",
        "Write about waiting, without using the word 'wait'.",
        "A poem made entirely of questions.",
        "Write about something small that outlived someone.",
    ],
    "journal": [
        "What did you almost say today, but didn't?",
        "Describe today as weather.",
        "What's a small thing you're avoiding right now?",
        "Write a letter to yourself from one year ago.",
        "What did you notice today that no one else seemed to?",
    ],
}

# Standard Mood Options with display emojis
MOOD_CHOICES = [
    "😔 Struggling",
    "😐 Neutral",
    "🙂 Good",
    "😊 Great",
    "🌟 Amazing",
]
