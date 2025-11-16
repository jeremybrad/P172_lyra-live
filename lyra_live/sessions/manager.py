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
from lyra_live.ear_training.rhythm import RhythmExerciseGenerator, RhythmValidator, Beat
from lyra_live.ear_training.validator import ExerciseValidator
from lyra_live.ableton_backend.client import AbletonMCPClient
from lyra_live.lessons.core import Lesson
from lyra_live.devices.test_device import TestDeviceProfile
from lyra_live.devices.drum_kit import DrumKitProfile
from typing import List
import time


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

    def run_rhythm_snare_drill(
        self,
        subdivision: str = "eighth",
        tempo_bpm: int = 80,
        num_bars: int = 4
    ):
        """
        Run rhythm drill focusing on snare only.

        Args:
            subdivision: "quarter", "eighth", or "sixteenth"
            tempo_bpm: Tempo in beats per minute
            num_bars: Number of bars to play

        Returns:
            RhythmResult with timing analysis
        """
        if not isinstance(self.device, DrumKitProfile):
            print("Error: This drill requires a drum kit device profile")
            return None

        print(f"\n🥁 Starting Snare Rhythm Drill")
        print(f"   Device: {self.device.device_name}")
        print(f"   Pattern: Straight {subdivision} notes")
        print(f"   Tempo: {tempo_bpm} BPM")
        print(f"   Bars: {num_bars}")
        print(f"   Instructions: Play steady {subdivision} notes on snare\n")

        # Generate exercise
        exercise = RhythmExerciseGenerator.generate_straight_pattern(
            drum_part="snare",
            subdivision=subdivision,
            tempo_bpm=tempo_bpm,
            num_bars=num_bars
        )

        # Calculate duration
        duration_ms = exercise.grid.get_duration_ms()

        print(f"Ready? Starting in 3...")
        time.sleep(1)
        print("2...")
        time.sleep(1)
        print("1...")
        time.sleep(1)
        print("GO!\n")

        # Record start time
        start_time = time.time() * 1000

        # Capture drum hits
        midi_events = self.device.detect_input(timeout_ms=duration_ms + 1000)

        if not midi_events:
            print("No drum hits detected.\n")
            return None

        # Convert MIDI events to Beats
        actual_beats = []
        for event in midi_events:
            if event.type == 'note_on':
                drum_part = self.device.get_drum_part(event.pitch)
                if drum_part:
                    # Adjust timestamp relative to start
                    relative_time = event.timestamp_ms - start_time
                    actual_beats.append(Beat(
                        time_ms=int(relative_time),
                        drum_part=drum_part,
                        velocity=event.velocity
                    ))

        # Validate
        result = RhythmValidator.validate_rhythm(
            expected_grid=exercise.grid,
            actual_hits=actual_beats,
            tolerance_ms=50,
            drum_part_filter="snare"
        )

        # Display results
        print(f"\n{'='*50}")
        print(f"Snare Rhythm Drill Complete!")
        print(f"  Expected hits: {result.total_expected_hits}")
        print(f"  Your hits: {result.total_actual_hits}")
        print(f"  Correct: {result.correct_hits}")
        print(f"  Accuracy: {result.accuracy_percentage:.1f}%")
        if result.average_timing_error_ms != 0:
            if result.average_timing_error_ms > 0:
                print(f"  Timing: Rushing by {result.average_timing_error_ms:.1f}ms")
            else:
                print(f"  Timing: Dragging by {abs(result.average_timing_error_ms):.1f}ms")
        print(f"\n  {result.feedback}")
        print(f"{'='*50}\n")

        return result

    def run_rhythm_kit_drill(
        self,
        pattern_type: str = "backbeat",
        tempo_bpm: int = 80,
        num_bars: int = 4
    ):
        """
        Run rhythm drill with full kit pattern.

        Args:
            pattern_type: "backbeat" or "syncopated"
            tempo_bpm: Tempo in beats per minute
            num_bars: Number of bars to play

        Returns:
            RhythmResult with timing analysis
        """
        if not isinstance(self.device, DrumKitProfile):
            print("Error: This drill requires a drum kit device profile")
            return None

        print(f"\n🥁 Starting Full Kit Rhythm Drill")
        print(f"   Device: {self.device.device_name}")
        print(f"   Pattern: {pattern_type}")
        print(f"   Tempo: {tempo_bpm} BPM")
        print(f"   Bars: {num_bars}")
        print(f"   Instructions: Play the full kit pattern\n")

        # Generate exercise
        if pattern_type == "backbeat":
            exercise = RhythmExerciseGenerator.generate_backbeat_pattern(
                tempo_bpm=tempo_bpm,
                num_bars=num_bars
            )
        else:
            exercise = RhythmExerciseGenerator.generate_syncopated_pattern(
                drum_part="snare",
                complexity=1,
                tempo_bpm=tempo_bpm,
                num_bars=num_bars
            )

        # Show pattern
        print("Pattern breakdown:")
        if pattern_type == "backbeat":
            print("  Kick: beats 1 and 3")
            print("  Snare: beats 2 and 4\n")

        # Calculate duration
        duration_ms = exercise.grid.get_duration_ms()

        print(f"Ready? Starting in 3...")
        time.sleep(1)
        print("2...")
        time.sleep(1)
        print("1...")
        time.sleep(1)
        print("GO!\n")

        # Record start time
        start_time = time.time() * 1000

        # Capture drum hits
        midi_events = self.device.detect_input(timeout_ms=duration_ms + 1000)

        if not midi_events:
            print("No drum hits detected.\n")
            return None

        # Convert MIDI events to Beats
        actual_beats = []
        for event in midi_events:
            if event.type == 'note_on':
                drum_part = self.device.get_drum_part(event.pitch)
                if drum_part:
                    # Adjust timestamp relative to start
                    relative_time = event.timestamp_ms - start_time
                    actual_beats.append(Beat(
                        time_ms=int(relative_time),
                        drum_part=drum_part,
                        velocity=event.velocity
                    ))

        # Validate (no drum part filter for full kit)
        result = RhythmValidator.validate_rhythm(
            expected_grid=exercise.grid,
            actual_hits=actual_beats,
            tolerance_ms=50
        )

        # Display results
        print(f"\n{'='*50}")
        print(f"Full Kit Rhythm Drill Complete!")
        print(f"  Expected hits: {result.total_expected_hits}")
        print(f"  Your hits: {result.total_actual_hits}")
        print(f"  Correct: {result.correct_hits}")
        print(f"  Accuracy: {result.accuracy_percentage:.1f}%")
        if result.average_timing_error_ms != 0:
            if result.average_timing_error_ms > 0:
                print(f"  Timing: Rushing by {result.average_timing_error_ms:.1f}ms")
            else:
                print(f"  Timing: Dragging by {abs(result.average_timing_error_ms):.1f}ms")
        print(f"\n  {result.feedback}")
        print(f"{'='*50}\n")

        return result
