"""
Improvisation analysis engine.

Analyzes jazz solos for harmonic awareness, guide-tone usage,
and rhythmic characteristics.
"""

from typing import List, Tuple, Dict
from lyra_live.improv.core import (
    ImprovNote,
    ImprovChorus,
    ImprovAnalysisResult,
    HarmonicStats,
    RhythmicStats
)
from lyra_live.standards.core import StandardTune


# Chord tone intervals from root (in semitones)
CHORD_TONES = {
    # Triads
    'maj': [0, 4, 7],
    'min': [0, 3, 7],
    'dim': [0, 3, 6],
    'aug': [0, 4, 8],

    # Seventh chords
    'maj7': [0, 4, 7, 11],
    'min7': [0, 3, 7, 10],
    '7': [0, 4, 7, 10],  # Dominant 7th
    'm7b5': [0, 3, 6, 10],  # Half-diminished
    'dim7': [0, 3, 6, 9],

    # Extensions (common)
    'maj9': [0, 4, 7, 11, 14],
    'min9': [0, 3, 7, 10, 14],
    '9': [0, 4, 7, 10, 14],
    '13': [0, 4, 7, 10, 14, 21],
}

# Tension intervals (relative to root)
TENSIONS = [2, 5, 9, 14, 17, 21]  # 9th, 11th, 13th and their octaves


def parse_chord_symbol(chord_symbol: str) -> Tuple[int, str]:
    """
    Parse a chord symbol into root note and quality.

    Args:
        chord_symbol: E.g. "Cmaj7", "Dm7", "G7", "F#m7b5"

    Returns:
        Tuple of (root_pitch_class, quality)
        where root_pitch_class is 0-11 (C=0) and quality is the chord type
    """
    # Note name mapping
    note_map = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}

    # Get root note
    root_letter = chord_symbol[0].upper()
    root = note_map.get(root_letter, 0)

    # Check for sharp/flat
    if len(chord_symbol) > 1:
        if chord_symbol[1] == '#':
            root = (root + 1) % 12
            quality_start = 2
        elif chord_symbol[1] == 'b':
            root = (root - 1) % 12
            quality_start = 2
        else:
            quality_start = 1
    else:
        quality_start = 1

    # Extract quality
    quality = chord_symbol[quality_start:].lower()

    # Normalize quality
    if not quality or quality == '':
        quality = 'maj'
    elif 'maj7' in quality or 'M7' in quality or 'Δ' in quality:
        quality = 'maj7'
    elif 'm7b5' in quality or 'ø' in quality:
        quality = 'm7b5'
    elif 'dim7' in quality or '°7' in quality:
        quality = 'dim7'
    elif 'm7' in quality or 'min7' in quality or '-7' in quality:
        quality = 'min7'
    elif quality == 'm' or quality == 'min' or quality == '-':
        quality = 'min'
    elif '7' in quality:
        quality = '7'

    return root, quality


def get_chord_intervals(chord_symbol: str) -> List[int]:
    """
    Get the intervals (in semitones) for a chord symbol.

    Args:
        chord_symbol: E.g. "Cmaj7", "Dm7"

    Returns:
        List of intervals from root (e.g. [0, 4, 7, 11] for maj7)
    """
    _, quality = parse_chord_symbol(chord_symbol)

    # Try to find exact match first
    if quality in CHORD_TONES:
        return CHORD_TONES[quality]

    # Fallbacks for common variations
    if 'maj' in quality:
        return CHORD_TONES['maj7']
    elif 'm' in quality or 'min' in quality:
        return CHORD_TONES['min7']
    elif '7' in quality:
        return CHORD_TONES['7']

    # Default to major triad
    return CHORD_TONES['maj']


def classify_note(note_pitch: int, chord_symbol: str) -> Tuple[str, str]:
    """
    Classify a note relative to the underlying chord.

    Args:
        note_pitch: MIDI note number
        chord_symbol: Current chord (e.g. "Cmaj7")

    Returns:
        Tuple of (classification, function)
        classification: "chord_tone", "tension", or "outside"
        function: "root", "3rd", "5th", "7th", "9th", etc.
    """
    root_pc, quality = parse_chord_symbol(chord_symbol)
    note_pc = note_pitch % 12

    # Calculate interval from root
    interval = (note_pc - root_pc) % 12

    # Get chord intervals
    chord_intervals = get_chord_intervals(chord_symbol)

    # Check if it's a chord tone
    if interval in chord_intervals:
        # Determine function
        if interval == 0:
            function = "root"
        elif interval in [3, 4]:
            function = "3rd"
        elif interval in [6, 7, 8]:
            function = "5th"
        elif interval in [10, 11]:
            function = "7th"
        else:
            function = "chord_tone"

        return "chord_tone", function

    # Check if it's a common tension
    if interval in TENSIONS or interval in [1, 2, 5, 9]:  # 9th, 11th variants
        if interval in [1, 2]:
            function = "9th"
        elif interval == 5:
            function = "11th"
        elif interval == 9:
            function = "13th"
        else:
            function = "tension"

        return "tension", function

    # Otherwise it's outside
    return "outside", "chromatic"


