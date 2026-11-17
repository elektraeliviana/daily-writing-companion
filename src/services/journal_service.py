"""
Journal Service: Facade combining entry persistence, streaks, goals, and statistics.
Used by the presentation/GUI layer to coordinate business workflows.
"""

from datetime import date
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from src.models.entry import Entry
from src.repositories.entry_repository import EntryRepository
from src.repositories.category_repository import CategoryRepository
from src.repositories.prompt_repository import PromptRepository
from src.repositories.goal_repository import GoalRepository
from src.services.streak_service import StreakService
from src.services.goal_service import GoalService


class JournalService:
    """Core application service coordinating journal logic."""

    def __init__(self, session: Session):
        self.session = session
        self.entry_repo = EntryRepository(session)
        self.category_repo = CategoryRepository(session)
        self.prompt_repo = PromptRepository(session)
        self.goal_repo = GoalRepository(session)
        self.goal_service = GoalService(session)

    def save_new_entry(
        self,
        content: str,
        prompt_text: str = "",
        category_name: str = "journal",
        duration_seconds: int = 0,
        mood: Optional[str] = None,
        entry_date: Optional[date] = None,
    ) -> Entry:
        """Saves a new entry and returns it."""
        return self.entry_repo.create_entry(
            content=content,
            prompt_text=prompt_text,
            category_name=category_name,
            entry_date=entry_date or date.today(),
            duration_seconds=duration_seconds,
            mood=mood,
        )

    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Provides all metrics needed for the main UI dashboard."""
        dates = self.entry_repo.get_all_dates()
        current_streak, longest_streak, written_today = StreakService.calculate_streaks(dates)
        stats = self.entry_repo.get_stats_summary()
        today_progress = self.goal_service.get_today_progress()

        return {
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "written_today": written_today,
            "today_progress": today_progress,
            "stats": stats,
        }
