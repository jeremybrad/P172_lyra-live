"""
Exercise validation logic.

Validates user responses against expected answers for various exercise types.
For MVP (Phase 1), focuses on pitch-only validation (ignores timing and velocity).
"""

from lyra_live.ear_training.base import Note, ExerciseResult
from lyra_live.ear_training.intervals import IntervalExercise
from typing import List


# Import chord and melody classes (avoid circular import)
def _get_chord_exercise():
    from lyra_live.ear_training.chords import ChordQualityExercise
    return ChordQualityExercise


def _get_melody_exercise():
    from lyra_live.ear_training.melodies import MelodyImitationExercise
    return MelodyImitationExercise


class ExerciseValidator:
    """Validate user responses against expected answers"""

    @staticmethod
    def validate_interval(expected: List[Note], actual: List[Note]) -> ExerciseResult:
        """
        Check if user played correct interval.

        For MVP, validates based on pitch only - the interval size must match,
        but the starting note can be different.

        Args:
            expected: Expected notes from the exercise
            actual: Notes played by the user

        Returns:
            ExerciseResult with validation outcome and feedback
        """
        # Check that we got exactly 2 notes
        if len(actual) != 2:
            return ExerciseResult(
                exercise_id="",
                user_notes=actual,
                correct=False,
                feedback=f"Expected 2 notes, got {len(actual)}"
            )

        # Calculate intervals (difference in semitones)
        expected_interval = expected[1].pitch - expected[0].pitch
        actual_interval = actual[1].pitch - actual[0].pitch

        # Check if intervals match
        correct = (expected_interval == actual_interval)

        # Generate feedback message
        if correct:
            interval_name = IntervalExercise.get_interval_name(expected_interval)
            feedback = f"Correct! That's a {interval_name}."
        else:
            expected_name = IntervalExercise.get_interval_name(expected_interval)
            actual_name = IntervalExercise.get_interval_name(actual_interval)
            feedback = f"Not quite. Expected {expected_name}, got {actual_name}."

        return ExerciseResult(
            exercise_id="",
            user_notes=actual,
            correct=correct,
            feedback=feedback
        )

    @staticmethod
    def validate_chord(expected: List[Note], actual: List[Note]) -> ExerciseResult:
        """
        Validate chord quality exercise.

        Checks if the user played the correct chord quality (intervals from root).
        The starting note can be different (any transposition is valid).

        Args:
            expected: Expected chord notes
            actual: Notes played by the user

        Returns:
            ExerciseResult with validation outcome and feedback
        """
        ChordQualityExercise = _get_chord_exercise()

        # Check that we have at least 3 notes (minimum for a chord)
        if len(actual) < 3:
            return ExerciseResult(
                exercise_id="",
                user_notes=actual,
                correct=False,
                feedback=f"Expected at least 3 notes for a chord, got {len(actual)}"
            )

        # Check that note counts match
        if len(actual) != len(expected):
            return ExerciseResult(
                exercise_id="",
                user_notes=actual,
                correct=False,
                feedback=f"Expected {len(expected)} notes, got {len(actual)}"
            )

        # Calculate intervals from root for both chords
        expected_intervals = sorted([note.pitch - expected[0].pitch for note in expected])
        actual_intervals = sorted([note.pitch - actual[0].pitch for note in actual])

        # Check if interval patterns match
        correct = (expected_intervals == actual_intervals)

        # Generate feedback
        if correct:
            # Identify the chord quality
            expected_quality = ChordQualityExercise.identify_chord_quality(expected)
            chord_name = ChordQualityExercise.get_chord_name(expected_quality)
            feedback = f"Correct! That's a {chord_name} chord."
        else:
            expected_quality = ChordQualityExercise.identify_chord_quality(expected)
            actual_quality = ChordQualityExercise.identify_chord_quality(actual)

            expected_name = ChordQualityExercise.get_chord_name(expected_quality)
            actual_name = ChordQualityExercise.get_chord_name(actual_quality)

            feedback = f"Not quite. Expected {expected_name}, got {actual_name}."

        return ExerciseResult(
            exercise_id="",
            user_notes=actual,
            correct=correct,
            feedback=feedback
        )

    @staticmethod
    def validate_melody(expected: List[Note], actual: List[Note]) -> ExerciseResult:
        """
        Validate melody imitation exercise.

        Checks if the user played the correct sequence of pitches.
        Provides partial credit for partially correct sequences.

        Args:
            expected: Expected melody notes
            actual: Notes played by the user

        Returns:
            ExerciseResult with validation outcome and feedback
        """
        MelodyImitationExercise = _get_melody_exercise()

        if not actual:
            return ExerciseResult(
                exercise_id="",
                user_notes=actual,
                correct=False,
                feedback="No notes detected. Please try again."
            )

        # Use the melody exercise's validation logic
        is_perfect, accuracy = MelodyImitationExercise.validate_sequence(expected, actual)

        # Generate feedback based on accuracy
        if is_perfect:
            feedback = f"Perfect! You got all {len(expected)} notes correct."
        elif accuracy >= 0.8:
            feedback = f"Very good! {int(accuracy * 100)}% correct. Almost there!"
        elif accuracy >= 0.5:
            feedback = f"Good try. {int(accuracy * 100)}% correct. Keep practicing!"
        else:
            feedback = f"Not quite. {int(accuracy * 100)}% correct. Listen carefully and try again."

        return ExerciseResult(
            exercise_id="",
            user_notes=actual,
            correct=is_perfect,
            feedback=feedback
        )
