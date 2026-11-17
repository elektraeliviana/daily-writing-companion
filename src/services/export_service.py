"""
Export Service for exporting entries into clean text or markdown formats.
"""

from datetime import date
from pathlib import Path
from typing import List
from sqlalchemy.orm import Session
from src.repositories.entry_repository import EntryRepository
from src.repositories.goal_repository import GoalRepository
from src.services.streak_service import StreakService


class ExportService:
    """Handles data export formatting and disk writing."""

    def __init__(self, session: Session):
        self.session = session
        self.entry_repo = EntryRepository(session)
        self.goal_repo = GoalRepository(session)

    def export_to_text(self, output_dir: Path) -> Path:
        """
        Exports all entries to a nicely formatted text file.
        Returns the created Path.
        """
        entries = self.entry_repo.get_all()
        dates = self.entry_repo.get_all_dates()
        current_streak, longest_streak, _ = StreakService.calculate_streaks(dates)
        goal = self.goal_repo.get_active_goal()
        total_words = sum(e.word_count for e in entries)

        today_str = date.today().isoformat()
        filename = output_dir / f"Journal_Export_{today_str}.txt"

        lines: List[str] = [
            "=" * 60,
            " MY WRITING JOURNAL - EXPORT",
            f" Export Date   : {today_str}",
            f" Total Entries : {len(entries)}",
            f" Total Words   : {total_words}",
            f" Current Streak: {current_streak} day(s)",
            f" Longest Streak: {longest_streak} day(s)",
            f" Daily Goal    : {goal} words/day",
            "=" * 60,
            "\n",
        ]

        # Sort entries chronologically for reading
        sorted_entries = sorted(entries, key=lambda e: (e.entry_date, e.id))

        for idx, entry in enumerate(sorted_entries, start=1):
            lines.append(f"--- Entry #{idx} ---")
            lines.append(f"Date     : {entry.entry_date}")
            lines.append(f"Category : {entry.category_name.capitalize()}")
            lines.append(f"Words    : {entry.word_count} ({entry.duration_seconds}s)")
            if entry.mood:
                lines.append(f"Mood     : {entry.mood}")
            if entry.prompt_text:
                lines.append(f"Prompt   : {entry.prompt_text}")
            lines.append("")
            lines.append(entry.content)
            lines.append("\n" + "-" * 60 + "\n")

        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        return filename
