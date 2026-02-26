"""
Test device profile for simulation and automated testing.

Provides fake MIDI devices that can simulate user responses
without requiring actual hardware. Useful for CI/CD and demos.
"""

from lyra_live.devices.base import DeviceProfile, DeviceCapabilities, MIDIEvent
from lyra_live.ear_training.base import Note
from typing import List, Optional
import time


class TestDeviceProfile(DeviceProfile):
    """
    Simulated MIDI device for testing.

    Can operate in different modes:
    - "correct": Always plays back the correct answer
    - "wrong_interval": Plays intervals off by one semitone
    - "wrong_chord": Plays wrong chord quality
    - "partial_melody": Plays melody with some wrong notes
    - "timeout": Never responds (simulates user timeout)
    """

    name_pattern = "test_device"
    capabilities = DeviceCapabilities(
        has_lights=True,  # Can simulate all features
        has_aftertouch=True,
        is_mpe=True,
        note_range=(0, 127)
    )

    def __init__(self, mode: str = "correct", error_rate: float = 0.0):
        """
        Initialize test device.

        Args:
            mode: Behavior mode (correct, wrong_interval, wrong_chord, etc.)
            error_rate: Probability of making an error (0.0 to 1.0)
        """
        self.device_name = "TestDevice"
        self.mode = mode
        self.error_rate = error_rate
        self.expected_notes: Optional[List[Note]] = None
        self.response_delay_ms = 100  # Simulate human response time

    def set_expected_answer(self, notes: List[Note]):
        """
        Set the expected correct answer for the next exercise.

        Args:
            notes: The correct notes for the exercise
        """
        self.expected_notes = notes

    def send_note(self, pitch: int, velocity: int, duration_ms: int):
        """
        Simulate sending a note (no-op for test device).

        Args:
            pitch: MIDI note number
            velocity: Note velocity
            duration_ms: Note duration
        """
        # Test device doesn't actually send MIDI
        pass

    def detect_input(self, timeout_ms: int = 5000) -> Optional[List[MIDIEvent]]:
        """
        Simulate detecting MIDI input based on mode and expected answer.

        Args:
            timeout_ms: How long to wait for input

        Returns:
            List of simulated MIDI events, or None if timeout mode
        """
        # Simulate response time
        time.sleep(self.response_delay_ms / 1000.0)

        if self.mode == "timeout":
            # Simulate no response
            return None

        if self.expected_notes is None:
            # No expected answer set, return empty
            return []

        # Generate response based on mode
        if self.mode == "correct":
            return self._generate_correct_response()

        elif self.mode == "wrong_interval":
            return self._generate_wrong_interval()

        elif self.mode == "wrong_chord":
            return self._generate_wrong_chord()

        elif self.mode == "partial_melody":
            return self._generate_partial_melody()

        else:
            # Default: correct response
            return self._generate_correct_response()

    def _generate_correct_response(self) -> List[MIDIEvent]:
        """Generate correct response matching expected notes."""
        events = []
        for note in self.expected_notes:
            events.append(MIDIEvent(
                type='note_on',
                pitch=note.pitch,
                velocity=note.velocity,
                timestamp_ms=int(time.time() * 1000)
            ))
        return events

    def _generate_wrong_interval(self) -> List[MIDIEvent]:
        """Generate interval response that's off by one semitone."""
        if len(self.expected_notes) != 2:
            return self._generate_correct_response()

        events = []
        # First note correct
        events.append(MIDIEvent(
            type='note_on',
            pitch=self.expected_notes[0].pitch,
            velocity=self.expected_notes[0].velocity,
            timestamp_ms=int(time.time() * 1000)
        ))
        # Second note off by 1 semitone
        events.append(MIDIEvent(
            type='note_on',
            pitch=self.expected_notes[1].pitch + 1,
            velocity=self.expected_notes[1].velocity,
            timestamp_ms=int(time.time() * 1000)
        ))
        return events

    def _generate_wrong_chord(self) -> List[MIDIEvent]:
        """Generate wrong chord quality (change one interval)."""
        if len(self.expected_notes) < 3:
            return self._generate_correct_response()

        events = []
        # First two notes correct
        for i in range(min(2, len(self.expected_notes))):
            events.append(MIDIEvent(
                type='note_on',
                pitch=self.expected_notes[i].pitch,
                velocity=self.expected_notes[i].velocity,
                timestamp_ms=int(time.time() * 1000)
            ))

        # Third note altered by 1 semitone
        if len(self.expected_notes) >= 3:
            events.append(MIDIEvent(
                type='note_on',
                pitch=self.expected_notes[2].pitch + 1,
                velocity=self.expected_notes[2].velocity,
                timestamp_ms=int(time.time() * 1000)
            ))

        # Rest correct
        for i in range(3, len(self.expected_notes)):
            events.append(MIDIEvent(
                type='note_on',
                pitch=self.expected_notes[i].pitch,
                velocity=self.expected_notes[i].velocity,
                timestamp_ms=int(time.time() * 1000)
            ))

        return events

    def _generate_partial_melody(self) -> List[MIDIEvent]:
        """Generate melody with 70% accuracy."""
        events = []
        for i, note in enumerate(self.expected_notes):
            # Every 3rd note is wrong
            if i % 3 == 2:
                pitch = note.pitch + 2  # Off by a whole step
            else:
                pitch = note.pitch

            events.append(MIDIEvent(
                type='note_on',
                pitch=pitch,
                velocity=note.velocity,
                timestamp_ms=int(time.time() * 1000)
            ))
        return events

    def close(self):
        """Close device (no-op for test device)."""
        pass


