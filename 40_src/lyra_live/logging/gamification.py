"""
Gamification system for practice tracking.

Provides XP calculation, rank determination, and badge system
to encourage consistent practice and skill development.
"""

from dataclasses import dataclass
from typing import List
from lyra_live.logging.practice_log import PracticeSessionRecord
from lyra_live.logging import progress_stats


# Base XP rate: 10 XP per minute of practice
BASE_XP_PER_MINUTE = 10.0


@dataclass
class RankInfo:
    """Information about a player rank."""
    name: str
    min_xp: int
    description: str


# Rank thresholds (cumulative XP required)
RANKS = [
    RankInfo("Peasant", 0, "Just beginning the musical journey"),
    RankInfo("Apprentice", 1000, "Learning the fundamentals"),
    RankInfo("Squire", 3000, "Developing core skills"),
    RankInfo("Journeyman", 6000, "Gaining musical competence"),
    RankInfo("Adept", 10000, "Demonstrating mastery"),
    RankInfo("Expert", 15000, "Highly skilled musician"),
    RankInfo("Sage", 22000, "Deep musical wisdom"),
    RankInfo("Master", 30000, "Peak performance ability"),
    RankInfo("Wizard", 40000, "Transcendent musicianship"),
]


def compute_xp_for_session(record: PracticeSessionRecord) -> int:
    """
    Calculate XP earned for a single practice session.

    Base XP: 10 XP per minute
    Bonuses:
    - High chord tone ratio (>=70%): +20% XP
    - High rhythm accuracy (>=85%): +20% XP
    - Multi-instrument day bonus: +10% (applied separately)
    - Streak maintenance: handled at aggregate level

    Args:
        record: Practice session record

    Returns:
        XP earned (integer)
    """
    # Skip demo sessions
    if record.source == "demo":
        return 0

    # Base XP from time
    base_xp = record.duration_seconds / 60.0 * BASE_XP_PER_MINUTE

    # Bonus multiplier
    multiplier = 1.0

    # Improvisation bonus
    if record.chord_tone_ratio is not None and record.chord_tone_ratio >= 70:
        multiplier += 0.2  # +20% for strong harmonic awareness

    # Rhythm bonus
    if record.rhythm_accuracy is not None and record.rhythm_accuracy >= 85:
        multiplier += 0.2  # +20% for good rhythm

    # Ear training bonus
    if record.interval_accuracy is not None and record.interval_accuracy >= 80:
        multiplier += 0.15  # +15% for strong ear

    if record.chord_accuracy is not None and record.chord_accuracy >= 80:
        multiplier += 0.15  # +15% for chord recognition

    # Apply multiplier and round
    total_xp = int(base_xp * multiplier)

    return total_xp


def compute_total_xp(sessions: List[PracticeSessionRecord]) -> int:
    """
    Compute total XP across all sessions.

    Also applies streak bonuses:
    - 7+ day streak: +10% to recent week's XP
    - 30+ day streak: +20% to recent month's XP

    Args:
        sessions: List of practice session records

    Returns:
        Total XP earned
    """
    # Base XP from all sessions
    base_xp = sum(compute_xp_for_session(s) for s in sessions)

    # Streak bonuses
    streak = progress_stats.compute_recent_streak(sessions, days=30)

    bonus_xp = 0

    if streak >= 30:
        # 30-day streak: +20% bonus on last month
        recent_30 = progress_stats.filter_sessions(sessions, since_days=30)
        month_base = sum(compute_xp_for_session(s) for s in recent_30)
        bonus_xp += int(month_base * 0.2)
    elif streak >= 7:
        # 7-day streak: +10% bonus on last week
        recent_7 = progress_stats.filter_sessions(sessions, since_days=7)
        week_base = sum(compute_xp_for_session(s) for s in recent_7)
        bonus_xp += int(week_base * 0.1)

    return base_xp + bonus_xp


def determine_rank(total_xp: int) -> RankInfo:
    """
    Determine player rank based on total XP.

    Args:
        total_xp: Total XP accumulated

    Returns:
        RankInfo for the current rank
    """
    # Find the highest rank we've achieved
    current_rank = RANKS[0]

    for rank in RANKS:
        if total_xp >= rank.min_xp:
            current_rank = rank
        else:
            break

    return current_rank


def get_next_rank(total_xp: int) -> tuple[RankInfo, int]:
    """
    Get information about the next rank to achieve.

    Args:
        total_xp: Total XP accumulated

    Returns:
        Tuple of (next_rank_info, xp_needed)
    """
    current = determine_rank(total_xp)

    # Find next rank
    current_index = RANKS.index(current)

    if current_index < len(RANKS) - 1:
        next_rank = RANKS[current_index + 1]
        xp_needed = next_rank.min_xp - total_xp
        return next_rank, xp_needed
    else:
        # Already at max rank
        return current, 0