def analyze_improvisation(chorus: ImprovChorus) -> ImprovAnalysisResult:
    """
    Analyze a complete improvised chorus.

    Args:
        chorus: ImprovChorus with notes to analyze

    Returns:
        ImprovAnalysisResult with complete analysis
    """
    tune = chorus.tune

    # First pass: Annotate each note with harmonic context
    for note in chorus.notes:
        # Find the chord at this note's time
        chord_symbol = tune.get_chord_at_time(note.bar, note.beat)
        if chord_symbol:
            note.chord_at_time = chord_symbol

            # Classify the note
            classification, function = classify_note(note.pitch, chord_symbol)
            note.classification = classification
            note.note_function = function

    # Calculate harmonic stats
    harmonic_stats = _calculate_harmonic_stats(chorus)

    # Calculate rhythmic stats
    rhythmic_stats = _calculate_rhythmic_stats(chorus)

    # Find guide-tone hits
    guide_tone_hits = find_guide_tones(chorus)

    # Classify notes by type
    chord_tone_notes = [n for n in chorus.notes if n.classification == "chord_tone"]
    tension_notes = [n for n in chorus.notes if n.classification == "tension"]
    outside_notes = [n for n in chorus.notes if n.classification == "outside"]

    # Generate feedback
    feedback, strengths, suggestions, score = _generate_feedback(
        harmonic_stats,
        rhythmic_stats,
        guide_tone_hits,
        len(chorus.notes)
    )

    return ImprovAnalysisResult(
        tune_title=tune.title,
        chorus_number=chorus.chorus_number,
        total_notes=len(chorus.notes),
        harmonic_stats=harmonic_stats,
        rhythmic_stats=rhythmic_stats,
        chord_tone_notes=chord_tone_notes,
        tension_notes=tension_notes,
        outside_notes=outside_notes,
        feedback=feedback,
        strengths=strengths,
        suggestions=suggestions,
        overall_score=score
    )


def _calculate_harmonic_stats(chorus: ImprovChorus) -> HarmonicStats:
    """Calculate harmonic statistics for a chorus."""
    total_notes = len(chorus.notes)
    if total_notes == 0:
        return HarmonicStats(0, 0, 0, 0, 0)

    chord_tone_count = sum(1 for n in chorus.notes if n.classification == "chord_tone")
    tension_count = sum(1 for n in chorus.notes if n.classification == "tension")
    outside_count = sum(1 for n in chorus.notes if n.classification == "outside")
    root_count = sum(1 for n in chorus.notes if n.note_function == "root")

    # Find guide-tone hits
    guide_tone_hits = find_guide_tones(chorus)

    return HarmonicStats(
        chord_tone_ratio=(chord_tone_count / total_notes) * 100,
        tension_ratio=(tension_count / total_notes) * 100,
        outside_ratio=(outside_count / total_notes) * 100,
        guide_tone_hits=guide_tone_hits,
        root_usage=(root_count / total_notes) * 100
    )


def _calculate_rhythmic_stats(chorus: ImprovChorus) -> RhythmicStats:
    """Calculate rhythmic statistics for a chorus."""
    if not chorus.notes:
        return RhythmicStats(0, 0, 0, 0, 0)

    total_notes = len(chorus.notes)

    # Count downbeat vs offbeat notes
    downbeat_count = sum(
        1 for n in chorus.notes
        if abs(n.beat - round(n.beat)) < 0.1  # Within 0.1 beat of integer
    )
    offbeat_count = total_notes - downbeat_count

    # Analyze phrase lengths (gaps > 500ms are considered rests)
    phrases = []
    current_phrase = []
    last_note_end = 0

    for note in sorted(chorus.notes, key=lambda n: n.time_ms):
        # Check if there's a gap since last note
        if last_note_end > 0 and (note.time_ms - last_note_end) > 500:
            if current_phrase:
                phrases.append(len(current_phrase))
                current_phrase = []

        current_phrase.append(note)
        last_note_end = note.time_ms + note.duration_ms

    # Add last phrase
    if current_phrase:
        phrases.append(len(current_phrase))

    avg_phrase = sum(phrases) / len(phrases) if phrases else 0
    longest_phrase = max(phrases) if phrases else 0
    total_rests = len(phrases) - 1 if phrases else 0

    return RhythmicStats(
        downbeat_percentage=(downbeat_count / total_notes) * 100,
        offbeat_percentage=(offbeat_count / total_notes) * 100,
        average_phrase_length=avg_phrase,
        longest_phrase=longest_phrase,
        total_rests=total_rests
    )