class TestDrumKitProfile(DeviceProfile):
    """
    Simulated drum kit for testing rhythm exercises.

    Can operate in different modes:
    - "perfect": Perfect timing on all hits
    - "rushing": Consistently early by 20ms
    - "dragging": Consistently late by 20ms
    - "inconsistent": Random timing variations (±30ms)
    - "missed_hits": Randomly misses some hits
    - "extra_hits": Adds extra hits randomly
    """

    name_pattern = "test_drum_kit"
    capabilities = DeviceCapabilities(
        has_lights=False,
        has_aftertouch=False,
        is_mpe=False,
        note_range=(35, 81)  # General MIDI drum range
    )

    def __init__(self, mode: str = "perfect"):
        """
        Initialize test drum kit.

        Args:
            mode: Behavior mode (perfect, rushing, dragging, inconsistent, etc.)
        """
        from lyra_live.devices.drum_kit import GENERAL_MIDI_DRUM_MAP

        self.device_name = "TestDrumKit"
        self.mode = mode
        self.note_mapping = GENERAL_MIDI_DRUM_MAP
        self.part_to_note = {v: k for k, v in self.note_mapping.items()}
        self.expected_beats: Optional[List] = None

    def get_drum_part(self, midi_note: int) -> Optional[str]:
        """Get drum part name from MIDI note number."""
        return self.note_mapping.get(midi_note)

    def set_expected_pattern(self, beats):
        """
        Set the expected rhythm pattern for the next exercise.

        Args:
            beats: List of Beat objects with timing and drum parts
        """
        self.expected_beats = beats

    def send_note(self, pitch: int, velocity: int, duration_ms: int):
        """Simulate sending a note (no-op for test device)."""
        pass

    def detect_input(self, timeout_ms: int = 5000) -> Optional[List[MIDIEvent]]:
        """
        Simulate detecting drum hits based on mode and expected pattern.

        Args:
            timeout_ms: How long to wait for input

        Returns:
            List of simulated MIDI events with timing
        """
        if self.expected_beats is None:
            return []

        import random

        start_time = time.time() * 1000
        events = []

        for beat in self.expected_beats:
            # Check if we should skip this beat (missed_hits mode)
            if self.mode == "missed_hits" and random.random() < 0.2:
                continue

            # Calculate timing offset based on mode
            timing_offset = 0
            if self.mode == "rushing":
                timing_offset = -20  # 20ms early
            elif self.mode == "dragging":
                timing_offset = 20  # 20ms late
            elif self.mode == "inconsistent":
                timing_offset = random.randint(-30, 30)  # ±30ms variation

            # Get MIDI note for drum part
            midi_note = self.part_to_note.get(beat.drum_part, 38)  # Default to snare

            # Create event
            timestamp = int(start_time + beat.time_ms + timing_offset)
            events.append(MIDIEvent(
                type='note_on',
                pitch=midi_note,
                velocity=beat.velocity or 80,
                timestamp_ms=timestamp
            ))

        # Add extra hits for "extra_hits" mode
        if self.mode == "extra_hits":
            # Add a random extra hit
            if self.expected_beats:
                random_beat = random.choice(self.expected_beats)
                extra_time = random_beat.time_ms + random.randint(100, 200)
                midi_note = self.part_to_note.get(random_beat.drum_part, 38)

                events.append(MIDIEvent(
                    type='note_on',
                    pitch=midi_note,
                    velocity=80,
                    timestamp_ms=int(start_time + extra_time)
                ))

        return events if events else None

    def close(self):
        """Close device (no-op for test device)."""
        pass
