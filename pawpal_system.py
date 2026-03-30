"""PawPal+ logic layer — backend classes for pet care scheduling."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path

VALID_PRIORITIES = ("low", "medium", "high")
PRIORITY_WEIGHTS = {"low": 1, "medium": 2, "high": 3}
VALID_FREQUENCIES = ("once", "daily", "weekly")

# Emoji maps for UI formatting
PRIORITY_EMOJI = {"high": "\U0001f534", "medium": "\U0001f7e1", "low": "\U0001f7e2"}
CATEGORY_EMOJI = {
    "walk": "\U0001f6b6",
    "feeding": "\U0001f355",
    "meds": "\U0001f48a",
    "enrichment": "\U0001f9e9",
    "grooming": "\u2702\ufe0f",
    "general": "\U0001f4cb",
}


def _time_to_minutes(time_str: str) -> int:
    """Convert an 'HH:MM' string to total minutes since midnight."""
    hours, minutes = time_str.split(":")
    return int(hours) * 60 + int(minutes)


def _minutes_to_time(minutes: int) -> str:
    """Convert total minutes since midnight to 'HH:MM' string."""
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------
@dataclass
class Task:
    """A single pet-care activity that can be scheduled."""

    title: str
    duration_minutes: int
    priority: str  # "low", "medium", or "high"
    category: str = "general"
    completed: bool = False
    scheduled_time: str = ""  # "HH:MM" format, empty = unscheduled
    frequency: str = "once"  # "once", "daily", or "weekly"
    pet_name: str = ""  # which pet this task belongs to
    due_date: date | None = None  # when this task is due

    def __post_init__(self) -> None:
        if self.priority not in VALID_PRIORITIES:
            raise ValueError(
                f"Invalid priority '{self.priority}'. Must be one of {VALID_PRIORITIES}."
            )
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be positive.")
        if self.frequency not in VALID_FREQUENCIES:
            raise ValueError(
                f"Invalid frequency '{self.frequency}'. Must be one of {VALID_FREQUENCIES}."
            )
        if self.scheduled_time and not self._valid_time(self.scheduled_time):
            raise ValueError(
                f"Invalid scheduled_time '{self.scheduled_time}'. Use 'HH:MM' format."
            )

    @staticmethod
    def _valid_time(t: str) -> bool:
        """Check that a string matches HH:MM with valid hour/minute ranges."""
        parts = t.split(":")
        if len(parts) != 2:
            return False
        try:
            h, m = int(parts[0]), int(parts[1])
            return 0 <= h <= 23 and 0 <= m <= 59
        except ValueError:
            return False

    def priority_value(self) -> int:
        """Return a numeric weight for sorting (high=3, medium=2, low=1)."""
        return PRIORITY_WEIGHTS[self.priority]

    def start_minutes(self) -> int:
        """Return scheduled start time as minutes since midnight, or -1 if unscheduled."""
        if not self.scheduled_time:
            return -1
        return _time_to_minutes(self.scheduled_time)

    def end_minutes(self) -> int:
        """Return scheduled end time as minutes since midnight, or -1 if unscheduled."""
        if not self.scheduled_time:
            return -1
        return self.start_minutes() + self.duration_minutes

    def mark_complete(self) -> Task | None:
        """Mark this task as completed. Returns a new Task for the next occurrence if recurring."""
        self.completed = True
        if self.frequency == "once":
            return None
        delta = timedelta(days=1) if self.frequency == "daily" else timedelta(weeks=1)
        next_due = (self.due_date or date.today()) + delta
        return Task(
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            category=self.category,
            completed=False,
            scheduled_time=self.scheduled_time,
            frequency=self.frequency,
            pet_name=self.pet_name,
            due_date=next_due,
        )

    def to_dict(self) -> dict:
        """Serialize this task to a JSON-compatible dictionary."""
        return {
            "title": self.title,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
            "category": self.category,
            "completed": self.completed,
            "scheduled_time": self.scheduled_time,
            "frequency": self.frequency,
            "pet_name": self.pet_name,
            "due_date": self.due_date.isoformat() if self.due_date else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Task:
        """Deserialize a task from a dictionary."""
        due = data.get("due_date")
        return cls(
            title=data["title"],
            duration_minutes=data["duration_minutes"],
            priority=data["priority"],
            category=data.get("category", "general"),
            completed=data.get("completed", False),
            scheduled_time=data.get("scheduled_time", ""),
            frequency=data.get("frequency", "once"),
            pet_name=data.get("pet_name", ""),
            due_date=date.fromisoformat(due) if due else None,
        )

    def format_priority(self) -> str:
        """Return priority with emoji indicator."""
        return f"{PRIORITY_EMOJI.get(self.priority, '')} {self.priority.capitalize()}"

    def format_category(self) -> str:
        """Return category with emoji indicator."""
        return f"{CATEGORY_EMOJI.get(self.category, '')} {self.category.capitalize()}"


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------
@dataclass
class Pet:
    """A pet with its own list of care tasks."""

    name: str
    species: str
    age: int
    special_needs: list[str] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task for this pet and tag it with the pet's name."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, title: str) -> bool:
        """Remove a task by title. Returns True if found and removed."""
        for i, task in enumerate(self.tasks):
            if task.title == title:
                self.tasks.pop(i)
                return True
        return False

    def pending_tasks(self) -> list[Task]:
        """Return only tasks that have not been completed."""
        return [t for t in self.tasks if not t.completed]

    def completed_tasks(self) -> list[Task]:
        """Return only tasks that have been completed."""
        return [t for t in self.tasks if t.completed]

    def get_summary(self) -> str:
        """Return a readable description of this pet."""
        needs = ", ".join(self.special_needs) if self.special_needs else "none"
        return f"{self.name} ({self.species}, age {self.age}) — special needs: {needs}"

    def to_dict(self) -> dict:
        """Serialize this pet to a JSON-compatible dictionary."""
        return {
            "name": self.name,
            "species": self.species,
            "age": self.age,
            "special_needs": self.special_needs,
            "tasks": [t.to_dict() for t in self.tasks],
        }

    @classmethod
    def from_dict(cls, data: dict) -> Pet:
        """Deserialize a pet from a dictionary."""
        pet = cls(
            name=data["name"],
            species=data["species"],
            age=data["age"],
            special_needs=data.get("special_needs", []),
        )
        for t_data in data.get("tasks", []):
            pet.tasks.append(Task.from_dict(t_data))
        return pet


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------
@dataclass
class Owner:
    """A pet owner who manages one or more pets."""

    name: str
    available_time_minutes: int
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Collect every task across all of the owner's pets."""
        all_tasks: list[Task] = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks

    def get_all_pending_tasks(self) -> list[Task]:
        """Collect only incomplete tasks across all pets."""
        pending: list[Task] = []
        for pet in self.pets:
            pending.extend(pet.pending_tasks())
        return pending

    def filter_tasks(
        self,
        pet_name: str | None = None,
        completed: bool | None = None,
        category: str | None = None,
    ) -> list[Task]:
        """Filter tasks across all pets by pet name, completion status, or category."""
        tasks = self.get_all_tasks()
        if pet_name is not None:
            tasks = [t for t in tasks if t.pet_name == pet_name]
        if completed is not None:
            tasks = [t for t in tasks if t.completed is completed]
        if category is not None:
            tasks = [t for t in tasks if t.category == category]
        return tasks

    def get_summary(self) -> str:
        """Return a readable description of this owner."""
        pet_names = ", ".join(p.name for p in self.pets) if self.pets else "none"
        return (
            f"{self.name} — {self.available_time_minutes} min available today, "
            f"pets: {pet_names}"
        )

    def to_dict(self) -> dict:
        """Serialize this owner to a JSON-compatible dictionary."""
        return {
            "name": self.name,
            "available_time_minutes": self.available_time_minutes,
            "pets": [p.to_dict() for p in self.pets],
        }

    @classmethod
    def from_dict(cls, data: dict) -> Owner:
        """Deserialize an owner from a dictionary."""
        owner = cls(
            name=data["name"],
            available_time_minutes=data["available_time_minutes"],
        )
        for p_data in data.get("pets", []):
            owner.pets.append(Pet.from_dict(p_data))
        return owner

    def save_to_json(self, path: str = "data.json") -> None:
        """Save owner, pets, and tasks to a JSON file."""
        Path(path).write_text(json.dumps(self.to_dict(), indent=2))

    @classmethod
    def load_from_json(cls, path: str = "data.json") -> Owner | None:
        """Load owner from a JSON file. Returns None if file doesn't exist."""
        p = Path(path)
        if not p.exists():
            return None
        data = json.loads(p.read_text())
        return cls.from_dict(data)


