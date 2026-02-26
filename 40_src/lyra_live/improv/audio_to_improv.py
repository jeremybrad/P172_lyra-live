"""
Convert audio pitch curves to ImprovNote objects for analysis.

Takes pitch-over-time data from audio recordings and groups stable
segments into note events suitable for harmonic/rhythmic analysis.
"""

from typing import List, Tuple
from lyra_live.voice.pitch import PitchReading
from lyra_live.improv.core import ImprovNote, ImprovChorus
from lyra_live.standards.core import StandardTune
import math


def group_pitch_readings_into_notes(
    readings: List[PitchReading],
    min_duration_ms: int = 100,
    max_pitch_deviation: float = 50.0  # cents
) -> List[dict]:
    """
    Group pitch readings into note events.

    Consecutive readings with similar pitch are grouped into a single note.
    Very short notes (< min_duration_ms) are filtered out.

    Args:
        readings: List of PitchReading objects from pitch detection
        min_duration_ms: Minimum note duration to keep (milliseconds)
        max_pitch_deviation: Maximum pitch deviation (cents) to consider same note

    Returns:
        List of note dicts with keys:
            - pitch: MIDI note number
            - start_time_ms: Start time in milliseconds
            - duration_ms: Duration in milliseconds
            - cents_offset: Average cents deviation from tempered pitch
            - confidence: Average confidence
    """
    if not readings:
        return []

    notes = []
    current_note = None

    for reading in readings:
        # Skip invalid/silent readings
        if reading.pitch is None:
            # End current note if exists
            if current_note is not None:
                # Only add if long enough
                duration = current_note['end_time_ms'] - current_note['start_time_ms']
                if duration >= min_duration_ms:
                    current_note['duration_ms'] = duration
                    # Calculate averages
                    current_note['cents_offset'] = (
                        sum(current_note['cents_samples']) / len(current_note['cents_samples'])
                    )
                    current_note['confidence'] = (
                        sum(current_note['confidence_samples']) / len(current_note['confidence_samples'])
                    )
                    # Remove temporary fields
                    del current_note['cents_samples']
                    del current_note['confidence_samples']
                    del current_note['end_time_ms']
                    notes.append(current_note)

                current_note = None
            continue

        # Check if this continues the current note
        if current_note is not None:
            # Check if pitch is similar
            if reading.pitch == current_note['pitch']:
                # Same MIDI note - extend current note
                current_note['end_time_ms'] = reading.timestamp_ms
                if reading.cents_from_pitch is not None:
                    current_note['cents_samples'].append(reading.cents_from_pitch)
                current_note['confidence_samples'].append(reading.confidence)
                continue
            else:
                # Different pitch - finish current note and start new one
                duration = current_note['end_time_ms'] - current_note['start_time_ms']
                if duration >= min_duration_ms:
                    current_note['duration_ms'] = duration
                    current_note['cents_offset'] = (
                        sum(current_note['cents_samples']) / len(current_note['cents_samples'])
                        if current_note['cents_samples'] else 0.0
                    )
                    current_note['confidence'] = (
                        sum(current_note['confidence_samples']) / len(current_note['confidence_samples'])
                    )
                    del current_note['cents_samples']
                    del current_note['confidence_samples']
                    del current_note['end_time_ms']
                    notes.append(current_note)

        # Start new note
        current_note = {
            'pitch': reading.pitch,
            'start_time_ms': reading.timestamp_ms,
            'end_time_ms': reading.timestamp_ms,
            'cents_samples': [reading.cents_from_pitch] if reading.cents_from_pitch is not None else [],
            'confidence_samples': [reading.confidence],
        }

    # Don't forget the last note
    if current_note is not None:
        duration = current_note['end_time_ms'] - current_note['start_time_ms']
        if duration >= min_duration_ms:
            current_note['duration_ms'] = duration
            current_note['cents_offset'] = (
                sum(current_note['cents_samples']) / len(current_note['cents_samples'])
                if current_note['cents_samples'] else 0.0
            )
            current_note['confidence'] = (
                sum(current_note['confidence_samples']) / len(current_note['confidence_samples'])
            )
            del current_note['cents_samples']
            del current_note['confidence_samples']
            del current_note['end_time_ms']
            notes.append(current_note)

    return notes


