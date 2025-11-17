"""
Unit tests for melody imitation exercises.
"""

import pytest
from lyra_live.ear_training.melodies import MelodyImitationExercise, SCALES, MELODIC_PATTERNS
from lyra_live.ear_training.base import ExerciseType, Note


def test_melody_from_notes():
    """Test creating melody from explicit notes"""
    notes = [
        Note(60, 500),
        Note(62, 500),
        Note(64, 500),
    ]

    exercise = MelodyImitationExercise.generate(notes)

    assert exercise.type == ExerciseType.MELODY
    assert len(exercise.notes) == 3
    assert exercise.notes == notes


def test_melody_from_pattern():
    """Test generating melody from pattern"""
    exercise = MelodyImitationExercise.generate_from_pattern(
        pattern_name="ascending_scale",
        scale="major",
        root_note=60
    )

    assert exercise.type == ExerciseType.MELODY
    assert len(exercise.notes) > 0


def test_all_melodic_patterns():
    """Test all defined melodic patterns"""
    root = 60

    for pattern_name in MELODIC_PATTERNS.keys():
        exercise = MelodyImitationExercise.generate_from_pattern(
            pattern_name=pattern_name,
            scale="major",
            root_note=root
        )
        assert len(exercise.notes) > 0
        assert exercise.type == ExerciseType.MELODY


def test_random_melody_generation():
    """Test random melody generation"""
    exercise = MelodyImitationExercise.generate_random(length=6)

    assert exercise.type == ExerciseType.MELODY
    assert len(exercise.notes) == 6


def test_melody_validation_perfect_match():
    """Test melody validation with perfect match"""
    expected = [Note(60, 500), Note(62, 500), Note(64, 500)]
    actual = [Note(60, 500), Note(62, 500), Note(64, 500)]

    is_perfect, accuracy = MelodyImitationExercise.validate_sequence(expected, actual)

    assert is_perfect is True
    assert accuracy == 1.0


def test_melody_validation_partial_match():
    """Test melody validation with partial match"""
    expected = [Note(60, 500), Note(62, 500), Note(64, 500), Note(65, 500)]
    actual = [Note(60, 500), Note(62, 500), Note(63, 500), Note(65, 500)]  # One wrong

    is_perfect, accuracy = MelodyImitationExercise.validate_sequence(expected, actual)

    assert is_perfect is False
    assert accuracy == 0.75  # 3 out of 4 correct


def test_melody_validation_length_mismatch():
    """Test melody validation with length mismatch"""
    expected = [Note(60, 500), Note(62, 500), Note(64, 500)]
    actual = [Note(60, 500), Note(62, 500)]  # Too short

    is_perfect, accuracy = MelodyImitationExercise.validate_sequence(expected, actual)

    assert is_perfect is False
    assert accuracy < 1.0


def test_invalid_pattern():
    """Test that invalid pattern raises error"""
    with pytest.raises(ValueError):
        MelodyImitationExercise.generate_from_pattern(
            pattern_name="invalid_pattern",
            scale="major"
        )


def test_invalid_scale():
    """Test that invalid scale raises error"""
    with pytest.raises(ValueError):
        MelodyImitationExercise.generate_from_pattern(
            pattern_name="ascending_scale",
            scale="invalid_scale"
        )


def test_empty_melody():
    """Test that empty melody raises error"""
    with pytest.raises(ValueError):
        MelodyImitationExercise.generate([])
