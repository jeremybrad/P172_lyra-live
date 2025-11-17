"""
Core data structures for jazz standards library.

Manages tune metadata, backing tracks, and chord changes.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from pathlib import Path
import yaml
import json


@dataclass
class ChordChange:
    """A single chord change at a specific time."""
    bar: int  # Bar number (0-indexed)
    beat: float  # Beat within bar (1.0, 1.5, 2.0, etc.)
    chord_symbol: str  # e.g. "Cmaj7", "Dm7", "G7"
    duration_beats: float  # How long this chord lasts


@dataclass
class StandardTune:
    """
    Metadata for a jazz standard.

    Includes tune information, file paths, and chord changes.
    """
    id: str  # Unique identifier (e.g. "things_aint_what_they_used_to_be")
    title: str  # Display title
    composer: Optional[str] = None
    key: str = "C"  # Primary key
    alternate_keys: List[str] = field(default_factory=list)
    time_signature: tuple = (4, 4)
    tempo: int = 120  # BPM
    form: str = "AABA"  # Song form (AABA, ABAC, blues, etc.)
    chorus_length_bars: int = 32

    # File paths (relative to data/standards/)
    midi_path: Optional[str] = None
    audio_path: Optional[str] = None

    # Chord changes (optional, can be parsed from MIDI or provided in metadata)
    chord_changes: List[ChordChange] = field(default_factory=list)

    # Additional metadata
    style: str = "swing"  # swing, latin, ballad, etc.
    difficulty: str = "intermediate"
    notes: str = ""  # Practice notes or tips

    def get_full_midi_path(self, base_dir: Path) -> Optional[Path]:
        """Get absolute path to MIDI file."""
        if not self.midi_path:
            return None
        return base_dir / "data" / "standards" / self.midi_path

    def get_full_audio_path(self, base_dir: Path) -> Optional[Path]:
        """Get absolute path to audio file."""
        if not self.audio_path:
            return None
        return base_dir / "data" / "standards" / self.audio_path

    def get_chord_at_time(self, bar: int, beat: float) -> Optional[str]:
        """
        Get the chord symbol at a specific bar/beat position.

        Args:
            bar: Bar number (0-indexed)
            beat: Beat within bar (1.0-based)

        Returns:
            Chord symbol or None if not found
        """
        if not self.chord_changes:
            return None

        # Find the active chord at this time
        current_chord = None
        for change in self.chord_changes:
            if change.bar > bar:
                break
            if change.bar == bar and change.beat > beat:
                break
            current_chord = change.chord_symbol

        return current_chord

    def get_chords_in_range(self, start_bar: int, end_bar: int) -> List[ChordChange]:
        """
        Get all chord changes within a bar range.

        Args:
            start_bar: Starting bar (inclusive)
            end_bar: Ending bar (exclusive)

        Returns:
            List of chord changes in range
        """
        return [
            change for change in self.chord_changes
            if start_bar <= change.bar < end_bar
        ]


class StandardsLibrary:
    """
    Library of jazz standards with metadata and file references.

    Loads tune definitions from YAML/JSON index files and provides
    lookup and search functionality.
    """

    def __init__(self, index_path: Optional[Path] = None, base_dir: Optional[Path] = None):
        """
        Initialize standards library.

        Args:
            index_path: Path to index file (YAML or JSON)
            base_dir: Base directory for resolving relative paths
        """
        self.base_dir = base_dir or Path.cwd()
        self.tunes: Dict[str, StandardTune] = {}

        if index_path:
            self.load_index(index_path)

    def load_index(self, index_path: Path):
        """
        Load tunes from an index file.

        Supports both YAML and JSON formats.

        Args:
            index_path: Path to index file
        """
        index_path = Path(index_path)

        if not index_path.exists():
            raise FileNotFoundError(f"Index file not found: {index_path}")

        # Determine format from extension
        suffix = index_path.suffix.lower()

        with open(index_path, 'r') as f:
            if suffix in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            elif suffix == '.json':
                data = json.load(f)
            else:
                raise ValueError(f"Unsupported index format: {suffix}")

        # Parse tune entries
        if not isinstance(data, dict) or 'tunes' not in data:
            raise ValueError("Index file must contain a 'tunes' key")

        for tune_data in data['tunes']:
            tune = self._parse_tune_data(tune_data)
            self.tunes[tune.id] = tune

    def _parse_tune_data(self, data: dict) -> StandardTune:
        """Parse a single tune entry from the index."""
        # Handle chord changes if present
        chord_changes = []
        if 'chord_changes' in data:
            for change_data in data['chord_changes']:
                chord_changes.append(ChordChange(
                    bar=change_data['bar'],
                    beat=change_data.get('beat', 1.0),
                    chord_symbol=change_data['chord'],
                    duration_beats=change_data.get('duration', 4.0)
                ))

        return StandardTune(
            id=data['id'],
            title=data['title'],
            composer=data.get('composer'),
            key=data.get('key', 'C'),
            alternate_keys=data.get('alternate_keys', []),
            time_signature=tuple(data.get('time_signature', [4, 4])),
            tempo=data.get('tempo', 120),
            form=data.get('form', 'AABA'),
            chorus_length_bars=data.get('chorus_length_bars', 32),
            midi_path=data.get('midi_path'),
            audio_path=data.get('audio_path'),
            chord_changes=chord_changes,
            style=data.get('style', 'swing'),
            difficulty=data.get('difficulty', 'intermediate'),
            notes=data.get('notes', '')
        )

    def list_tunes(self, style: Optional[str] = None, difficulty: Optional[str] = None) -> List[StandardTune]:
        """
        List all tunes, optionally filtered by style or difficulty.

        Args:
            style: Filter by style (swing, latin, ballad, etc.)
            difficulty: Filter by difficulty (beginner, intermediate, advanced)

        Returns:
            List of matching tunes
        """
        tunes = list(self.tunes.values())

        if style:
            tunes = [t for t in tunes if t.style.lower() == style.lower()]

        if difficulty:
            tunes = [t for t in tunes if t.difficulty.lower() == difficulty.lower()]

        return sorted(tunes, key=lambda t: t.title)

    def get_tune(self, id_or_title: str) -> Optional[StandardTune]:
        """
        Get a tune by ID or title.

        Args:
            id_or_title: Tune ID or title (case-insensitive partial match)

        Returns:
            StandardTune if found, None otherwise
        """
        # Try exact ID match first
        if id_or_title in self.tunes:
            return self.tunes[id_or_title]

        # Try case-insensitive title match
        search_term = id_or_title.lower()
        for tune in self.tunes.values():
            if search_term in tune.title.lower():
                return tune

        return None

    def add_tune(self, tune: StandardTune):
        """
        Add a tune to the library.

        Args:
            tune: StandardTune to add
        """
        self.tunes[tune.id] = tune

    def save_index(self, output_path: Path, format: str = 'yaml'):
        """
        Save the current library to an index file.

        Args:
            output_path: Path to save index
            format: Output format ('yaml' or 'json')
        """
        data = {
            'tunes': [
                {
                    'id': tune.id,
                    'title': tune.title,
                    'composer': tune.composer,
                    'key': tune.key,
                    'alternate_keys': tune.alternate_keys,
                    'time_signature': list(tune.time_signature),
                    'tempo': tune.tempo,
                    'form': tune.form,
                    'chorus_length_bars': tune.chorus_length_bars,
                    'midi_path': tune.midi_path,
                    'audio_path': tune.audio_path,
                    'style': tune.style,
                    'difficulty': tune.difficulty,
                    'notes': tune.notes,
                    'chord_changes': [
                        {
                            'bar': ch.bar,
                            'beat': ch.beat,
                            'chord': ch.chord_symbol,
                            'duration': ch.duration_beats
                        }
                        for ch in tune.chord_changes
                    ] if tune.chord_changes else []
                }
                for tune in self.tunes.values()
            ]
        }

        with open(output_path, 'w') as f:
            if format == 'yaml':
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            else:
                json.dump(data, f, indent=2)
