"""
Streak Service: pure business logic for calculating consecutive writing streaks.
Separated from storage to enable deterministic unit testing.
"""

from datetime import date, timedelta
from typing import List, Set, Tuple


class StreakService:
    """
    Calculates current streaks and longest streaks from dates.
    """

    @staticmethod
    def calculate_streaks(entry_dates: List[date], reference_date: date = None) -> Tuple[int, int, bool]:
        """
        Calculates:
        1. current_streak (consecutive days active up to reference_date)
        2. longest_streak (all-time longest streak)
        3. written_today (True if reference_date has at least one entry)

        Note: If the user hasn't written *today* yet, but wrote *yesterday*,
        their current streak is still preserved! It only resets if yesterday was also missed.
        """
        if reference_date is None:
            reference_date = date.today()

        if not entry_dates:
            return (0, 0, False)

        unique_dates: Set[date] = set(entry_dates)
        written_today = reference_date in unique_dates

        # Calculate current streak
        # Start counting backwards from today or yesterday
        current_streak = 0
        cursor = reference_date if written_today else reference_date - timedelta(days=1)

        while cursor in unique_dates:
            current_streak += 1
            cursor -= timedelta(days=1)

        # Calculate all-time longest streak
        sorted_dates = sorted(unique_dates)
        longest_streak = 0
        running_streak = 0
        prev_date = None

        for d in sorted_dates:
            if prev_date is None:
                running_streak = 1
            elif d == prev_date + timedelta(days=1):
                running_streak += 1
            elif d == prev_date:
                # Same day duplicate
                pass
            else:
                running_streak = 1

            if running_streak > longest_streak:
                longest_streak = running_streak
            prev_date = d

        return (current_streak, longest_streak, written_today)
