"""
Unit tests for chord quality exercises.
"""

import pytest
from lyra_live.ear_training.chords import ChordQualityExercise, CHORD_FORMULAS
from lyra_live.ear_training.base import ExerciseType, Note


def test_major_chord_generation():
    """Test major chord generation"""
    exercise = ChordQualityExercise.generate("major", root_note=60)

    assert exercise.type == ExerciseType.CHORD
    assert len(exercise.notes) == 3
    assert exercise.notes[0].pitch == 60  # Root
    assert exercise.notes[1].pitch == 64  # Major third (60 + 4)
    assert exercise.notes[2].pitch == 67  # Perfect fifth (60 + 7)


def test_minor_chord_generation():
    """Test minor chord generation"""
    exercise = ChordQualityExercise.generate("minor", root_note=60)

    assert len(exercise.notes) == 3
    assert exercise.notes[0].pitch == 60  # Root
    assert exercise.notes[1].pitch == 63  # Minor third (60 + 3)
    assert exercise.notes[2].pitch == 67  # Perfect fifth (60 + 7)


def test_seventh_chord_generation():
    """Test 7th chord generation"""
    exercise = ChordQualityExercise.generate("dominant_7", root_note=60)

    assert len(exercise.notes) == 4
    assert exercise.notes[0].pitch == 60  # Root
    assert exercise.notes[1].pitch == 64  # Major third
    assert exercise.notes[2].pitch == 67  # Perfect fifth
    assert exercise.notes[3].pitch == 70  # Minor seventh


def test_all_chord_types():
    """Test all defined chord types"""
    root = 60

    for chord_type, formula in CHORD_FORMULAS.items():
        exercise = ChordQualityExercise.generate(chord_type, root_note=root)

        assert len(exercise.notes) == len(formula)
        for i, interval in enumerate(formula):
            assert exercise.notes[i].pitch == root + interval


def test_random_chord_generation():
    """Test random chord generation"""
    exercise = ChordQualityExercise.generate_random()

    assert len(exercise.notes) >= 3  # At least a triad
    assert exercise.type == ExerciseType.CHORD


def test_chord_quality_identification():
    """Test identifying chord quality from notes"""
    # Major chord
    notes = [Note(60, 1000), Note(64, 1000), Note(67, 1000)]
    quality = ChordQualityExercise.identify_chord_quality(notes)
    assert quality == "major"

    # Minor chord
    notes = [Note(60, 1000), Note(63, 1000), Note(67, 1000)]
    quality = ChordQualityExercise.identify_chord_quality(notes)
    assert quality == "minor"


def test_invalid_chord_type():
    """Test that invalid chord type raises error"""
    with pytest.raises(ValueError):
        ChordQualityExercise.generate("invalid_chord", root_note=60)


def test_chord_name_lookup():
    """Test chord name lookup"""
    assert ChordQualityExercise.get_chord_name("major") == "major"
    assert ChordQualityExercise.get_chord_name("dominant_7") == "dominant 7th"
