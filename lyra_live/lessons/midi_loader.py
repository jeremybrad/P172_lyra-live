"""
MIDI file loading and phrase extraction.

Utilities for loading external MIDI files and converting them
into Lesson objects with LessonPhrase segments.
"""

import mido
from typing import List, Optional
from lyra_live.ear_training.base import Note
from lyra_live.lessons.core import Lesson, LessonPhrase


def load_midi_file(file_path: str, track_index: int = 0) -> List[Note]:
    """
    Load a MIDI file and extract notes from a specific track.

    Args:
        file_path: Path to MIDI file
        track_index: Which track to extract (default: 0 = first track)

    Returns:
        List of Note objects from the track
    """
    try:
        mid = mido.MidiFile(file_path)
    except Exception as e:
        raise ValueError(f"Could not load MIDI file {file_path}: {e}")

    if track_index >= len(mid.tracks):
        raise ValueError(f"Track {track_index} not found (file has {len(mid.tracks)} tracks)")

    track = mid.tracks[track_index]
    notes = []
    current_time = 0
    active_notes = {}  # Track note_on events to calculate durations

    for msg in track:
        current_time += msg.time

        if msg.type == 'note_on' and msg.velocity > 0:
            # Note start
            active_notes[msg.note] = {
                'start_time': current_time,
                'velocity': msg.velocity
            }

        elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
            # Note end
            if msg.note in active_notes:
                note_data = active_notes[msg.note]
                duration_ticks = current_time - note_data['start_time']

                # Convert ticks to milliseconds (approximate)
                # MIDI tempo is typically 500000 microseconds per quarter note (120 BPM)
                # This is a simplification; real tempo changes require parsing
                ticks_per_beat = mid.ticks_per_beat
                duration_ms = int((duration_ticks / ticks_per_beat) * 500)  # Rough estimate

                notes.append(Note(
                    pitch=msg.note,
                    duration_ms=max(duration_ms, 100),  # Minimum 100ms
                    velocity=note_data['velocity']
                ))

                del active_notes[msg.note]

    return notes


def slice_into_phrases(
    notes: List[Note],
    phrase_length: int = 8,
    overlap: int = 0
) -> List[List[Note]]:
    """
    Slice a melody into phrases of a given length.

    Args:
        notes: List of notes to slice
        phrase_length: Number of notes per phrase
        overlap: Number of overlapping notes between phrases

    Returns:
        List of phrase note lists
    """
    if not notes:
        return []

    phrases = []
    i = 0

    while i < len(notes):
        end_idx = min(i + phrase_length, len(notes))
        phrase = notes[i:end_idx]

        if len(phrase) > 0:
            phrases.append(phrase)

        # Move forward by phrase_length - overlap
        step = max(phrase_length - overlap, 1)
        i += step

        # Stop if the remaining notes are too short
        if i < len(notes) and len(notes) - i < phrase_length // 2:
            # Add the remaining as final phrase
            phrases.append(notes[i:])
            break

    return phrases


def create_lesson_from_midi(
    file_path: str,
    lesson_id: str,
    title: str,
    artist: Optional[str] = None,
    track_index: int = 0,
    phrase_length: int = 8,
    difficulty: str = "intermediate"
) -> Lesson:
    """
    Create a Lesson object from a MIDI file.

    Args:
        file_path: Path to MIDI file
        lesson_id: Unique ID for the lesson
        title: Lesson title
        artist: Artist/composer name
        track_index: Which track to use from MIDI file
        phrase_length: How many notes per phrase
        difficulty: Difficulty level

    Returns:
        Lesson object with phrases extracted from MIDI
    """
    # Load notes from MIDI
    notes = load_midi_file(file_path, track_index)

    # Slice into phrases
    phrase_note_lists = slice_into_phrases(notes, phrase_length=phrase_length)

    # Create LessonPhrase objects
    phrases = []
    for i, phrase_notes in enumerate(phrase_note_lists):
        phrase = LessonPhrase(
            id=f"{lesson_id}_phrase_{i+1}",
            notes=phrase_notes,
            description=f"Phrase {i+1}"
        )
        phrases.append(phrase)

    # Create Lesson
    lesson = Lesson(
        id=lesson_id,
        title=title,
        artist=artist,
        difficulty=difficulty,
        phrases=phrases,
        metadata={"source_file": file_path}
    )

    return lesson
