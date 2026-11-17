"""
Entry Model representing a journal/writing session record.
"""

from datetime import date, datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy import Integer, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.base import Base

if TYPE_CHECKING:
    from src.models.category import Category


class Entry(Base):
    """
    Represents an individual journal or creative writing entry.
    """
    __tablename__ = "entries"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True
    )
    prompt_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    word_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    mood: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    entry_date: Mapped[date] = mapped_column(Date, default=date.today, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    category: Mapped[Optional["Category"]] = relationship("Category", back_populates="entries")

    @property
    def category_name(self) -> str:
        """Helper to get category name or 'uncategorized'"""
        return self.category.name if self.category else "general"

    def recalculate_word_count(self) -> int:
        """Calculates and updates the word count from content."""
        self.word_count = len(self.content.split()) if self.content else 0
        return self.word_count

    def __repr__(self) -> str:
        return f"<Entry(id={self.id}, date={self.entry_date}, words={self.word_count}, mood='{self.mood}')>"
