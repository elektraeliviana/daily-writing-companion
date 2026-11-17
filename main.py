"""
Daily Writing Companion - Main Application Entrypoint.
Launch with: python main.py
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.ui.app import WritingCompanionApp


def main():
    """Initializes and runs the Daily Writing Companion desktop app."""
    app = WritingCompanionApp()
    app.mainloop()


if __name__ == "__main__":
    main()
