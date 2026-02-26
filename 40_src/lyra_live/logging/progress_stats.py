"""
Progress statistics and analysis utilities.

Pure data processing functions that operate on PracticeSessionRecord objects
to compute totals, averages, streaks, and other useful metrics.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from collections import defaultdict
from lyra_live.logging.practice_log import PracticeSessionRecord


def compute_totals(sessions: List[PracticeSessionRecord]) -> float:
    """
    Compute total minutes practiced across all sessions.

    Args:
        sessions: List of practice session records

    Returns:
        Total minutes practiced
    """
    total_seconds = sum(s.duration_seconds for s in sessions)
    return total_seconds / 60.0


def compute_minutes_by_instrument(sessions: List[PracticeSessionRecord]) -> Dict[str, float]:
    """
    Compute minutes practiced per instrument.

    Args:
        sessions: List of practice session records

    Returns:
        Mapping of instrument name → minutes practiced
    """
    minutes_by_instrument = defaultdict(float)

    for session in sessions:
        minutes_by_instrument[session.instrument] += session.duration_seconds / 60.0

    return dict(minutes_by_instrument)


def compute_minutes_by_mode(sessions: List[PracticeSessionRecord]) -> Dict[str, float]:
    """
    Compute minutes practiced per mode.

    Args:
        sessions: List of practice session records

    Returns:
        Mapping of mode name → minutes practiced
    """
    minutes_by_mode = defaultdict(float)

    for session in sessions:
        minutes_by_mode[session.mode] += session.duration_seconds / 60.0

    return dict(minutes_by_mode)


def compute_recent_streak(sessions: List[PracticeSessionRecord], days: int = 7) -> int:
    """
    Compute how many consecutive recent days have at least one non-demo session.

    Counts backwards from today. Streak ends when we hit a day with no practice.

    Args:
        sessions: List of practice session records
        days: Maximum number of days to look back

    Returns:
        Number of consecutive days with practice (0 if no practice today/yesterday)
    """
    # Filter out demo sessions
    real_sessions = [s for s in sessions if s.source != "demo"]

    if not real_sessions:
        return 0

    # Get dates with practice (as date objects, not datetime)
    practice_dates = set()
    for session in real_sessions:
        session_date = datetime.fromisoformat(session.timestamp).date()
        practice_dates.add(session_date)

    # Count backwards from today
    today = datetime.now().date()
    streak = 0

    for i in range(days):
        check_date = today - timedelta(days=i)
        if check_date in practice_dates:
            streak += 1
        else:
            # Streak broken
            break

    return streak


def compute_average_metrics(
    sessions: List[PracticeSessionRecord],
    metric_name: str,
    days: Optional[int] = None
) -> Optional[float]:
    """
    Compute average value for a specific metric over sessions.

    Args:
        sessions: List of practice session records
        metric_name: Name of the metric field (e.g., "chord_tone_ratio")
        days: If specified, only include sessions from last N days

    Returns:
        Average value of the metric, or None if no sessions have this metric
    """
    # Filter by date if specified
    if days is not None:
        cutoff = datetime.now() - timedelta(days=days)
        sessions = [
            s for s in sessions
            if datetime.fromisoformat(s.timestamp) >= cutoff
        ]

    # Collect metric values
    values = []
    for session in sessions:
        value = getattr(session, metric_name, None)
        if value is not None:
            values.append(value)

    if not values:
        return None

    return sum(values) / len(values)


def filter_sessions(
    sessions: List[PracticeSessionRecord],
    instrument: Optional[str] = None,
    mode: Optional[str] = None,
    tune_id: Optional[str] = None,
    source: Optional[str] = None,
    since_days: Optional[int] = None
) -> List[PracticeSessionRecord]:
    """
    Filter sessions by various criteria.

    Args:
        sessions: List of practice session records
        instrument: Only include this instrument (e.g., "keyboard")
        mode: Only include this mode (e.g., "improv_midi")
        tune_id: Only include this tune (e.g., "autumn_leaves")
        source: Only include this source (e.g., "cli" to exclude demos)
        since_days: Only include sessions from last N days

    Returns:
        Filtered list of sessions
    """
    filtered = sessions

    if instrument:
        filtered = [s for s in filtered if s.instrument == instrument]

    if mode:
        filtered = [s for s in filtered if s.mode == mode]

    if tune_id:
        filtered = [s for s in filtered if s.tune_id == tune_id]

    if source:
        filtered = [s for s in filtered if s.source == source]

    if since_days is not None:
        cutoff = datetime.now() - timedelta(days=since_days)
        filtered = [
            s for s in filtered
            if datetime.fromisoformat(s.timestamp) >= cutoff
        ]

    return filtered


def get_most_practiced_tune(sessions: List[PracticeSessionRecord]) -> Optional[str]:
    """
    Get the tune ID that has been practiced the most (by time).

    Args:
        sessions: List of practice session records

    Returns:
        Tune ID with most practice time, or None if no tunes practiced
    """
    # Only consider sessions with tune_id
    tune_sessions = [s for s in sessions if s.tune_id]

    if not tune_sessions:
        return None

    # Sum time by tune
    time_by_tune = defaultdict(float)
    for session in tune_sessions:
        time_by_tune[session.tune_id] += session.duration_seconds

    # Find max
    most_practiced = max(time_by_tune.items(), key=lambda x: x[1])
    return most_practiced[0]


def count_unique_tunes(sessions: List[PracticeSessionRecord]) -> int:
    """
    Count how many unique tunes have been practiced.

    Args:
        sessions: List of practice session records

    Returns:
        Number of unique tunes practiced
    """
    tunes = {s.tune_id for s in sessions if s.tune_id}
    return len(tunes)


def count_unique_instruments(sessions: List[PracticeSessionRecord]) -> int:
    """
    Count how many unique instruments have been used.

    Args:
        sessions: List of practice session records

    Returns:
        Number of unique instruments
    """
    instruments = {s.instrument for s in sessions}
    return len(instruments)


def compute_practice_days(sessions: List[PracticeSessionRecord]) -> int:
    """
    Count total number of days on which practice occurred.

    Args:
        sessions: List of practice session records

    Returns:
        Number of unique days with practice
    """
    # Filter out demo sessions
    real_sessions = [s for s in sessions if s.source != "demo"]

    practice_dates = {
        datetime.fromisoformat(s.timestamp).date()
        for s in real_sessions
    }

    return len(practice_dates)


def compute_sessions_per_day(sessions: List[PracticeSessionRecord]) -> float:
    """
    Compute average sessions per practice day.

    Args:
        sessions: List of practice session records

    Returns:
        Average sessions per day, or 0 if no practice days
    """
    # Filter out demo sessions
    real_sessions = [s for s in sessions if s.source != "demo"]

    if not real_sessions:
        return 0.0

    num_days = compute_practice_days(real_sessions)
    if num_days == 0:
        return 0.0

    return len(real_sessions) / num_days