def compute_badges(sessions: List[PracticeSessionRecord]) -> List[str]:
    """
    Compute which badges have been earned based on practice history.

    Badges:
    - "First_Steps": Complete 1 practice session
    - "Getting_Started": Complete 10 practice sessions
    - "Dedicated": Complete 50 practice sessions
    - "Committed": Complete 100 practice sessions
    - "First_100_Minutes": Practice for 100+ minutes total
    - "Century_Club": Practice for 500+ minutes total
    - "Thousand_Hour_Journey": Practice for 1000+ minutes total
    - "Week_Warrior": 7-day practice streak
    - "Month_Master": 30-day practice streak
    - "Multi_Instrumentalist": Practice on 3+ different instruments
    - "Guide_Tone_Guru": Average 5+ guide tone hits in improv sessions
    - "Rhythm_Monk": 85%+ average rhythm accuracy over 10+ sessions
    - "Harmonic_Awareness": 70%+ average chord tone ratio over 10+ improv sessions
    - "Ear_Training_Expert": 80%+ average on all ear training modes
    - "Standards_Explorer": Practice 10+ different tunes

    Args:
        sessions: List of practice session records

    Returns:
        List of badge names earned
    """
    badges = []

    # Filter out demos
    real_sessions = [s for s in sessions if s.source != "demo"]

    # Session count badges
    num_sessions = len(real_sessions)
    if num_sessions >= 1:
        badges.append("First_Steps")
    if num_sessions >= 10:
        badges.append("Getting_Started")
    if num_sessions >= 50:
        badges.append("Dedicated")
    if num_sessions >= 100:
        badges.append("Committed")

    # Time badges
    total_minutes = progress_stats.compute_totals(real_sessions)
    if total_minutes >= 100:
        badges.append("First_100_Minutes")
    if total_minutes >= 500:
        badges.append("Century_Club")
    if total_minutes >= 1000:
        badges.append("Thousand_Hour_Journey")

    # Streak badges
    streak = progress_stats.compute_recent_streak(real_sessions, days=30)
    if streak >= 7:
        badges.append("Week_Warrior")
    if streak >= 30:
        badges.append("Month_Master")

    # Multi-instrument badge
    num_instruments = progress_stats.count_unique_instruments(real_sessions)
    if num_instruments >= 3:
        badges.append("Multi_Instrumentalist")

    # Improvisation badges
    improv_sessions = [s for s in real_sessions if 'improv' in s.mode]
    if len(improv_sessions) >= 10:
        avg_guide_tones = progress_stats.compute_average_metrics(improv_sessions, 'guide_tone_hits')
        if avg_guide_tones and avg_guide_tones >= 5:
            badges.append("Guide_Tone_Guru")

        avg_chord_tone = progress_stats.compute_average_metrics(improv_sessions, 'chord_tone_ratio')
        if avg_chord_tone and avg_chord_tone >= 70:
            badges.append("Harmonic_Awareness")

    # Rhythm badges
    rhythm_sessions = [s for s in real_sessions if s.mode == 'rhythm']
    if len(rhythm_sessions) >= 10:
        avg_accuracy = progress_stats.compute_average_metrics(rhythm_sessions, 'rhythm_accuracy')
        if avg_accuracy and avg_accuracy >= 85:
            badges.append("Rhythm_Monk")

    # Ear training badges
    interval_sessions = [s for s in real_sessions if s.mode == 'intervals']
    chord_sessions = [s for s in real_sessions if s.mode == 'chords']
    melody_sessions = [s for s in real_sessions if s.mode == 'melody']

    if interval_sessions and chord_sessions and melody_sessions:
        avg_interval = progress_stats.compute_average_metrics(interval_sessions, 'interval_accuracy')
        avg_chord = progress_stats.compute_average_metrics(chord_sessions, 'chord_accuracy')
        avg_melody = progress_stats.compute_average_metrics(melody_sessions, 'melody_accuracy')

        if (avg_interval and avg_interval >= 80 and
            avg_chord and avg_chord >= 80 and
            avg_melody and avg_melody >= 80):
            badges.append("Ear_Training_Expert")

    # Standards exploration badge
    num_tunes = progress_stats.count_unique_tunes(real_sessions)
    if num_tunes >= 10:
        badges.append("Standards_Explorer")

    return badges


def format_badge_display(badge_name: str) -> str:
    """
    Format a badge name for display.

    Args:
        badge_name: Internal badge name (e.g., "First_100_Minutes")

    Returns:
        Human-readable badge name (e.g., "First 100 Minutes")
    """
    return badge_name.replace('_', ' ')
