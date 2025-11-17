"""
Rhythm exercise generation and validation.

Generates rhythm patterns for drum practice and validates timing accuracy.
Supports single-limb exercises, full-kit patterns, and adaptive difficulty.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
from lyra_live.ear_training.base import Exercise, ExerciseType
import random


@dataclass
class Beat:
    """
    A single drum hit at a specific time.

    Attributes:
        time_ms: Timestamp in milliseconds from start of pattern
        drum_part: Name of drum part to hit (e.g., "snare", "kick", "hihat_closed")
        velocity: Hit velocity (0-127), represents dynamics
        subdivision: Which subdivision of the beat this represents (e.g., 8th note, 16th note)
    """
    time_ms: int
    drum_part: str
    velocity: int = 80
    subdivision: Optional[str] = None  # "quarter", "eighth", "sixteenth"


@dataclass
class RhythmGrid:
    """
    A rhythm pattern on a time grid.

    Represents a rhythmic pattern with tempo, time signature, and expected hits.
    """
    tempo_bpm: int
    time_signature: tuple[int, int] = (4, 4)  # (beats_per_bar, note_value)
    num_bars: int = 1
    beats: List[Beat] = field(default_factory=list)

    def get_duration_ms(self) -> int:
        """Calculate total duration of the pattern in milliseconds."""
        beats_per_bar, note_value = self.time_signature
        total_beats = beats_per_bar * self.num_bars
        ms_per_beat = (60000 / self.tempo_bpm) * (4 / note_value)
        return int(total_beats * ms_per_beat)

    def get_beat_duration_ms(self) -> float:
        """Get duration of one beat in milliseconds."""
        _, note_value = self.time_signature
        return (60000 / self.tempo_bpm) * (4 / note_value)


@dataclass
class RhythmExercise:
    """
    A rhythm exercise for drum practice.

    Contains a rhythm grid with the pattern to play and metadata.
    """
    id: str
    description: str
    grid: RhythmGrid
    focus_part: str = "snare"  # Which drum part this exercise focuses on
    difficulty: str = "beginner"  # beginner, intermediate, advanced

    def to_exercise(self) -> Exercise:
        """Convert to generic Exercise object."""
        # Convert beats to Notes for compatibility
        from lyra_live.ear_training.base import Note
        notes = [
            Note(pitch=0, duration_ms=beat.time_ms, velocity=beat.velocity)
            for beat in self.grid.beats
        ]

        return Exercise(
            id=self.id,
            type=ExerciseType.MELODY,  # Reuse MELODY type for now
            notes=notes,
            correct_response=notes
        )


@dataclass
class RhythmResult:
    """
    Result of a rhythm exercise attempt.

    Contains detailed timing analysis and scoring.
    """
    exercise_id: str
    total_expected_hits: int
    total_actual_hits: int
    correct_hits: int  # Hits within timing window
    missed_hits: int  # Expected hits not played
    extra_hits: int  # Unexpected hits played
    average_timing_error_ms: float  # Average early/late in milliseconds
    accuracy_percentage: float
    feedback: str
    per_hit_errors: List[float] = field(default_factory=list)  # Individual timing errors


class RhythmExerciseGenerator:
    """Generate rhythm exercises of various types and difficulties."""

    @staticmethod
    def generate_straight_pattern(
        drum_part: str,
        subdivision: str,  # "quarter", "eighth", "sixteenth"
        tempo_bpm: int = 80,
        num_bars: int = 1,
        time_signature: tuple[int, int] = (4, 4)
    ) -> RhythmExercise:
        """
        Generate a straight rhythm pattern (all hits on the grid).

        Args:
            drum_part: Which drum to hit
            subdivision: "quarter", "eighth", or "sixteenth"
            tempo_bpm: Tempo in beats per minute
            num_bars: Number of bars to generate
            time_signature: Time signature (beats_per_bar, note_value)

        Returns:
            RhythmExercise with straight pattern
        """
        grid = RhythmGrid(
            tempo_bpm=tempo_bpm,
            time_signature=time_signature,
            num_bars=num_bars
        )

        beat_duration_ms = grid.get_beat_duration_ms()
        beats_per_bar, _ = time_signature

        # Determine hits per beat based on subdivision
        if subdivision == "quarter":
            hits_per_beat = 1
        elif subdivision == "eighth":
            hits_per_beat = 2
        elif subdivision == "sixteenth":
            hits_per_beat = 4
        else:
            hits_per_beat = 1

        # Generate hits
        beats = []
        current_time_ms = 0
        hit_interval_ms = beat_duration_ms / hits_per_beat

        total_hits = beats_per_bar * num_bars * hits_per_beat
        for i in range(total_hits):
            beats.append(Beat(
                time_ms=int(current_time_ms),
                drum_part=drum_part,
                velocity=80,
                subdivision=subdivision
            ))
            current_time_ms += hit_interval_ms

        grid.beats = beats

        return RhythmExercise(
            id=f"straight_{subdivision}_{drum_part}_{tempo_bpm}bpm",
            description=f"Straight {subdivision} notes on {drum_part} at {tempo_bpm} BPM",
            grid=grid,
            focus_part=drum_part,
            difficulty="beginner" if subdivision == "quarter" else "intermediate"
        )

    @staticmethod
    def generate_backbeat_pattern(
        tempo_bpm: int = 80,
        num_bars: int = 1
    ) -> RhythmExercise:
        """
        Generate a basic rock backbeat pattern (kick + snare).

        Pattern: Kick on 1 and 3, Snare on 2 and 4

        Args:
            tempo_bpm: Tempo in beats per minute
            num_bars: Number of bars

        Returns:
            RhythmExercise with backbeat pattern
        """
        grid = RhythmGrid(
            tempo_bpm=tempo_bpm,
            time_signature=(4, 4),
            num_bars=num_bars
        )

        beat_duration_ms = grid.get_beat_duration_ms()
        beats = []

        for bar in range(num_bars):
            bar_offset_ms = bar * 4 * beat_duration_ms

            # Kick on beats 1 and 3
            beats.append(Beat(
                time_ms=int(bar_offset_ms + 0 * beat_duration_ms),
                drum_part="kick",
                velocity=90
            ))
            beats.append(Beat(
                time_ms=int(bar_offset_ms + 2 * beat_duration_ms),
                drum_part="kick",
                velocity=90
            ))

            # Snare on beats 2 and 4
            beats.append(Beat(
                time_ms=int(bar_offset_ms + 1 * beat_duration_ms),
                drum_part="snare",
                velocity=85
            ))
            beats.append(Beat(
                time_ms=int(bar_offset_ms + 3 * beat_duration_ms),
                drum_part="snare",
                velocity=85
            ))

        grid.beats = beats

        return RhythmExercise(
            id=f"backbeat_{tempo_bpm}bpm",
            description=f"Basic backbeat (kick 1-3, snare 2-4) at {tempo_bpm} BPM",
            grid=grid,
            focus_part="full_kit",
            difficulty="intermediate"
        )

    @staticmethod
    def generate_syncopated_pattern(
        drum_part: str = "snare",
        complexity: int = 1,  # 1-3, higher = more syncopation
        tempo_bpm: int = 80,
        num_bars: int = 1
    ) -> RhythmExercise:
        """
        Generate a syncopated rhythm pattern with off-beat hits.

        Args:
            drum_part: Which drum to hit
            complexity: 1-3, how syncopated the pattern is
            tempo_bpm: Tempo in BPM
            num_bars: Number of bars

        Returns:
            RhythmExercise with syncopated pattern
        """
        grid = RhythmGrid(
            tempo_bpm=tempo_bpm,
            time_signature=(4, 4),
            num_bars=num_bars
        )

        beat_duration_ms = grid.get_beat_duration_ms()
        eighth_note_ms = beat_duration_ms / 2

        beats = []

        # Simple syncopation patterns
        if complexity == 1:
            # Hit on "and" of beat 2
            pattern_times = [0, 2.5]  # Beat 1 and "and" of beat 3
        elif complexity == 2:
            # More off-beat hits
            pattern_times = [0, 1.5, 2, 3.5]
        else:
            # Complex syncopation
            pattern_times = [0.5, 1, 2.5, 3, 3.5]

        for bar in range(num_bars):
            bar_offset_ms = bar * 4 * beat_duration_ms

            for time_in_beats in pattern_times:
                beats.append(Beat(
                    time_ms=int(bar_offset_ms + time_in_beats * beat_duration_ms),
                    drum_part=drum_part,
                    velocity=80
                ))

        grid.beats = beats

        return RhythmExercise(
            id=f"syncopated_{drum_part}_{complexity}_{tempo_bpm}bpm",
            description=f"Syncopated pattern (complexity {complexity}) on {drum_part} at {tempo_bpm} BPM",
            grid=grid,
            focus_part=drum_part,
            difficulty="intermediate" if complexity == 1 else "advanced"
        )


class RhythmValidator:
    """Validate rhythm performance with timing analysis."""

    @staticmethod
    def validate_rhythm(
        expected_grid: RhythmGrid,
        actual_hits: List[Beat],
        tolerance_ms: int = 50,
        drum_part_filter: Optional[str] = None
    ) -> RhythmResult:
        """
        Validate rhythm performance with timing accuracy.

        Args:
            expected_grid: Expected rhythm pattern
            actual_hits: Actual drum hits played
            tolerance_ms: Timing window in milliseconds (±tolerance)
            drum_part_filter: If set, only validate hits on this drum part

        Returns:
            RhythmResult with detailed timing analysis
        """
        expected_beats = expected_grid.beats

        # Filter by drum part if specified
        if drum_part_filter:
            expected_beats = [b for b in expected_beats if b.drum_part == drum_part_filter]
            actual_hits = [b for b in actual_hits if b.drum_part == drum_part_filter]

        total_expected = len(expected_beats)
        total_actual = len(actual_hits)

        # Match actual hits to expected beats
        matched_hits = []
        timing_errors = []
        expected_times = [b.time_ms for b in expected_beats]
        actual_times = [b.time_ms for b in actual_hits]

        used_actual_indices = set()

        for exp_time in expected_times:
            best_match_idx = None
            best_match_error = float('inf')

            for act_idx, act_time in enumerate(actual_times):
                if act_idx in used_actual_indices:
                    continue

                error = abs(act_time - exp_time)
                if error < best_match_error and error <= tolerance_ms:
                    best_match_error = error
                    best_match_idx = act_idx

            if best_match_idx is not None:
                matched_hits.append(best_match_idx)
                used_actual_indices.add(best_match_idx)

                # Record timing error (positive = late, negative = early)
                error_signed = actual_times[best_match_idx] - exp_time
                timing_errors.append(error_signed)

        correct_hits = len(matched_hits)
        missed_hits = total_expected - correct_hits
        extra_hits = total_actual - correct_hits

        avg_timing_error = sum(timing_errors) / len(timing_errors) if timing_errors else 0
        accuracy = (correct_hits / total_expected * 100) if total_expected > 0 else 0

        # Generate feedback
        feedback_parts = []
        feedback_parts.append(f"Accuracy: {accuracy:.1f}%")

        if avg_timing_error > 5:
            feedback_parts.append(f"Tend to rush (+{avg_timing_error:.1f}ms average)")
        elif avg_timing_error < -5:
            feedback_parts.append(f"Tend to drag ({avg_timing_error:.1f}ms average)")
        else:
            feedback_parts.append("Excellent timing!")

        if missed_hits > 0:
            feedback_parts.append(f"{missed_hits} missed hits")
        if extra_hits > 0:
            feedback_parts.append(f"{extra_hits} extra hits")

        feedback = ". ".join(feedback_parts)

        return RhythmResult(
            exercise_id="",
            total_expected_hits=total_expected,
            total_actual_hits=total_actual,
            correct_hits=correct_hits,
            missed_hits=missed_hits,
            extra_hits=extra_hits,
            average_timing_error_ms=avg_timing_error,
            accuracy_percentage=accuracy,
            feedback=feedback,
            per_hit_errors=timing_errors
        )
