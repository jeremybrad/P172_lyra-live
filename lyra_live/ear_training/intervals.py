"""
Interval recognition exercise generator.

Generates interval ear training exercises with various interval types.
For MVP, focuses on basic interval recognition (unison through octave).
"""

import random
from lyra_live.ear_training.base import Exercise, Note, ExerciseType
from typing import List


# Map interval names to semitone distances
INTERVALS = {
    "unison": 0,
    "minor_second": 1,
    "major_second": 2,
    "minor_third": 3,
    "major_third": 4,
    "perfect_fourth": 5,
    "tritone": 6,
    "perfect_fifth": 7,
    "minor_sixth": 8,
    "major_sixth": 9,
    "minor_seventh": 10,
    "major_seventh": 11,
    "octave": 12,
}

# Human-readable names for feedback
INTERVAL_NAMES = {
    0: "unison",
    1: "minor second",
    2: "major second",
    3: "minor third",
    4: "major third",
    5: "perfect fourth",
    6: "tritone",
    7: "perfect fifth",
    8: "minor sixth",
    9: "major sixth",
    10: "minor seventh",
    11: "major seventh",
    12: "octave",
}


class IntervalExercise:
    """Generate interval recognition exercises"""

    @staticmethod
    def generate(interval_type: str, root_note: int = 60) -> Exercise:
        """
        Create interval exercise with specific interval type.

        Args:
            interval_type: Name of interval (e.g., "perfect_fifth")
            root_note: Starting MIDI note number (default: 60 = middle C)

        Returns:
            Exercise with two notes forming the specified interval
        """
        if interval_type not in INTERVALS:
            raise ValueError(f"Unknown interval type: {interval_type}")

        semitones = INTERVALS[interval_type]
        notes = [
            Note(pitch=root_note, duration_ms=1000, role="root"),
            Note(pitch=root_note + semitones, duration_ms=1000, role="interval")
        ]
        return Exercise(
            id=f"interval_{interval_type}_{root_note}",
            type=ExerciseType.INTERVAL,
            notes=notes,
            correct_response=notes  # User should play same interval
        )

    @staticmethod
    def generate_random(root_range: tuple[int, int] = (48, 72)) -> Exercise:
        """
        Generate random interval exercise.

        Args:
            root_range: Tuple of (min, max) MIDI note numbers for root note
                       Default: (48, 72) = C3 to C5

        Returns:
            Exercise with random interval
        """
        interval_type = random.choice(list(INTERVALS.keys()))
        root_note = random.randint(root_range[0], root_range[1])
        return IntervalExercise.generate(interval_type, root_note)

    @staticmethod
    def get_interval_name(semitones: int) -> str:
        """
        Get human-readable name for interval size.

        Args:
            semitones: Number of semitones in the interval

        Returns:
            Human-readable interval name
        """
        return INTERVAL_NAMES.get(abs(semitones), f"{semitones} semitones")
