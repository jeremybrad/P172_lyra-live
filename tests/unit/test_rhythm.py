"""
Unit tests for rhythm exercises.
"""

import pytest
from lyra_live.ear_training.rhythm import (
    Beat,
    RhythmGrid,
    RhythmExercise,
    RhythmResult,
    RhythmExerciseGenerator,
    RhythmValidator
)


def test_beat_creation():
    """Test Beat dataclass creation"""
    beat = Beat(time_ms=500, drum_part="snare", velocity=80)

    assert beat.time_ms == 500
    assert beat.drum_part == "snare"
    assert beat.velocity == 80
    assert beat.subdivision is None


def test_rhythm_grid_creation():
    """Test RhythmGrid creation"""
    grid = RhythmGrid(
        tempo_bpm=120,
        time_signature=(4, 4),
        num_bars=2,
        beats=[]
    )

    assert grid.tempo_bpm == 120
    assert grid.time_signature == (4, 4)
    assert grid.num_bars == 2


def test_rhythm_grid_duration():
    """Test RhythmGrid duration calculation"""
    # 120 BPM = 500ms per beat
    # 4/4 time, 2 bars = 8 beats = 4000ms
    grid = RhythmGrid(
        tempo_bpm=120,
        time_signature=(4, 4),
        num_bars=2,
        beats=[]
    )

    assert grid.get_duration_ms() == 4000


def test_rhythm_grid_duration_different_tempo():
    """Test duration with different tempo"""
    # 60 BPM = 1000ms per beat
    # 4/4 time, 1 bar = 4 beats = 4000ms
    grid = RhythmGrid(
        tempo_bpm=60,
        time_signature=(4, 4),
        num_bars=1,
        beats=[]
    )

    assert grid.get_duration_ms() == 4000


def test_straight_quarter_pattern():
    """Test straight quarter note pattern generation"""
    exercise = RhythmExerciseGenerator.generate_straight_pattern(
        drum_part="snare",
        subdivision="quarter",
        tempo_bpm=120,
        num_bars=1
    )

    assert len(exercise.grid.beats) == 4  # 4 quarter notes per bar
    assert all(b.drum_part == "snare" for b in exercise.grid.beats)

    # Check timing: 120 BPM = 500ms per beat
    expected_times = [0, 500, 1000, 1500]
    actual_times = [b.time_ms for b in exercise.grid.beats]
    assert actual_times == expected_times


def test_straight_eighth_pattern():
    """Test straight eighth note pattern generation"""
    exercise = RhythmExerciseGenerator.generate_straight_pattern(
        drum_part="kick",
        subdivision="eighth",
        tempo_bpm=120,
        num_bars=1
    )

    assert len(exercise.grid.beats) == 8  # 8 eighth notes per bar
    assert all(b.drum_part == "kick" for b in exercise.grid.beats)

    # Check timing: eighth notes at 250ms intervals
    expected_times = [0, 250, 500, 750, 1000, 1250, 1500, 1750]
    actual_times = [b.time_ms for b in exercise.grid.beats]
    assert actual_times == expected_times


def test_straight_sixteenth_pattern():
    """Test straight sixteenth note pattern generation"""
    exercise = RhythmExerciseGenerator.generate_straight_pattern(
        drum_part="hi_hat",
        subdivision="sixteenth",
        tempo_bpm=120,
        num_bars=1
    )

    assert len(exercise.grid.beats) == 16  # 16 sixteenth notes per bar
    assert all(b.drum_part == "hi_hat" for b in exercise.grid.beats)


def test_backbeat_pattern():
    """Test backbeat pattern generation"""
    exercise = RhythmExerciseGenerator.generate_backbeat_pattern(
        tempo_bpm=120,
        num_bars=1
    )

    # Backbeat has kick on 1&3, snare on 2&4
    # Should have 4 beats total in one bar
    assert len(exercise.grid.beats) == 4

    # Check drum parts (added as kick, kick, snare, snare)
    drum_parts = [b.drum_part for b in exercise.grid.beats]
    expected_parts = ["kick", "kick", "snare", "snare"]
    assert drum_parts == expected_parts

    # Check timing (120 BPM = 500ms per beat)
    # kick on 1 (0ms), kick on 3 (1000ms), snare on 2 (500ms), snare on 4 (1500ms)
    expected_times = [0, 1000, 500, 1500]
    actual_times = [b.time_ms for b in exercise.grid.beats]
    assert actual_times == expected_times


