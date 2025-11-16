"""
End-to-end tests using TestDeviceProfile.

Tests complete session flows without requiring real MIDI hardware.
"""

import pytest
import random
from lyra_live.devices.test_device import TestDeviceProfile
from lyra_live.sessions.manager import SessionManager
from lyra_live.ableton_backend.client import AbletonMCPClient
from lyra_live.lessons.core import Lesson, LessonPhrase
from lyra_live.ear_training.base import Note


@pytest.fixture
def ableton_client():
    """Create Ableton MCP client"""
    return AbletonMCPClient()


def test_interval_session_correct_answers(ableton_client):
    """Test complete interval session with all correct answers"""
    random.seed(100)

    device = TestDeviceProfile(mode="correct")
    manager = SessionManager(device, ableton_client)

    results = manager.run_interval_drill(num_exercises=5)

    assert len(results) == 5
    assert all(r.correct for r in results)
    assert all(r.exercise_id for r in results)


def test_interval_session_wrong_answers(ableton_client):
    """Test interval session with wrong answers"""
    random.seed(101)

    device = TestDeviceProfile(mode="wrong_interval")
    manager = SessionManager(device, ableton_client)

    results = manager.run_interval_drill(num_exercises=5)

    assert len(results) == 5
    assert all(not r.correct for r in results)


def test_chord_session_correct_answers(ableton_client):
    """Test complete chord session with all correct answers"""
    random.seed(200)

    device = TestDeviceProfile(mode="correct")
    manager = SessionManager(device, ableton_client)

    results = manager.run_chord_drill(num_exercises=5)

    assert len(results) == 5
    assert all(r.correct for r in results)


def test_chord_session_wrong_answers(ableton_client):
    """Test chord session with wrong answers"""
    random.seed(201)

    device = TestDeviceProfile(mode="wrong_chord")
    manager = SessionManager(device, ableton_client)

    results = manager.run_chord_drill(num_exercises=5)

    assert len(results) == 5
    assert all(not r.correct for r in results)


def test_melody_session_correct_answers(ableton_client):
    """Test melody session with all correct answers"""
    random.seed(300)

    device = TestDeviceProfile(mode="correct")
    manager = SessionManager(device, ableton_client)

    results = manager.run_melody_drill(num_exercises=5, melody_length=4)

    assert len(results) == 5
    assert all(r.correct for r in results)


def test_melody_session_partial_accuracy(ableton_client):
    """Test melody session with partial accuracy"""
    random.seed(301)

    device = TestDeviceProfile(mode="partial_melody")
    manager = SessionManager(device, ableton_client)

    results = manager.run_melody_drill(num_exercises=5, melody_length=6)

    assert len(results) == 5
    # Partial melody mode should have some wrong answers
    assert not all(r.correct for r in results)


def test_lesson_practice_session(ableton_client):
    """Test lesson practice with multiple phrases"""
    random.seed(400)

    device = TestDeviceProfile(mode="correct")
    manager = SessionManager(device, ableton_client)

    # Create test lesson
    lesson = Lesson(
        id="test_lesson",
        title="Test Lesson",
        difficulty="beginner"
    )

    lesson.add_phrase(LessonPhrase(
        id="phrase1",
        notes=[Note(60, 500), Note(62, 500), Note(64, 500)],
        description="Test phrase 1"
    ))

    lesson.add_phrase(LessonPhrase(
        id="phrase2",
        notes=[Note(67, 500), Note(65, 500), Note(64, 500), Note(62, 500)],
        description="Test phrase 2"
    ))

    results = manager.run_lesson_practice(lesson)

    assert len(results) == 2
    assert all(r.correct for r in results)


def test_timeout_handling(ableton_client):
    """Test that timeout mode is handled gracefully"""
    random.seed(500)

    device = TestDeviceProfile(mode="timeout")
    manager = SessionManager(device, ableton_client)

    results = manager.run_interval_drill(num_exercises=3)

    assert len(results) == 3
    assert all(not r.correct for r in results)
    assert all("No input detected" in r.feedback for r in results)


def test_session_accuracy_calculation(ableton_client):
    """Test that session accuracy is calculated correctly"""
    random.seed(600)

    device = TestDeviceProfile(mode="wrong_interval")
    manager = SessionManager(device, ableton_client)

    results = manager.run_interval_drill(num_exercises=10)

    correct_count = sum(1 for r in results if r.correct)
    total = len(results)
    accuracy = (correct_count / total) * 100 if total > 0 else 0

    # All should be wrong in wrong_interval mode
    assert accuracy == 0.0


def test_chord_types_filtering(ableton_client):
    """Test that chord type filtering works"""
    random.seed(700)

    device = TestDeviceProfile(mode="correct")
    manager = SessionManager(device, ableton_client)

    # Test with triads only
    results = manager.run_chord_drill(
        num_exercises=5,
        chord_types=["major", "minor"]
    )

    assert len(results) == 5
    assert all(r.correct for r in results)


def test_melody_length_variation(ableton_client):
    """Test melodies with different lengths"""
    random.seed(800)

    device = TestDeviceProfile(mode="correct")
    manager = SessionManager(device, ableton_client)

    for length in [3, 5, 8]:
        results = manager.run_melody_drill(num_exercises=2, melody_length=length)
        assert len(results) == 2
        assert all(r.correct for r in results)
