"""
Voice package - singing drills and pitch detection.

Provides infrastructure for vocal exercises including pitch matching,
scale singing, and sight-singing practice.
"""

from lyra_live.voice.pitch import (
    PitchDetector,
    AubioPitchDetector,
    PitchReading,
    frequency_to_midi,
    midi_to_frequency
)

from lyra_live.voice.exercises import (
    PitchMatchExercise,
    ScaleExercise,
    SightSingingExercise,
    VoiceResult
)

from lyra_live.voice.test_utils import TestVoiceInput

__all__ = [
    'PitchDetector',
    'AubioPitchDetector',
    'PitchReading',
    'frequency_to_midi',
    'midi_to_frequency',
    'PitchMatchExercise',
    'ScaleExercise',
    'SightSingingExercise',
    'VoiceResult',
    'TestVoiceInput'
]
