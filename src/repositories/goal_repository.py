"""
DailyGoal Repository for managing writing goals.
"""

from typing import Optional
from sqlalchemy.orm import Session
from src.models.goal import DailyGoal
from src.repositories.base_repository import BaseRepository
from config.settings import DEFAULT_DAILY_WORD_GOAL


class GoalRepository(BaseRepository[DailyGoal]):
    """Data access layer for daily word count goals."""

    def __init__(self, session: Session):
        super().__init__(DailyGoal, session)

    def get_active_goal(self) -> int:
        """Returns the current active target word count, or creates default."""
        goal = (
            self.session.query(DailyGoal)
            .filter(DailyGoal.is_active.is_(True))
            .order_by(DailyGoal.set_at.desc())
            .first()
        )
        if goal:
            return goal.target_word_count

        # Seed default goal if none exists
        default_goal = DailyGoal(target_word_count=DEFAULT_DAILY_WORD_GOAL, is_active=True)
        self.add(default_goal)
        self.session.commit()
        return default_goal.target_word_count

    def set_goal(self, target_word_count: int) -> DailyGoal:
        """Deactivates old active goals and activates the new one."""
        self.session.query(DailyGoal).filter(DailyGoal.is_active.is_(True)).update(
            {"is_active": False}
        )
        new_goal = DailyGoal(target_word_count=target_word_count, is_active=True)
        self.add(new_goal)
        self.session.commit()
        return new_goal
