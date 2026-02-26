"""
Melody imitation exercise generator.

Generates melodic phrase exercises where the user must play back
short 4-8 note melodic sequences by ear.

Phase 2 feature.
"""

import random
from lyra_live.ear_training.base import Exercise, Note, ExerciseType
from typing import List


# Scale patterns (semitones from root)
SCALES = {
    "major": [0, 2, 4, 5, 7, 9, 11, 12],
    "minor": [0, 2, 3, 5, 7, 8, 10, 12],
    "pentatonic_major": [0, 2, 4, 7, 9, 12],
    "pentatonic_minor": [0, 3, 5, 7, 10, 12],
}

# Melodic patterns (scale degree movements)
MELODIC_PATTERNS = {
    "ascending_scale": [0, 1, 2, 3, 4],
    "descending_scale": [4, 3, 2, 1, 0],
    "arpeggio_up": [0, 2, 4, 7],
    "arpeggio_down": [7, 4, 2, 0],
    "stepwise": [0, 1, 2, 1, 0],
    "simple_phrase": [0, 2, 4, 2, 0],
}


class MelodyImitationExercise:
    """Generate melody imitation exercises"""

    @staticmethod
    def generate(
        notes: List[Note],
        exercise_id: str = None
    ) -> Exercise:
        """
        Create melody imitation exercise from provided notes.

        Args:
            notes: List of Note objects forming the melody
            exercise_id: Optional custom ID

        Returns:
            Exercise with the given melody
        """
        if not notes:
            raise ValueError("Melody must have at least one note")

        if exercise_id is None:
            pitch_str = "_".join(str(n.pitch) for n in notes[:3])
            exercise_id = f"melody_{pitch_str}_{len(notes)}notes"

        return Exercise(
            id=exercise_id,
            type=ExerciseType.MELODY,
            notes=notes,
            correct_response=notes
        )

    @staticmethod
    def generate_from_pattern(
        pattern_name: str,
        scale: str = "major",
        root_note: int = 60,
        note_duration_ms: int = 500
    ) -> Exercise:
        """
        Generate melody from a named pattern and scale.

        Args:
            pattern_name: Name of melodic pattern (e.g., "ascending_scale")
            scale: Scale to use (default: "major")
            root_note: Root MIDI note number (default: 60 = middle C)
            note_duration_ms: Duration of each note in milliseconds

        Returns:
            Exercise with generated melody
        """
        if pattern_name not in MELODIC_PATTERNS:
            raise ValueError(f"Unknown pattern: {pattern_name}")

        if scale not in SCALES:
            raise ValueError(f"Unknown scale: {scale}")

        pattern = MELODIC_PATTERNS[pattern_name]
        scale_intervals = SCALES[scale]

        notes = []
        for i, scale_degree in enumerate(pattern):
            if scale_degree >= len(scale_intervals):
                scale_degree = len(scale_intervals) - 1

            pitch = root_note + scale_intervals[scale_degree]
            notes.append(Note(
                pitch=pitch,
                duration_ms=note_duration_ms,
                velocity=80,
                role=f"note_{i}"
            ))

        exercise_id = f"melody_{pattern_name}_{scale}_{root_note}"
        return MelodyImitationExercise.generate(notes, exercise_id)

    @staticmethod
    def generate_random(
        length: int = None,
        scale: str = "major",
        root_range: tuple[int, int] = (48, 72),
        note_duration_ms: int = 500
    ) -> Exercise:
        """
        Generate random melody exercise.

        Args:
            length: Number of notes (default: random 4-8)
            scale: Scale to use for melody generation
            root_range: Range for root note selection
            note_duration_ms: Duration of each note

        Returns:
            Exercise with random melody
        """
        if length is None:
            length = random.randint(4, 8)

        if scale not in SCALES:
            scale = "major"

        root_note = random.randint(root_range[0], root_range[1])
        scale_intervals = SCALES[scale]

        notes = []
        for i in range(length):
            # Random walk through scale
            scale_degree = random.randint(0, len(scale_intervals) - 1)
            pitch = root_note + scale_intervals[scale_degree]

            notes.append(Note(
                pitch=pitch,
                duration_ms=note_duration_ms,
                velocity=80,
                role=f"note_{i}"
            ))

        exercise_id = f"melody_random_{root_note}_{length}notes"
        return MelodyImitationExercise.generate(notes, exercise_id)

    @staticmethod
    def validate_sequence(expected: List[Note], actual: List[Note]) -> tuple[bool, float]:
        """
        Validate melody sequence with partial credit.

        Args:
            expected: Expected note sequence
            actual: User's played sequence

        Returns:
            Tuple of (is_perfect_match, accuracy_percentage)
        """
        if len(expected) != len(actual):
            # Penalize length mismatch heavily
            max_len = max(len(expected), len(actual))
            min_len = min(len(expected), len(actual))
            length_penalty = min_len / max_len

            # Check matching notes up to shorter length
            matches = sum(1 for i in range(min_len)
                         if expected[i].pitch == actual[i].pitch)
            accuracy = (matches / max_len) * length_penalty
            return False, accuracy

        # Same length - check note-by-note
        matches = sum(1 for i in range(len(expected))
                     if expected[i].pitch == actual[i].pitch)
        accuracy = matches / len(expected)
        is_perfect = (matches == len(expected))

        return is_perfect, accuracy
