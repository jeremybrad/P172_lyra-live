"""
Unit tests for Phase 4: Standards Library and Improvisation Analysis.

Tests:
- StandardsLibrary loading from YAML index
- Chord symbol parsing and interval extraction
- Note classification (chord tones, tensions, outside notes)
- Guide-tone detection and targeting
- Harmonic and rhythmic statistics calculation
- Complete improvisation analysis workflow
- TestImprovGenerator for synthetic solos
"""

import pytest
from pathlib import Path
from lyra_live.standards.core import StandardsLibrary, StandardTune, ChordChange
from lyra_live.improv.core import ImprovNote, ImprovChorus, HarmonicStats, RhythmicStats
from lyra_live.improv.analysis import (
    parse_chord_symbol,
    get_chord_intervals,
    classify_note,
    analyze_improvisation,
    find_guide_tones,
    calculate_metrics
)
from lyra_live.improv.test_utils import TestImprovGenerator


class TestStandardsLibrary:
    """Test StandardsLibrary loading and searching"""

    def test_load_from_yaml(self):
        """Test loading standards library from YAML index"""
        index_path = Path("data/standards/index.yaml")

        if not index_path.exists():
            pytest.skip(f"Index file not found at {index_path}")

        library = StandardsLibrary(index_path)

        # Should have loaded some tunes
        assert len(library.tunes) > 0

        # Get tunes as a list
        tune_list = library.list_tunes()
        assert len(tune_list) > 0

        # Check first tune has required fields
        tune = tune_list[0]
        assert tune.id is not None
        assert tune.title is not None
        assert tune.key is not None
        assert tune.tempo > 0
        assert tune.chorus_length_bars > 0

    def test_find_by_title(self):
        """Test searching for tunes by title"""
        index_path = Path("data/standards/index.yaml")

        if not index_path.exists():
            pytest.skip(f"Index file not found at {index_path}")

        library = StandardsLibrary(index_path)

        # Find a known tune (if it exists)
        tune = library.get_tune("Autumn Leaves")

        if tune:
            assert tune.title == "Autumn Leaves"
            assert tune.key is not None

        # Search should be case-insensitive
        tune2 = library.get_tune("autumn leaves")
        if tune:
            assert tune2 == tune

        # Non-existent tune should return None
        assert library.get_tune("Nonexistent Tune XYZ") is None

    def test_filter_by_difficulty(self):
        """Test filtering tunes by difficulty"""
        index_path = Path("data/standards/index.yaml")

        if not index_path.exists():
            pytest.skip(f"Index file not found at {index_path}")

        library = StandardsLibrary(index_path)

        # Filter by difficulty using list_tunes()
        beginner_tunes = library.list_tunes(difficulty='beginner')

        # All should have beginner difficulty
        for tune in beginner_tunes:
            assert tune.difficulty == 'beginner'


class TestChordParsing:
    """Test chord symbol parsing"""

    def test_parse_major_chords(self):
        """Test parsing major chord symbols"""
        root, quality = parse_chord_symbol("Cmaj7")
        assert root == 0  # C
        assert quality == "maj7"

        root, quality = parse_chord_symbol("Dbmaj7")
        assert root == 1  # Db
        assert quality == "maj7"

        root, quality = parse_chord_symbol("F#maj7")
        assert root == 6  # F#
        assert quality == "maj7"

    def test_parse_minor_chords(self):
        """Test parsing minor chord symbols"""
        root, quality = parse_chord_symbol("Dm7")
        assert root == 2  # D
        assert quality == "min7"

        root, quality = parse_chord_symbol("Am7")
        assert root == 9  # A
        assert quality == "min7"

    def test_parse_dominant_chords(self):
        """Test parsing dominant 7th chords"""
        root, quality = parse_chord_symbol("G7")
        assert root == 7  # G
        assert quality == "7"

        root, quality = parse_chord_symbol("C7")
        assert root == 0  # C
        assert quality == "7"

    def test_parse_half_diminished(self):
        """Test parsing half-diminished chords"""
        root, quality = parse_chord_symbol("Bm7b5")
        assert root == 11  # B
        assert quality == "m7b5"

    def test_get_chord_intervals(self):
        """Test getting intervals for different chord types"""
        # Major 7th: R, M3, P5, M7
        intervals = get_chord_intervals("Cmaj7")
        assert intervals == [0, 4, 7, 11]

        # Minor 7th: R, m3, P5, m7
        intervals = get_chord_intervals("Dm7")
        assert intervals == [0, 3, 7, 10]

        # Dominant 7th: R, M3, P5, m7
        intervals = get_chord_intervals("G7")
        assert intervals == [0, 4, 7, 10]


