"""
Unit tests for Phase 4.5: Audio-based Improvisation.

Tests the complete pipeline from pitch detection → ImprovNote conversion → analysis.
"""

import pytest
from pathlib import Path
from lyra_live.voice.pitch import PitchReading
from lyra_live.improv.audio_to_improv import (
    group_pitch_readings_into_notes,
    calculate_bar_and_beat,
    pitch_readings_to_improv_notes
)
from lyra_live.improv.audio_capture import AudioCapture, SimulatedAudioCapture
from lyra_live.improv.test_utils import AudioImprovGenerator
from lyra_live.improv.analysis import analyze_improvisation
from lyra_live.standards.core import StandardTune, ChordChange


class TestPitchReadingGrouping:
    """Test grouping pitch readings into notes"""

    def test_group_stable_pitch(self):
        """Test grouping consecutive readings of the same pitch"""
        readings = [
            PitchReading(frequency=440.0, pitch=69, confidence=0.9, timestamp_ms=0),
            PitchReading(frequency=440.0, pitch=69, confidence=0.9, timestamp_ms=10),
            PitchReading(frequency=440.0, pitch=69, confidence=0.9, timestamp_ms=20),
            PitchReading(frequency=440.0, pitch=69, confidence=0.9, timestamp_ms=30),
            PitchReading(frequency=440.0, pitch=69, confidence=0.9, timestamp_ms=40),
        ]

        notes = group_pitch_readings_into_notes(readings, min_duration_ms=20)

        # Should group into single note
        assert len(notes) == 1
        assert notes[0]['pitch'] == 69
        assert notes[0]['start_time_ms'] == 0
        assert notes[0]['duration_ms'] >= 40

    def test_filter_short_notes(self):
        """Test that very short notes are filtered out"""
        readings = [
            # Short note (50ms)
            PitchReading(frequency=440.0, pitch=69, confidence=0.9, timestamp_ms=0),
            PitchReading(frequency=440.0, pitch=69, confidence=0.9, timestamp_ms=10),
            PitchReading(frequency=440.0, pitch=69, confidence=0.9, timestamp_ms=20),
            PitchReading(frequency=440.0, pitch=69, confidence=0.9, timestamp_ms=30),
            PitchReading(frequency=440.0, pitch=69, confidence=0.9, timestamp_ms=40),

            # Silence
            PitchReading(frequency=0.0, pitch=None, confidence=0.2, timestamp_ms=50),
            PitchReading(frequency=0.0, pitch=None, confidence=0.2, timestamp_ms=60),

            # Long note (200ms)
            PitchReading(frequency=523.25, pitch=72, confidence=0.9, timestamp_ms=70),
            PitchReading(frequency=523.25, pitch=72, confidence=0.9, timestamp_ms=80),
            PitchReading(frequency=523.25, pitch=72, confidence=0.9, timestamp_ms=90),
            # ... more readings for this note
        ]

        # Add more readings for the long note
        for t in range(100, 270, 10):
            readings.append(
                PitchReading(frequency=523.25, pitch=72, confidence=0.9, timestamp_ms=t)
            )

        notes = group_pitch_readings_into_notes(readings, min_duration_ms=100)

        # Should only have the long note (2nd one >= 100ms)
        assert len(notes) == 1
        assert notes[0]['pitch'] == 72

    def test_separate_different_pitches(self):
        """Test that different pitches are separated into different notes"""
        readings = [
            # First note: C (60)
            PitchReading(frequency=261.63, pitch=60, confidence=0.9, timestamp_ms=0),
            PitchReading(frequency=261.63, pitch=60, confidence=0.9, timestamp_ms=10),
            PitchReading(frequency=261.63, pitch=60, confidence=0.9, timestamp_ms=20),
            # ... extend to 150ms
        ]

        for t in range(30, 150, 10):
            readings.append(
                PitchReading(frequency=261.63, pitch=60, confidence=0.9, timestamp_ms=t)
            )

        # Second note: E (64)
        for t in range(150, 300, 10):
            readings.append(
                PitchReading(frequency=329.63, pitch=64, confidence=0.9, timestamp_ms=t)
            )

        notes = group_pitch_readings_into_notes(readings, min_duration_ms=100)

        # Should have 2 notes
        assert len(notes) == 2
        assert notes[0]['pitch'] == 60
        assert notes[1]['pitch'] == 64

    def test_skip_invalid_readings(self):
        """Test that invalid/silent readings are skipped"""
        readings = [
            PitchReading(frequency=440.0, pitch=69, confidence=0.9, timestamp_ms=0),
            PitchReading(frequency=440.0, pitch=69, confidence=0.9, timestamp_ms=10),

            # Invalid readings (no pitch detected)
            PitchReading(frequency=0.0, pitch=None, confidence=0.2, timestamp_ms=20),
            PitchReading(frequency=0.0, pitch=None, confidence=0.2, timestamp_ms=30),

            PitchReading(frequency=440.0, pitch=69, confidence=0.9, timestamp_ms=40),
            PitchReading(frequency=440.0, pitch=69, confidence=0.9, timestamp_ms=50),
        ]

        # Extend both note segments to meet min duration
        for t in range(60, 120, 10):
            readings.insert(2, PitchReading(frequency=440.0, pitch=69, confidence=0.9, timestamp_ms=t))

        notes = group_pitch_readings_into_notes(readings, min_duration_ms=50)

        # Should skip the silent readings and group valid ones
        assert len(notes) >= 1


