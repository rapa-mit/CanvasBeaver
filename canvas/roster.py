#!/usr/bin/env python3
"""
roster.py
--------------------------------
Roster class to manage course participants by role.
Supports students, instructors, TAs, admins, and observers.

Usage example (without Canvas API):

    from roster import Roster

    r = Roster()
    r.add_students([
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
    ])
    r.add_instructors({"id": 10, "name": "Prof. Smith"})
    print(r.counts())           # {"students": 2, "instructors": 1, "tas": 0, "admins": 0, "observers": 0}
    print(r.find_user(1))       # ("students", {"id": 1, "name": "Alice"})

Optional Canvas integration:

    # Given a canvasapi.course.Course instance `course`:
    r = Roster()
    r.load_from_canvas(course)

"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Tuple

try:
    # Optional runtime dependency
    from canvasapi.course import Course  # type: ignore
    from canvasapi.enrollment import Enrollment  # type: ignore
    from canvasapi.user import User  # type: ignore
except Exception:  # pragma: no cover - keep optional
    Course = Any  # type: ignore
    Enrollment = Any  # type: ignore
    User = Any  # type: ignore


RoleName = str
UserDict = Dict[str, Any]


class Roster:
    """In-memory roster of course participants organized by roles.

    Roles supported: students, instructors, tas, admins, observers.
    Stores users as minimal serializable dictionaries.
    """

    DEFAULT_ROLES: Tuple[RoleName, ...] = (
        "students",
        "instructors",
        "tas",
        "admins",
        "observers",
    )

    def __init__(self, roles: Optional[Iterable[RoleName]] = None) -> None:
        self._roles: Tuple[RoleName, ...] = tuple(roles) if roles else self.DEFAULT_ROLES
        self._data: Dict[RoleName, Dict[Any, UserDict]] = {role: {} for role in self._roles}

    # -------------------- Introspection --------------------
    @property
    def roles(self) -> Tuple[RoleName, ...]:
        return self._roles

    def counts(self) -> Dict[RoleName, int]:
        return {role: len(self._data.get(role, {})) for role in self._roles}

    def get_all(self) -> Dict[RoleName, List[UserDict]]:
        return {role: list(self._data.get(role, {}).values()) for role in self._roles}

    # -------------------- Normalization --------------------
    def _normalize_user(self, user: Any) -> UserDict:
        """Return a serializable dict for a user-like object or dict.

        Supports:
        - Canvas API User objects
        - dicts with id/name/login/email
        - objects with attributes id/name/login/email
        """
        if isinstance(user, dict):
            if "id" not in user:
                raise ValueError("User dictionary must include an 'id' field")
            # Copy a minimal safe subset to avoid unexpected mutation
            return {
                k: user.get(k)
                for k in ("id", "name", "login", "email", "sis_user_id")
                if k in user
            }

        # Canvas User or any object with attributes
        user_id = getattr(user, "id", None)
        if user_id is None:
            raise ValueError("User object must have an 'id' attribute")

        out: UserDict = {"id": user_id}
        for attr, key in (
            ("name", "name"),
            ("login_id", "login"),
            ("email", "email"),
            ("sis_user_id", "sis_user_id"),
        ):
            val = getattr(user, attr, None)
            if val is not None:
                out[key] = val
        return out

    def _ensure_role(self, role: RoleName) -> None:
        if role not in self._roles:
            raise ValueError(f"Unknown role '{role}'. Valid roles: {', '.join(self._roles)}")

    # -------------------- Core operations --------------------
    def set_users(self, role: RoleName, users: Iterable[Any]) -> None:
        self._ensure_role(role)
        bucket: Dict[Any, UserDict] = {}
        for u in users:
            nu = self._normalize_user(u)
            bucket[nu["id"]] = nu
        self._data[role] = bucket

    def add_user(self, role: RoleName, user: Any) -> None:
        self._ensure_role(role)
        nu = self._normalize_user(user)
        self._data[role][nu["id"]] = nu  # upsert

    def add_users(self, role: RoleName, users: Iterable[Any]) -> None:
        for u in users:
            self.add_user(role, u)

    def get_users(self, role: RoleName) -> List[UserDict]:
        self._ensure_role(role)
        return list(self._data[role].values())

    def remove_user(self, role: RoleName, user_id: Any) -> Optional[UserDict]:
        self._ensure_role(role)
        return self._data[role].pop(user_id, None)

    def clear_role(self, role: RoleName) -> None:
        self._ensure_role(role)
        self._data[role].clear()

    def clear_all(self) -> None:
        for role in self._roles:
            self._data[role].clear()

    def find_user(self, user_id: Any) -> Optional[Tuple[RoleName, UserDict]]:
        for role in self._roles:
            if user_id in self._data[role]:
                return role, self._data[role][user_id]
        return None

    # -------------------- Role-specific helpers --------------------
    def add_students(self, users: Iterable[Any] | Any) -> None:
        if isinstance(users, (list, tuple, set)):
            self.add_users("students", users)
        else:
            self.add_user("students", users)

    def add_instructors(self, users: Iterable[Any] | Any) -> None:
        if isinstance(users, (list, tuple, set)):
            self.add_users("instructors", users)
        else:
            self.add_user("instructors", users)

    def add_tas(self, users: Iterable[Any] | Any) -> None:
        if isinstance(users, (list, tuple, set)):
            self.add_users("tas", users)
        else:
            self.add_user("tas", users)

    def add_admins(self, users: Iterable[Any] | Any) -> None:
        if isinstance(users, (list, tuple, set)):
            self.add_users("admins", users)
        else:
            self.add_user("admins", users)

    def add_observers(self, users: Iterable[Any] | Any) -> None:
        if isinstance(users, (list, tuple, set)):
            self.add_users("observers", users)
        else:
            self.add_user("observers", users)

    # -------------------- Serialization --------------------
    def to_dict(self) -> Dict[str, Any]:
        return {
            "roles": list(self._roles),
            "data": {role: list(bucket.values()) for role, bucket in self._data.items()},
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "Roster":
        roles = payload.get("roles") or cls.DEFAULT_ROLES
        r = cls(roles)
        data = payload.get("data", {})
        for role, users in data.items():
            if role in r._roles and isinstance(users, list):
                r.set_users(role, users)
        return r

    # -------------------- Canvas integration (optional) --------------------
    def load_from_canvas(self, course: Any, include_inactive: bool = False) -> None:
        """Populate roster using a canvasapi Course.

        Attempts to derive users by enrollment type and role. This requires the
        canvasapi package and appropriate API permissions.
        """
        if course is None:
            raise ValueError("course is required")

        # Map Canvas enrollment types/roles to our roles
        type_map = {
            "StudentEnrollment": "students",
            "TeacherEnrollment": "instructors",
            "TaEnrollment": "tas",
            "ObserverEnrollment": "observers",
            # Some institutions use custom role names containing 'Admin'
            # We'll handle admins separately below.
        }

        # Fetch enrollments and bucket users
        params = {"state": None} if include_inactive else {"state": ["active"]}
        enrollments = list(course.get_enrollments(**params))  # type: ignore[attr-defined]

        by_role: Dict[RoleName, Dict[Any, UserDict]] = {role: {} for role in self._roles}

        for enr in enrollments:
            try:
                # enrollment.type could be 'StudentEnrollment', etc.
                etype = getattr(enr, "type", None)
                role_name = None
                if etype in type_map:
                    role_name = type_map[etype]
                else:
                    # Fallback: check role string for 'Admin'
                    role_str = getattr(enr, "role", "") or getattr(enr, "role_id", "")
                    if isinstance(role_str, str) and "admin" in role_str.lower():
                        role_name = "admins"

                if role_name and role_name in by_role:
                    # enrollment has user dict under 'user'
                    u = getattr(enr, "user", None)
                    if u is None and hasattr(enr, "user_id"):
                        u = {"id": getattr(enr, "user_id")}
                    if u is None:
                        continue
                    nu = self._normalize_user(u)
                    by_role[role_name][nu["id"]] = nu
            except Exception:
                continue

        # Replace existing
        for role in self._roles:
            self._data[role] = by_role.get(role, {})

