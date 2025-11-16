"""
Unit tests for voice exercises.
"""

import pytest
from lyra_live.voice.exercises import (
    PitchMatchExercise,
    ScaleExercise,
    SightSingingExercise,
    VoiceResult
)
from lyra_live.voice.pitch import frequency_to_midi, midi_to_frequency
from lyra_live.ear_training.base import ExerciseType, Note


def test_frequency_conversion():
    """Test frequency to MIDI conversion"""
    # A4 = 440 Hz = MIDI 69
    assert frequency_to_midi(440.0) == 69

    # C4 = ~261.63 Hz = MIDI 60
    assert frequency_to_midi(261.63) == 60

    # Round trip
    for midi_note in range(60, 72):
        freq = midi_to_frequency(midi_note)
        assert frequency_to_midi(freq) == midi_note


def test_pitch_match_generation():
    """Test pitch matching exercise generation"""
    exercise = PitchMatchExercise.generate(60)

    assert exercise.type == ExerciseType.VOICE_PITCH_MATCH
    assert len(exercise.notes) == 1
    assert exercise.notes[0].pitch == 60
    assert exercise.metadata["target_pitch"] == 60
    assert exercise.metadata["tolerance_cents"] == 50


def test_pitch_match_random():
    """Test random pitch matching exercise"""
    exercise = PitchMatchExercise.generate_random(min_pitch=60, max_pitch=72)

    assert exercise.type == ExerciseType.VOICE_PITCH_MATCH
    assert len(exercise.notes) == 1
    assert 60 <= exercise.notes[0].pitch <= 72


def test_pitch_match_validation_correct():
    """Test pitch match validation with correct pitch"""
    result = PitchMatchExercise.validate(
        target_pitch=60,
        sung_pitch=60,
        cents_deviation=0.0,
        tolerance_cents=50
    )

    assert result.correct is True
    assert result.target_pitch == 60
    assert result.sung_pitch == 60
    assert result.accuracy_percentage == 100.0


def test_pitch_match_validation_slightly_off():
    """Test pitch match validation with slightly off pitch"""
    result = PitchMatchExercise.validate(
        target_pitch=60,
        sung_pitch=60,
        cents_deviation=30.0,  # 30 cents sharp
        tolerance_cents=50
    )

    assert result.correct is True  # Within tolerance
    assert result.accuracy_percentage == 70.0  # 100 - 30


def test_pitch_match_validation_too_far():
    """Test pitch match validation with pitch too far off"""
    result = PitchMatchExercise.validate(
        target_pitch=60,
        sung_pitch=61,
        cents_deviation=100.0,  # 100 cents = semitone
        tolerance_cents=50
    )

    assert result.correct is False
    assert result.accuracy_percentage == 0.0


def test_pitch_match_validation_no_input():
    """Test pitch match validation with no pitch detected"""
    result = PitchMatchExercise.validate(
        target_pitch=60,
        sung_pitch=None,
        cents_deviation=None,
        tolerance_cents=50
    )

    assert result.correct is False
    assert result.sung_pitch is None
    assert result.accuracy_percentage == 0.0


def test_scale_generation():
    """Test scale exercise generation"""
    exercise = ScaleExercise.generate("major", root_note=60)

    assert exercise.type == ExerciseType.VOICE_SCALE
    assert len(exercise.notes) == 8  # Major scale has 8 notes (including octave)
    assert exercise.notes[0].pitch == 60  # Root
    assert exercise.notes[-1].pitch == 72  # Octave
    assert exercise.metadata["scale_type"] == "major"


def test_minor_scale_generation():
    """Test natural minor scale generation"""
    exercise = ScaleExercise.generate("natural_minor", root_note=60)

    assert len(exercise.notes) == 8
    expected_pitches = [60, 62, 63, 65, 67, 68, 70, 72]  # Natural minor
    actual_pitches = [n.pitch for n in exercise.notes]
    assert actual_pitches == expected_pitches


