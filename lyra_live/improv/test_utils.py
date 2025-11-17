"""
Test utilities for improvisation analysis.

Generates synthetic solos for testing without requiring real-time playback.
"""

import random
from typing import List
from lyra_live.improv.core import ImprovNote, ImprovChorus
from lyra_live.standards.core import StandardTune, ChordChange
from lyra_live.improv.analysis import parse_chord_symbol, get_chord_intervals


class TestImprovGenerator:
    """
    Generates synthetic improvised solos for testing.

    Can create solos with different characteristics (e.g., mostly chord tones,
    mostly outside notes, etc.) for testing the analysis engine.
    """

    def __init__(self, seed: int = 42):
        """
        Initialize test generator.

        Args:
            seed: Random seed for reproducibility
        """
        random.seed(seed)

    def generate_simple_blues_solo(
        self,
        style: str = "chord_tones",
        note_count: int = 30
    ) -> ImprovChorus:
        """
        Generate a simple 12-bar blues solo.

        Args:
            style: "chord_tones", "tensions", or "outside"
            note_count: Approximate number of notes to generate

        Returns:
            ImprovChorus with synthetic solo
        """
        # Create a simple F blues progression
        tune = StandardTune(
            id="test_blues",
            title="Test Blues in F",
            key="F",
            tempo=120,
            form="blues",
            chorus_length_bars=12,
            time_signature=(4, 4),
            chord_changes=[
                # I - I - I - I
                ChordChange(0, 1.0, "F7", 4.0),
                ChordChange(1, 1.0, "F7", 4.0),
                ChordChange(2, 1.0, "F7", 4.0),
                ChordChange(3, 1.0, "F7", 4.0),
                # IV - IV - I - I
                ChordChange(4, 1.0, "Bb7", 4.0),
                ChordChange(5, 1.0, "Bb7", 4.0),
                ChordChange(6, 1.0, "F7", 4.0),
                ChordChange(7, 1.0, "F7", 4.0),
                # V - IV - I - V
                ChordChange(8, 1.0, "C7", 4.0),
                ChordChange(9, 1.0, "Bb7", 4.0),
                ChordChange(10, 1.0, "F7", 4.0),
                ChordChange(11, 1.0, "C7", 4.0),
            ]
        )

        chorus = ImprovChorus(
            chorus_number=1,
            tune=tune,
            start_time_ms=0
        )

        # Generate notes based on style
        current_time_ms = 0
        beat_duration_ms = (60000 // tune.tempo)  # Duration of one beat

        for _ in range(note_count):
            # Calculate position
            bar = (current_time_ms // (beat_duration_ms * 4)) % 12
            beat_in_bar = ((current_time_ms % (beat_duration_ms * 4)) / beat_duration_ms) + 1.0

            # Get current chord
            chord_symbol = tune.get_chord_at_time(bar, beat_in_bar)

            # Generate note based on style
            if style == "chord_tones":
                pitch = self._generate_chord_tone(chord_symbol)
            elif style == "tensions":
                pitch = self._generate_tension_note(chord_symbol)
            else:  # outside
                pitch = random.randint(60, 80)

            note = ImprovNote(
                time_ms=current_time_ms,
                pitch=pitch,
                velocity=random.randint(70, 100),
                duration_ms=random.randint(200, 600),
                bar=bar,
                beat=beat_in_bar
            )

            chorus.notes.append(note)

            # Advance time (with some variation)
            current_time_ms += random.randint(200, 800)

        chorus.end_time_ms = current_time_ms

        return chorus

    def generate_ii_v_i_solo(
        self,
        style: str = "chord_tones",
        note_count: int = 20
    ) -> ImprovChorus:
        """
        Generate a solo over a ii-V-I progression.

        Args:
            style: "chord_tones", "tensions", or "outside"
            note_count: Number of notes to generate

        Returns:
            ImprovChorus with synthetic solo
        """
        # Create a Dm7 - G7 - Cmaj7 progression (4 bars)
        tune = StandardTune(
            id="test_ii_v_i",
            title="Test ii-V-I in C",
            key="C",
            tempo=140,
            form="progression",
            chorus_length_bars=4,
            time_signature=(4, 4),
            chord_changes=[
                ChordChange(0, 1.0, "Dm7", 4.0),
                ChordChange(1, 1.0, "G7", 4.0),
                ChordChange(2, 1.0, "Cmaj7", 8.0),
            ]
        )

        chorus = ImprovChorus(
            chorus_number=1,
            tune=tune,
            start_time_ms=0
        )

        # Generate notes
        current_time_ms = 0
        beat_duration_ms = (60000 // tune.tempo)

        for _ in range(note_count):
            bar = (current_time_ms // (beat_duration_ms * 4)) % 4
            beat_in_bar = ((current_time_ms % (beat_duration_ms * 4)) / beat_duration_ms) + 1.0

            chord_symbol = tune.get_chord_at_time(bar, beat_in_bar)

            if style == "chord_tones":
                pitch = self._generate_chord_tone(chord_symbol)
            elif style == "tensions":
                pitch = self._generate_tension_note(chord_symbol)
            else:
                pitch = random.randint(60, 80)

            note = ImprovNote(
                time_ms=current_time_ms,
                pitch=pitch,
                velocity=random.randint(70, 100),
                duration_ms=random.randint(150, 400),
                bar=bar,
                beat=beat_in_bar
            )

            chorus.notes.append(note)
            current_time_ms += random.randint(150, 600)

        chorus.end_time_ms = current_time_ms

        return chorus

    def _generate_chord_tone(self, chord_symbol: str) -> int:
        """Generate a pitch that is a chord tone."""
        root_pc, _ = parse_chord_symbol(chord_symbol)
        intervals = get_chord_intervals(chord_symbol)

        # Pick a random chord tone
        interval = random.choice(intervals)

        # Random octave (C4-C6)
        octave = random.randint(4, 5)
        pitch = 60 + (octave - 4) * 12 + ((root_pc + interval) % 12)

        return pitch

    def _generate_tension_note(self, chord_symbol: str) -> int:
        """Generate a pitch that is a tension (9/11/13)."""
        root_pc, _ = parse_chord_symbol(chord_symbol)

        # Common tensions: 9th (2 semitones), 11th (5), 13th (9)
        tensions = [2, 5, 9]
        interval = random.choice(tensions)

        octave = random.randint(4, 5)
        pitch = 60 + (octave - 4) * 12 + ((root_pc + interval) % 12)

        return pitch

    def generate_guide_tone_focused_solo(self, note_count: int = 24) -> ImprovChorus:
        """
        Generate a solo that deliberately targets guide tones (3rds and 7ths)
        on strong beats at chord changes.

        This should score high on guide-tone targeting.
        """
        tune = StandardTune(
            id="test_rhythm_changes",
            title="Test Rhythm Changes (A section)",
            key="Bb",
            tempo=160,
            form="AABA",
            chorus_length_bars=8,
            time_signature=(4, 4),
            chord_changes=[
                ChordChange(0, 1.0, "Bbmaj7", 2.0),
                ChordChange(0, 3.0, "G7", 2.0),
                ChordChange(1, 1.0, "Cm7", 2.0),
                ChordChange(1, 3.0, "F7", 2.0),
                ChordChange(2, 1.0, "Dm7", 2.0),
                ChordChange(2, 3.0, "G7", 2.0),
                ChordChange(3, 1.0, "Cm7", 2.0),
                ChordChange(3, 3.0, "F7", 2.0),
                # ... more changes
            ]
        )

        chorus = ImprovChorus(
            chorus_number=1,
            tune=tune,
            start_time_ms=0
        )

        beat_duration_ms = (60000 // tune.tempo)

        # Deliberately place 3rds and 7ths on beats 1 and 3 at changes
        for change in tune.chord_changes[:note_count // 2]:
            # Generate a 3rd or 7th at this chord change
            root_pc, _ = parse_chord_symbol(change.chord_symbol)

            # Choose 3rd or 7th
            if random.random() < 0.5:
                interval = 4 if 'maj' in change.chord_symbol.lower() else 3  # Major or minor 3rd
            else:
                interval = 11 if 'maj7' in change.chord_symbol.lower() else 10  # Major or dom 7th

            pitch = 60 + ((root_pc + interval) % 12)

            time_ms = (change.bar * 4 + (change.beat - 1.0)) * beat_duration_ms

            note = ImprovNote(
                time_ms=int(time_ms),
                pitch=pitch,
                velocity=90,
                duration_ms=400,
                bar=change.bar,
                beat=change.beat
            )

            chorus.notes.append(note)

        # Fill in with some other chord tones
        current_time = 100
        while len(chorus.notes) < note_count:
            bar = (current_time // (beat_duration_ms * 4)) % 8
            beat_in_bar = ((current_time % (beat_duration_ms * 4)) / beat_duration_ms) + 1.0

            chord_symbol = tune.get_chord_at_time(bar, beat_in_bar)
            if chord_symbol:
                pitch = self._generate_chord_tone(chord_symbol)

                note = ImprovNote(
                    time_ms=current_time,
                    pitch=pitch,
                    velocity=80,
                    duration_ms=300,
                    bar=bar,
                    beat=beat_in_bar
                )

                chorus.notes.append(note)

            current_time += random.randint(200, 500)

        chorus.end_time_ms = max(n.time_ms for n in chorus.notes) + 500

        # Sort notes by time
        chorus.notes.sort(key=lambda n: n.time_ms)

        return chorus