def test_syncopated_pattern():
    """Test syncopated pattern generation"""
    exercise = RhythmExerciseGenerator.generate_syncopated_pattern(
        drum_part="snare",
        complexity=1,
        tempo_bpm=120,
        num_bars=1
    )

    # Complexity 1 has 2 hits (beat 1 and "and" of beat 3)
    assert len(exercise.grid.beats) == 2
    assert all(b.drum_part == "snare" for b in exercise.grid.beats)

    # Check timing: 120 BPM = 500ms per beat
    # Beat 1 = 0ms, "and" of beat 3 = 1250ms (2.5 beats)
    expected_times = [0, 1250]
    actual_times = [b.time_ms for b in exercise.grid.beats]
    assert actual_times == expected_times


def test_rhythm_validation_perfect():
    """Test rhythm validation with perfect timing"""
    # Create expected grid
    grid = RhythmGrid(
        tempo_bpm=120,
        time_signature=(4, 4),
        num_bars=1,
        beats=[
            Beat(0, "snare", 80),
            Beat(500, "snare", 80),
            Beat(1000, "snare", 80),
            Beat(1500, "snare", 80)
        ]
    )

    # Perfect actual hits
    actual_hits = [
        Beat(0, "snare", 80),
        Beat(500, "snare", 80),
        Beat(1000, "snare", 80),
        Beat(1500, "snare", 80)
    ]

    result = RhythmValidator.validate_rhythm(
        expected_grid=grid,
        actual_hits=actual_hits,
        tolerance_ms=50,
        drum_part_filter="snare"
    )

    assert result.correct_hits == 4
    assert result.total_expected_hits == 4
    assert result.total_actual_hits == 4
    assert result.accuracy_percentage == 100.0
    assert result.average_timing_error_ms == 0.0


def test_rhythm_validation_rushing():
    """Test rhythm validation with rushing (early hits)"""
    grid = RhythmGrid(
        tempo_bpm=120,
        time_signature=(4, 4),
        num_bars=1,
        beats=[
            Beat(0, "snare", 80),
            Beat(500, "snare", 80),
            Beat(1000, "snare", 80)
        ]
    )

    # Hits are 20ms early (rushing)
    actual_hits = [
        Beat(-20, "snare", 80),
        Beat(480, "snare", 80),
        Beat(980, "snare", 80)
    ]

    result = RhythmValidator.validate_rhythm(
        expected_grid=grid,
        actual_hits=actual_hits,
        tolerance_ms=50
    )

    assert result.correct_hits == 3
    assert result.average_timing_error_ms < 0  # Negative = early/rushing
    assert abs(result.average_timing_error_ms - (-20)) < 5  # Approximately -20ms


def test_rhythm_validation_dragging():
    """Test rhythm validation with dragging (late hits)"""
    grid = RhythmGrid(
        tempo_bpm=120,
        time_signature=(4, 4),
        num_bars=1,
        beats=[
            Beat(0, "snare", 80),
            Beat(500, "snare", 80)
        ]
    )

    # Hits are 25ms late (dragging)
    actual_hits = [
        Beat(25, "snare", 80),
        Beat(525, "snare", 80)
    ]

    result = RhythmValidator.validate_rhythm(
        expected_grid=grid,
        actual_hits=actual_hits,
        tolerance_ms=50
    )

    assert result.correct_hits == 2
    assert result.average_timing_error_ms > 0  # Positive = late/dragging
    assert abs(result.average_timing_error_ms - 25) < 5  # Approximately 25ms