def test_pentatonic_scale_generation():
    """Test pentatonic scale generation"""
    exercise = ScaleExercise.generate("major_pentatonic", root_note=60)

    assert len(exercise.notes) == 6  # Pentatonic has 6 notes
    expected_pitches = [60, 62, 64, 67, 69, 72]
    actual_pitches = [n.pitch for n in exercise.notes]
    assert actual_pitches == expected_pitches


def test_scale_validation_perfect():
    """Test scale validation with perfect performance"""
    expected_notes = [Note(60, 1000), Note(62, 1000), Note(64, 1000)]
    sung_pitches = [60, 62, 64]

    is_perfect, accuracy, feedback = ScaleExercise.validate_sequence(
        expected_notes, sung_pitches
    )

    assert is_perfect is True
    assert accuracy == 100.0


def test_scale_validation_partial():
    """Test scale validation with partial accuracy"""
    expected_notes = [Note(60, 1000), Note(62, 1000), Note(64, 1000), Note(65, 1000)]
    sung_pitches = [60, 62, 63, 65]  # Third note is wrong

    is_perfect, accuracy, feedback = ScaleExercise.validate_sequence(
        expected_notes, sung_pitches
    )

    assert is_perfect is False
    assert accuracy == 75.0  # 3 out of 4 correct


def test_scale_validation_wrong_length():
    """Test scale validation with wrong number of notes"""
    expected_notes = [Note(60, 1000), Note(62, 1000), Note(64, 1000)]
    sung_pitches = [60, 62]  # Missing one note

    is_perfect, accuracy, feedback = ScaleExercise.validate_sequence(
        expected_notes, sung_pitches
    )

    assert is_perfect is False
    assert accuracy == 0.0


def test_sight_singing_from_intervals():
    """Test sight-singing exercise from intervals"""
    exercise = SightSingingExercise.generate_from_intervals(
        root_note=60,
        intervals=[0, 2, 4, 5, 4, 2, 0]  # Simple melodic phrase
    )

    assert exercise.type == ExerciseType.VOICE_SIGHT_SINGING
    assert len(exercise.notes) == 7
    expected_pitches = [60, 62, 64, 65, 64, 62, 60]
    actual_pitches = [n.pitch for n in exercise.notes]
    assert actual_pitches == expected_pitches


def test_sight_singing_diatonic_phrase():
    """Test diatonic phrase generation"""
    exercise = SightSingingExercise.generate_diatonic_phrase(
        scale_type="major",
        root_note=60,
        phrase_length=4
    )

    assert exercise.type == ExerciseType.VOICE_SIGHT_SINGING
    assert len(exercise.notes) == 4

    # All notes should be within major scale
    major_scale = {60, 62, 64, 65, 67, 69, 71, 72}
    for note in exercise.notes:
        assert note.pitch in major_scale


def test_sight_singing_stepwise_phrase():
    """Test stepwise phrase generation"""
    exercise = SightSingingExercise.generate_stepwise_phrase(
        root_note=60,
        phrase_length=5
    )

    assert exercise.type == ExerciseType.VOICE_SIGHT_SINGING
    assert len(exercise.notes) == 5

    # Check that intervals between notes are stepwise (1 or 2 semitones)
    for i in range(len(exercise.notes) - 1):
        interval = abs(exercise.notes[i+1].pitch - exercise.notes[i].pitch)
        assert interval <= 2, f"Interval {interval} is too large for stepwise motion"


def test_invalid_scale_type():
    """Test that invalid scale type raises error"""
    with pytest.raises(ValueError):
        ScaleExercise.generate("invalid_scale", root_note=60)


def test_random_scale_generation():
    """Test random scale generation"""
    exercise = ScaleExercise.generate_random()

    assert exercise.type == ExerciseType.VOICE_SCALE
    assert len(exercise.notes) >= 3  # At least a few notes


def test_all_scale_types():
    """Test all defined scale types"""
    root = 60

    for scale_type in ScaleExercise.SCALE_FORMULAS.keys():
        exercise = ScaleExercise.generate(scale_type, root_note=root)

        assert exercise.type == ExerciseType.VOICE_SCALE
        assert len(exercise.notes) > 0
        assert exercise.notes[0].pitch == root
