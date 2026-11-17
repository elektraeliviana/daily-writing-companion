"""
Unit tests for Data Migration logic.
"""

import json
from pathlib import Path
from src.repositories.entry_repository import EntryRepository
from src.repositories.goal_repository import GoalRepository
from src.repositories.category_repository import CategoryRepository
from src.models.entry import Entry
from scripts.migrate_json_to_db import backup_json_file


def test_backup_creation(tmp_path):
    json_file = tmp_path / "data.json"
    json_file.write_text('{"entries": []}', encoding="utf-8")

    backup = backup_json_file(json_file)
    assert backup.exists()
    assert backup.name.startswith("data_backup_")


def test_migration_fidelity(db_session, tmp_path):
    category_repo = CategoryRepository(db_session)
    category_repo.seed_defaults()
    entry_repo = EntryRepository(db_session)
    goal_repo = GoalRepository(db_session)

    # Mock legacy data
    mock_data = {
        "entries": [
            {
                "date": "2026-06-28",
                "category": "journal",
                "prompt": "Write a letter to yourself.",
                "text": "I wish I can be better.",
                "word_count": 6,
                "duration_seconds": 6,
            },
            {
                "date": "2026-07-18",
                "category": "story",
                "prompt": "Write about a magical doorway.",
                "text": "The portal opened with a whisper.",
                "word_count": 6,
                "duration_seconds": 15,
                "mood": "🌟 Amazing",
            },
        ],
        "streak": 1,
        "goal": 250,
    }

    goal_repo.set_goal(mock_data["goal"])

    for item in mock_data["entries"]:
        entry_repo.create_entry(
            content=item["text"],
            prompt_text=item["prompt"],
            category_name=item["category"],
            duration_seconds=item["duration_seconds"],
            mood=item.get("mood"),
        )

    all_entries = db_session.query(Entry).all()
    assert len(all_entries) == 2
    assert sum(e.word_count for e in all_entries) == 12
    assert goal_repo.get_active_goal() == 250
    assert all_entries[1].mood == "🌟 Amazing"
