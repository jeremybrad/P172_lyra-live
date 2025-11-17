"""
MIDI parsing utilities for jazz standards.

Extracts tempo, time signature, and attempts to infer chord changes
from MIDI files (typically exported from Band-in-a-Box).
"""

from pathlib import Path
from typing import Optional, List, Tuple, Dict
from dataclasses import dataclass
import mido

from lyra_live.standards.core import ChordChange


@dataclass
class MIDIMetadata:
    """Metadata extracted from a MIDI file."""
    tempo: int  # BPM
    time_signature: Tuple[int, int]
    total_bars: int
    total_ticks: int
    ticks_per_beat: int


def parse_standard_midi(midi_path: Path) -> MIDIMetadata:
    """
    Parse metadata from a standard MIDI file.

    Args:
        midi_path: Path to MIDI file

    Returns:
        MIDIMetadata with tempo, time signature, and structure info
    """
    midi_file = mido.MidiFile(midi_path)

    # Default values
    tempo_bpm = 120
    time_sig = (4, 4)
    ticks_per_beat = midi_file.ticks_per_beat

    # Scan for tempo and time signature events
    for track in midi_file.tracks:
        for msg in track:
            if msg.type == 'set_tempo':
                # Convert microseconds per beat to BPM
                tempo_bpm = int(mido.tempo2bpm(msg.tempo))
            elif msg.type == 'time_signature':
                time_sig = (msg.numerator, msg.denominator)

    # Calculate total length
    total_ticks = max(
        sum(msg.time for msg in track)
        for track in midi_file.tracks
    )

    # Calculate bars
    beats_per_bar = time_sig[0]
    ticks_per_bar = ticks_per_beat * beats_per_bar
    total_bars = (total_ticks + ticks_per_bar - 1) // ticks_per_bar  # Ceiling division

    return MIDIMetadata(
        tempo=tempo_bpm,
        time_signature=time_sig,
        total_bars=total_bars,
        total_ticks=total_ticks,
        ticks_per_beat=ticks_per_beat
    )


def extract_chord_grid(
    midi_path: Path,
    chord_track_name: Optional[str] = None
) -> List[ChordChange]:
    """
    Extract chord changes from a MIDI file.

    Band-in-a-Box often exports chord symbols as text meta events
    or in a dedicated chord track. This function attempts to parse them.

    Args:
        midi_path: Path to MIDI file
        chord_track_name: Name of track containing chords (if known)

    Returns:
        List of ChordChange objects
    """
    midi_file = mido.MidiFile(midi_path)
    metadata = parse_standard_midi(midi_path)

    chord_changes = []
    ticks_per_beat = metadata.ticks_per_beat
    beats_per_bar = metadata.time_signature[0]

    # Try to find chord information in text events or markers
    for track_idx, track in enumerate(midi_file.tracks):
        # Check if this is a likely chord track
        if chord_track_name and hasattr(track, 'name'):
            if chord_track_name not in track.name:
                continue

        current_tick = 0
        for msg in track:
            current_tick += msg.time

            # Look for text events that might contain chord symbols
            if msg.type in ['text', 'marker', 'lyrics']:
                text = msg.text.strip()

                # Simple heuristic: if it looks like a chord symbol, parse it
                if _looks_like_chord_symbol(text):
                    # Calculate bar and beat
                    beat_number = current_tick / ticks_per_beat
                    bar = int(beat_number // beats_per_bar)
                    beat_in_bar = (beat_number % beats_per_bar) + 1.0

                    chord_changes.append(ChordChange(
                        bar=bar,
                        beat=beat_in_bar,
                        chord_symbol=text,
                        duration_beats=4.0  # Default duration
                    ))

    # If we found chord changes, calculate durations
    if chord_changes:
        _calculate_chord_durations(chord_changes, metadata.total_bars, beats_per_bar)

    return chord_changes


def _looks_like_chord_symbol(text: str) -> bool:
    """
    Heuristic to determine if a text string looks like a chord symbol.

    Examples: "Cmaj7", "Dm7", "G7", "F#m7b5", "Bb9", etc.
    """
    if not text or len(text) > 10:
        return False

    # Must start with a note name (A-G, possibly with # or b)
    if text[0] not in 'ABCDEFG':
        return False

    # Common chord quality indicators
    chord_patterns = ['maj', 'min', 'm7', 'M7', '7', '9', '11', '13',
                      'dim', 'aug', 'sus', '+', '-', '°', 'Δ', 'ø']

    # Check if it contains any chord quality indicator
    text_upper = text.upper()
    has_quality = any(pattern.upper() in text_upper for pattern in chord_patterns)

    # Or is just a root note (e.g., "C" for C major)
    is_simple_root = len(text) <= 2 and text[0] in 'ABCDEFG'

    return has_quality or is_simple_root


def _calculate_chord_durations(
    changes: List[ChordChange],
    total_bars: int,
    beats_per_bar: int
):
    """
    Calculate duration for each chord change based on the next change.

    Modifies the changes list in place.
    """
    for i, change in enumerate(changes):
        if i < len(changes) - 1:
            # Duration until next change
            next_change = changes[i + 1]

            # Calculate beats between changes
            bars_diff = next_change.bar - change.bar
            beats_diff = (next_change.beat - change.beat) + (bars_diff * beats_per_bar)

            change.duration_beats = max(1.0, beats_diff)
        else:
            # Last change: duration until end of chorus or default
            bars_remaining = total_bars - change.bar
            change.duration_beats = bars_remaining * beats_per_bar


def simplify_chord_grid(changes: List[ChordChange], bars_per_chorus: int) -> List[ChordChange]:
    """
    Simplify a chord grid to one chorus (if it contains multiple choruses).

    Assumes the chord changes repeat after bars_per_chorus.

    Args:
        changes: Full list of chord changes
        bars_per_chorus: Number of bars in one chorus

    Returns:
        Simplified list with just one chorus
    """
    # Filter to first chorus only
    first_chorus = [
        ChordChange(
            bar=ch.bar % bars_per_chorus,
            beat=ch.beat,
            chord_symbol=ch.chord_symbol,
            duration_beats=ch.duration_beats
        )
        for ch in changes
        if ch.bar < bars_per_chorus
    ]

    return first_chorus


def get_chord_symbols_by_bar(changes: List[ChordChange]) -> Dict[int, List[str]]:
    """
    Group chord changes by bar number.

    Args:
        changes: List of chord changes

    Returns:
        Dict mapping bar number to list of chord symbols in that bar
    """
    by_bar: Dict[int, List[str]] = {}

    for change in changes:
        if change.bar not in by_bar:
            by_bar[change.bar] = []
        by_bar[change.bar].append(change.chord_symbol)

    return by_bar
