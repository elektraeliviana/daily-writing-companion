"""
Category Repository for managing categories.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from src.models.category import Category
from src.repositories.base_repository import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    """Data access layer for Category models."""

    def __init__(self, session: Session):
        super().__init__(Category, session)

    def get_by_name(self, name: str) -> Optional[Category]:
        """Fetch category by exact case-insensitive name."""
        return self.session.query(Category).filter(Category.name.ilike(name.strip())).first()

    def get_or_create(self, name: str, description: Optional[str] = None, is_default: bool = False) -> Category:
        """Find category by name or create it if not present."""
        clean_name = name.strip().lower()
        existing = self.get_by_name(clean_name)
        if existing:
            return existing

        category = Category(name=clean_name, description=description, is_default=is_default)
        self.add(category)
        self.session.commit()
        return category

    def seed_defaults(self) -> List[Category]:
        """Seeds standard default categories: story, poem, journal."""
        defaults = [
            ("journal", "Daily self-reflections, feelings, and personal memories.", True),
            ("story", "Creative fiction, narrative writing, and character development.", True),
            ("poem", "Poetic explorations, imagery, and verse.", True),
        ]
        results = []
        for name, desc, is_def in defaults:
            results.append(self.get_or_create(name=name, description=desc, is_default=is_def))
        return results