def calculate_bar_and_beat(
    time_ms: int,
    tempo_bpm: int,
    time_signature: Tuple[int, int]
) -> Tuple[int, float]:
    """
    Calculate bar and beat position from time in milliseconds.

    Args:
        time_ms: Time in milliseconds
        tempo_bpm: Tempo in beats per minute
        time_signature: (numerator, denominator) e.g., (4, 4)

    Returns:
        (bar, beat) where bar is 0-indexed and beat is 1-indexed float
    """
    numerator, denominator = time_signature

    # Calculate total beats elapsed
    beats_elapsed = (time_ms / 1000.0) * (tempo_bpm / 60.0)

    # Calculate beats per bar
    beats_per_bar = numerator

    # Calculate bar (0-indexed)
    bar = int(beats_elapsed / beats_per_bar)

    # Calculate beat within bar (1-indexed)
    beat = (beats_elapsed % beats_per_bar) + 1.0

    return bar, beat


def pitch_readings_to_improv_notes(
    readings: List[PitchReading],
    tune: StandardTune,
    min_duration_ms: int = 100
) -> List[ImprovNote]:
    """
    Convert pitch readings to ImprovNote objects.

    This is the main conversion function that takes raw pitch detection
    data and creates properly structured ImprovNote objects with:
    - Bar/beat positions
    - Chord context
    - Cents deviation

    Args:
        readings: List of PitchReading objects from pitch detection
        tune: StandardTune to provide tempo, time signature, and chord context
        min_duration_ms: Minimum note duration to keep

    Returns:
        List of ImprovNote objects ready for analysis
    """
    # Group readings into notes
    note_dicts = group_pitch_readings_into_notes(readings, min_duration_ms)

    # Convert to ImprovNote objects
    improv_notes = []

    for note_dict in note_dicts:
        # Calculate bar and beat
        bar, beat = calculate_bar_and_beat(
            note_dict['start_time_ms'],
            tune.tempo,
            tune.time_signature
        )

        # Get chord at this position
        chord_at_time = tune.get_chord_at_time(bar, beat)

        # Create ImprovNote
        improv_note = ImprovNote(
            time_ms=note_dict['start_time_ms'],
            pitch=note_dict['pitch'],
            velocity=int(note_dict['confidence'] * 127),  # Map confidence to velocity
            duration_ms=note_dict['duration_ms'],
            bar=bar,
            beat=beat
        )

        # Set additional fields
        improv_note.chord_at_time = chord_at_time

        # Store cents offset as additional metadata if needed
        # (This isn't in the base ImprovNote but could be useful)

        improv_notes.append(improv_note)

    return improv_notes


def audio_to_improv_chorus(
    audio_path: str,
    tune: StandardTune,
    chorus_number: int = 1,
    min_note_duration_ms: int = 100
) -> ImprovChorus:
    """
    Convert an audio recording to an ImprovChorus for analysis.

    This is the complete pipeline:
    1. Detect pitch over time from audio
    2. Group pitch readings into notes
    3. Create ImprovNote objects with bar/beat/chord context
    4. Wrap in ImprovChorus structure

    Args:
        audio_path: Path to WAV file containing the solo
        tune: StandardTune for tempo/time sig/chord context
        chorus_number: Which chorus this is (default: 1)
        min_note_duration_ms: Minimum note duration to keep

    Returns:
        ImprovChorus ready for harmonic/rhythmic analysis

    Raises:
        ImportError: If aubio is not installed
        FileNotFoundError: If audio file doesn't exist
    """
    from lyra_live.voice.pitch import detect_pitch_over_time

    # Step 1: Detect pitch over time
    print(f"🎵 Analyzing audio: {audio_path}")
    pitch_readings = detect_pitch_over_time(audio_path)
    print(f"   Detected {len(pitch_readings)} pitch readings")

    # Step 2 & 3: Convert to ImprovNotes
    improv_notes = pitch_readings_to_improv_notes(
        pitch_readings,
        tune,
        min_note_duration_ms
    )
    print(f"   Grouped into {len(improv_notes)} notes")

    # Step 4: Create ImprovChorus
    chorus = ImprovChorus(
        chorus_number=chorus_number,
        tune=tune,
        start_time_ms=0,
        notes=improv_notes
    )

    return chorus
