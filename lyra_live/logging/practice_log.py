"""
Practice session logging to JSONL.

Provides persistent storage of all practice sessions with detailed metrics.
Each session is logged as one line of JSON for easy appending and parsing.
"""

import json
import fcntl
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, List


@dataclass
class PracticeSessionRecord:
    """
    Record of a single practice session.

    Captures all relevant information about a practice session including
    mode, instrument, duration, and mode-specific metrics.
    """

    # Core session info
    timestamp: str  # ISO 8601 format
    mode: str  # "intervals", "chords", "melody", "rhythm", "voice", "lesson", "improv_midi", "improv_audio"
    instrument: str  # "keyboard", "drums", "voice", "sax", "test_device"
    duration_seconds: float
    source: str = "cli"  # "cli", "demo", "test"

    # Optional session parameters
    tune_id: Optional[str] = None  # e.g. "autumn_leaves" for standards
    num_exercises: Optional[int] = None  # For ear training drills
    choruses: Optional[int] = None  # For standards improv

    # Improvisation metrics (nullable)
    chord_tone_ratio: Optional[float] = None  # 0-100
    tension_ratio: Optional[float] = None  # 0-100
    outside_ratio: Optional[float] = None  # 0-100
    guide_tone_hits: Optional[int] = None

    # Voice/audio metrics
    avg_cents_deviation: Optional[float] = None  # Average intonation error

    # Rhythm metrics
    rhythm_accuracy: Optional[float] = None  # 0-100 percentage
    avg_timing_error_ms: Optional[float] = None  # Average timing deviation
    rush_drag_bias: Optional[float] = None  # Positive = rushing, negative = dragging

    # Ear training metrics
    interval_accuracy: Optional[float] = None  # 0-100 percentage
    chord_accuracy: Optional[float] = None  # 0-100 percentage
    melody_accuracy: Optional[float] = None  # 0-100 percentage

    # Freeform notes
    notes: Optional[str] = None

    # Schema version
    version: str = "v1"

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'PracticeSessionRecord':
        """Create from dictionary (from JSON)."""
        return cls(**data)


def get_log_path() -> Path:
    """
    Get the path to the practice sessions log file.

    Returns:
        Path to data/logs/practice_sessions.jsonl
    """
    # Assume we're in the project root
    return Path("data/logs/practice_sessions.jsonl")


def append_session(record: PracticeSessionRecord) -> None:
    """
    Append a practice session record to the log file.

    Uses file locking to handle concurrent writes safely.
    Creates the log file and directory if they don't exist.

    Args:
        record: PracticeSessionRecord to append
    """
    log_path = get_log_path()

    # Ensure directory exists
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Convert to JSON
    json_line = json.dumps(record.to_dict()) + '\n'

    # Append with file locking for concurrent safety
    with open(log_path, 'a') as f:
        # Acquire exclusive lock
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            f.write(json_line)
            f.flush()
        finally:
            # Release lock
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def load_sessions() -> List[PracticeSessionRecord]:
    """
    Load all practice session records from the log file.

    Returns:
        List of PracticeSessionRecord objects, ordered by timestamp (oldest first)

    Returns empty list if log file doesn't exist or is empty.
    Skips malformed lines with a warning.
    """
    log_path = get_log_path()

    if not log_path.exists():
        return []

    sessions = []

    with open(log_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue  # Skip empty lines

            try:
                data = json.loads(line)
                session = PracticeSessionRecord.from_dict(data)
                sessions.append(session)
            except (json.JSONDecodeError, TypeError) as e:
                print(f"Warning: Skipping malformed line {line_num} in practice log: {e}")
                continue

    return sessions


def load_sessions_since(since: datetime) -> List[PracticeSessionRecord]:
    """
    Load practice sessions since a given datetime.

    Args:
        since: Only return sessions after this datetime

    Returns:
        List of PracticeSessionRecord objects since the given time
    """
    all_sessions = load_sessions()

    filtered = []
    for session in all_sessions:
        session_time = datetime.fromisoformat(session.timestamp)
        if session_time >= since:
            filtered.append(session)

    return filtered


def count_sessions() -> int:
    """
    Count total number of logged sessions.

    Returns:
        Number of sessions in the log
    """
    return len(load_sessions())


def clear_log() -> None:
    """
    Clear the practice session log.

    WARNING: This deletes all logged data permanently!
    Only use for testing or explicit user request.
    """
    log_path = get_log_path()

    if log_path.exists():
        log_path.unlink()