class TestBarBeatCalculation:
    """Test bar and beat position calculations"""

    def test_calculate_bar_beat_4_4(self):
        """Test bar/beat calculation in 4/4 time"""
        tempo = 120  # BPM
        time_sig = (4, 4)

        # At time 0: bar 0, beat 1
        bar, beat = calculate_bar_and_beat(0, tempo, time_sig)
        assert bar == 0
        assert beat == 1.0

        # After 500ms (1 beat at 120 BPM): bar 0, beat 2
        bar, beat = calculate_bar_and_beat(500, tempo, time_sig)
        assert bar == 0
        assert 1.9 < beat < 2.1  # Allow small float precision

        # After 2000ms (4 beats = 1 bar): bar 1, beat 1
        bar, beat = calculate_bar_and_beat(2000, tempo, time_sig)
        assert bar == 1
        assert 0.9 < beat < 1.1

    def test_calculate_bar_beat_different_tempo(self):
        """Test bar/beat calculation at different tempos"""
        time_sig = (4, 4)

        # 60 BPM (slower - 1 beat per second)
        bar, beat = calculate_bar_and_beat(1000, 60, time_sig)
        assert bar == 0
        assert 1.9 < beat < 2.1

        # 240 BPM (faster - 4 beats per second)
        bar, beat = calculate_bar_and_beat(1000, 240, time_sig)
        assert bar == 1
        assert 0.9 < beat < 1.1


class TestPitchToImprovNoteConversion:
    """Test converting pitch readings to ImprovNote objects"""

    def test_convert_simple_melody(self):
        """Test converting a simple melody to ImprovNotes"""
        # Create a simple tune
        tune = StandardTune(
            id="test_conv",
            title="Test Conversion",
            key="C",
            tempo=120,
            form="test",
            chorus_length_bars=4,
            time_signature=(4, 4),
            chord_changes=[ChordChange(0, 1.0, "Cmaj7", 16.0)]
        )

        # Create pitch readings for a simple melody: C - E - G (arpeggiated Cmaj7)
        readings = []

        # C (60) for 500ms
        for t in range(0, 500, 10):
            readings.append(
                PitchReading(frequency=261.63, pitch=60, confidence=0.9, timestamp_ms=t)
            )

        # E (64) for 500ms
        for t in range(500, 1000, 10):
            readings.append(
                PitchReading(frequency=329.63, pitch=64, confidence=0.9, timestamp_ms=t)
            )

        # G (67) for 500ms
        for t in range(1000, 1500, 10):
            readings.append(
                PitchReading(frequency=392.00, pitch=67, confidence=0.9, timestamp_ms=t)
            )

        # Convert to ImprovNotes
        improv_notes = pitch_readings_to_improv_notes(readings, tune, min_duration_ms=200)

        # Should have 3 notes
        assert len(improv_notes) == 3

        # Check pitches
        assert improv_notes[0].pitch == 60
        assert improv_notes[1].pitch == 64
        assert improv_notes[2].pitch == 67

        # Check that chord context is set
        for note in improv_notes:
            assert note.chord_at_time == "Cmaj7"


