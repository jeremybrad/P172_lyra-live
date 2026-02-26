"""
Teacher journal generator.

Generates "teacher's log" style summaries of recent practice sessions
using rule-based templates (no LLM required - deterministic and testable).
"""

from datetime import datetime, timedelta
from typing import List
from lyra_live.logging.practice_log import PracticeSessionRecord
from lyra_live.logging import progress_stats


def generate_teacher_entry(sessions: List[PracticeSessionRecord], days: int = 7) -> str:
    """
    Generate a teacher's journal entry from recent practice sessions.

    Uses rule-based templates to create a narrative summary in "teacher voice"
    covering consistency, strengths, and areas for improvement.

    Args:
        sessions: List of all practice session records
        days: Number of days to analyze (default: 7)

    Returns:
        Markdown-formatted teacher journal entry
    """
    # Filter to last N days and exclude demos
    cutoff = datetime.now() - timedelta(days=days)
    recent = [
        s for s in sessions
        if datetime.fromisoformat(s.timestamp) >= cutoff and s.source != "demo"
    ]

    if not recent:
        return f"# Practice Journal ({days}-Day Summary)\n\nNo practice sessions logged in the past {days} days.\n"

    # Compute key stats
    total_minutes = progress_stats.compute_totals(recent)
    practice_days = progress_stats.compute_practice_days(recent)
    streak = progress_stats.compute_recent_streak(sessions, days=days)
    minutes_by_instrument = progress_stats.compute_minutes_by_instrument(recent)
    minutes_by_mode = progress_stats.compute_minutes_by_mode(recent)
    num_instruments = len(minutes_by_instrument)
    num_tunes = progress_stats.count_unique_tunes(recent)

    # Build the entry
    lines = []
    lines.append(f"# Practice Journal ({days}-Day Summary)")
    lines.append("")
    lines.append(f"*{datetime.now().strftime('%B %d, %Y')}*")
    lines.append("")

    # === Consistency ===
    lines.append("## Consistency")
    lines.append("")

    if practice_days == days:
        lines.append(f"**Excellent consistency!** Practiced all {days} days this week.")
    elif practice_days >= days * 0.7:  # 70%+
        lines.append(f"**Strong consistency.** Practiced {practice_days} out of {days} days.")
    elif practice_days >= days * 0.4:  # 40-70%
        lines.append(f"**Moderate consistency.** Practiced {practice_days} out of {days} days.")
    else:
        lines.append(f"**Room for improvement on consistency.** Only practiced {practice_days} out of {days} days.")

    if streak > 0:
        if streak == 1:
            lines.append(f"Current streak: {streak} day.")
        else:
            lines.append(f"Current streak: **{streak} consecutive days**.")

    lines.append("")
    lines.append(f"**Total practice time:** {total_minutes:.1f} minutes ({total_minutes/60:.1f} hours)")
    lines.append("")

    # === Distribution ===
    lines.append("## Practice Distribution")
    lines.append("")

    # By instrument
    lines.append("**By Instrument:**")
    for instrument, minutes in sorted(minutes_by_instrument.items(), key=lambda x: -x[1]):
        percentage = (minutes / total_minutes) * 100
        lines.append(f"- {instrument.capitalize()}: {minutes:.1f} min ({percentage:.0f}%)")
    lines.append("")

    # By mode
    lines.append("**By Mode:**")
    for mode, minutes in sorted(minutes_by_mode.items(), key=lambda x: -x[1]):
        percentage = (minutes / total_minutes) * 100
        mode_display = mode.replace('_', ' ').title()
        lines.append(f"- {mode_display}: {minutes:.1f} min ({percentage:.0f}%)")
    lines.append("")

    # === Strengths ===
    lines.append("## Strengths")
    lines.append("")

    strengths = _identify_strengths(recent, minutes_by_instrument, minutes_by_mode)
    for strength in strengths:
        lines.append(f"- {strength}")

    if not strengths:
        lines.append("- Keep building your practice foundation!")

    lines.append("")

    # === Areas for Growth ===
    lines.append("## Areas for Growth")
    lines.append("")

    suggestions = _generate_suggestions(recent, minutes_by_instrument, minutes_by_mode, num_instruments, num_tunes)
    for suggestion in suggestions:
        lines.append(f"- {suggestion}")

    if not suggestions:
        lines.append("- Excellent work! Keep up the balanced practice.")

    lines.append("")

    # === Closing ===
    lines.append("---")
    lines.append("")
    if total_minutes >= 60:  # 1+ hours
        lines.append("*Keep up the excellent work! Your dedication is showing.*")
    elif total_minutes >= 30:
        lines.append("*Good progress this week. Stay consistent!*")
    else:
        lines.append("*Remember: even short daily sessions build strong fundamentals.*")

    return '\n'.join(lines)


