"""
Category Model for organizing prompts and journal entries.
"""

from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.base import Base

if TYPE_CHECKING:
    from src.models.entry import Entry
    from src.models.prompt import Prompt


class Category(Base):
    """
    Represents a writing category (e.g. Journal, Story, Poem, or user-defined).
    """
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    entries: Mapped[List["Entry"]] = relationship("Entry", back_populates="category", cascade="all, delete-orphan")
    prompts: Mapped[List["Prompt"]] = relationship("Prompt", back_populates="category", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name='{self.name}')>"