# ---------------------------------------------------------------------------
# DailyPlan
# ---------------------------------------------------------------------------
@dataclass
class DailyPlan:
    """The resulting schedule for a day."""

    scheduled_tasks: list[Task] = field(default_factory=list)
    skipped_tasks: list[Task] = field(default_factory=list)
    total_duration: int = 0
    conflicts: list[str] = field(default_factory=list)

    def get_explanation(self) -> str:
        """Produce a human-readable rationale for the plan."""
        lines: list[str] = []

        if self.conflicts:
            lines.append("⚠ Conflicts detected:")
            for warning in self.conflicts:
                lines.append(f"  - {warning}")
            lines.append("")

        if self.scheduled_tasks:
            lines.append("Scheduled tasks (in priority order):")
            for i, task in enumerate(self.scheduled_tasks, start=1):
                time_str = f" @ {task.scheduled_time}" if task.scheduled_time else ""
                pet_str = f" [{task.pet_name}]" if task.pet_name else ""
                lines.append(
                    f"  {i}. {task.title}{pet_str} — {task.duration_minutes} min"
                    f"{time_str} (priority: {task.priority}, category: {task.category})"
                )
            lines.append(f"  Total time used: {self.total_duration} min")
        else:
            lines.append("No tasks could be scheduled.")

        if self.skipped_tasks:
            lines.append("")
            lines.append("Skipped (not enough time remaining):")
            for task in self.skipped_tasks:
                lines.append(
                    f"  - {task.title} — {task.duration_minutes} min "
                    f"(priority: {task.priority})"
                )

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------
class Scheduler:
    """The brain — retrieves tasks from the Owner's pets and builds a plan."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by scheduled_time (HH:MM). Unscheduled tasks go to the end."""
        return sorted(
            tasks,
            key=lambda t: (
                t.scheduled_time == "",
                _time_to_minutes(t.scheduled_time) if t.scheduled_time else 9999,
            ),
        )

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by priority descending, with shorter duration as tiebreaker."""
        return sorted(
            tasks,
            key=lambda t: (-t.priority_value(), t.duration_minutes),
        )

    def detect_conflicts(self, tasks: list[Task]) -> list[str]:
        """Detect overlapping tasks based on scheduled_time and duration."""
        warnings: list[str] = []
        scheduled = [t for t in tasks if t.scheduled_time]
        scheduled.sort(key=lambda t: t.start_minutes())

        for i in range(len(scheduled)):
            for j in range(i + 1, len(scheduled)):
                a, b = scheduled[i], scheduled[j]
                if b.start_minutes() < a.end_minutes():
                    warnings.append(
                        f"'{a.title}' ({a.scheduled_time}-{_minutes_to_time(a.end_minutes())})"
                        f" overlaps with "
                        f"'{b.title}' ({b.scheduled_time}-{_minutes_to_time(b.end_minutes())})"
                    )
                else:
                    break
        return warnings

    def find_next_available_slot(self, duration: int, day_start: str = "07:00", day_end: str = "21:00") -> str | None:
        """Find the earliest time slot of the given duration that doesn't conflict with existing tasks.

        Scans from day_start to day_end, looking for a gap between already-scheduled
        tasks that is at least `duration` minutes long.  Returns the start time as
        'HH:MM' or None if no slot fits.
        """
        start_min = _time_to_minutes(day_start)
        end_min = _time_to_minutes(day_end)

        # Collect all scheduled (pending) task intervals, sorted by start
        scheduled = [
            t for t in self.owner.get_all_pending_tasks() if t.scheduled_time
        ]
        scheduled.sort(key=lambda t: t.start_minutes())

        # Build list of occupied intervals
        occupied = [(t.start_minutes(), t.end_minutes()) for t in scheduled]

        # Try to fit in the gaps
        cursor = start_min
        for occ_start, occ_end in occupied:
            # Gap before this occupied block
            if cursor + duration <= occ_start:
                return _minutes_to_time(cursor)
            # Move cursor past this block if it overlaps
            if occ_end > cursor:
                cursor = occ_end

        # Check gap after the last occupied block
        if cursor + duration <= end_min:
            return _minutes_to_time(cursor)

        return None

    def complete_task(self, pet_name: str, task_title: str) -> Task | None:
        """Mark a task complete and return the next occurrence if recurring."""
        for pet in self.owner.pets:
            if pet.name != pet_name:
                continue
            for task in pet.tasks:
                if task.title == task_title and not task.completed:
                    next_task = task.mark_complete()
                    if next_task is not None:
                        pet.add_task(next_task)
                    return next_task
        return None

    def generate_plan(self) -> DailyPlan:
        """Build a DailyPlan by fitting the highest-priority tasks first."""
        pending = self.owner.get_all_pending_tasks()
        sorted_tasks = self.sort_by_priority(pending)
        conflicts = self.detect_conflicts(sorted_tasks)

        budget = self.owner.available_time_minutes
        scheduled: list[Task] = []
        skipped: list[Task] = []
        time_used = 0

        for task in sorted_tasks:
            if time_used + task.duration_minutes <= budget:
                scheduled.append(task)
                time_used += task.duration_minutes
            else:
                skipped.append(task)

        return DailyPlan(
            scheduled_tasks=scheduled,
            skipped_tasks=skipped,
            total_duration=time_used,
            conflicts=conflicts,
        )