def test_rhythm_validation_missed_hits():
    """Test rhythm validation with missed hits"""
    grid = RhythmGrid(
        tempo_bpm=120,
        time_signature=(4, 4),
        num_bars=1,
        beats=[
            Beat(0, "snare", 80),
            Beat(500, "snare", 80),
            Beat(1000, "snare", 80),
            Beat(1500, "snare", 80)
        ]
    )

    # Only hit 2 out of 4
    actual_hits = [
        Beat(0, "snare", 80),
        Beat(1000, "snare", 80)
    ]

    result = RhythmValidator.validate_rhythm(
        expected_grid=grid,
        actual_hits=actual_hits,
        tolerance_ms=50
    )

    assert result.total_expected_hits == 4
    assert result.total_actual_hits == 2
    assert result.correct_hits == 2
    assert result.missed_hits == 2
    assert result.accuracy_percentage == 50.0


def test_rhythm_validation_extra_hits():
    """Test rhythm validation with extra hits"""
    grid = RhythmGrid(
        tempo_bpm=120,
        time_signature=(4, 4),
        num_bars=1,
        beats=[
            Beat(0, "snare", 80),
            Beat(500, "snare", 80)
        ]
    )

    # Hit expected notes plus extras
    actual_hits = [
        Beat(0, "snare", 80),
        Beat(250, "snare", 80),  # Extra
        Beat(500, "snare", 80),
        Beat(750, "snare", 80)   # Extra
    ]

    result = RhythmValidator.validate_rhythm(
        expected_grid=grid,
        actual_hits=actual_hits,
        tolerance_ms=50
    )

    assert result.total_expected_hits == 2
    assert result.total_actual_hits == 4
    assert result.correct_hits == 2
    assert result.extra_hits == 2


def test_rhythm_validation_out_of_tolerance():
    """Test rhythm validation with hits outside tolerance window"""
    grid = RhythmGrid(
        tempo_bpm=120,
        time_signature=(4, 4),
        num_bars=1,
        beats=[
            Beat(0, "snare", 80),
            Beat(500, "snare", 80)
        ]
    )

    # Second hit is 100ms late (outside ±50ms tolerance)
    actual_hits = [
        Beat(0, "snare", 80),
        Beat(600, "snare", 80)
    ]

    result = RhythmValidator.validate_rhythm(
        expected_grid=grid,
        actual_hits=actual_hits,
        tolerance_ms=50
    )

    assert result.correct_hits == 1  # Only first hit is correct
    assert result.total_expected_hits == 2


def test_drum_part_filter():
    """Test rhythm validation with drum part filtering"""
    grid = RhythmGrid(
        tempo_bpm=120,
        time_signature=(4, 4),
        num_bars=1,
        beats=[
            Beat(0, "snare", 80),
            Beat(500, "kick", 80),
            Beat(1000, "snare", 80)
        ]
    )

    # Play both snare and kick
    actual_hits = [
        Beat(0, "snare", 80),
        Beat(500, "kick", 80),
        Beat(1000, "snare", 80)
    ]

    # Filter for snare only
    result = RhythmValidator.validate_rhythm(
        expected_grid=grid,
        actual_hits=actual_hits,
        tolerance_ms=50,
        drum_part_filter="snare"
    )

    # Should only count 2 snare hits
    assert result.total_expected_hits == 2
    assert result.total_actual_hits == 2
    assert result.correct_hits == 2


def test_invalid_subdivision_defaults_to_quarter():
    """Test that invalid subdivision defaults to quarter notes"""
    exercise = RhythmExerciseGenerator.generate_straight_pattern(
        drum_part="snare",
        subdivision="invalid",
        tempo_bpm=120,
        num_bars=1
    )

    # Should default to quarter notes (4 per bar)
    assert len(exercise.grid.beats) == 4


def test_multiple_bars():
    """Test pattern generation across multiple bars"""
    exercise = RhythmExerciseGenerator.generate_straight_pattern(
        drum_part="snare",
        subdivision="quarter",
        tempo_bpm=120,
        num_bars=2
    )

    # 4 quarter notes per bar × 2 bars = 8 beats
    assert len(exercise.grid.beats) == 8
    assert exercise.grid.num_bars == 2


def test_different_time_signatures():
    """Test RhythmGrid with different time signature"""
    # 3/4 time
    grid = RhythmGrid(
        tempo_bpm=120,
        time_signature=(3, 4),
        num_bars=1,
        beats=[]
    )

    # 3 beats per bar at 120 BPM = 1500ms
    assert grid.get_duration_ms() == 1500
