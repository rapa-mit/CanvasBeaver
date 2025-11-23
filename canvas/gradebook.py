#!/usr/bin/env python3
"""
gradebook.py
--------------------------------
Fetch and analyze Canvas course gradebook data.

Provides a Gradebook class that loads assignments and submissions,
builds per-student grade summaries, and computes aggregate statistics.

Canvas API permissions required:
- View assignments
- View student enrollments
- View submissions/grades

Offline usage supported via load_from_data().
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from statistics import mean, median, pstdev
from datetime import datetime
import pickle
from pathlib import Path


@dataclass
class Assignment:
    id: int
    name: str
    points_possible: float | None = None
    due_at: Optional[str] = None  # ISO string
    assignment_group_id: Optional[int] = None  # Canvas assignment group


@dataclass
class StudentScore:
    assignment_id: int
    score: Optional[float] = None
    points_possible: Optional[float] = None
    submitted_at: Optional[str] = None
    workflow_state: Optional[str] = None  # 'graded', 'submitted', etc.
    late: Optional[bool] = None
    missing: Optional[bool] = None
    excused: Optional[bool] = None


@dataclass
class StudentSummary:
    id: Any
    name: Optional[str] = None
    login: Optional[str] = None
    email: Optional[str] = None
    scores: Dict[int, StudentScore] = field(default_factory=dict)  # by assignment_id
    total_score: float = 0.0
    total_points: float = 0.0

    @property
    def percent(self) -> Optional[float]:
        if self.total_points and self.total_points > 0:
            return 100.0 * self.total_score / self.total_points
        return None


class Gradebook:
    """Gradebook model with data and analysis helpers."""

    def __init__(self) -> None:
        self.course_id: Optional[int] = None
        self.assignments: Dict[int, Assignment] = {}
        self.students: Dict[Any, StudentSummary] = {}

    # -------------------- Loaders --------------------
    def load_from_canvas(self, canvas_connection: Any, course_id: int, include_inactive: bool = False) -> None:
        """Load assignments, students (enrollments), and submissions from Canvas."""
        self.course_id = course_id
        canvas = canvas_connection.get_canvas()
        course = canvas.get_course(course_id)

        # Fetch assignments
        try:
            for a in course.get_assignments():
                pts = getattr(a, 'points_possible', None)
                due = getattr(a, 'due_at', None)
                group_id = getattr(a, 'assignment_group_id', None)
                self.assignments[a.id] = Assignment(
                    id=a.id,
                    name=a.name,
                    points_possible=float(pts) if pts is not None else None,
                    due_at=due,
                    assignment_group_id=group_id,
                )
        except Exception as e:
            raise RuntimeError(f"Unable to retrieve assignments: {e}")

        # Fetch student enrollments
        try:
            state = None if include_inactive else ["active"]
            enrollments = list(course.get_enrollments(
                type=["StudentEnrollment"], 
                state=state,
                include=["email"]  # Request email addresses
            ))
            for enr in enrollments:
                user = getattr(enr, 'user', None)
                uid = getattr(enr, 'user_id', None) or (user.get('id') if isinstance(user, dict) else getattr(user, 'id', None))
                if uid is None:
                    continue
                name = (user.get('name') if isinstance(user, dict) else getattr(user, 'name', None)) if user else None
                login = (user.get('login_id') if isinstance(user, dict) else getattr(user, 'login_id', None)) if user else None
                email = (user.get('email') if isinstance(user, dict) else getattr(user, 'email', None)) if user else None
                self.students[uid] = StudentSummary(id=uid, name=name, login=login, email=email)
        except Exception as e:
            raise RuntimeError(f"Unable to retrieve student enrollments: {e}")

        # Fetch submissions for each assignment
        for aid, assignment in list(self.assignments.items()):
            try:
                submissions = assignment  # type: ignore[assignment]
                # Using course.get_assignment(aid) first to ensure proper object
                aobj = course.get_assignment(aid)
                for sub in aobj.get_submissions(include=["user"]):
                    user = getattr(sub, 'user', None)
                    uid = getattr(sub, 'user_id', None) or (user.get('id') if isinstance(user, dict) else getattr(user, 'id', None))
                    if uid is None:
                        continue
                    if uid not in self.students:
                        # If submission for a user not in enrollments (e.g., inactive), optionally include
                        if include_inactive:
                            self.students[uid] = StudentSummary(id=uid, name=(user.get('name') if isinstance(user, dict) else getattr(user, 'name', None)))
                        else:
                            continue
                    score = getattr(sub, 'score', None)
                    submitted_at = getattr(sub, 'submitted_at', None)
                    workflow_state = getattr(sub, 'workflow_state', None)
                    late = getattr(sub, 'late', None)
                    missing = getattr(sub, 'missing', None)
                    excused = getattr(sub, 'excused', None)

                    ss = StudentScore(
                        assignment_id=aid,
                        score=float(score) if score is not None else None,
                        points_possible=assignment.points_possible,
                        submitted_at=submitted_at,
                        workflow_state=workflow_state,
                        late=late,
                        missing=missing,
                        excused=excused,
                    )
                    self.students[uid].scores[aid] = ss
            except Exception:
                # Continue on per-assignment errors to be resilient
                continue

        # Compute totals
        self._compute_totals()

    def load_from_data(self, assignments: List[Dict[str, Any]], submissions: List[Dict[str, Any]], students: List[Dict[str, Any]]) -> None:
        """Load gradebook from provided dicts (for testing/offline)."""
        self.assignments.clear()
        self.students.clear()

        for a in assignments:
            self.assignments[a['id']] = Assignment(
                id=a['id'],
                name=a.get('name', f"Assignment {a['id']}")
                , points_possible=float(a['points_possible']) if a.get('points_possible') is not None else None,
                due_at=a.get('due_at'),
                assignment_group_id=a.get('assignment_group_id')
            )
        for u in students:
            uid = u['id']
            self.students[uid] = StudentSummary(id=uid, name=u.get('name'), login=u.get('login'), email=u.get('email'))
        for s in submissions:
            uid = s['user_id']
            aid = s['assignment_id']
            if uid not in self.students or aid not in self.assignments:
                continue
            assignment = self.assignments[aid]
            self.students[uid].scores[aid] = StudentScore(
                assignment_id=aid,
                score=s.get('score'),
                points_possible=assignment.points_possible,
                submitted_at=s.get('submitted_at'),
                workflow_state=s.get('workflow_state'),
                late=s.get('late'),
                missing=s.get('missing'),
                excused=s.get('excused'),
            )
        self._compute_totals()

    # -------------------- Computation helpers --------------------
    def _compute_totals(self) -> None:
        """Compute per-student totals including points for missing assignments.

        If a student lacks a submission for an assignment, its points are
        included in the denominator (total_points) with zero contribution to
        total_score. Excused submissions contribute neither points nor score.
        """
        for stu in self.students.values():
            total_score = 0.0
            total_points = 0.0
            for aid, assignment in self.assignments.items():
                sc = stu.scores.get(aid)
                pts = assignment.points_possible if assignment.points_possible is not None else 0.0
                if sc is None:
                    # Missing submission: count points, score = 0
                    total_points += pts
                    continue
                if sc.excused:
                    # Excused: skip both score and points
                    continue
                total_points += pts
                if sc.score is not None:
                    total_score += sc.score
            stu.total_score = total_score
            stu.total_points = total_points

    # -------------------- Queries --------------------
    def get_assignments(self) -> List[Assignment]:
        return list(self.assignments.values())

    def get_students(self) -> List[StudentSummary]:
        return list(self.students.values())

    def get_student(self, user_id: Any) -> Optional[StudentSummary]:
        return self.students.get(user_id)

    # -------------------- Analytics --------------------
    def overall_stats(self) -> Dict[str, Any]:
        """Compute stats across students with a percent value."""
        percents = [s.percent for s in self.students.values() if s.percent is not None]
        if not percents:
            return {"count": 0, "mean": None, "median": None, "std": None}
        return {
            "count": len(percents),
            "mean": mean(percents),
            "median": median(percents),
            "std": pstdev(percents) if len(percents) > 1 else 0.0,
            "min": min(percents),
            "max": max(percents),
        }

    def assignment_stats(self, assignment_id: int) -> Dict[str, Any]:
        scores: List[float] = []
        missing = 0
        excused = 0
        for s in self.students.values():
            sc = s.scores.get(assignment_id)
            if sc is None:
                missing += 1
                continue
            if sc.excused:
                excused += 1
                continue
            if sc.score is not None:
                scores.append(sc.score)
            else:
                missing += 1
        if not scores:
            return {"count": 0, "mean": None, "median": None, "std": None, "missing": missing, "excused": excused}
        return {
            "count": len(scores),
            "mean": mean(scores),
            "median": median(scores),
            "std": pstdev(scores) if len(scores) > 1 else 0.0,
            "min": min(scores),
            "max": max(scores),
            "missing": missing,
            "excused": excused,
        }

    def top_students(self, n: int = 10) -> List[Tuple[Any, float]]:
        pairs = [(s.id, s.percent) for s in self.students.values() if s.percent is not None]
        pairs.sort(key=lambda x: x[1], reverse=True)
        return pairs[:n]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "course_id": self.course_id,
            "assignments": [a.__dict__ for a in self.assignments.values()],
            "students": [
                {
                    "id": s.id,
                    "name": s.name,
                    "login": s.login,
                    "email": s.email,
                    "total_score": s.total_score,
                    "total_points": s.total_points,
                    "percent": s.percent,
                }
                for s in self.students.values()
            ],
        }
    
    def save_to_cache(self, cache_file: str = "gradebook_cache.pkl") -> None:
        """Save gradebook to cache file for faster loading.
        
        Args:
            cache_file: Path to cache file (default: gradebook_cache.pkl)
        """
        cache_path = Path(cache_file)
        with open(cache_path, 'wb') as f:
            pickle.dump(self, f)
        print(f"Gradebook cached to {cache_file}")
    
    @classmethod
    def load_from_cache(cls, cache_file: str = "gradebook_cache.pkl") -> "Gradebook":
        """Load gradebook from cache file.
        
        Args:
            cache_file: Path to cache file
            
        Returns:
            Gradebook object loaded from cache
            
        Raises:
            FileNotFoundError: If cache file doesn't exist
        """
        cache_path = Path(cache_file)
        if not cache_path.exists():
            raise FileNotFoundError(f"Cache file {cache_file} not found")
        
        with open(cache_path, 'rb') as f:
            gb = pickle.load(f)
        
        print(f"Gradebook loaded from cache: {cache_file}")
        print(f"  Course ID: {gb.course_id}")
        print(f"  {len(gb.assignments)} assignments, {len(gb.students)} students")
        return gb


def get_course_gradebook(canvas_connection: Any, course_id: int, include_inactive: bool = False) -> Gradebook:
    gb = Gradebook()
    gb.load_from_canvas(canvas_connection, course_id, include_inactive=include_inactive)
    return gb