def _identify_strengths(
    sessions: List[PracticeSessionRecord],
    minutes_by_instrument: dict,
    minutes_by_mode: dict
) -> List[str]:
    """Identify strengths based on session data."""
    strengths = []

    # Check improvisation metrics
    improv_sessions = [s for s in sessions if 'improv' in s.mode]
    if improv_sessions:
        avg_chord_tone = progress_stats.compute_average_metrics(improv_sessions, 'chord_tone_ratio')
        avg_guide_tones = progress_stats.compute_average_metrics(improv_sessions, 'guide_tone_hits')

        if avg_chord_tone and avg_chord_tone >= 70:
            strengths.append(f"Strong harmonic awareness - averaging {avg_chord_tone:.0f}% chord tones in improvisation")

        if avg_guide_tones and avg_guide_tones >= 5:
            strengths.append(f"Excellent guide-tone targeting ({avg_guide_tones:.1f} hits per chorus on average)")

    # Check rhythm metrics
    rhythm_sessions = [s for s in sessions if s.mode == 'rhythm']
    if rhythm_sessions:
        avg_accuracy = progress_stats.compute_average_metrics(rhythm_sessions, 'rhythm_accuracy')
        if avg_accuracy and avg_accuracy >= 85:
            strengths.append(f"Solid rhythm accuracy ({avg_accuracy:.0f}%)")

    # Check ear training metrics
    interval_sessions = [s for s in sessions if s.mode == 'intervals']
    if interval_sessions:
        avg_interval_acc = progress_stats.compute_average_metrics(interval_sessions, 'interval_accuracy')
        if avg_interval_acc and avg_interval_acc >= 80:
            strengths.append(f"Strong interval recognition ({avg_interval_acc:.0f}% accuracy)")

    # Check multi-instrument practice
    if len(minutes_by_instrument) >= 3:
        strengths.append(f"Great variety - practicing on {len(minutes_by_instrument)} different instruments")

    # Check improv focus
    improv_minutes = sum(m for mode, m in minutes_by_mode.items() if 'improv' in mode)
    if improv_minutes > 0:
        percentage = (improv_minutes / sum(minutes_by_mode.values())) * 100
        if percentage >= 40:
            strengths.append("Focused improvisation practice - building creative skills")

    return strengths


def _generate_suggestions(
    sessions: List[PracticeSessionRecord],
    minutes_by_instrument: dict,
    minutes_by_mode: dict,
    num_instruments: int,
    num_tunes: int
) -> List[str]:
    """Generate suggestions for improvement."""
    suggestions = []

    # Check for lack of variety in instruments
    if num_instruments == 1 and len(sessions) > 3:
        suggestions.append("Consider exploring other instruments to develop well-rounded musicianship")

    # Check for lack of variety in tunes
    improv_sessions = [s for s in sessions if 'improv' in s.mode and s.tune_id]
    if len(improv_sessions) > 5 and num_tunes == 1:
        tune_id = improv_sessions[0].tune_id
        suggestions.append(f"Try branching out from '{tune_id}' to practice different harmonic contexts")

    # Check voice intonation if applicable
    voice_sessions = [s for s in sessions if s.instrument == 'voice']
    if voice_sessions:
        avg_cents = progress_stats.compute_average_metrics(voice_sessions, 'avg_cents_deviation')
        if avg_cents and avg_cents > 30:
            suggestions.append(f"Focus on intonation - current average deviation is {avg_cents:.0f} cents")

    # Check rhythm timing
    rhythm_sessions = [s for s in sessions if s.mode == 'rhythm']
    if rhythm_sessions:
        avg_accuracy = progress_stats.compute_average_metrics(rhythm_sessions, 'rhythm_accuracy')
        if avg_accuracy and avg_accuracy < 70:
            suggestions.append("Work on rhythm accuracy with slower tempos and metronome practice")

        avg_timing_error = progress_stats.compute_average_metrics(rhythm_sessions, 'avg_timing_error_ms')
        if avg_timing_error and avg_timing_error > 50:
            suggestions.append(f"Tighten timing precision (currently ±{avg_timing_error:.0f}ms on average)")

    # Check improvisation metrics
    improv_sessions = [s for s in sessions if 'improv' in s.mode]
    if improv_sessions:
        avg_chord_tone = progress_stats.compute_average_metrics(improv_sessions, 'chord_tone_ratio')
        avg_outside = progress_stats.compute_average_metrics(improv_sessions, 'outside_ratio')

        if avg_chord_tone and avg_chord_tone < 50:
            suggestions.append("Focus on targeting chord tones in your improvisation")

        if avg_outside and avg_outside > 40:
            suggestions.append("Practice outlining chord changes more clearly before adding outside notes")

    # Check ear training balance
    total_minutes = sum(minutes_by_mode.values())
    ear_training_modes = ['intervals', 'chords', 'melody']
    ear_training_minutes = sum(m for mode, m in minutes_by_mode.items() if mode in ear_training_modes)

    if ear_training_minutes / total_minutes < 0.2 and total_minutes > 30:
        suggestions.append("Consider adding more ear training drills to strengthen fundamentals")

    return suggestions
