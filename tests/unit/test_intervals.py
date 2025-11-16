"""
Unit tests for interval exercise generation.
"""

import pytest
from lyra_live.ear_training.intervals import IntervalExercise, INTERVALS
from lyra_live.ear_training.base import ExerciseType


def test_interval_generation():
    """Test interval exercise generation with specific interval"""
    exercise = IntervalExercise.generate("perfect_fifth", root_note=60)

    assert exercise.type == ExerciseType.INTERVAL
    assert len(exercise.notes) == 2
    assert exercise.notes[0].pitch == 60
    assert exercise.notes[1].pitch == 67  # 60 + 7 semitones
    assert exercise.notes[0].role == "root"
    assert exercise.notes[1].role == "interval"


def test_all_intervals():
    """Test that all defined intervals generate correctly"""
    root = 60

    for interval_name, semitones in INTERVALS.items():
        exercise = IntervalExercise.generate(interval_name, root_note=root)

        assert len(exercise.notes) == 2
        assert exercise.notes[0].pitch == root
        assert exercise.notes[1].pitch == root + semitones
        assert exercise.id == f"interval_{interval_name}_{root}"


def test_random_interval():
    """Test random interval generation"""
    exercise = IntervalExercise.generate_random()

    assert len(exercise.notes) == 2
    assert 48 <= exercise.notes[0].pitch <= 72  # Within expected range
    assert exercise.type == ExerciseType.INTERVAL


def test_random_interval_custom_range():
    """Test random interval with custom root range"""
    exercise = IntervalExercise.generate_random(root_range=(36, 48))

    assert len(exercise.notes) == 2
    assert 36 <= exercise.notes[0].pitch <= 48


def test_invalid_interval_type():
    """Test that invalid interval type raises error"""
    with pytest.raises(ValueError):
        IntervalExercise.generate("invalid_interval", root_note=60)


def test_interval_name_lookup():
    """Test interval name lookup function"""
    assert IntervalExercise.get_interval_name(0) == "unison"
    assert IntervalExercise.get_interval_name(7) == "perfect fifth"
    assert IntervalExercise.get_interval_name(12) == "octave"
    assert IntervalExercise.get_interval_name(15) == "15 semitones"  # Unknown interval
