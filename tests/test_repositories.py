"""
Unit tests for the Repository Layer.
"""

from datetime import date, timedelta
from src.repositories.category_repository import CategoryRepository
from src.repositories.prompt_repository import PromptRepository
from src.repositories.goal_repository import GoalRepository
from src.repositories.entry_repository import EntryRepository


def test_category_repository_seed_and_find(db_session):
    repo = CategoryRepository(db_session)
    seeded = repo.seed_defaults()
    assert len(seeded) >= 3

    journal_cat = repo.get_by_name("journal")
    assert journal_cat is not None
    assert journal_cat.is_default is True

    # Case insensitive
    story_cat = repo.get_by_name("STORY")
    assert story_cat is not None
    assert story_cat.name == "story"


def test_prompt_repository_seed_and_random(db_session):
    repo = PromptRepository(db_session)
    seeded_count = repo.seed_default_prompts()
    assert seeded_count > 0

    prompt = repo.get_random_prompt("journal")
    assert prompt is not None
    assert len(prompt.content) > 0

    all_story_prompts = repo.get_by_category("story")
    assert len(all_story_prompts) >= 5


def test_goal_repository_activation(db_session):
    repo = GoalRepository(db_session)

    # Initial default
    default_goal = repo.get_active_goal()
    assert default_goal == 200

    # Change goal
    new_goal = repo.set_goal(500)
    assert new_goal.target_word_count == 500
    assert repo.get_active_goal() == 500


def test_entry_repository_crud_and_search(db_session):
    repo = EntryRepository(db_session)

    # 1. Create entry
    entry = repo.create_entry(
        content="Exploring the ancient ruins in the misty morning.",
        prompt_text="Describe a secret place.",
        category_name="story",
        entry_date=date(2026, 7, 10),
        duration_seconds=120,
        mood="🌟 Amazing",
    )
    assert entry.id is not None
    assert entry.word_count == 8
    assert entry.mood == "🌟 Amazing"
    assert entry.category_name == "story"

    # 2. Get by ID
    fetched = repo.get_by_id(entry.id)
    assert fetched is not None
    assert fetched.content == "Exploring the ancient ruins in the misty morning."

    # 3. Update entry
    updated = repo.update_entry(
        entry_id=entry.id,
        content="Exploring the ancient ruins in the misty morning with a friend.",
        mood="😊 Great",
    )
    assert updated.word_count == 11
    assert updated.mood == "😊 Great"

    # 4. Search by keyword
    results = repo.search(keyword="ruins")
    assert len(results) == 1
    assert results[0].id == entry.id

    # 5. Search by category
    results = repo.search(category_name="story")
    assert len(results) == 1

    results_empty = repo.search(category_name="poem")
    assert len(results_empty) == 0

    # 6. Search by mood
    results_mood = repo.search(mood="😊 Great")
    assert len(results_mood) == 1

    # 7. Delete
    deleted = repo.delete_by_id(entry.id)
    assert deleted is True
    assert repo.get_by_id(entry.id) is None