class TestNoteClassification:
    """Test note classification relative to chords"""

    def test_classify_chord_tones(self):
        """Test identifying chord tones"""
        # C in Cmaj7 = root
        classification, function = classify_note(60, "Cmaj7")  # C4
        assert classification == "chord_tone"
        assert function == "root"

        # E in Cmaj7 = 3rd
        classification, function = classify_note(64, "Cmaj7")  # E4
        assert classification == "chord_tone"
        assert function == "3rd"

        # G in Cmaj7 = 5th
        classification, function = classify_note(67, "Cmaj7")  # G4
        assert classification == "chord_tone"
        assert function == "5th"

        # B in Cmaj7 = 7th
        classification, function = classify_note(71, "Cmaj7")  # B4
        assert classification == "chord_tone"
        assert function == "7th"

    def test_classify_tensions(self):
        """Test identifying tension notes"""
        # D in Cmaj7 = 9th
        classification, function = classify_note(62, "Cmaj7")  # D4
        assert classification == "tension"
        assert function == "9th"

        # A in Cmaj7 = 13th
        classification, function = classify_note(69, "Cmaj7")  # A4
        assert classification == "tension"
        assert function == "13th"

    def test_classify_outside_notes(self):
        """Test identifying outside/chromatic notes"""
        # Eb in Cmaj7 = outside (minor 3rd in major chord)
        classification, function = classify_note(63, "Cmaj7")  # Eb4
        assert classification == "outside"
        assert function == "chromatic"

        # Ab in Cmaj7 = outside (b6)
        classification, function = classify_note(68, "Cmaj7")  # Ab4
        assert classification == "outside"
        assert function == "chromatic"


class TestGuideToneDetection:
    """Test guide-tone hit detection"""

    def test_guide_tone_hits_on_strong_beats(self):
        """Test that 3rds and 7ths on beats 1 and 3 are detected"""
        # Create a simple tune with one chord change
        tune = StandardTune(
            id="test_guide_tones",
            title="Test Guide Tones",
            key="C",
            tempo=120,
            form="test",
            chorus_length_bars=4,
            time_signature=(4, 4),
            chord_changes=[
                ChordChange(0, 1.0, "Cmaj7", 4.0),
                ChordChange(1, 1.0, "Dm7", 4.0),
            ]
        )

        chorus = ImprovChorus(chorus_number=1, tune=tune, start_time_ms=0)

        # Add a 3rd (E) on beat 1 of bar 0 (Cmaj7)
        note1 = ImprovNote(
            time_ms=0,
            pitch=64,  # E4
            velocity=80,
            duration_ms=400,
            bar=0,
            beat=1.0
        )
        note1.chord_at_time = "Cmaj7"
        note1.classification = "chord_tone"
        note1.note_function = "3rd"

        # Add a 7th (C) on beat 1 of bar 1 (Dm7)
        note2 = ImprovNote(
            time_ms=2000,
            pitch=60,  # C4 (7th of Dm7)
            velocity=80,
            duration_ms=400,
            bar=1,
            beat=1.0
        )
        note2.chord_at_time = "Dm7"
        note2.classification = "chord_tone"
        note2.note_function = "7th"

        chorus.notes = [note1, note2]

        # Should detect 2 guide-tone hits
        guide_tone_hits = find_guide_tones(chorus)
        assert guide_tone_hits == 2

    def test_no_guide_tones_on_weak_beats(self):
        """Test that 3rds and 7ths on weak beats are not counted"""
        tune = StandardTune(
            id="test_no_guide",
            title="Test No Guide",
            key="C",
            tempo=120,
            form="test",
            chorus_length_bars=2,
            time_signature=(4, 4),
            chord_changes=[ChordChange(0, 1.0, "Cmaj7", 8.0)]
        )

        chorus = ImprovChorus(chorus_number=1, tune=tune, start_time_ms=0)

        # Add a 3rd on beat 2 (weak beat)
        note = ImprovNote(
            time_ms=500,
            pitch=64,  # E4
            velocity=80,
            duration_ms=400,
            bar=0,
            beat=2.0
        )
        note.chord_at_time = "Cmaj7"
        note.classification = "chord_tone"
        note.note_function = "3rd"

        chorus.notes = [note]

        # Should not count as guide-tone hit (not on beat 1 or 3)
        guide_tone_hits = find_guide_tones(chorus)
        assert guide_tone_hits == 0


