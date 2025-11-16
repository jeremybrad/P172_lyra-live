"""
Session Manager - orchestrates practice sessions.

Coordinates the flow of exercises, device input, validation, and feedback.
This is the main orchestrator that ties together all components.
"""

from lyra_live.devices.base import DeviceProfile, MIDIEvent
from lyra_live.ear_training.base import Exercise, ExerciseResult, Note
from lyra_live.ear_training.intervals import IntervalExercise
from lyra_live.ear_training.chords import ChordQualityExercise
from lyra_live.ear_training.melodies import MelodyImitationExercise
from lyra_live.ear_training.validator import ExerciseValidator
from lyra_live.ableton_backend.client import AbletonMCPClient
from lyra_live.lessons.core import Lesson
from lyra_live.devices.test_device import TestDeviceProfile
from typing import List


class SessionManager:
    """Orchestrate practice sessions"""

    def __init__(self, device: DeviceProfile, ableton_client: AbletonMCPClient):
        """
        Initialize session manager.

        Args:
            device: DeviceProfile for the MIDI device being used
            ableton_client: AbletonMCPClient for playing exercises
        """
        self.device = device
        self.ableton = ableton_client

    def run_interval_drill(self, num_exercises: int = 10):
        """
        Run interval recognition drill session.

        Generates random interval exercises, plays them via Ableton,
        captures user input, validates responses, and provides feedback.

        Args:
            num_exercises: Number of exercises to run in this session
        """
        results = []

        print(f"\n🎵 Starting Interval Recognition Drill")
        print(f"   Device: {self.device.device_name}")
        print(f"   Exercises: {num_exercises}")
        print(f"   Instructions: Listen to each interval, then play it back on your device\n")

        for i in range(num_exercises):
            # Generate exercise
            exercise = IntervalExercise.generate_random()

            # Set expected answer for test device
            if isinstance(self.device, TestDeviceProfile):
                self.device.set_expected_answer(exercise.correct_response)

            # Display exercise info
            print(f"Exercise {i+1}/{num_exercises}:")
            print(f"  Listen to the interval...")

            # Play via Ableton (stubbed for MVP)
            self.ableton.play_exercise(exercise)

            # For MVP without Ableton integration, show the notes
            print(f"  [Exercise plays: {exercise.notes[0]} to {exercise.notes[1]}]")

            # Get user response
            print(f"  Now play the interval on your device (or press Ctrl+C to skip)...")

            try:
                midi_events = self.device.detect_input(timeout_ms=10000)

                if not midi_events:
                    print(f"  ⏱️  No input detected. Moving to next exercise.\n")
                    results.append(ExerciseResult(
                        exercise_id=exercise.id,
                        user_notes=[],
                        correct=False,
                        feedback="No input detected"
                    ))
                    continue

                # Convert MIDI events to Notes (filter for note_on events)
                user_notes = [
                    Note(pitch=event.pitch, duration_ms=1000, velocity=event.velocity)
                    for event in midi_events
                    if event.type == 'note_on'
                ]

                # Validate
                result = ExerciseValidator.validate_interval(
                    exercise.correct_response,
                    user_notes
                )
                result.exercise_id = exercise.id

                # Display feedback
                if result.correct:
                    print(f"  ✓ {result.feedback}\n")
                else:
                    print(f"  ✗ {result.feedback}")
                    print(f"    You played: {user_notes}\n")

                results.append(result)

            except KeyboardInterrupt:
                print("\n\n⏸️  Session paused by user.")
                break

        # Session summary
        correct_count = sum(1 for r in results if r.correct)
        total_attempted = len(results)

        print(f"\n{'='*50}")
        print(f"Session Complete!")
        print(f"  Score: {correct_count}/{total_attempted} correct")
        if total_attempted > 0:
            percentage = (correct_count / total_attempted) * 100
            print(f"  Accuracy: {percentage:.1f}%")

        if correct_count == total_attempted and total_attempted > 0:
            print(f"  🌟 Perfect score! Excellent work!")
        elif percentage >= 80:
            print(f"  🎵 Great job! You're developing a good ear.")
        elif percentage >= 60:
            print(f"  👍 Good progress! Keep practicing.")
        else:
            print(f"  💪 Keep practicing - you'll improve!")

        print(f"{'='*50}\n")

        return results

    def run_chord_drill(self, num_exercises: int = 10, chord_types: List[str] = None):
        """
        Run chord quality recognition drill session.

        Args:
            num_exercises: Number of exercises to run
            chord_types: List of chord types to practice (default: all triads)
        """
        results = []

        print(f"\n🎵 Starting Chord Quality Recognition Drill")
        print(f"   Device: {self.device.device_name}")
        print(f"   Exercises: {num_exercises}")
        print(f"   Instructions: Listen to each chord, then play it back on your device\n")

        for i in range(num_exercises):
            # Generate exercise
            exercise = ChordQualityExercise.generate_random(chord_types=chord_types)

            # Set expected answer for test device
            if isinstance(self.device, TestDeviceProfile):
                self.device.set_expected_answer(exercise.correct_response)

            # Display exercise info
            print(f"Exercise {i+1}/{num_exercises}:")
            print(f"  Listen to the chord...")

            # Play via Ableton (stubbed for MVP)
            self.ableton.play_exercise(exercise)

            # For MVP without Ableton integration, show the notes
            chord_pitches = [str(n.pitch) for n in exercise.notes]
            print(f"  [Exercise plays: {', '.join(chord_pitches)}]")

            # Get user response
            print(f"  Now play the chord on your device (or press Ctrl+C to skip)...")

            try:
                midi_events = self.device.detect_input(timeout_ms=10000)

                if not midi_events:
                    print(f"  ⏱️  No input detected. Moving to next exercise.\n")
                    results.append(ExerciseResult(
                        exercise_id=exercise.id,
                        user_notes=[],
                        correct=False,
                        feedback="No input detected"
                    ))
                    continue

                # Convert MIDI events to Notes
                user_notes = [
                    Note(pitch=event.pitch, duration_ms=2000, velocity=event.velocity)
                    for event in midi_events
                    if event.type == 'note_on'
                ]

                # Validate
                result = ExerciseValidator.validate_chord(
                    exercise.correct_response,
                    user_notes
                )
                result.exercise_id = exercise.id

                # Display feedback
                if result.correct:
                    print(f"  ✓ {result.feedback}\n")
                else:
                    print(f"  ✗ {result.feedback}\n")

                results.append(result)

            except KeyboardInterrupt:
                print("\n\n⏸️  Session paused by user.")
                break

        # Session summary
        self._print_session_summary(results, "Chord Quality")

        return results

    def run_melody_drill(self, num_exercises: int = 10, melody_length: int = 5):
        """
        Run melody imitation drill session.

        Args:
            num_exercises: Number of exercises to run
            melody_length: Number of notes per melody phrase
        """
        results = []

        print(f"\n🎵 Starting Melody Imitation Drill")
        print(f"   Device: {self.device.device_name}")
        print(f"   Exercises: {num_exercises}")
        print(f"   Instructions: Listen to each melody, then play it back exactly\n")

        for i in range(num_exercises):
            # Generate exercise
            exercise = MelodyImitationExercise.generate_random(length=melody_length)

            # Set expected answer for test device
            if isinstance(self.device, TestDeviceProfile):
                self.device.set_expected_answer(exercise.correct_response)

            # Display exercise info
            print(f"Exercise {i+1}/{num_exercises}:")
            print(f"  Listen to the melody...")

            # Play via Ableton (stubbed for MVP)
            self.ableton.play_exercise(exercise)

            # For MVP without Ableton integration, show the notes
            melody_pitches = [str(n.pitch) for n in exercise.notes]
            print(f"  [Exercise plays: {' -> '.join(melody_pitches)}]")

            # Get user response
            print(f"  Now play the melody on your device (or press Ctrl+C to skip)...")

            try:
                midi_events = self.device.detect_input(timeout_ms=15000)

                if not midi_events:
                    print(f"  ⏱️  No input detected. Moving to next exercise.\n")
                    results.append(ExerciseResult(
                        exercise_id=exercise.id,
                        user_notes=[],
                        correct=False,
                        feedback="No input detected"
                    ))
                    continue

                # Convert MIDI events to Notes
                user_notes = [
                    Note(pitch=event.pitch, duration_ms=500, velocity=event.velocity)
                    for event in midi_events
                    if event.type == 'note_on'
                ]

                # Validate
                result = ExerciseValidator.validate_melody(
                    exercise.correct_response,
                    user_notes
                )
                result.exercise_id = exercise.id

                # Display feedback
                if result.correct:
                    print(f"  ✓ {result.feedback}\n")
                else:
                    print(f"  ✗ {result.feedback}\n")

                results.append(result)

            except KeyboardInterrupt:
                print("\n\n⏸️  Session paused by user.")
                break

        # Session summary
        self._print_session_summary(results, "Melody Imitation")

        return results

    def run_lesson_practice(self, lesson: Lesson, phrase_ids: List[str] = None):
        """
        Practice specific phrases from a lesson.

        Args:
            lesson: Lesson object to practice
            phrase_ids: Optional list of specific phrase IDs to practice
                       If None, practices all phrases
        """
        results = []

        # Determine which phrases to practice
        if phrase_ids:
            phrases = [lesson.get_phrase(pid) for pid in phrase_ids]
            phrases = [p for p in phrases if p is not None]
        else:
            phrases = lesson.get_all_phrases()

        if not phrases:
            print("No phrases to practice.")
            return []

        print(f"\n🎵 Practicing Lesson: {lesson.title}")
        if lesson.artist:
            print(f"   Artist: {lesson.artist}")
        print(f"   Device: {self.device.device_name}")
        print(f"   Phrases: {len(phrases)}")
        print(f"   Instructions: Listen to each phrase, then play it back exactly\n")

        for i, phrase in enumerate(phrases):
            # Convert phrase to exercise
            exercise = phrase.to_exercise()

            # Set expected answer for test device
            if isinstance(self.device, TestDeviceProfile):
                self.device.set_expected_answer(exercise.correct_response)

            # Display phrase info
            print(f"Phrase {i+1}/{len(phrases)}: {phrase.description or phrase.id}")
            print(f"  Listen to the phrase...")

            # Play via Ableton (stubbed for MVP)
            self.ableton.play_exercise(exercise)

            # For MVP without Ableton integration, show the notes
            phrase_pitches = [str(n.pitch) for n in exercise.notes]
            print(f"  [Phrase plays: {' -> '.join(phrase_pitches)}]")

            # Get user response
            print(f"  Now play the phrase on your device (or press Ctrl+C to skip)...")

            try:
                midi_events = self.device.detect_input(timeout_ms=15000)

                if not midi_events:
                    print(f"  ⏱️  No input detected. Moving to next phrase.\n")
                    results.append(ExerciseResult(
                        exercise_id=exercise.id,
                        user_notes=[],
                        correct=False,
                        feedback="No input detected"
                    ))
                    continue

                # Convert MIDI events to Notes
                user_notes = [
                    Note(pitch=event.pitch, duration_ms=500, velocity=event.velocity)
                    for event in midi_events
                    if event.type == 'note_on'
                ]

                # Validate
                result = ExerciseValidator.validate_melody(
                    exercise.correct_response,
                    user_notes
                )
                result.exercise_id = exercise.id

                # Display feedback
                if result.correct:
                    print(f"  ✓ {result.feedback}\n")
                else:
                    print(f"  ✗ {result.feedback}\n")

                results.append(result)

            except KeyboardInterrupt:
                print("\n\n⏸️  Session paused by user.")
                break

        # Session summary
        self._print_session_summary(results, f"Lesson: {lesson.title}")

        return results

    def _print_session_summary(self, results: List[ExerciseResult], session_type: str):
        """
        Print session summary with statistics.

        Args:
            results: List of exercise results
            session_type: Type of session for display
        """
        correct_count = sum(1 for r in results if r.correct)
        total_attempted = len(results)

        print(f"\n{'='*50}")
        print(f"{session_type} Session Complete!")
        print(f"  Score: {correct_count}/{total_attempted} correct")
        if total_attempted > 0:
            percentage = (correct_count / total_attempted) * 100
            print(f"  Accuracy: {percentage:.1f}%")

            if correct_count == total_attempted:
                print(f"  🌟 Perfect score! Excellent work!")
            elif percentage >= 80:
                print(f"  🎵 Great job! You're developing a good ear.")
            elif percentage >= 60:
                print(f"  👍 Good progress! Keep practicing.")
            else:
                print(f"  💪 Keep practicing - you'll improve!")

        print(f"{'='*50}\n")
