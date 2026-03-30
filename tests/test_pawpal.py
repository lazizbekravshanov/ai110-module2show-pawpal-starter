"""Tests for PawPal+ core logic."""

import pytest
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


def test_add_task_tags_pet_name():
    """Adding a task to a Pet should set the task's pet_name field."""
    pet = Pet("Mochi", "dog", 3)
    task = Task("Walk", 20, "high")
    pet.add_task(task)
    assert task.pet_name == "Mochi"


def test_remove_task_by_title():
    """Removing a task by title should decrease the task list and return True."""
    pet = Pet("Mochi", "dog", 3)
    pet.add_task(Task("Walk", 20, "high"))
    pet.add_task(Task("Feed", 10, "high"))

    assert pet.remove_task("Walk") is True
    assert len(pet.tasks) == 1
    assert pet.tasks[0].title == "Feed"


def test_remove_nonexistent_task_returns_false():
    """Removing a task that doesn't exist should return False."""
    pet = Pet("Mochi", "dog", 3)
    assert pet.remove_task("Ghost task") is False


# ── Validation tests ─────────────────────────────────────────────────────

def test_invalid_priority_raises_error():
    """Creating a Task with an invalid priority should raise ValueError."""
    with pytest.raises(ValueError, match="Invalid priority"):
        Task("Bad", 10, "urgent")


def test_zero_duration_raises_error():
    """Creating a Task with zero duration should raise ValueError."""
    with pytest.raises(ValueError, match="duration_minutes must be positive"):
        Task("Bad", 0, "high")


def test_invalid_frequency_raises_error():
    """Creating a Task with an invalid frequency should raise ValueError."""
    with pytest.raises(ValueError, match="Invalid frequency"):
        Task("Bad", 10, "high", frequency="monthly")


def test_invalid_scheduled_time_raises_error():
    """Creating a Task with a bad time format should raise ValueError."""
    with pytest.raises(ValueError, match="Invalid scheduled_time"):
        Task("Bad", 10, "high", scheduled_time="25:00")


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


def test_sort_by_priority_shorter_duration_wins_tiebreak():
    """Within the same priority, shorter tasks should come first."""
    owner = Owner("Test", 120)
    pet = Pet("Rex", "dog", 2)
    owner.add_pet(pet)
    pet.add_task(Task("Long high", 60, "high"))
    pet.add_task(Task("Short high", 10, "high"))

    scheduler = Scheduler(owner)
    sorted_tasks = scheduler.sort_by_priority(owner.get_all_tasks())

    assert sorted_tasks[0].title == "Short high"
    assert sorted_tasks[1].title == "Long high"


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


def test_filter_combined_pet_and_category():
    """Combining pet_name and category filters should narrow results."""
    owner = Owner("Test", 120)
    pet_a = Pet("Alpha", "dog", 2)
    pet_b = Pet("Beta", "cat", 4)
    owner.add_pet(pet_a)
    owner.add_pet(pet_b)
    pet_a.add_task(Task("Dog walk", 20, "high", "walk"))
    pet_a.add_task(Task("Dog feed", 10, "high", "feeding"))
    pet_b.add_task(Task("Cat walk", 15, "medium", "walk"))

    result = owner.filter_tasks(pet_name="Alpha", category="walk")
    assert len(result) == 1
    assert result[0].title == "Dog walk"


def test_filter_no_match_returns_empty():
    """Filtering with no matching criteria should return an empty list."""
    owner = Owner("Test", 120)
    pet = Pet("Rex", "dog", 2)
    owner.add_pet(pet)
    pet.add_task(Task("Walk", 20, "high", "walk"))

    result = owner.filter_tasks(pet_name="Ghost")
    assert result == []


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


def test_scheduler_complete_task_adds_next_to_pet():
    """Scheduler.complete_task() should add the next occurrence to the pet's task list."""
    owner = Owner("Test", 120)
    pet = Pet("Rex", "dog", 2)
    owner.add_pet(pet)
    pet.add_task(Task("Walk", 30, "high", "walk", frequency="daily", due_date=date.today()))

    scheduler = Scheduler(owner)
    scheduler.complete_task("Rex", "Walk")

    # Original completed + new pending occurrence
    assert len(pet.tasks) == 2
    assert pet.tasks[0].completed is True
    assert pet.tasks[1].completed is False
    assert pet.tasks[1].due_date == date.today() + timedelta(days=1)


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


def test_detect_exact_same_time_conflict():
    """Two tasks at the exact same time should be flagged as a conflict."""
    owner = Owner("Test", 120)
    pet = Pet("Rex", "dog", 2)
    owner.add_pet(pet)
    pet.add_task(Task("Walk", 30, "high", "walk", scheduled_time="09:00"))
    pet.add_task(Task("Feed", 10, "high", "feeding", scheduled_time="09:00"))

    scheduler = Scheduler(owner)
    conflicts = scheduler.detect_conflicts(owner.get_all_tasks())

    assert len(conflicts) == 1


def test_conflict_across_different_pets():
    """Overlapping tasks on different pets should still be flagged."""
    owner = Owner("Test", 120)
    dog = Pet("Rex", "dog", 2)
    cat = Pet("Whiskers", "cat", 5)
    owner.add_pet(dog)
    owner.add_pet(cat)
    dog.add_task(Task("Dog walk", 30, "high", "walk", scheduled_time="07:00"))
    cat.add_task(Task("Cat feed", 10, "high", "feeding", scheduled_time="07:10"))

    scheduler = Scheduler(owner)
    conflicts = scheduler.detect_conflicts(owner.get_all_tasks())

    assert len(conflicts) == 1
    assert "Dog walk" in conflicts[0]
    assert "Cat feed" in conflicts[0]


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


# ── Scheduling edge cases ────────────────────────────────────────────────

def test_pet_with_no_tasks_produces_empty_plan():
    """A pet with no tasks should produce an empty plan."""
    owner = Owner("Test", 60)
    pet = Pet("Rex", "dog", 2)
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()

    assert plan.scheduled_tasks == []
    assert plan.skipped_tasks == []
    assert plan.total_duration == 0


def test_all_tasks_exceed_budget():
    """When every task exceeds the budget, all should be skipped."""
    owner = Owner("Test", 5)
    pet = Pet("Rex", "dog", 2)
    owner.add_pet(pet)
    pet.add_task(Task("Long walk", 60, "high", "walk"))
    pet.add_task(Task("Grooming", 30, "medium", "grooming"))

    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()

    assert plan.scheduled_tasks == []
    assert len(plan.skipped_tasks) == 2
    assert plan.total_duration == 0


def test_completed_tasks_excluded_from_plan():
    """Completed tasks should not appear in the generated plan."""
    owner = Owner("Test", 120)
    pet = Pet("Rex", "dog", 2)
    owner.add_pet(pet)
    pet.add_task(Task("Done task", 10, "high"))
    pet.add_task(Task("Pending task", 10, "high"))
    pet.tasks[0].mark_complete()

    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()

    assert len(plan.scheduled_tasks) == 1
    assert plan.scheduled_tasks[0].title == "Pending task"


def test_plan_fills_budget_exactly():
    """Tasks that exactly fill the budget should all be scheduled with none skipped."""
    owner = Owner("Test", 30)
    pet = Pet("Rex", "dog", 2)
    owner.add_pet(pet)
    pet.add_task(Task("Task A", 15, "high"))
    pet.add_task(Task("Task B", 15, "high"))

    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()

    assert len(plan.scheduled_tasks) == 2
    assert plan.skipped_tasks == []
    assert plan.total_duration == 30