class TestImprovAnalysis:
    """Test complete improvisation analysis"""

    def test_analyze_chord_tone_solo(self):
        """Test analysis of a solo using mostly chord tones"""
        generator = TestImprovGenerator(seed=123)
        chorus = generator.generate_ii_v_i_solo(style="chord_tones", note_count=20)

        result = analyze_improvisation(chorus)

        # Should have high chord-tone ratio
        assert result.harmonic_stats.chord_tone_ratio > 60

        # Should have analyzed all notes
        assert result.total_notes == 20

        # Should have generated feedback
        assert len(result.feedback) > 0
        assert len(result.strengths) >= 0
        assert len(result.suggestions) >= 0

        # Score should be reasonable (0-100)
        assert 0 <= result.overall_score <= 100

    def test_analyze_tension_solo(self):
        """Test analysis of a solo using tensions"""
        generator = TestImprovGenerator(seed=456)
        chorus = generator.generate_ii_v_i_solo(style="tensions", note_count=20)

        result = analyze_improvisation(chorus)

        # Should have some tension notes
        assert result.harmonic_stats.tension_ratio > 0

        # Should have feedback
        assert len(result.feedback) > 0

    def test_analyze_outside_solo(self):
        """Test analysis of a solo with many outside notes"""
        generator = TestImprovGenerator(seed=789)
        chorus = generator.generate_ii_v_i_solo(style="outside", note_count=20)

        result = analyze_improvisation(chorus)

        # Should have some outside notes (random notes will have varying percentages)
        assert result.harmonic_stats.outside_ratio > 0

        # Overall score should be lower for outside-heavy solos
        assert result.overall_score < 80

    def test_guide_tone_focused_analysis(self):
        """Test analysis of a solo deliberately targeting guide tones"""
        generator = TestImprovGenerator(seed=999)
        chorus = generator.generate_guide_tone_focused_solo(note_count=24)

        result = analyze_improvisation(chorus)

        # Should detect guide-tone hits
        assert result.harmonic_stats.guide_tone_hits > 0

        # Should mention guide tones in feedback
        feedback_text = " ".join(result.strengths + result.suggestions).lower()
        assert "guide" in feedback_text or "3rd" in feedback_text or "7th" in feedback_text

    def test_calculate_metrics(self):
        """Test raw metrics calculation"""
        generator = TestImprovGenerator(seed=555)
        chorus = generator.generate_simple_blues_solo(style="chord_tones", note_count=30)

        metrics = calculate_metrics(chorus)

        # Should have all expected keys
        assert 'chord_tone_ratio' in metrics
        assert 'tension_ratio' in metrics
        assert 'outside_ratio' in metrics
        assert 'guide_tone_hits' in metrics
        assert 'downbeat_percentage' in metrics
        assert 'average_phrase_length' in metrics
        assert 'overall_score' in metrics

        # All percentages should be 0-100
        assert 0 <= metrics['chord_tone_ratio'] <= 100
        assert 0 <= metrics['tension_ratio'] <= 100
        assert 0 <= metrics['outside_ratio'] <= 100
        assert 0 <= metrics['overall_score'] <= 100


