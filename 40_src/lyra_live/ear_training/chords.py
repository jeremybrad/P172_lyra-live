"""
Chord quality recognition exercise generator.

Generates chord ear training exercises with various chord qualities:
- Triads: major, minor, diminished, augmented
- 7th chords: dominant 7, major 7, minor 7, half-diminished 7

Phase 2 feature.
"""

import random
from lyra_live.ear_training.base import Exercise, Note, ExerciseType
from typing import List, Dict


# Chord formulas: semitone intervals from root
CHORD_FORMULAS: Dict[str, List[int]] = {
    # Triads
    "major": [0, 4, 7],
    "minor": [0, 3, 7],
    "diminished": [0, 3, 6],
    "augmented": [0, 4, 8],

    # 7th chords
    "dominant_7": [0, 4, 7, 10],
    "major_7": [0, 4, 7, 11],
    "minor_7": [0, 3, 7, 10],
    "half_diminished_7": [0, 3, 6, 10],
}

# Human-readable names
CHORD_NAMES: Dict[str, str] = {
    "major": "major",
    "minor": "minor",
    "diminished": "diminished",
    "augmented": "augmented",
    "dominant_7": "dominant 7th",
    "major_7": "major 7th",
    "minor_7": "minor 7th",
    "half_diminished_7": "half-diminished 7th",
}

# Role names for chord tones
CHORD_ROLES = ["root", "third", "fifth", "seventh"]


class ChordQualityExercise:
    """Generate chord quality recognition exercises"""

    @staticmethod
    def generate(chord_type: str, root_note: int = 60) -> Exercise:
        """
        Create chord quality exercise with specific chord type.

        Args:
            chord_type: Name of chord (e.g., "major", "minor_7")
            root_note: Root MIDI note number (default: 60 = middle C)

        Returns:
            Exercise with notes forming the specified chord
        """
        if chord_type not in CHORD_FORMULAS:
            raise ValueError(f"Unknown chord type: {chord_type}")

        formula = CHORD_FORMULAS[chord_type]
        notes = []

        for i, interval in enumerate(formula):
            role = CHORD_ROLES[i] if i < len(CHORD_ROLES) else f"tone_{i}"
            notes.append(Note(
                pitch=root_note + interval,
                duration_ms=2000,  # Longer duration for chords
                velocity=80,
                role=role
            ))

        return Exercise(
            id=f"chord_{chord_type}_{root_note}",
            type=ExerciseType.CHORD,
            notes=notes,
            correct_response=notes
        )

    @staticmethod
    def generate_random(
        chord_types: List[str] = None,
        root_range: tuple[int, int] = (48, 72)
    ) -> Exercise:
        """
        Generate random chord quality exercise.

        Args:
            chord_types: List of chord types to choose from (default: all triads)
            root_range: Tuple of (min, max) MIDI note numbers for root note
                       Default: (48, 72) = C3 to C5

        Returns:
            Exercise with random chord
        """
        if chord_types is None:
            # Default to triads only
            chord_types = ["major", "minor", "diminished", "augmented"]

        chord_type = random.choice(chord_types)
        root_note = random.randint(root_range[0], root_range[1])
        return ChordQualityExercise.generate(chord_type, root_note)

    @staticmethod
    def get_chord_name(chord_type: str) -> str:
        """
        Get human-readable name for chord type.

        Args:
            chord_type: Chord type key

        Returns:
            Human-readable chord name
        """
        return CHORD_NAMES.get(chord_type, chord_type)

    @staticmethod
    def identify_chord_quality(notes: List[Note]) -> str:
        """
        Identify chord quality from a list of notes.

        Args:
            notes: List of notes forming a chord

        Returns:
            Chord type string, or "unknown" if not recognized
        """
        if len(notes) < 3:
            return "unknown"

        # Calculate intervals from root
        root = notes[0].pitch
        intervals = sorted([note.pitch - root for note in notes])

        # Match against known formulas
        for chord_type, formula in CHORD_FORMULAS.items():
            if intervals == formula:
                return chord_type

        return "unknown"
