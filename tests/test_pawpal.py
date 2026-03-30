"""Tests for PawPal+ core logic."""

from pawpal_system import Pet, Task


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
