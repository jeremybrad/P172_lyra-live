"""
Improvisation analysis package.

Analyzes jazz solos for harmonic awareness, guide-tone usage,
rhythmic variety, and overall musicality.
"""

from lyra_live.improv.core import (
    ImprovNote,
    ImprovChorus,
    ImprovAnalysisResult
)

from lyra_live.improv.analysis import (
    analyze_improvisation,
    classify_note,
    find_guide_tones,
    calculate_metrics
)

from lyra_live.improv.test_utils import TestImprovGenerator

__all__ = [
    'ImprovNote',
    'ImprovChorus',
    'ImprovAnalysisResult',
    'analyze_improvisation',
    'classify_note',
    'find_guide_tones',
    'calculate_metrics',
    'TestImprovGenerator'
]
