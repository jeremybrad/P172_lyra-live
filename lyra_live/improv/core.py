"""
Core data structures for improvisation analysis.

Represents improvised notes, choruses, and analysis results.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from lyra_live.standards.core import StandardTune, ChordChange


@dataclass
class ImprovNote:
    """
    A single note in an improvised solo.

    Includes timing, pitch, and harmonic context.
    """
    time_ms: int  # Absolute time in milliseconds
    pitch: int  # MIDI note number
    velocity: int
    duration_ms: int

    # Calculated position in form
    bar: int = 0  # Bar number within chorus
    beat: float = 1.0  # Beat within bar

    # Harmonic analysis (filled in by analyzer)
    chord_at_time: Optional[str] = None  # The underlying chord
    note_function: Optional[str] = None  # "root", "3rd", "5th", "7th", "9th", etc.
    classification: Optional[str] = None  # "chord_tone", "tension", "outside"

    def __post_init__(self):
        """Calculate note name for display."""
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        self.note_name = note_names[self.pitch % 12]
        self.octave = (self.pitch // 12) - 1


@dataclass
class ImprovChorus:
    """
    A complete chorus of improvisation.

    Contains all notes played during one trip through the form.
    """
    chorus_number: int
    tune: StandardTune
    notes: List[ImprovNote] = field(default_factory=list)
    start_time_ms: int = 0
    end_time_ms: int = 0

    def get_notes_in_bar(self, bar: int) -> List[ImprovNote]:
        """Get all notes that occur in a specific bar."""
        return [n for n in self.notes if n.bar == bar]

    def get_notes_on_chord(self, chord_symbol: str) -> List[ImprovNote]:
        """Get all notes played over a specific chord."""
        return [n for n in self.notes if n.chord_at_time == chord_symbol]

    @property
    def total_duration_ms(self) -> int:
        """Total duration of the chorus."""
        return self.end_time_ms - self.start_time_ms

    @property
    def note_count(self) -> int:
        """Total number of notes in the chorus."""
        return len(self.notes)


@dataclass
class RhythmicStats:
    """Rhythmic characteristics of a solo."""
    downbeat_percentage: float  # % of notes on downbeats
    offbeat_percentage: float  # % of notes on offbeats
    average_phrase_length: float  # Average notes before rest
    longest_phrase: int  # Most consecutive notes without rest
    total_rests: int  # Number of rests/gaps


@dataclass
class HarmonicStats:
    """Harmonic characteristics of a solo."""
    chord_tone_ratio: float  # % notes that are 1/3/5/7
    tension_ratio: float  # % notes that are 9/11/13
    outside_ratio: float  # % notes outside the chord
    guide_tone_hits: int  # # of 3rds/7ths on strong beats at changes
    root_usage: float  # % notes that are chord roots


@dataclass
class ImprovAnalysisResult:
    """
    Complete analysis of an improvised solo.

    Includes harmonic, rhythmic, and qualitative feedback.
    """
    tune_title: str
    chorus_number: int
    total_notes: int

    # Harmonic analysis
    harmonic_stats: HarmonicStats

    # Rhythmic analysis
    rhythmic_stats: RhythmicStats

    # Note classification breakdown
    chord_tone_notes: List[ImprovNote] = field(default_factory=list)
    tension_notes: List[ImprovNote] = field(default_factory=list)
    outside_notes: List[ImprovNote] = field(default_factory=list)

    # Qualitative assessment
    feedback: str = ""
    strengths: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)

    # Overall score (0-100)
    overall_score: float = 0.0

    def print_summary(self):
        """Print a human-readable summary of the analysis."""
        print(f"\n{'='*60}")
        print(f"IMPROVISATION ANALYSIS: {self.tune_title}")
        print(f"Chorus #{self.chorus_number}")
        print(f"{'='*60}\n")

        print(f"📊 HARMONIC ANALYSIS:")
        print(f"   Chord tones (1/3/5/7): {self.harmonic_stats.chord_tone_ratio:.1f}%")
        print(f"   Tensions (9/11/13):    {self.harmonic_stats.tension_ratio:.1f}%")
        print(f"   Outside notes:         {self.harmonic_stats.outside_ratio:.1f}%")
        print(f"   Guide-tone hits:       {self.harmonic_stats.guide_tone_hits}")
        print()

        print(f"🎵 RHYTHMIC ANALYSIS:")
        print(f"   Downbeat notes:        {self.rhythmic_stats.downbeat_percentage:.1f}%")
        print(f"   Offbeat notes:         {self.rhythmic_stats.offbeat_percentage:.1f}%")
        print(f"   Avg phrase length:     {self.rhythmic_stats.average_phrase_length:.1f} notes")
        print(f"   Longest phrase:        {self.rhythmic_stats.longest_phrase} notes")
        print()

        print(f"💯 OVERALL SCORE: {self.overall_score:.0f}/100\n")

        if self.strengths:
            print(f"✅ STRENGTHS:")
            for strength in self.strengths:
                print(f"   • {strength}")
            print()

        if self.suggestions:
            print(f"💡 SUGGESTIONS:")
            for suggestion in self.suggestions:
                print(f"   • {suggestion}")
            print()

        if self.feedback:
            print(f"📝 FEEDBACK:")
            print(f"   {self.feedback}\n")

        print(f"{'='*60}\n")