class TestRhythmicAnalysis:
    """Test rhythmic analysis features"""

    def test_downbeat_vs_offbeat_detection(self):
        """Test detection of downbeat vs offbeat notes"""
        tune = StandardTune(
            id="test_rhythm",
            title="Test Rhythm",
            key="C",
            tempo=120,
            form="test",
            chorus_length_bars=4,
            time_signature=(4, 4),
            chord_changes=[ChordChange(0, 1.0, "C7", 16.0)]
        )

        chorus = ImprovChorus(chorus_number=1, tune=tune, start_time_ms=0)

        # Add notes on downbeats (beats 1, 2, 3, 4)
        for i in range(4):
            note = ImprovNote(
                time_ms=i * 500,
                pitch=60,
                velocity=80,
                duration_ms=400,
                bar=0,
                beat=float(i + 1)
            )
            note.chord_at_time = "C7"
            note.classification = "chord_tone"
            note.note_function = "root"
            chorus.notes.append(note)

        result = analyze_improvisation(chorus)

        # All notes are on downbeats
        assert result.rhythmic_stats.downbeat_percentage == 100
        assert result.rhythmic_stats.offbeat_percentage == 0

    def test_phrase_length_detection(self):
        """Test phrase length calculation with rests"""
        tune = StandardTune(
            id="test_phrases",
            title="Test Phrases",
            key="C",
            tempo=120,
            form="test",
            chorus_length_bars=4,
            time_signature=(4, 4),
            chord_changes=[ChordChange(0, 1.0, "C7", 16.0)]
        )

        chorus = ImprovChorus(chorus_number=1, tune=tune, start_time_ms=0)

        # Phrase 1: 3 notes
        for i in range(3):
            chorus.notes.append(ImprovNote(
                time_ms=i * 200,
                pitch=60 + i,
                velocity=80,
                duration_ms=150,
                bar=0,
                beat=1.0 + i * 0.5
            ))

        # Gap of 600ms (rest)

        # Phrase 2: 4 notes
        for i in range(4):
            chorus.notes.append(ImprovNote(
                time_ms=1200 + i * 200,
                pitch=64 + i,
                velocity=80,
                duration_ms=150,
                bar=0,
                beat=2.0 + i * 0.5
            ))

        result = analyze_improvisation(chorus)

        # Should detect 2 phrases
        assert result.rhythmic_stats.total_rests == 1

        # Average phrase length should be (3 + 4) / 2 = 3.5
        assert result.rhythmic_stats.average_phrase_length == 3.5


class TestTestImprovGenerator:
    """Test the synthetic solo generator"""

    def test_generate_blues_solo(self):
        """Test generating a blues solo"""
        generator = TestImprovGenerator(seed=42)
        chorus = generator.generate_simple_blues_solo(style="chord_tones", note_count=30)

        # Should have generated notes
        assert len(chorus.notes) == 30

        # Tune should be F blues
        assert chorus.tune.key == "F"
        assert chorus.tune.chorus_length_bars == 12

        # All notes should have timing info
        for note in chorus.notes:
            assert note.time_ms >= 0
            assert note.pitch > 0
            assert 0 <= note.bar < 12

    def test_generate_ii_v_i_solo(self):
        """Test generating a ii-V-I solo"""
        generator = TestImprovGenerator(seed=43)
        chorus = generator.generate_ii_v_i_solo(style="tensions", note_count=20)

        # Should have generated notes
        assert len(chorus.notes) == 20

        # Tune should be in C
        assert chorus.tune.key == "C"
        assert chorus.tune.chorus_length_bars == 4

    def test_reproducibility(self):
        """Test that generator with same seed produces same results"""
        gen1 = TestImprovGenerator(seed=100)
        chorus1 = gen1.generate_simple_blues_solo(style="chord_tones", note_count=10)

        gen2 = TestImprovGenerator(seed=100)
        chorus2 = gen2.generate_simple_blues_solo(style="chord_tones", note_count=10)

        # Should have same number of notes
        assert len(chorus1.notes) == len(chorus2.notes)

        # Notes should have same pitches (same random seed)
        for n1, n2 in zip(chorus1.notes, chorus2.notes):
            assert n1.pitch == n2.pitch
