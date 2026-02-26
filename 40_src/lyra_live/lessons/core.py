"""
Core lesson data structures.

Defines Lesson, LessonPhrase, and LessonPack for organizing
musical content into structured practice sessions.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
from lyra_live.ear_training.base import Note, Exercise, ExerciseType
from lyra_live.ear_training.melodies import MelodyImitationExercise


@dataclass
class LessonPhrase:
    """
    A short musical phrase within a lesson.

    Represents a slice of a larger piece that can be practiced
    as a standalone exercise.
    """
    id: str
    notes: List[Note]
    description: Optional[str] = None
    start_measure: Optional[int] = None
    end_measure: Optional[int] = None

    def to_exercise(self, exercise_type: ExerciseType = ExerciseType.MELODY) -> Exercise:
        """
        Convert this phrase to an Exercise.

        Args:
            exercise_type: Type of exercise to create (default: MELODY)

        Returns:
            Exercise object ready for practice
        """
        if exercise_type == ExerciseType.MELODY:
            return MelodyImitationExercise.generate(
                notes=self.notes,
                exercise_id=f"lesson_phrase_{self.id}"
            )
        else:
            # For other types, create a basic exercise
            return Exercise(
                id=f"lesson_phrase_{self.id}",
                type=exercise_type,
                notes=self.notes,
                correct_response=self.notes
            )


@dataclass
class Lesson:
    """
    A complete musical lesson.

    Represents a song, etude, or exercise piece that can be broken
    into phrases for practice.
    """
    id: str
    title: str
    artist: Optional[str] = None
    difficulty: str = "intermediate"  # beginner, intermediate, advanced
    description: Optional[str] = None
    key: Optional[str] = None
    tempo_bpm: Optional[int] = None
    phrases: List[LessonPhrase] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)

    def get_phrase(self, phrase_id: str) -> Optional[LessonPhrase]:
        """
        Get a specific phrase by ID.

        Args:
            phrase_id: ID of the phrase to retrieve

        Returns:
            LessonPhrase if found, None otherwise
        """
        for phrase in self.phrases:
            if phrase.id == phrase_id:
                return phrase
        return None

    def get_all_phrases(self) -> List[LessonPhrase]:
        """Get all phrases in this lesson."""
        return self.phrases

    def add_phrase(self, phrase: LessonPhrase):
        """Add a phrase to this lesson."""
        self.phrases.append(phrase)


@dataclass
class LessonPack:
    """
    A collection of related lessons.

    Examples: "Beatles Melodies Vol. 1", "Jazz Standards Essentials"
    """
    id: str
    title: str
    description: Optional[str] = None
    lessons: List[Lesson] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    def get_lesson(self, lesson_id: str) -> Optional[Lesson]:
        """
        Get a specific lesson by ID.

        Args:
            lesson_id: ID of the lesson to retrieve

        Returns:
            Lesson if found, None otherwise
        """
        for lesson in self.lessons:
            if lesson.id == lesson_id:
                return lesson
        return None

    def get_all_lessons(self) -> List[Lesson]:
        """Get all lessons in this pack."""
        return self.lessons

    def add_lesson(self, lesson: Lesson):
        """Add a lesson to this pack."""
        self.lessons.append(lesson)

    def get_lessons_by_difficulty(self, difficulty: str) -> List[Lesson]:
        """
        Get all lessons of a specific difficulty level.

        Args:
            difficulty: Difficulty level (beginner, intermediate, advanced)

        Returns:
            List of matching lessons
        """
        return [lesson for lesson in self.lessons
                if lesson.difficulty == difficulty]
