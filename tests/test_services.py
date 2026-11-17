"""
Unit tests for Business Logic Services (StreakService, GoalService).
"""

from datetime import date, timedelta
from src.services.streak_service import StreakService
from src.services.goal_service import GoalService
from src.repositories.entry_repository import EntryRepository


def test_streak_empty_dates():
    today = date(2026, 8, 20)
    current, longest, written_today = StreakService.calculate_streaks([], reference_date=today)
    assert current == 0
    assert longest == 0
    assert not written_today


def test_streak_written_today():
    today = date(2026, 8, 20)
    dates = [today]
    current, longest, written_today = StreakService.calculate_streaks(dates, reference_date=today)
    assert current == 1
    assert longest == 1
    assert written_today


def test_streak_written_yesterday_not_today_grace_period():
    today = date(2026, 8, 20)
    yesterday = today - timedelta(days=1)
    dates = [yesterday]
    current, longest, written_today = StreakService.calculate_streaks(dates, reference_date=today)
    # The streak should still be 1 (grace period until end of today)
    assert current == 1
    assert longest == 1
    assert not written_today


def test_streak_broken_two_days_ago():
    today = date(2026, 8, 20)
    two_days_ago = today - timedelta(days=2)
    dates = [two_days_ago]
    current, longest, written_today = StreakService.calculate_streaks(dates, reference_date=today)
    assert current == 0
    assert longest == 1
    assert not written_today


def test_streak_consecutive_days_and_longest():
    today = date(2026, 8, 20)
    # Historical 5-day streak in June
    past_dates = [date(2026, 6, 1) + timedelta(days=i) for i in range(5)]
    # Current 3-day streak in August
    current_dates = [today - timedelta(days=i) for i in range(3)]
    # Plus a duplicate entry on today
    all_dates = past_dates + current_dates + [today]

    current, longest, written_today = StreakService.calculate_streaks(all_dates, reference_date=today)
    assert current == 3
    assert longest == 5
    assert written_today


def test_goal_service_progress(db_session):
    goal_service = GoalService(db_session)
    entry_repo = EntryRepository(db_session)

    goal_service.set_daily_goal(100)
    today = date.today()

    # Progress before writing
    progress_before = goal_service.get_today_progress(target_date=today)
    assert progress_before["words_today"] == 0
    assert progress_before["remaining"] == 100
    assert progress_before["percentage"] == 0.0
    assert not progress_before["is_reached"]

    # Write 40 words
    entry_repo.create_entry(
        content=" ".join(["word"] * 40),
        entry_date=today,
    )
    progress_mid = goal_service.get_today_progress(target_date=today)
    assert progress_mid["words_today"] == 40
    assert progress_mid["remaining"] == 60
    assert progress_mid["percentage"] == 40.0
    assert not progress_mid["is_reached"]

    # Write another 70 words (total 110 >= 100)
    entry_repo.create_entry(
        content=" ".join(["word"] * 70),
        entry_date=today,
    )
    progress_done = goal_service.get_today_progress(target_date=today)
    assert progress_done["words_today"] == 110
    assert progress_done["remaining"] == 0
    assert progress_done["percentage"] == 100.0
    assert progress_done["is_reached"]
