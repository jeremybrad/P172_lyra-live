"""
Audio capture module for improvisation sessions.

Provides simple audio recording from microphone for a specified duration.
Works with the existing voice/pitch detection infrastructure.
"""

import wave
import tempfile
from pathlib import Path
from typing import Optional, Tuple
import time


class AudioCapture:
    """
    Simple audio capture for improvisation sessions.

    Records audio from the default microphone for a specified duration
    and saves to a temporary WAV file.
    """

    def __init__(self, sample_rate: int = 44100, channels: int = 1):
        """
        Initialize audio capture.

        Args:
            sample_rate: Audio sample rate in Hz (default: 44100)
            channels: Number of audio channels (default: 1 for mono)
        """
        self.sample_rate = sample_rate
        self.channels = channels

    def calculate_duration(self, tune_tempo: int, time_signature: Tuple[int, int],
                          chorus_bars: int, chorus_count: int) -> float:
        """
        Calculate the duration in seconds for N choruses at a given tempo.

        Args:
            tune_tempo: Tempo in BPM
            time_signature: (numerator, denominator) e.g., (4, 4)
            chorus_bars: Number of bars per chorus
            chorus_count: Number of choruses to record

        Returns:
            Duration in seconds
        """
        numerator, denominator = time_signature

        # Calculate beats per bar
        beats_per_bar = numerator

        # Total beats = bars * beats_per_bar * chorus_count
        total_beats = chorus_bars * beats_per_bar * chorus_count

        # Duration in seconds = total_beats / (tempo / 60)
        duration_seconds = (total_beats / tune_tempo) * 60

        # Add a small buffer (0.5 seconds) to ensure we capture everything
        return duration_seconds + 0.5

    def record(self, duration_seconds: float, output_path: Optional[Path] = None) -> Path:
        """
        Record audio from the microphone for a specified duration.

        Args:
            duration_seconds: How long to record in seconds
            output_path: Optional path to save the WAV file. If None, uses a temp file.

        Returns:
            Path to the recorded WAV file

        Raises:
            ImportError: If pyaudio is not installed
            OSError: If no microphone is available
        """
        try:
            import pyaudio
        except ImportError:
            raise ImportError(
                "Audio capture requires pyaudio. Install with: pip install pyaudio"
            )

        # Create output path
        if output_path is None:
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            output_path = Path(temp_file.name)
            temp_file.close()
        else:
            output_path = Path(output_path)

        # Initialize PyAudio
        p = pyaudio.PyAudio()

        # Audio format
        format = pyaudio.paInt16  # 16-bit audio
        chunk_size = 1024  # Frames per buffer

        try:
            # Open audio stream
            stream = p.open(
                format=format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=chunk_size
            )

            print(f"🎤 Recording for {duration_seconds:.1f} seconds...")

            frames = []
            num_chunks = int(self.sample_rate / chunk_size * duration_seconds)

            start_time = time.time()

            # Record audio
            for i in range(num_chunks):
                data = stream.read(chunk_size)
                frames.append(data)

                # Show progress
                elapsed = time.time() - start_time
                if int(elapsed) != int(elapsed - 0.5):  # Print once per second
                    remaining = duration_seconds - elapsed
                    if remaining > 0:
                        print(f"   Recording... {remaining:.1f}s remaining", end='\r')

            print(f"\n✓ Recording complete")

            # Stop and close stream
            stream.stop_stream()
            stream.close()

            # Write to WAV file
            with wave.open(str(output_path), 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(p.get_sample_size(format))
                wf.setframerate(self.sample_rate)
                wf.writeframes(b''.join(frames))

        finally:
            p.terminate()

        return output_path

    def record_for_tune(self, tune_tempo: int, time_signature: Tuple[int, int],
                       chorus_bars: int, chorus_count: int,
                       output_path: Optional[Path] = None) -> Path:
        """
        Record audio for a specific number of choruses of a tune.

        Convenience method that calculates duration and records.

        Args:
            tune_tempo: Tempo in BPM
            time_signature: (numerator, denominator)
            chorus_bars: Number of bars per chorus
            chorus_count: Number of choruses to record
            output_path: Optional output path

        Returns:
            Path to the recorded WAV file
        """
        duration = self.calculate_duration(
            tune_tempo, time_signature, chorus_bars, chorus_count
        )

        return self.record(duration, output_path)


class SimulatedAudioCapture(AudioCapture):
    """
    Simulated audio capture for testing without a microphone.

    Generates silent audio or accepts pre-generated audio buffers.
    """

    def __init__(self, sample_rate: int = 44100, channels: int = 1):
        super().__init__(sample_rate, channels)
        self.simulated_audio_path: Optional[Path] = None

    def set_simulated_audio(self, audio_path: Path):
        """
        Set a pre-recorded audio file to use for simulation.

        Args:
            audio_path: Path to a WAV file to use instead of recording
        """
        self.simulated_audio_path = audio_path

    def record(self, duration_seconds: float, output_path: Optional[Path] = None) -> Path:
        """
        Simulate recording by either copying a pre-set audio file or generating silence.

        Args:
            duration_seconds: Duration (used for generating silence if no audio set)
            output_path: Optional output path

        Returns:
            Path to the audio file
        """
        if self.simulated_audio_path and self.simulated_audio_path.exists():
            # Use pre-set audio file
            if output_path is None:
                return self.simulated_audio_path
            else:
                # Copy to requested path
                import shutil
                shutil.copy(self.simulated_audio_path, output_path)
                return Path(output_path)
        else:
            # Generate silent audio for testing
            if output_path is None:
                temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
                output_path = Path(temp_file.name)
                temp_file.close()
            else:
                output_path = Path(output_path)

            # Create silent WAV file
            num_samples = int(self.sample_rate * duration_seconds)

            with wave.open(str(output_path), 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(self.sample_rate)
                # Write silence
                wf.writeframes(b'\x00\x00' * num_samples * self.channels)

            return output_path
