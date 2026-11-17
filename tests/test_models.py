"""
Unit tests for SQLAlchemy Domain Models.
"""

from datetime import date
from src.models.category import Category
from src.models.prompt import Prompt
from src.models.entry import Entry
from src.models.goal import DailyGoal


def test_create_category(db_session):
    cat = Category(name="fiction", description="Creative fiction", is_default=False)
    db_session.add(cat)
    db_session.commit()

    saved = db_session.query(Category).filter_by(name="fiction").first()
    assert saved is not None
    assert saved.id is not None
    assert saved.description == "Creative fiction"
    assert not saved.is_default


def test_create_prompt_with_category(db_session):
    cat = Category(name="reflection", is_default=True)
    db_session.add(cat)
    db_session.commit()

    prompt = Prompt(category_id=cat.id, content="What made you smile today?", is_ai_generated=True)
    db_session.add(prompt)
    db_session.commit()

    saved_prompt = db_session.query(Prompt).filter_by(content="What made you smile today?").first()
    assert saved_prompt is not None
    assert saved_prompt.is_ai_generated is True
    assert saved_prompt.category.name == "reflection"


def test_entry_word_count_calculation():
    entry = Entry(
        content="The quick brown fox jumps over the lazy dog.",
        prompt_text="Write a sentence.",
        entry_date=date.today(),
    )
    assert entry.recalculate_word_count() == 9
    assert entry.word_count == 9

    # Empty content
    entry.content = ""
    assert entry.recalculate_word_count() == 0


def test_daily_goal_creation(db_session):
    goal = DailyGoal(target_word_count=350, is_active=True)
    db_session.add(goal)
    db_session.commit()

    saved_goal = db_session.query(DailyGoal).filter_by(target_word_count=350).first()
    assert saved_goal is not None
    assert saved_goal.is_active is True