def find_guide_tones(chorus: ImprovChorus) -> int:
    """
    Count guide-tone hits (3rds and 7ths on strong beats at chord changes).

    Guide tones are considered especially important when they land on
    beats 1 or 3 right at a chord change.

    Args:
        chorus: ImprovChorus to analyze

    Returns:
        Number of guide-tone hits
    """
    tune = chorus.tune
    guide_tone_count = 0

    # Get all chord changes
    for change in tune.chord_changes:
        # Look for notes on this chord change
        # (within ±0.5 beat of the change, on beats 1 or 3)
        for note in chorus.notes:
            if note.bar != change.bar:
                continue

            # Check if note is on beat 1 or 3 (±0.25 tolerance)
            is_strong_beat = (
                abs(note.beat - 1.0) < 0.25 or
                abs(note.beat - 3.0) < 0.25
            )

            if not is_strong_beat:
                continue

            # Check if note is a guide tone (3rd or 7th)
            if note.note_function in ["3rd", "7th"]:
                guide_tone_count += 1

    return guide_tone_count


def _generate_feedback(
    harmonic: HarmonicStats,
    rhythmic: RhythmicStats,
    guide_tones: int,
    total_notes: int
) -> Tuple[str, List[str], List[str], float]:
    """
    Generate qualitative feedback based on analysis.

    Returns:
        Tuple of (feedback_text, strengths, suggestions, overall_score)
    """
    strengths = []
    suggestions = []
    score = 50.0  # Start at 50/100

    # Harmonic assessment
    if harmonic.chord_tone_ratio > 70:
        strengths.append("Strong harmonic awareness - excellent use of chord tones")
        score += 15
    elif harmonic.chord_tone_ratio < 40:
        suggestions.append("Try targeting more chord tones (1/3/5/7) to strengthen harmonic foundation")
        score -= 10

    if harmonic.tension_ratio > 20:
        strengths.append("Good use of tensions (9/11/13) for color")
        score += 10
    elif harmonic.tension_ratio < 5:
        suggestions.append("Experiment with more tensions (9ths, 11ths, 13ths) to add sophistication")

    if harmonic.outside_ratio > 30:
        suggestions.append("High percentage of outside notes - consider resolving chromaticism more")
        score -= 5
    elif 5 < harmonic.outside_ratio < 20:
        strengths.append("Tasteful use of chromatic approaches")
        score += 5

    # Guide tones
    if guide_tones > 4:
        strengths.append(f"Excellent guide-tone targeting ({guide_tones} hits)")
        score += 15
    elif guide_tones == 0:
        suggestions.append("Focus on hitting 3rds and 7ths on strong beats at chord changes")
        score -= 5

    # Rhythmic assessment
    if 40 < rhythmic.downbeat_percentage < 70:
        strengths.append("Good balance between downbeat and offbeat phrases")
        score += 10
    elif rhythmic.downbeat_percentage > 80:
        suggestions.append("Try more syncopation and offbeat accents for rhythmic interest")
        score -= 5

    if rhythmic.average_phrase_length > 3:
        strengths.append("Confident phrase lengths")
        score += 5
    elif rhythmic.average_phrase_length < 2:
        suggestions.append("Try building longer phrases - connect your musical ideas")

    if rhythmic.total_rests > 2:
        strengths.append("Good use of space and phrasing")
        score += 5
    elif rhythmic.total_rests == 0 and total_notes > 20:
        suggestions.append("Leave more space - rests are musical too!")

    # Generate summary feedback
    if score >= 80:
        feedback = "Excellent improvisation! Your harmonic choices and phrasing show strong musicality."
    elif score >= 65:
        feedback = "Solid solo with good moments. Keep developing your harmonic vocabulary."
    elif score >= 50:
        feedback = "Good foundation. Focus on chord-tone targeting and rhythmic variety."
    else:
        feedback = "Keep practicing! Work on hitting chord tones and outlining the changes."

    # Clamp score to 0-100
    score = max(0, min(100, score))

    return feedback, strengths, suggestions, score


def calculate_metrics(chorus: ImprovChorus) -> Dict[str, float]:
    """
    Calculate raw metrics dictionary for a chorus.

    Useful for tracking progress over time.

    Args:
        chorus: ImprovChorus to analyze

    Returns:
        Dict of metric name to value
    """
    result = analyze_improvisation(chorus)

    return {
        'chord_tone_ratio': result.harmonic_stats.chord_tone_ratio,
        'tension_ratio': result.harmonic_stats.tension_ratio,
        'outside_ratio': result.harmonic_stats.outside_ratio,
        'guide_tone_hits': result.harmonic_stats.guide_tone_hits,
        'downbeat_percentage': result.rhythmic_stats.downbeat_percentage,
        'average_phrase_length': result.rhythmic_stats.average_phrase_length,
        'overall_score': result.overall_score
    }
