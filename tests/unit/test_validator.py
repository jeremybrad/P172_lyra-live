"""
Unit tests for exercise validation logic.
"""

import pytest
from lyra_live.ear_training.base import Note
from lyra_live.ear_training.validator import ExerciseValidator


def test_correct_interval():
    """Test validation with correct interval"""
    expected = [Note(60, 1000), Note(67, 1000)]  # Perfect fifth
    actual = [Note(48, 1000), Note(55, 1000)]    # Same interval, different octave

    result = ExerciseValidator.validate_interval(expected, actual)

    assert result.correct
    assert "Correct" in result.feedback
    assert "perfect fifth" in result.feedback


def test_incorrect_interval():
    """Test validation with wrong interval"""
    expected = [Note(60, 1000), Note(67, 1000)]  # Perfect fifth (7 semitones)
    actual = [Note(60, 1000), Note(64, 1000)]    # Major third (4 semitones)

    result = ExerciseValidator.validate_interval(expected, actual)

    assert not result.correct
    assert "Not quite" in result.feedback


def test_too_many_notes():
    """Test validation with too many notes"""
    expected = [Note(60, 1000), Note(67, 1000)]
    actual = [Note(60, 1000), Note(64, 1000), Note(67, 1000)]  # 3 notes instead of 2

    result = ExerciseValidator.validate_interval(expected, actual)

    assert not result.correct
    assert "Expected 2 notes, got 3" in result.feedback


def test_too_few_notes():
    """Test validation with too few notes"""
    expected = [Note(60, 1000), Note(67, 1000)]
    actual = [Note(60, 1000)]  # Only 1 note

    result = ExerciseValidator.validate_interval(expected, actual)

    assert not result.correct
    assert "Expected 2 notes, got 1" in result.feedback


def test_unison_interval():
    """Test validation of unison (0 semitones)"""
    expected = [Note(60, 1000), Note(60, 1000)]
    actual = [Note(48, 1000), Note(48, 1000)]

    result = ExerciseValidator.validate_interval(expected, actual)

    assert result.correct
    assert "unison" in result.feedback


def test_octave_interval():
    """Test validation of octave (12 semitones)"""
    expected = [Note(60, 1000), Note(72, 1000)]
    actual = [Note(48, 1000), Note(60, 1000)]

    result = ExerciseValidator.validate_interval(expected, actual)

    assert result.correct
    assert "octave" in result.feedback


def test_descending_interval():
    """Test validation with descending interval"""
    expected = [Note(67, 1000), Note(60, 1000)]  # Descending perfect fifth (-7)
    actual = [Note(55, 1000), Note(48, 1000)]    # Same descending interval

    result = ExerciseValidator.validate_interval(expected, actual)

    assert result.correct
