"""PawPal+ logic layer — backend classes for pet care scheduling."""

from dataclasses import dataclass, field

VALID_PRIORITIES = ("low", "medium", "high")
PRIORITY_WEIGHTS = {"low": 1, "medium": 2, "high": 3}


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

    def __post_init__(self) -> None:
        if self.priority not in VALID_PRIORITIES:
            raise ValueError(
                f"Invalid priority '{self.priority}'. Must be one of {VALID_PRIORITIES}."
            )
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be positive.")

    def priority_value(self) -> int:
        """Return a numeric weight for sorting (high=3, medium=2, low=1)."""
        return PRIORITY_WEIGHTS[self.priority]

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True


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
        """Add a care task for this pet."""
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

    def get_summary(self) -> str:
        """Return a readable description of this pet."""
        needs = ", ".join(self.special_needs) if self.special_needs else "none"
        return f"{self.name} ({self.species}, age {self.age}) — special needs: {needs}"


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

    def get_summary(self) -> str:
        """Return a readable description of this owner."""
        pet_names = ", ".join(p.name for p in self.pets) if self.pets else "none"
        return (
            f"{self.name} — {self.available_time_minutes} min available today, "
            f"pets: {pet_names}"
        )


# ---------------------------------------------------------------------------
# DailyPlan
# ---------------------------------------------------------------------------
@dataclass
class DailyPlan:
    """The resulting schedule for a day."""

    scheduled_tasks: list[Task] = field(default_factory=list)
    skipped_tasks: list[Task] = field(default_factory=list)
    total_duration: int = 0

    def get_explanation(self) -> str:
        """Produce a human-readable rationale for the plan."""
        lines: list[str] = []

        if self.scheduled_tasks:
            lines.append("Scheduled tasks (in priority order):")
            for i, task in enumerate(self.scheduled_tasks, start=1):
                lines.append(
                    f"  {i}. {task.title} — {task.duration_minutes} min "
                    f"(priority: {task.priority}, category: {task.category})"
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

    def generate_plan(self) -> DailyPlan:
        """Build a DailyPlan by fitting the highest-priority tasks first."""
        pending = self.owner.get_all_pending_tasks()

        # Sort by priority descending, then by shorter duration as tiebreaker
        sorted_tasks = sorted(
            pending,
            key=lambda t: (-t.priority_value(), t.duration_minutes),
        )

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
        )