class TestAudioImprovAnalysis:
    """Test end-to-end audio improvisation analysis"""

    def test_analyze_chord_tone_solo(self):
        """Test analysis of a chord-tone-focused audio solo"""
        generator = AudioImprovGenerator(seed=123)

        # Create a simple tune
        tune = StandardTune(
            id="test_blues_audio",
            title="Test Blues (Audio)",
            key="F",
            tempo=120,
            form="blues",
            chorus_length_bars=12,
            time_signature=(4, 4),
            chord_changes=[
                ChordChange(0, 1.0, "F7", 4.0),
                ChordChange(1, 1.0, "F7", 4.0),
                ChordChange(2, 1.0, "F7", 4.0),
                ChordChange(3, 1.0, "F7", 4.0),
                ChordChange(4, 1.0, "Bb7", 4.0),
                ChordChange(5, 1.0, "Bb7", 4.0),
                ChordChange(6, 1.0, "F7", 4.0),
                ChordChange(7, 1.0, "F7", 4.0),
                ChordChange(8, 1.0, "C7", 4.0),
                ChordChange(9, 1.0, "Bb7", 4.0),
                ChordChange(10, 1.0, "F7", 4.0),
                ChordChange(11, 1.0, "C7", 4.0),
            ]
        )

        # Generate synthetic solo with mostly chord tones
        chorus = generator.generate_audio_blues_solo(tune, style="chord_tones")

        # Analyze
        result = analyze_improvisation(chorus)

        # Should have high chord-tone ratio
        assert result.harmonic_stats.chord_tone_ratio > 50

        # Should have reasonable score
        assert 0 <= result.overall_score <= 100

        # Should have feedback
        assert len(result.feedback) > 0

    def test_analyze_different_styles(self):
        """Test that analysis distinguishes between different solo styles"""
        generator = AudioImprovGenerator(seed=456)

        # Create a simple tune
        tune = StandardTune(
            id="test_standard_audio",
            title="Test Standard (Audio)",
            key="C",
            tempo=140,
            form="AABA",
            chorus_length_bars=4,
            time_signature=(4, 4),
            chord_changes=[
                ChordChange(0, 1.0, "Dm7", 4.0),
                ChordChange(1, 1.0, "G7", 4.0),
                ChordChange(2, 1.0, "Cmaj7", 4.0),
                ChordChange(3, 1.0, "Cmaj7", 4.0),
            ]
        )

        # Generate chord-tone solo
        chorus_inside = generator.generate_audio_standard_solo(tune, style="chord_tones")
        result_inside = analyze_improvisation(chorus_inside)

        # Generate outside solo
        chorus_outside = generator.generate_audio_standard_solo(tune, style="outside")
        result_outside = analyze_improvisation(chorus_outside)

        # Chord-tone solo should have higher chord-tone ratio
        assert result_inside.harmonic_stats.chord_tone_ratio > result_outside.harmonic_stats.chord_tone_ratio

        # Outside solo should have higher outside ratio
        assert result_outside.harmonic_stats.outside_ratio > result_inside.harmonic_stats.outside_ratio


class TestAudioCapture:
    """Test audio capture functionality"""

    def test_duration_calculation(self):
        """Test calculating recording duration from tune parameters"""
        capture = AudioCapture()

        # 12-bar blues at 120 BPM in 4/4 time
        # 12 bars * 4 beats = 48 beats
        # At 120 BPM: 48 beats / 120 BPM * 60 sec/min = 24 seconds
        duration = capture.calculate_duration(
            tune_tempo=120,
            time_signature=(4, 4),
            chorus_bars=12,
            chorus_count=1
        )

        # Should be ~24 seconds (plus small buffer)
        assert 24.0 < duration < 25.0

    def test_duration_multiple_choruses(self):
        """Test duration calculation for multiple choruses"""
        capture = AudioCapture()

        # 3 choruses of 32-bar AABA at 140 BPM in 4/4
        # 32 bars * 4 beats * 3 choruses = 384 beats
        # At 140 BPM: 384 / 140 * 60 = 164.57 seconds
        duration = capture.calculate_duration(
            tune_tempo=140,
            time_signature=(4, 4),
            chorus_bars=32,
            chorus_count=3
        )

        # Should be ~164-165 seconds
        assert 164.0 < duration < 166.0

    def test_simulated_audio_capture(self):
        """Test simulated audio capture for testing"""
        sim_capture = SimulatedAudioCapture()

        # Should generate silent audio without requiring microphone
        audio_path = sim_capture.record(duration_seconds=1.0)

        # File should exist
        assert audio_path.exists()

        # Should be a WAV file
        assert audio_path.suffix == '.wav'

        # Clean up
        import os
        os.unlink(audio_path)


class TestAudioImprovGeneratorTests:
    """Test synthetic audio improvisation generator"""

    def test_generator_creates_notes(self):
        """Test that generator creates valid ImprovChorus"""
        generator = AudioImprovGenerator(seed=42)

        tune = StandardTune(
            id="test_gen",
            title="Test Generator",
            key="C",
            tempo=120,
            form="AABA",
            chorus_length_bars=4,
            time_signature=(4, 4),
            chord_changes=[ChordChange(0, 1.0, "Cmaj7", 16.0)]
        )

        chorus = generator.generate_audio_standard_solo(tune, style="chord_tones")

        # Should have notes
        assert len(chorus.notes) > 0

        # Notes should have required fields
        for note in chorus.notes:
            assert note.pitch is not None
            assert note.time_ms >= 0
            assert note.duration_ms > 0

    def test_generator_reproducibility(self):
        """Test that generator with same seed produces same results"""
        tune = StandardTune(
            id="test_repro",
            title="Test Reproducibility",
            key="F",
            tempo=120,
            form="blues",
            chorus_length_bars=12,
            time_signature=(4, 4),
            chord_changes=[ChordChange(0, 1.0, "F7", 48.0)]
        )

        gen1 = AudioImprovGenerator(seed=100)
        chorus1 = gen1.generate_audio_blues_solo(tune, style="chord_tones")

        gen2 = AudioImprovGenerator(seed=100)
        chorus2 = gen2.generate_audio_blues_solo(tune, style="chord_tones")

        # Should have same number of notes
        assert len(chorus1.notes) == len(chorus2.notes)

        # First few notes should have same pitches
        for n1, n2 in zip(chorus1.notes[:5], chorus2.notes[:5]):
            assert n1.pitch == n2.pitch
