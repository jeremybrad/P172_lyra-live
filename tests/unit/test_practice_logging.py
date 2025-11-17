"""
Unit tests for Phase 5: Practice Logging & Progress Tracking.

Tests logging, stats computation, journal generation, and gamification.
"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path
from lyra_live.logging.practice_log import (
    PracticeSessionRecord,
    append_session,
    load_sessions,
    clear_log
)
from lyra_live.logging import progress_stats, gamification
from lyra_live.logging.teacher_journal import generate_teacher_entry


@pytest.fixture
def clean_log():
    """Ensure log is empty before and after tests."""
    clear_log()
    yield
    clear_log()


@pytest.fixture
def sample_sessions():
    """Create a sample set of practice sessions for testing."""
    # Use dates ending today for streak to work
    base_time = datetime.now() - timedelta(days=6)

    sessions = []

    # Day 1: Interval practice
    sessions.append(PracticeSessionRecord(
        timestamp=(base_time + timedelta(days=0, hours=10)).isoformat(),
        mode="intervals",
        instrument="keyboard",
        duration_seconds=600,  # 10 minutes
        num_exercises=10,
        interval_accuracy=80.0,
        source="cli"
    ))

    # Day 2: Chord practice
    sessions.append(PracticeSessionRecord(
        timestamp=(base_time + timedelta(days=1, hours=14)).isoformat(),
        mode="chords",
        instrument="keyboard",
        duration_seconds=900,  # 15 minutes
        num_exercises=12,
        chord_accuracy=75.0,
        source="cli"
    ))

    # Day 3: Improv on sax
    sessions.append(PracticeSessionRecord(
        timestamp=(base_time + timedelta(days=2, hours=16)).isoformat(),
        mode="improv_audio",
        instrument="sax",
        duration_seconds=1200,  # 20 minutes
        tune_id="autumn_leaves",
        choruses=3,
        chord_tone_ratio=65.0,
        tension_ratio=25.0,
        outside_ratio=10.0,
        guide_tone_hits=4,
        source="cli"
    ))

    # Day 4: Rhythm on drums
    sessions.append(PracticeSessionRecord(
        timestamp=(base_time + timedelta(days=3, hours=18)).isoformat(),
        mode="rhythm",
        instrument="drums",
        duration_seconds=720,  # 12 minutes
        rhythm_accuracy=88.0,
        avg_timing_error_ms=15.0,
        source="cli"
    ))

    # Day 5: More improv (MIDI)
    sessions.append(PracticeSessionRecord(
        timestamp=(base_time + timedelta(days=4, hours=15)).isoformat(),
        mode="improv_midi",
        instrument="keyboard",
        duration_seconds=1500,  # 25 minutes
        tune_id="blue_bossa",
        choruses=4,
        chord_tone_ratio=72.0,
        tension_ratio=18.0,
        outside_ratio=10.0,
        guide_tone_hits=6,
        source="cli"
    ))

    # Day 6: Voice practice
    sessions.append(PracticeSessionRecord(
        timestamp=(base_time + timedelta(days=5, hours=9)).isoformat(),
        mode="voice",
        instrument="voice",
        duration_seconds=480,  # 8 minutes
        avg_cents_deviation=25.0,
        source="cli"
    ))

    # Day 7: Intervals again
    sessions.append(PracticeSessionRecord(
        timestamp=(base_time + timedelta(days=6, hours=11)).isoformat(),
        mode="intervals",
        instrument="keyboard",
        duration_seconds=600,  # 10 minutes
        num_exercises=10,
        interval_accuracy=85.0,
        source="cli"
    ))

    # Add a demo session (should be filtered in some stats)
    sessions.append(PracticeSessionRecord(
        timestamp=(base_time + timedelta(days=7, hours=12)).isoformat(),
        mode="chords",
        instrument="test_device",
        duration_seconds=300,
        num_exercises=5,
        chord_accuracy=100.0,
        source="demo"
    ))

    return sessions


class TestPracticeLog:
    """Test JSONL logging functionality"""

    def test_append_and_load_session(self, clean_log):
        """Test appending and loading a single session"""
        record = PracticeSessionRecord(
            timestamp=datetime.now().isoformat(),
            mode="intervals",
            instrument="keyboard",
            duration_seconds=600,
            num_exercises=10,
            interval_accuracy=80.0
        )

        append_session(record)

        # Load and verify
        sessions = load_sessions()
        assert len(sessions) == 1
        assert sessions[0].mode == "intervals"
        assert sessions[0].interval_accuracy == 80.0

    def test_multiple_sessions(self, clean_log, sample_sessions):
        """Test loading multiple sessions"""
        # Append all sample sessions
        for session in sample_sessions:
            append_session(session)

        # Load and verify count
        loaded = load_sessions()
        assert len(loaded) == len(sample_sessions)

    def test_empty_log(self, clean_log):
        """Test loading from empty/non-existent log"""
        sessions = load_sessions()
        assert sessions == []


class TestProgressStats:
    """Test progress statistics functions"""

    def test_compute_totals(self, sample_sessions):
        """Test total minutes calculation"""
        # Exclude the demo session (last one)
        real_sessions = [s for s in sample_sessions if s.source != "demo"]

        total_minutes = progress_stats.compute_totals(real_sessions)

        # Sum: 10 + 15 + 20 + 12 + 25 + 8 + 10 = 100 minutes
        assert total_minutes == 100.0

    def test_minutes_by_instrument(self, sample_sessions):
        """Test breakdown by instrument"""
        real_sessions = [s for s in sample_sessions if s.source != "demo"]

        minutes = progress_stats.compute_minutes_by_instrument(real_sessions)

        # Keyboard: 10 + 15 + 25 + 10 = 60 min (two interval sessions + chords + improv)
        assert minutes["keyboard"] == 60.0
        # Sax: 20 min
        assert minutes["sax"] == 20.0
        # Drums: 12 min
        assert minutes["drums"] == 12.0
        # Voice: 8 min
        assert minutes["voice"] == 8.0

    def test_minutes_by_mode(self, sample_sessions):
        """Test breakdown by mode"""
        real_sessions = [s for s in sample_sessions if s.source != "demo"]

        minutes = progress_stats.compute_minutes_by_mode(real_sessions)

        # Intervals: 10 + 10 = 20 min
        assert minutes["intervals"] == 20.0
        # Chords: 15 min
        assert minutes["chords"] == 15.0
        # Improv: 20 + 25 = 45 min
        assert minutes["improv_audio"] == 20.0
        assert minutes["improv_midi"] == 25.0

    def test_recent_streak(self, sample_sessions):
        """Test streak calculation"""
        real_sessions = [s for s in sample_sessions if s.source != "demo"]

        # All 7 days have practice
        streak = progress_stats.compute_recent_streak(real_sessions, days=7)
        assert streak == 7

    def test_compute_average_metrics(self, sample_sessions):
        """Test average metric computation"""
        # Average chord_tone_ratio for improv sessions
        improv_sessions = [s for s in sample_sessions if 'improv' in s.mode]

        avg = progress_stats.compute_average_metrics(improv_sessions, 'chord_tone_ratio')

        # (65.0 + 72.0) / 2 = 68.5
        assert avg == pytest.approx(68.5)

    def test_filter_sessions(self, sample_sessions):
        """Test session filtering"""
        # Filter by instrument
        keyboard_only = progress_stats.filter_sessions(
            sample_sessions,
            instrument="keyboard"
        )
        assert len(keyboard_only) == 4  # 2x intervals, chords, improv_midi

        # Filter by mode
        improv_only = progress_stats.filter_sessions(
            sample_sessions,
            mode="improv_midi"
        )
        assert len(improv_only) == 1

        # Filter by source
        real_only = progress_stats.filter_sessions(
            sample_sessions,
            source="cli"
        )
        assert len(real_only) == 7  # Excludes the demo


class TestGamification:
    """Test XP, ranks, and badges"""

    def test_compute_xp_for_session(self):
        """Test XP calculation for a session"""
        # Base: 10 XP/minute * 10 minutes = 100 XP
        record = PracticeSessionRecord(
            timestamp=datetime.now().isoformat(),
            mode="intervals",
            instrument="keyboard",
            duration_seconds=600,  # 10 minutes
            interval_accuracy=85.0,  # Triggers +15% bonus
            source="cli"
        )

        xp = gamification.compute_xp_for_session(record)

        # 100 * 1.15 = 115 (114 after int rounding)
        assert xp == 114

    def test_compute_xp_with_multiple_bonuses(self):
        """Test XP with multiple bonuses"""
        record = PracticeSessionRecord(
            timestamp=datetime.now().isoformat(),
            mode="improv_midi",
            instrument="keyboard",
            duration_seconds=600,
            chord_tone_ratio=75.0,  # +20% bonus
            source="cli"
        )

        xp = gamification.compute_xp_for_session(record)

        # 100 * 1.2 = 120
        assert xp == 120

    def test_demo_sessions_give_no_xp(self):
        """Test that demo sessions don't award XP"""
        record = PracticeSessionRecord(
            timestamp=datetime.now().isoformat(),
            mode="chords",
            instrument="test_device",
            duration_seconds=600,
            chord_accuracy=100.0,
            source="demo"
        )

        xp = gamification.compute_xp_for_session(record)
        assert xp == 0

    def test_determine_rank(self):
        """Test rank determination"""
        # Test each rank threshold
        assert gamification.determine_rank(0).name == "Peasant"
        assert gamification.determine_rank(500).name == "Peasant"
        assert gamification.determine_rank(1000).name == "Apprentice"
        assert gamification.determine_rank(3000).name == "Squire"
        assert gamification.determine_rank(10000).name == "Adept"
        assert gamification.determine_rank(40000).name == "Wizard"

    def test_get_next_rank(self):
        """Test next rank calculation"""
        next_rank, xp_needed = gamification.get_next_rank(500)

        assert next_rank.name == "Apprentice"
        assert xp_needed == 500  # Need 1000 total, have 500

    def test_compute_badges(self, sample_sessions):
        """Test badge computation"""
        real_sessions = [s for s in sample_sessions if s.source != "demo"]

        badges = gamification.compute_badges(real_sessions)

        # Should have First_Steps (1+ session)
        assert "First_Steps" in badges

        # Should have First_100_Minutes (100 minutes total)
        assert "First_100_Minutes" in badges

        # Should have Week_Warrior (7-day streak)
        assert "Week_Warrior" in badges

        # Should have Multi_Instrumentalist (keyboard, sax, drums, voice)
        assert "Multi_Instrumentalist" in badges


