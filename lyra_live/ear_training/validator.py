"""
Exercise validation logic.

Validates user responses against expected answers for various exercise types.
For MVP (Phase 1), focuses on pitch-only validation (ignores timing and velocity).
"""

from lyra_live.ear_training.base import Note, ExerciseResult
from lyra_live.ear_training.intervals import IntervalExercise
from typing import List


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

        Phase 2 feature - stub for now.
        """
        # TODO Phase 2: Implement chord validation
        return ExerciseResult(
            exercise_id="",
            user_notes=actual,
            correct=False,
            feedback="Chord validation not yet implemented (Phase 2)"
        )

    @staticmethod
    def validate_melody(expected: List[Note], actual: List[Note]) -> ExerciseResult:
        """
        Validate melody imitation exercise.

        Phase 2 feature - stub for now.
        """
        # TODO Phase 2: Implement melody validation
        return ExerciseResult(
            exercise_id="",
            user_notes=actual,
            correct=False,
            feedback="Melody validation not yet implemented (Phase 2)"
        )
