"""
DailyGoal Model for tracking user writing goals.
"""

from datetime import datetime, timezone
from sqlalchemy import Integer, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from src.db.base import Base


class DailyGoal(Base):
    """
    Represents a daily word count goal.
    Allows historical changes to goals while keeping the active one flagged.
    """
    __tablename__ = "daily_goals"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    target_word_count: Mapped[int] = mapped_column(Integer, nullable=False, default=200)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    set_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def __repr__(self) -> str:
        return f"<DailyGoal(id={self.id}, target={self.target_word_count}, active={self.is_active})>"
