"""
Goal Service for managing daily word goals and tracking progress.
"""

from datetime import date
from typing import Dict, Any
from sqlalchemy.orm import Session
from src.repositories.goal_repository import GoalRepository
from src.repositories.entry_repository import EntryRepository


class GoalService:
    """Business logic for checking daily word goals and progress."""

    def __init__(self, session: Session):
        self.session = session
        self.goal_repo = GoalRepository(session)
        self.entry_repo = EntryRepository(session)

    def get_daily_goal(self) -> int:
        return self.goal_repo.get_active_goal()

    def set_daily_goal(self, target_word_count: int) -> int:
        goal = self.goal_repo.set_goal(target_word_count)
        return goal.target_word_count

    def get_today_progress(self, target_date: date = None) -> Dict[str, Any]:
        """
        Calculates words written today, goal target, percentage, and remaining words.
        """
        if target_date is None:
            target_date = date.today()

        goal = self.get_daily_goal()
        entries_today = self.entry_repo.search(start_date=target_date, end_date=target_date)
        words_today = sum(e.word_count for e in entries_today)

        percentage = min(100.0, (words_today / goal * 100.0)) if goal > 0 else 100.0
        remaining = max(0, goal - words_today)
        is_reached = words_today >= goal

        return {
            "date": target_date,
            "goal": goal,
            "words_today": words_today,
            "remaining": remaining,
            "percentage": round(percentage, 1),
            "is_reached": is_reached,
            "entries_count": len(entries_today),
        }
