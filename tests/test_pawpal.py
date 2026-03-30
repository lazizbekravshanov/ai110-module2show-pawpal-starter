"""Tests for PawPal+ core logic."""

from datetime import date, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler


# ── Basic tests ───────────────────────────────────────────────────────────

def test_mark_complete_changes_status():
    """Calling mark_complete() should flip completed from False to True."""
    task = Task("Morning walk", 30, "high", "walk")
    assert task.completed is False

    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    """Adding a task to a Pet should increase its task list length by one."""
    pet = Pet("Mochi", "dog", 3)
    assert len(pet.tasks) == 0

    pet.add_task(Task("Feed breakfast", 10, "high", "feeding"))
    assert len(pet.tasks) == 1

    pet.add_task(Task("Evening walk", 25, "medium", "walk"))
    assert len(pet.tasks) == 2


# ── Sorting tests ─────────────────────────────────────────────────────────

def test_sort_by_time_orders_by_scheduled_time():
    """Tasks should be ordered by HH:MM; unscheduled tasks go last."""
    owner = Owner("Test", 120)
    pet = Pet("Rex", "dog", 2)
    owner.add_pet(pet)
    pet.add_task(Task("Late task", 10, "low", scheduled_time="15:00"))
    pet.add_task(Task("Early task", 10, "low", scheduled_time="07:00"))
    pet.add_task(Task("No time", 10, "low"))

    scheduler = Scheduler(owner)
    sorted_tasks = scheduler.sort_by_time(owner.get_all_tasks())

    assert sorted_tasks[0].title == "Early task"
    assert sorted_tasks[1].title == "Late task"
    assert sorted_tasks[2].title == "No time"


def test_sort_by_priority_high_first():
    """High-priority tasks should come before lower ones."""
    owner = Owner("Test", 120)
    pet = Pet("Rex", "dog", 2)
    owner.add_pet(pet)
    pet.add_task(Task("Low", 10, "low"))
    pet.add_task(Task("High", 10, "high"))
    pet.add_task(Task("Medium", 10, "medium"))

    scheduler = Scheduler(owner)
    sorted_tasks = scheduler.sort_by_priority(owner.get_all_tasks())

    assert sorted_tasks[0].title == "High"
    assert sorted_tasks[1].title == "Medium"
    assert sorted_tasks[2].title == "Low"


# ── Filtering tests ───────────────────────────────────────────────────────

def test_filter_by_pet_name():
    """Filtering by pet name should return only that pet's tasks."""
    owner = Owner("Test", 120)
    pet_a = Pet("Alpha", "dog", 2)
    pet_b = Pet("Beta", "cat", 4)
    owner.add_pet(pet_a)
    owner.add_pet(pet_b)
    pet_a.add_task(Task("Walk", 20, "high", "walk"))
    pet_b.add_task(Task("Feed", 10, "high", "feeding"))

    result = owner.filter_tasks(pet_name="Alpha")
    assert len(result) == 1
    assert result[0].title == "Walk"


def test_filter_by_completion_status():
    """Filtering by completed=True should return only completed tasks."""
    owner = Owner("Test", 120)
    pet = Pet("Rex", "dog", 2)
    owner.add_pet(pet)
    pet.add_task(Task("Done task", 10, "low"))
    pet.add_task(Task("Pending task", 10, "high"))
    pet.tasks[0].mark_complete()

    result = owner.filter_tasks(completed=True)
    assert len(result) == 1
    assert result[0].title == "Done task"


def test_filter_by_category():
    """Filtering by category should return only matching tasks."""
    owner = Owner("Test", 120)
    pet = Pet("Rex", "dog", 2)
    owner.add_pet(pet)
    pet.add_task(Task("Walk", 20, "high", "walk"))
    pet.add_task(Task("Feed", 10, "high", "feeding"))
    pet.add_task(Task("Brush", 15, "medium", "grooming"))

    result = owner.filter_tasks(category="walk")
    assert len(result) == 1
    assert result[0].title == "Walk"


# ── Recurring task tests ──────────────────────────────────────────────────

def test_daily_recurring_creates_next_task():
    """Completing a daily task should create a new task due tomorrow."""
    task = Task("Walk", 30, "high", "walk", frequency="daily", due_date=date.today())
    next_task = task.mark_complete()

    assert task.completed is True
    assert next_task is not None
    assert next_task.completed is False
    assert next_task.due_date == date.today() + timedelta(days=1)
    assert next_task.frequency == "daily"


def test_weekly_recurring_creates_next_task():
    """Completing a weekly task should create a new task due in 7 days."""
    task = Task("Grooming", 60, "medium", "grooming", frequency="weekly", due_date=date.today())
    next_task = task.mark_complete()

    assert next_task is not None
    assert next_task.due_date == date.today() + timedelta(weeks=1)


def test_one_time_task_returns_none():
    """Completing a one-time task should not create a next occurrence."""
    task = Task("Vet visit", 60, "high", frequency="once")
    next_task = task.mark_complete()

    assert task.completed is True
    assert next_task is None


# ── Conflict detection tests ──────────────────────────────────────────────

def test_detect_overlapping_tasks():
    """Two tasks with overlapping times should produce a conflict warning."""
    owner = Owner("Test", 120)
    pet = Pet("Rex", "dog", 2)
    owner.add_pet(pet)
    pet.add_task(Task("Walk", 30, "high", "walk", scheduled_time="07:00"))
    pet.add_task(Task("Feed", 10, "high", "feeding", scheduled_time="07:15"))

    scheduler = Scheduler(owner)
    conflicts = scheduler.detect_conflicts(owner.get_all_tasks())

    assert len(conflicts) == 1
    assert "Walk" in conflicts[0]
    assert "Feed" in conflicts[0]


def test_no_conflict_for_non_overlapping_tasks():
    """Tasks that don't overlap should produce no warnings."""
    owner = Owner("Test", 120)
    pet = Pet("Rex", "dog", 2)
    owner.add_pet(pet)
    pet.add_task(Task("Walk", 30, "high", "walk", scheduled_time="07:00"))
    pet.add_task(Task("Feed", 10, "high", "feeding", scheduled_time="08:00"))

    scheduler = Scheduler(owner)
    conflicts = scheduler.detect_conflicts(owner.get_all_tasks())

    assert len(conflicts) == 0


def test_generate_plan_includes_conflicts():
    """generate_plan() should include conflict warnings in the DailyPlan."""
    owner = Owner("Test", 120)
    pet = Pet("Rex", "dog", 2)
    owner.add_pet(pet)
    pet.add_task(Task("Walk", 30, "high", "walk", scheduled_time="07:00"))
    pet.add_task(Task("Feed", 10, "high", "feeding", scheduled_time="07:15"))

    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()

    assert len(plan.conflicts) == 1
