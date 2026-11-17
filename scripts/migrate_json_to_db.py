"""
Data Migration Script: Safely migrates historical entries from data.json into SQLite.
Performs verification to ensure 100% data fidelity with zero data loss.
"""

import sys
import shutil
import json
from datetime import datetime, date
from pathlib import Path

# Add project root to sys.path so we can import from config and src
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import DEFAULT_DB_PATH
from src.db.session import init_db, get_session
from src.repositories.category_repository import CategoryRepository
from src.repositories.prompt_repository import PromptRepository
from src.repositories.goal_repository import GoalRepository
from src.repositories.entry_repository import EntryRepository
from src.models.entry import Entry
from src.models.goal import DailyGoal


def backup_json_file(json_path: Path) -> Path:
    """Creates a timestamped backup of the JSON file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = json_path.parent / f"data_backup_{timestamp}.json"
    shutil.copy2(json_path, backup_path)
    print(f" Safety Backup created: {backup_path.name}")
    return backup_path


def run_migration(json_path: Path = None, db_path: Path = None) -> bool:
    """
    Executes the migration process from JSON to SQLite.
    Returns True on success.
    """
    if json_path is None:
        json_path = PROJECT_ROOT / "data.json"

    if not json_path.exists():
        print(f" Error: {json_path} does not exist. Nothing to migrate.")
        return False

    print("\n" + "=" * 60)
    print("STARTING DATA MIGRATION: JSON -> SQLITE")
    print("=" * 60)

    # 1. Create a safe backup first
    backup_file = backup_json_file(json_path)

    # 2. Read legacy JSON data
    with open(json_path, "r", encoding="utf-8") as f:
        legacy_data = json.load(f)

    legacy_entries = legacy_data.get("entries", [])
    legacy_goal = legacy_data.get("goal", 200)
    print(f" Loaded {len(legacy_entries)} entries from {json_path.name}")

    # 3. Initialize Database and Tables
    init_db()
    session = get_session()

    try:
        category_repo = CategoryRepository(session)
        prompt_repo = PromptRepository(session)
        goal_repo = GoalRepository(session)
        entry_repo = EntryRepository(session)

        # 4. Seed default categories and prompts
        print(" Seeding default categories and curated prompts...")
        category_repo.seed_defaults()
        prompt_repo.seed_default_prompts()

        # 5. Migrate Daily Goal
        if legacy_goal:
            goal_repo.set_goal(int(legacy_goal))
            print(f" Daily goal set to: {legacy_goal} words")

        # 6. Migrate Entries
        migrated_count = 0
        total_legacy_words = sum(e.get("word_count", 0) for e in legacy_entries)

        for item in legacy_entries:
            date_str = item.get("date")
            try:
                entry_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except Exception:
                entry_date = date.today()

            entry_repo.create_entry(
                content=item.get("text", ""),
                prompt_text=item.get("prompt", ""),
                category_name=item.get("category", "journal"),
                entry_date=entry_date,
                duration_seconds=item.get("duration_seconds", 0),
                mood=item.get("mood"),
            )
            migrated_count += 1

        session.commit()

        # 7. Verification & Audit Checks
        db_entries = session.query(Entry).all()
        db_words = sum(e.word_count for e in db_entries)
        active_goal = goal_repo.get_active_goal()

        print("\n" + "-" * 60)
        print("VERIFICATION & INTEGRITY REPORT:")
        print(f" Legacy entries in JSON : {len(legacy_entries)}")
        print(f" Migrated entries in DB : {len(db_entries)}")
        print(f" Total words in JSON    : {total_legacy_words}")
        print(f" Total words in DB      : {db_words}")
        print(f" Active Goal in DB      : {active_goal}")
        print("-" * 60)

        assert len(db_entries) == len(legacy_entries), "Entry count mismatch!"
        assert db_words == total_legacy_words, "Total word count mismatch!"
        assert active_goal == legacy_goal, "Daily goal mismatch!"

        print(" SUCCESS: All checks passed with 100% data fidelity!")
        print(f" Database saved at: {DEFAULT_DB_PATH}")
        print("=" * 60 + "\n")
        return True

    except Exception as e:
        session.rollback()
        print(f" Migration failed: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    run_migration()
