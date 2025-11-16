"""
Core exercise data structures.

Defines the abstract representations for musical exercises, notes,
and results that are device-agnostic.
"""

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class ExerciseType(Enum):
    """Types of ear training exercises"""
    INTERVAL = "interval"
    CHORD = "chord"
    MELODY = "melody"


@dataclass
class Note:
    """
    Abstract note representation.

    Device-agnostic representation of a musical note.
    """
    pitch: int  # MIDI note number (0-127)
    duration_ms: int
    velocity: int = 80
    role: Optional[str] = None  # "root", "third", "fifth", etc.

    def __repr__(self):
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        octave = (self.pitch // 12) - 1
        note_name = note_names[self.pitch % 12]
        return f"Note({note_name}{octave}, pitch={self.pitch}, vel={self.velocity})"


@dataclass
class Exercise:
    """
    Base exercise structure.

    Represents a single ear training exercise with the notes to be played
    and the expected correct response.
    """
    id: str
    type: ExerciseType
    notes: List[Note]
    correct_response: List[Note]

    def __repr__(self):
        return f"Exercise(id={self.id}, type={self.type.value}, notes={len(self.notes)})"


@dataclass
class ExerciseResult:
    """
    Result of user's attempt at an exercise.

    Contains the user's response, whether it was correct,
    and feedback message.
    """
    exercise_id: str
    user_notes: List[Note]
    correct: bool
    feedback: str

    def __repr__(self):
        status = "✓" if self.correct else "✗"
        return f"ExerciseResult({status} {self.feedback})"
