"""
Entry Repository for querying, searching, and managing journal entries.
"""

from datetime import date
from typing import Optional, List, Dict, Any
from sqlalchemy import or_, desc, asc
from sqlalchemy.orm import Session
from src.models.entry import Entry
from src.models.category import Category
from src.repositories.base_repository import BaseRepository
from src.repositories.category_repository import CategoryRepository


class EntryRepository(BaseRepository[Entry]):
    """Data access layer for Entry models."""

    def __init__(self, session: Session):
        super().__init__(Entry, session)
        self.category_repo = CategoryRepository(session)

    def create_entry(
        self,
        content: str,
        prompt_text: str = "",
        category_name: Optional[str] = "journal",
        entry_date: Optional[date] = None,
        duration_seconds: int = 0,
        mood: Optional[str] = None,
    ) -> Entry:
        """Creates and persists a new writing entry."""
        if entry_date is None:
            entry_date = date.today()

        category = None
        if category_name:
            category = self.category_repo.get_or_create(category_name)

        clean_content = content.strip()
        word_count = len(clean_content.split()) if clean_content else 0

        entry = Entry(
            category_id=category.id if category else None,
            prompt_text=prompt_text.strip(),
            content=clean_content,
            word_count=word_count,
            duration_seconds=duration_seconds,
            mood=mood.strip() if mood else None,
            entry_date=entry_date,
        )
        self.add(entry)
        self.session.commit()
        return entry

    def update_entry(
        self,
        entry_id: int,
        content: Optional[str] = None,
        prompt_text: Optional[str] = None,
        category_name: Optional[str] = None,
        mood: Optional[str] = None,
    ) -> Optional[Entry]:
        """Updates an existing entry, recalculating word count if content changes."""
        entry = self.get_by_id(entry_id)
        if not entry:
            return None

        if content is not None:
            entry.content = content.strip()
            entry.recalculate_word_count()

        if prompt_text is not None:
            entry.prompt_text = prompt_text.strip()

        if category_name is not None:
            cat = self.category_repo.get_or_create(category_name)
            entry.category_id = cat.id

        if mood is not None:
            entry.mood = mood.strip() if mood else None

        self.session.commit()
        return entry

    def delete_by_id(self, entry_id: int) -> bool:
        """Deletes an entry by ID. Returns True if deleted, False if not found."""
        entry = self.get_by_id(entry_id)
        if not entry:
            return False
        self.delete(entry)
        self.session.commit()
        return True

    def get_recent(self, limit: int = 20) -> List[Entry]:
        """Returns the most recent entries sorted by date descending."""
        return (
            self.session.query(Entry)
            .order_by(desc(Entry.entry_date), desc(Entry.id))
            .limit(limit)
            .all()
        )

    def search(
        self,
        keyword: Optional[str] = None,
        category_name: Optional[str] = None,
        mood: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[Entry]:
        """
        Advanced filter and search entries by keyword (content or prompt),
        category, mood, and date range.
        """
        query = self.session.query(Entry)

        if keyword:
            term = f"%{keyword.strip().lower()}%"
            query = query.filter(
                or_(
                    Entry.content.ilike(term),
                    Entry.prompt_text.ilike(term),
                )
            )

        if category_name and category_name.lower() != "all":
            category = self.category_repo.get_by_name(category_name)
            if category:
                query = query.filter(Entry.category_id == category.id)
            else:
                return []

        if mood and mood.lower() != "all":
            query = query.filter(Entry.mood == mood.strip())

        if start_date:
            query = query.filter(Entry.entry_date >= start_date)

        if end_date:
            query = query.filter(Entry.entry_date <= end_date)

        return query.order_by(desc(Entry.entry_date), desc(Entry.id)).all()

    def get_all_dates(self) -> List[date]:
        """Returns a sorted list of unique dates with at least one entry."""
        results = (
            self.session.query(Entry.entry_date)
            .distinct()
            .order_by(asc(Entry.entry_date))
            .all()
        )
        return [r[0] for r in results]

    def get_stats_summary(self) -> Dict[str, Any]:
        """Returns aggregate writing statistics across all entries."""
        entries = self.session.query(Entry).all()
        if not entries:
            return {
                "total_entries": 0,
                "total_words": 0,
                "average_words": 0,
                "category_breakdown": {},
                "mood_breakdown": {},
                "longest_entry": None,
            }

        total_words = sum(e.word_count for e in entries)
        total_entries = len(entries)
        avg_words = total_words // total_entries if total_entries else 0

        # Category breakdown
        cat_counts: Dict[str, Dict[str, int]] = {}
        for e in entries:
            cat_name = e.category_name
            if cat_name not in cat_counts:
                cat_counts[cat_name] = {"count": 0, "words": 0}
            cat_counts[cat_name]["count"] += 1
            cat_counts[cat_name]["words"] += e.word_count

        # Mood breakdown
        mood_counts: Dict[str, int] = {}
        for e in entries:
            if e.mood:
                mood_counts[e.mood] = mood_counts.get(e.mood, 0) + 1

        longest_entry = max(entries, key=lambda e: e.word_count)

        return {
            "total_entries": total_entries,
            "total_words": total_words,
            "average_words": avg_words,
            "category_breakdown": cat_counts,
            "mood_breakdown": mood_counts,
            "longest_entry": longest_entry,
        }
