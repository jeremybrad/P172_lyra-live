"""
Pitch detection for voice input using aubio.

Provides real-time pitch detection for singing exercises,
with configurable tolerance and confidence thresholds.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List
import time


@dataclass
class PitchReading:
    """A single pitch detection reading."""
    frequency: float  # Hz
    pitch: Optional[int]  # MIDI note number (None if unpitched/too quiet)
    confidence: float  # 0.0 to 1.0
    timestamp_ms: int  # Milliseconds since detection started

    @property
    def cents_from_pitch(self) -> Optional[float]:
        """Calculate cents deviation from nearest MIDI pitch."""
        if self.pitch is None or self.frequency <= 0:
            return None

        import math
        midi_freq = 440.0 * (2.0 ** ((self.pitch - 69) / 12.0))
        cents = 1200.0 * math.log2(self.frequency / midi_freq)
        return cents


class PitchDetector(ABC):
    """
    Abstract base class for pitch detection.

    Implementations can use microphone input (aubio) or
    test/simulation input (for unit testing).
    """

    @abstractmethod
    def start_listening(self) -> None:
        """Begin pitch detection."""
        pass

    @abstractmethod
    def stop_listening(self) -> None:
        """Stop pitch detection."""
        pass

    @abstractmethod
    def get_pitch_reading(self) -> Optional[PitchReading]:
        """
        Get a single pitch reading.

        Returns None if no pitch detected (silence, noise, etc.)
        """
        pass

    @abstractmethod
    def get_sustained_pitch(
        self,
        duration_ms: int = 1000,
        min_confidence: float = 0.7
    ) -> Optional[int]:
        """
        Detect a sustained pitch over a duration.

        Args:
            duration_ms: How long to listen (milliseconds)
            min_confidence: Minimum confidence threshold (0.0 to 1.0)

        Returns:
            MIDI note number if consistent pitch detected, None otherwise
        """
        pass


class AubioPitchDetector(PitchDetector):
    """
    Pitch detector using aubio library for microphone input.

    Uses aubio's pitch detection algorithm (default: yinfft) for
    accurate fundamental frequency estimation.
    """

    def __init__(
        self,
        sample_rate: int = 44100,
        buffer_size: int = 2048,
        hop_size: int = 512,
        method: str = "yinfft",
        min_confidence: float = 0.6
    ):
        """
        Initialize aubio pitch detector.

        Args:
            sample_rate: Audio sample rate (Hz)
            buffer_size: Size of analysis buffer
            hop_size: Number of samples between analyses
            method: Pitch detection method (yinfft, yin, mcomb, fcomb, schmitt)
            min_confidence: Minimum confidence for valid detection
        """
        try:
            import aubio
            import pyaudio
        except ImportError as e:
            raise ImportError(
                f"Voice features require aubio and pyaudio: {e}\n"
                "Install with: pip install aubio pyaudio"
            )

        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.hop_size = hop_size
        self.min_confidence = min_confidence

        # Create aubio pitch detector
        self.pitch_detector = aubio.pitch(method, buffer_size, hop_size, sample_rate)
        self.pitch_detector.set_unit("midi")
        self.pitch_detector.set_silence(-40)  # dB threshold for silence

        # PyAudio setup
        self.pyaudio = pyaudio.PyAudio()
        self.stream = None
        self.start_time = None

    def start_listening(self) -> None:
        """Begin pitch detection from microphone."""
        import pyaudio

        self.stream = self.pyaudio.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.hop_size
        )
        self.start_time = time.time()

    def stop_listening(self) -> None:
        """Stop pitch detection."""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

    def get_pitch_reading(self) -> Optional[PitchReading]:
        """Get a single pitch reading from microphone."""
        import aubio
        import numpy as np

        if not self.stream:
            raise RuntimeError("Must call start_listening() first")

        # Read audio data
        audio_data = self.stream.read(self.hop_size, exception_on_overflow=False)
        audio_samples = np.frombuffer(audio_data, dtype=np.float32)

        # Detect pitch
        midi_pitch = self.pitch_detector(audio_samples)[0]
        confidence = self.pitch_detector.get_confidence()

        # Get timestamp
        timestamp_ms = int((time.time() - self.start_time) * 1000)

        # Convert MIDI to frequency
        if midi_pitch > 0 and confidence >= self.min_confidence:
            frequency = 440.0 * (2.0 ** ((midi_pitch - 69) / 12.0))
            pitch_int = int(round(midi_pitch))

            return PitchReading(
                frequency=frequency,
                pitch=pitch_int,
                confidence=confidence,
                timestamp_ms=timestamp_ms
            )
        else:
            # No valid pitch detected (silence, noise, etc.)
            return PitchReading(
                frequency=0.0,
                pitch=None,
                confidence=confidence,
                timestamp_ms=timestamp_ms
            )

    def get_sustained_pitch(
        self,
        duration_ms: int = 1000,
        min_confidence: float = 0.7
    ) -> Optional[int]:
        """
        Detect a sustained pitch over a duration.

        Collects pitch readings over the specified duration and returns
        the most common pitch if it meets confidence requirements.
        """
        if not self.stream:
            raise RuntimeError("Must call start_listening() first")

        readings: List[PitchReading] = []
        start = time.time()

        while (time.time() - start) * 1000 < duration_ms:
            reading = self.get_pitch_reading()
            if reading and reading.pitch is not None and reading.confidence >= min_confidence:
                readings.append(reading)

        if not readings:
            return None

        # Find most common pitch
        from collections import Counter
        pitch_counts = Counter(r.pitch for r in readings)
        most_common_pitch, count = pitch_counts.most_common(1)[0]

        # Require at least 60% consistency
        if count / len(readings) >= 0.6:
            return most_common_pitch

        return None

    def __del__(self):
        """Cleanup audio resources."""
        if self.stream:
            self.stop_listening()
        if hasattr(self, 'pyaudio'):
            self.pyaudio.terminate()


def frequency_to_midi(frequency: float) -> int:
    """
    Convert frequency (Hz) to MIDI note number.

    Args:
        frequency: Frequency in Hz

    Returns:
        MIDI note number (0-127)
    """
    import math

    if frequency <= 0:
        return 0

    midi = 69 + 12 * math.log2(frequency / 440.0)
    return max(0, min(127, int(round(midi))))


def midi_to_frequency(midi_note: int) -> float:
    """
    Convert MIDI note number to frequency (Hz).

    Args:
        midi_note: MIDI note number (0-127)

    Returns:
        Frequency in Hz
    """
    return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))


def detect_pitch_over_time(
    audio_path: str,
    sample_rate: int = 44100,
    buffer_size: int = 2048,
    hop_size: int = 512,
    method: str = "yinfft",
    min_confidence: float = 0.6
) -> List[PitchReading]:
    """
    Detect pitch over time from a recorded audio file.

    This is designed for analyzing improvisation solos - it processes
    the entire audio file and returns a time series of pitch readings.

    Args:
        audio_path: Path to WAV file to analyze
        sample_rate: Audio sample rate (should match the file)
        buffer_size: Size of analysis buffer
        hop_size: Number of samples between analyses
        method: Pitch detection method (yinfft, yin, mcomb, fcomb, schmitt)
        min_confidence: Minimum confidence for valid detection

    Returns:
        List of PitchReading objects with timestamps

    Raises:
        ImportError: If aubio is not installed
        FileNotFoundError: If audio file doesn't exist
    """
    try:
        import aubio
        import numpy as np
    except ImportError as e:
        raise ImportError(
            f"Pitch detection requires aubio: {e}\n"
            "Install with: pip install aubio"
        )

    from pathlib import Path
    import wave

    audio_path = Path(audio_path)
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    # Create aubio pitch detector
    pitch_detector = aubio.pitch(method, buffer_size, hop_size, sample_rate)
    pitch_detector.set_unit("midi")
    pitch_detector.set_silence(-40)  # dB threshold for silence

    # Read the WAV file
    with wave.open(str(audio_path), 'rb') as wf:
        # Verify it's mono
        if wf.getnchannels() != 1:
            raise ValueError("Audio file must be mono (1 channel)")

        # Read all audio data
        num_frames = wf.getnframes()
        audio_bytes = wf.readframes(num_frames)

        # Convert to numpy array
        # Most WAV files are 16-bit int
        audio_samples = np.frombuffer(audio_bytes, dtype=np.int16)
        # Convert to float32 in range [-1.0, 1.0]
        audio_samples = audio_samples.astype(np.float32) / 32768.0

    # Process audio in chunks
    readings: List[PitchReading] = []
    num_samples = len(audio_samples)

    for i in range(0, num_samples - hop_size, hop_size):
        # Extract chunk
        chunk = audio_samples[i:i + hop_size]

        # Detect pitch
        midi_pitch = pitch_detector(chunk)[0]
        confidence = pitch_detector.get_confidence()

        # Calculate timestamp in milliseconds
        timestamp_ms = int((i / sample_rate) * 1000)

        # Convert MIDI to frequency
        if midi_pitch > 0 and confidence >= min_confidence:
            frequency = 440.0 * (2.0 ** ((midi_pitch - 69) / 12.0))
            pitch_int = int(round(midi_pitch))

            readings.append(PitchReading(
                frequency=frequency,
                pitch=pitch_int,
                confidence=confidence,
                timestamp_ms=timestamp_ms
            ))
        else:
            # No valid pitch detected (silence, noise, etc.)
            readings.append(PitchReading(
                frequency=0.0,
                pitch=None,
                confidence=confidence,
                timestamp_ms=timestamp_ms
            ))

    return readings
