"""PawPal+ logic layer — backend classes for pet care scheduling."""

from dataclasses import dataclass, field


@dataclass
class Owner:
    """Represents the pet owner and their daily time constraint."""

    name: str
    available_time_minutes: int

    def get_summary(self) -> str:
        pass


@dataclass
class Pet:
    """Represents a pet being cared for."""

    name: str
    species: str
    age: int
    special_needs: list[str] = field(default_factory=list)

    def get_summary(self) -> str:
        pass


@dataclass
class Task:
    """A single care activity that can be scheduled."""

    title: str
    duration_minutes: int
    priority: str  # "low", "medium", or "high"
    category: str  # "walk", "feeding", "meds", "enrichment", "grooming"

    def priority_value(self) -> int:
        pass


@dataclass
class DailyPlan:
    """The output schedule for a given day."""

    scheduled_tasks: list[Task] = field(default_factory=list)
    skipped_tasks: list[Task] = field(default_factory=list)
    total_duration: int = 0

    def get_explanation(self) -> str:
        pass


class Scheduler:
    """Engine that builds a DailyPlan from tasks and constraints."""

    def __init__(self, owner: Owner, pet: Pet, tasks: list[Task]) -> None:
        self.owner = owner
        self.pet = pet
        self.tasks = tasks

    def generate_plan(self) -> DailyPlan:
        pass
