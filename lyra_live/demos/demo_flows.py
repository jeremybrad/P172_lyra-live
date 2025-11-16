"""
Scripted demo flows for video tutorials.

Each demo is deterministic (fixed random seed) and logs structured output
that can be aligned with recorded video later.
"""

import random
from lyra_live.devices.test_device import TestDeviceProfile
from lyra_live.sessions.manager import SessionManager
from lyra_live.ableton_backend.client import AbletonMCPClient
from lyra_live.lessons.core import Lesson, LessonPhrase
from lyra_live.ear_training.base import Note


def run_interval_demo(num_exercises: int = 3, mode: str = "correct"):
    """
    Run a deterministic interval recognition demo.

    Args:
        num_exercises: Number of exercises to demonstrate
        mode: TestDevice mode (correct, wrong_interval, etc.)

    Returns:
        List of exercise results
    """
    print("\n" + "="*60)
    print("LYRA LIVE - INTERVAL RECOGNITION DEMO")
    print("="*60)
    print(f"Mode: {mode}")
    print(f"Exercises: {num_exercises}")
    print()

    # Set random seed for reproducibility
    random.seed(42)

    # Create test device and session
    device = TestDeviceProfile(mode=mode)
    ableton = AbletonMCPClient()
    manager = SessionManager(device, ableton)

    # Run demo
    results = manager.run_interval_drill(num_exercises)

    print("\n📊 Demo Statistics:")
    correct = sum(1 for r in results if r.correct)
    print(f"   Total: {len(results)}")
    print(f"   Correct: {correct}")
    print(f"   Accuracy: {(correct/len(results)*100):.1f}%")
    print()

    return results


def run_chord_demo(num_exercises: int = 3, mode: str = "correct"):
    """
    Run a deterministic chord quality recognition demo.

    Args:
        num_exercises: Number of exercises to demonstrate
        mode: TestDevice mode (correct, wrong_chord, etc.)

    Returns:
        List of exercise results
    """
    print("\n" + "="*60)
    print("LYRA LIVE - CHORD QUALITY RECOGNITION DEMO")
    print("="*60)
    print(f"Mode: {mode}")
    print(f"Exercises: {num_exercises}")
    print()

    # Set random seed for reproducibility
    random.seed(123)

    # Create test device and session
    device = TestDeviceProfile(mode=mode)
    ableton = AbletonMCPClient()
    manager = SessionManager(device, ableton)

    # Run demo with triads only
    results = manager.run_chord_drill(
        num_exercises,
        chord_types=["major", "minor", "diminished", "augmented"]
    )

    print("\n📊 Demo Statistics:")
    correct = sum(1 for r in results if r.correct)
    print(f"   Total: {len(results)}")
    print(f"   Correct: {correct}")
    print(f"   Accuracy: {(correct/len(results)*100):.1f}%")
    print()

    return results


def run_melody_lesson_demo(mode: str = "correct"):
    """
    Run a deterministic melody lesson demo.

    Args:
        mode: TestDevice mode (correct, partial_melody, etc.)

    Returns:
        List of exercise results
    """
    print("\n" + "="*60)
    print("LYRA LIVE - MELODY LESSON DEMO")
    print("="*60)
    print(f"Mode: {mode}")
    print()

    # Set random seed for reproducibility
    random.seed(456)

    # Create test device and session
    device = TestDeviceProfile(mode=mode)
    ableton = AbletonMCPClient()
    manager = SessionManager(device, ableton)

    # Create a demo lesson with recognizable phrases
    lesson = Lesson(
        id="demo_beatles_intro",
        title="Beatles-style Melody (Demo)",
        artist="Demo Artist",
        difficulty="beginner",
        description="A simple Beatles-inspired melodic phrase"
    )

    # Phrase 1: Ascending major scale fragment
    phrase1 = LessonPhrase(
        id="phrase1",
        notes=[
            Note(60, 500),  # C
            Note(62, 500),  # D
            Note(64, 500),  # E
            Note(65, 500),  # F
            Note(67, 500),  # G
        ],
        description="Opening: Ascending scale"
    )

    # Phrase 2: Simple melodic hook
    phrase2 = LessonPhrase(
        id="phrase2",
        notes=[
            Note(67, 500),  # G
            Note(64, 500),  # E
            Note(62, 500),  # D
            Note(60, 1000), # C (longer)
        ],
        description="Hook: Descending to tonic"
    )

    lesson.add_phrase(phrase1)
    lesson.add_phrase(phrase2)

    # Run lesson practice
    results = manager.run_lesson_practice(lesson)

    print("\n📊 Demo Statistics:")
    correct = sum(1 for r in results if r.correct)
    print(f"   Total Phrases: {len(results)}")
    print(f"   Correct: {correct}")
    print(f"   Accuracy: {(correct/len(results)*100):.1f}%")
    print()

    return results


def run_full_demo_suite():
    """
    Run all demos in sequence for comprehensive demonstration.

    This is useful for recording a complete walkthrough video.
    """
    print("\n" + "="*70)
    print(" " * 15 + "LYRA LIVE - FULL DEMO SUITE")
    print("="*70)
    print()

    print("This demo suite demonstrates all core features of Lyra Live:")
    print("  1. Interval Recognition")
    print("  2. Chord Quality Recognition")
    print("  3. Melody/Lesson Practice")
    print()
    input("Press Enter to begin...")

    # Demo 1: Interval Recognition (all correct)
    print("\n\n📍 DEMO 1: Interval Recognition (Perfect Performance)")
    input("Press Enter to continue...")
    run_interval_demo(num_exercises=3, mode="correct")
    input("\nPress Enter for next demo...")

    # Demo 2: Chord Recognition (all correct)
    print("\n\n📍 DEMO 2: Chord Quality Recognition (Perfect Performance)")
    input("Press Enter to continue...")
    run_chord_demo(num_exercises=3, mode="correct")
    input("\nPress Enter for next demo...")

    # Demo 3: Melody Lesson (partial accuracy)
    print("\n\n📍 DEMO 3: Melody Lesson Practice (Partial Accuracy)")
    input("Press Enter to continue...")
    run_melody_lesson_demo(mode="partial_melody")

    print("\n\n" + "="*70)
    print(" " * 20 + "DEMO SUITE COMPLETE!")
    print("="*70)
    print("\nAll Lyra Live core features demonstrated successfully.")
    print("Thank you for watching!")
    print()
