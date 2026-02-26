"""
Voice exercises for singing practice.

Includes pitch matching, scale singing, and sight-singing exercises.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple
import random

from lyra_live.ear_training.base import Exercise, ExerciseType, Note


@dataclass
class VoiceResult:
    """Result of a voice exercise."""
    correct: bool
    target_pitch: int  # MIDI note
    sung_pitch: Optional[int]  # MIDI note (None if no pitch detected)
    cents_deviation: Optional[float]  # Cents from target
    accuracy_percentage: float  # 0.0 to 100.0
    feedback: str


class PitchMatchExercise:
    """
    Pitch matching exercise.

    Play a single note, student must match it by singing.
    Validates pitch accuracy within a tolerance (default ±50 cents).
    """

    @staticmethod
    def generate(target_pitch: int) -> Exercise:
        """
        Generate a pitch matching exercise.

        Args:
            target_pitch: MIDI note to match

        Returns:
            Exercise with single note to match
        """
        note = Note(pitch=target_pitch, duration_ms=2000)

        return Exercise(
            type=ExerciseType.VOICE_PITCH_MATCH,
            notes=[note],
            correct_response=[note],
            metadata={
                "target_pitch": target_pitch,
                "tolerance_cents": 50
            }
        )

    @staticmethod
    def generate_random(min_pitch: int = 55, max_pitch: int = 79) -> Exercise:
        """
        Generate a random pitch matching exercise.

        Args:
            min_pitch: Minimum MIDI note (default G3 = 55)
            max_pitch: Maximum MIDI note (default G5 = 79)

        Returns:
            Exercise with random pitch to match
        """
        pitch = random.randint(min_pitch, max_pitch)
        return PitchMatchExercise.generate(pitch)

    @staticmethod
    def validate(
        target_pitch: int,
        sung_pitch: Optional[int],
        cents_deviation: Optional[float],
        tolerance_cents: int = 50
    ) -> VoiceResult:
        """
        Validate a pitch matching attempt.

        Args:
            target_pitch: Target MIDI note
            sung_pitch: Detected sung pitch (None if no pitch detected)
            cents_deviation: Cents from target (None if no pitch)
            tolerance_cents: Acceptable deviation in cents

        Returns:
            VoiceResult with validation details
        """
        from lyra_live.ear_training.base import CHROMATIC_NOTES

        target_name = CHROMATIC_NOTES[target_pitch % 12]

        if sung_pitch is None:
            return VoiceResult(
                correct=False,
                target_pitch=target_pitch,
                sung_pitch=None,
                cents_deviation=None,
                accuracy_percentage=0.0,
                feedback=f"❌ No pitch detected. Target was {target_name}{target_pitch // 12 - 1}."
            )

        if cents_deviation is None:
            cents_deviation = 0.0

        # Check if within tolerance
        correct = abs(cents_deviation) <= tolerance_cents

        # Calculate accuracy percentage (100% at 0 cents, 0% at 100 cents)
        accuracy = max(0.0, 100.0 - abs(cents_deviation))

        sung_name = CHROMATIC_NOTES[sung_pitch % 12]

        if correct:
            feedback = (
                f"✅ Perfect! Target: {target_name}{target_pitch // 12 - 1}, "
                f"You sang: {sung_name}{sung_pitch // 12 - 1} "
                f"({cents_deviation:+.1f} cents)"
            )
        else:
            direction = "sharp" if cents_deviation > 0 else "flat"
            feedback = (
                f"❌ Not quite. Target: {target_name}{target_pitch // 12 - 1}, "
                f"You sang: {sung_name}{sung_pitch // 12 - 1} "
                f"({abs(cents_deviation):.1f} cents {direction})"
            )

        return VoiceResult(
            correct=correct,
            target_pitch=target_pitch,
            sung_pitch=sung_pitch,
            cents_deviation=cents_deviation,
            accuracy_percentage=accuracy,
            feedback=feedback
        )


class ScaleExercise:
    """
    Scale singing exercise.

    Sing a complete scale (major, minor, etc.) in order.
    Validates each note in the sequence.
    """

    SCALE_FORMULAS = {
        "major": [0, 2, 4, 5, 7, 9, 11, 12],
        "natural_minor": [0, 2, 3, 5, 7, 8, 10, 12],
        "harmonic_minor": [0, 2, 3, 5, 7, 8, 11, 12],
        "major_pentatonic": [0, 2, 4, 7, 9, 12],
        "minor_pentatonic": [0, 3, 5, 7, 10, 12],
    }

    @staticmethod
    def generate(scale_type: str, root_note: int, note_duration_ms: int = 1000) -> Exercise:
        """
        Generate a scale singing exercise.

        Args:
            scale_type: Type of scale (major, natural_minor, etc.)
            root_note: Root note of the scale (MIDI)
            note_duration_ms: Duration of each note

        Returns:
            Exercise with scale notes
        """
        if scale_type not in ScaleExercise.SCALE_FORMULAS:
            raise ValueError(f"Unknown scale type: {scale_type}")

        formula = ScaleExercise.SCALE_FORMULAS[scale_type]
        notes = [Note(root_note + interval, note_duration_ms) for interval in formula]

        return Exercise(
            type=ExerciseType.VOICE_SCALE,
            notes=notes,
            correct_response=notes,
            metadata={
                "scale_type": scale_type,
                "root_note": root_note,
                "tolerance_cents": 50
            }
        )

    @staticmethod
    def generate_random(
        scale_types: Optional[List[str]] = None,
        min_root: int = 48,
        max_root: int = 72
    ) -> Exercise:
        """
        Generate a random scale exercise.

        Args:
            scale_types: List of scale types to choose from (None = all)
            min_root: Minimum root note
            max_root: Maximum root note

        Returns:
            Random scale exercise
        """
        if scale_types is None:
            scale_types = list(ScaleExercise.SCALE_FORMULAS.keys())

        scale_type = random.choice(scale_types)
        root_note = random.randint(min_root, max_root)

        return ScaleExercise.generate(scale_type, root_note)

    @staticmethod
    def validate_sequence(
        expected_notes: List[Note],
        sung_pitches: List[int],
        tolerance_cents: int = 50
    ) -> Tuple[bool, float, str]:
        """
        Validate a sung scale sequence.

        Args:
            expected_notes: Expected note sequence
            sung_pitches: Detected sung pitches
            tolerance_cents: Acceptable deviation per note

        Returns:
            Tuple of (is_perfect, accuracy_percentage, feedback)
        """
        if len(sung_pitches) != len(expected_notes):
            return (
                False,
                0.0,
                f"❌ Wrong number of notes. Expected {len(expected_notes)}, got {len(sung_pitches)}."
            )

        correct_count = 0
        for expected, sung in zip(expected_notes, sung_pitches):
            # Check if same note (exact match)
            if sung == expected.pitch:
                correct_count += 1

        accuracy = (correct_count / len(expected_notes)) * 100
        is_perfect = correct_count == len(expected_notes)

        if is_perfect:
            feedback = f"✅ Perfect! You sang all {len(expected_notes)} notes correctly."
        else:
            feedback = (
                f"⚠️ Partially correct. {correct_count}/{len(expected_notes)} notes accurate "
                f"({accuracy:.1f}% accuracy)"
            )

        return is_perfect, accuracy, feedback


class SightSingingExercise:
    """
    Sight-singing exercise.

    Display a short melody (musical phrase), student sings it back.
    More challenging than pitch matching or scales as it tests
    sight-reading and melodic memory.
    """

    @staticmethod
    def generate_from_intervals(
        root_note: int,
        intervals: List[int],
        note_duration_ms: int = 800
    ) -> Exercise:
        """
        Generate sight-singing exercise from interval pattern.

        Args:
            root_note: Starting note
            intervals: List of intervals from root
            note_duration_ms: Duration per note

        Returns:
            Exercise with melodic phrase
        """
        notes = [Note(root_note + interval, note_duration_ms) for interval in intervals]

        return Exercise(
            type=ExerciseType.VOICE_SIGHT_SINGING,
            notes=notes,
            correct_response=notes,
            metadata={
                "root_note": root_note,
                "intervals": intervals,
                "tolerance_cents": 50
            }
        )

    @staticmethod
    def generate_diatonic_phrase(
        scale_type: str = "major",
        root_note: int = 60,
        phrase_length: int = 4
    ) -> Exercise:
        """
        Generate a diatonic melodic phrase within a scale.

        Args:
            scale_type: Scale to use (major, natural_minor, etc.)
            root_note: Root of the scale
            phrase_length: Number of notes in phrase

        Returns:
            Sight-singing exercise with diatonic melody
        """
        if scale_type not in ScaleExercise.SCALE_FORMULAS:
            raise ValueError(f"Unknown scale type: {scale_type}")

        scale_degrees = ScaleExercise.SCALE_FORMULAS[scale_type]

        # Generate melodic phrase using scale degrees
        phrase_intervals = [random.choice(scale_degrees) for _ in range(phrase_length)]

        return SightSingingExercise.generate_from_intervals(root_note, phrase_intervals)

    @staticmethod
    def generate_stepwise_phrase(root_note: int = 60, phrase_length: int = 5) -> Exercise:
        """
        Generate a stepwise melodic phrase (easy sight-singing).

        Args:
            root_note: Starting note
            phrase_length: Number of notes

        Returns:
            Exercise with stepwise melody
        """
        intervals = [0]  # Start at root
        current_interval = 0

        for _ in range(phrase_length - 1):
            # Step up or down by 1 or 2 semitones
            step = random.choice([-2, -1, 1, 2])
            current_interval += step
            # Keep within one octave
            current_interval = max(-6, min(6, current_interval))
            intervals.append(current_interval)

        return SightSingingExercise.generate_from_intervals(root_note, intervals)