class TestTeacherJournal:
    """Test teacher journal generation"""

    def test_generate_entry(self, sample_sessions):
        """Test journal entry generation"""
        entry = generate_teacher_entry(sample_sessions, days=7)

        # Should be a string
        assert isinstance(entry, str)

        # Should have markdown headings
        assert "# Practice Journal" in entry
        assert "## Consistency" in entry
        assert "## Strengths" in entry
        assert "## Areas for Growth" in entry

        # Should mention total time
        assert "100" in entry  # 100 minutes total

        # Should mention the streak
        assert "7" in entry or "consecutive" in entry.lower()

    def test_empty_sessions(self):
        """Test journal with no sessions"""
        entry = generate_teacher_entry([], days=7)

        assert "No practice sessions logged" in entry

    def test_identifies_strengths(self, sample_sessions):
        """Test that journal identifies strengths"""
        entry = generate_teacher_entry(sample_sessions, days=7)

        # With multiple instruments, should mention variety
        assert "variety" in entry.lower() or "instrument" in entry.lower()

    def test_generates_suggestions(self, sample_sessions):
        """Test that journal generates suggestions"""
        entry = generate_teacher_entry(sample_sessions, days=7)

        # Should have suggestions section
        assert "## Areas for Growth" in entry

        # Content depends on the data but should have something
        lines = entry.split('\n')
        suggestions_section = False
        has_suggestions = False

        for line in lines:
            if "## Areas for Growth" in line:
                suggestions_section = True
            if suggestions_section and line.strip().startswith('-'):
                has_suggestions = True
                break

        # Should either have suggestions or a positive message
        assert has_suggestions or "excellent work" in entry.lower() or "keep up" in entry.lower()


class TestIntegration:
    """Integration tests for the complete logging pipeline"""

    def test_full_workflow(self, clean_log):
        """Test the complete workflow: log → load → stats → journal"""
        # Create and log a session
        session = PracticeSessionRecord(
            timestamp=datetime.now().isoformat(),
            mode="intervals",
            instrument="keyboard",
            duration_seconds=600,
            num_exercises=10,
            interval_accuracy=80.0,
            source="cli"
        )

        append_session(session)

        # Load it back
        sessions = load_sessions()
        assert len(sessions) == 1

        # Compute stats
        total_minutes = progress_stats.compute_totals(sessions)
        assert total_minutes == 10.0

        # Compute XP
        total_xp = gamification.compute_total_xp(sessions)
        assert total_xp > 0

        # Generate journal
        entry = generate_teacher_entry(sessions, days=7)
        assert "intervals" in entry.lower()
