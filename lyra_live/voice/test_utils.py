"""
Test utilities for voice exercises.

Provides TestVoiceInput for simulating singing without a microphone.
"""

from typing import Optional
from lyra_live.voice.pitch import PitchDetector, PitchReading


class TestVoiceInput(PitchDetector):
    """
    Simulated voice input for testing.

    Allows testing voice exercises without a microphone by providing
    pre-programmed pitch responses.
    """

    def __init__(self, mode: str = "correct"):
        """
        Initialize test voice input.

        Args:
            mode: Simulation mode
                - "correct": Sing correct pitches
                - "off_pitch": Sing slightly sharp (+30 cents)
                - "wrong_note": Sing wrong notes (up a semitone)
                - "no_input": Simulate silence (no pitch detected)
        """
        self.mode = mode
        self.expected_pitch: Optional[int] = None
        self.is_listening = False
        self.start_time_ms = 0

    def set_expected_pitch(self, pitch: int):
        """Set the expected pitch for the next exercise."""
        self.expected_pitch = pitch

    def start_listening(self) -> None:
        """Begin pitch detection."""
        self.is_listening = True
        import time
        self.start_time_ms = int(time.time() * 1000)

    def stop_listening(self) -> None:
        """Stop pitch detection."""
        self.is_listening = False

    def get_pitch_reading(self) -> Optional[PitchReading]:
        """
        Get a single pitch reading.

        Returns simulated pitch based on mode and expected pitch.
        """
        if not self.is_listening:
            raise RuntimeError("Must call start_listening() first")

        if self.mode == "no_input" or self.expected_pitch is None:
            return PitchReading(
                frequency=0.0,
                pitch=None,
                confidence=0.0,
                timestamp_ms=0
            )

        import time
        from lyra_live.voice.pitch import midi_to_frequency

        timestamp_ms = int((time.time() * 1000) - self.start_time_ms)

        if self.mode == "correct":
            # Sing exactly the expected pitch
            freq = midi_to_frequency(self.expected_pitch)
            return PitchReading(
                frequency=freq,
                pitch=self.expected_pitch,
                confidence=0.95,
                timestamp_ms=timestamp_ms
            )

        elif self.mode == "off_pitch":
            # Sing 30 cents sharp
            freq = midi_to_frequency(self.expected_pitch) * (2 ** (30 / 1200))
            return PitchReading(
                frequency=freq,
                pitch=self.expected_pitch,  # Still same note, just sharp
                confidence=0.85,
                timestamp_ms=timestamp_ms
            )

        elif self.mode == "wrong_note":
            # Sing a semitone higher
            wrong_pitch = self.expected_pitch + 1
            freq = midi_to_frequency(wrong_pitch)
            return PitchReading(
                frequency=freq,
                pitch=wrong_pitch,
                confidence=0.90,
                timestamp_ms=timestamp_ms
            )

        return None

    def get_sustained_pitch(
        self,
        duration_ms: int = 1000,
        min_confidence: float = 0.7
    ) -> Optional[int]:
        """
        Detect a sustained pitch over a duration.

        For testing, immediately returns the simulated pitch.
        """
        if not self.is_listening:
            raise RuntimeError("Must call start_listening() first")

        if self.mode == "no_input":
            return None

        if self.expected_pitch is None:
            return None

        # Simulate reading over duration
        import time
        time.sleep(duration_ms / 1000.0)

        reading = self.get_pitch_reading()
        if reading and reading.pitch is not None and reading.confidence >= min_confidence:
            return reading.pitch

        return None

    def set_mode(self, mode: str):
        """Change the simulation mode."""
        self.mode = mode
