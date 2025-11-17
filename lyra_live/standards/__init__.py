"""
Standards library package.

Manages jazz standards, backing tracks, and tune metadata for improvisation practice.
"""

from lyra_live.standards.core import (
    StandardTune,
    StandardsLibrary
)

from lyra_live.standards.midi_utils import (
    parse_standard_midi,
    extract_chord_grid
)

__all__ = [
    'StandardTune',
    'StandardsLibrary',
    'parse_standard_midi',
    'extract_chord_grid'
]
