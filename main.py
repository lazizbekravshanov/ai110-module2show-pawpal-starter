"""CLI demo script — verifies PawPal+ logic before connecting to Streamlit."""

from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler


def main() -> None:
    # --- Setup owner ---
    owner = Owner("Jordan", available_time_minutes=90)

    # --- Setup pets ---
    mochi = Pet("Mochi", "dog", 3, special_needs=["needs daily medication"])
    whiskers = Pet("Whiskers", "cat", 7, special_needs=["indoor only"])

    owner.add_pet(mochi)
    owner.add_pet(whiskers)

    # --- Add tasks OUT OF ORDER to test sorting ---
    mochi.add_task(Task("Puzzle toy", 20, "low", "enrichment", scheduled_time="14:00"))
    mochi.add_task(Task("Morning walk", 30, "high", "walk", scheduled_time="07:00", frequency="daily", due_date=date.today()))
    mochi.add_task(Task("Medication", 5, "high", "meds", scheduled_time="08:00", frequency="daily", due_date=date.today()))
    mochi.add_task(Task("Brush coat", 15, "medium", "grooming", scheduled_time="10:00"))

    whiskers.add_task(Task("Feed breakfast", 10, "high", "feeding", scheduled_time="07:30", frequency="daily", due_date=date.today()))
    # Intentional conflict: overlaps with Mochi's morning walk (07:00-07:30)
    whiskers.add_task(Task("Litter box cleanup", 10, "medium", "grooming", scheduled_time="07:15"))
    whiskers.add_task(Task("Play with laser pointer", 15, "low", "enrichment", scheduled_time="15:00"))

    scheduler = Scheduler(owner)

    # ── 1. Sorting by time ────────────────────────────────────────────────
    print("=" * 55)
    print("  PawPal+ — Algorithmic Demo")
    print("=" * 55)

    all_pending = owner.get_all_pending_tasks()

    print("\n📋 All tasks sorted by SCHEDULED TIME:")
    for t in scheduler.sort_by_time(all_pending):
        pet = f"[{t.pet_name}]" if t.pet_name else ""
        print(f"  {t.scheduled_time or '--:--'} | {t.title} {pet} ({t.duration_minutes} min, {t.priority})")

    # ── 2. Filtering ──────────────────────────────────────────────────────
    print("\n🔍 Filter: only Mochi's tasks:")
    for t in owner.filter_tasks(pet_name="Mochi"):
        print(f"  - {t.title} ({t.priority}, {t.category})")

    print("\n🔍 Filter: only grooming tasks:")
    for t in owner.filter_tasks(category="grooming"):
        print(f"  - {t.title} [{t.pet_name}]")

    # ── 3. Generate plan (includes conflict detection) ────────────────────
    plan = scheduler.generate_plan()
    print("\n" + "-" * 55)
    print(plan.get_explanation())
    print("-" * 55)

    # ── 4. Recurring tasks — complete a daily task ────────────────────────
    print("\n🔁 Completing 'Morning walk' (daily recurring)...")
    next_task = scheduler.complete_task("Mochi", "Morning walk")
    if next_task:
        print(f"   Next occurrence created: '{next_task.title}' due {next_task.due_date}")

    print("\n🔍 Filter: Mochi's completed tasks:")
    for t in owner.filter_tasks(pet_name="Mochi", completed=True):
        print(f"  ✓ {t.title}")

    print("\n🔍 Filter: Mochi's pending tasks (after completion):")
    for t in owner.filter_tasks(pet_name="Mochi", completed=False):
        freq = f" [{t.frequency}]" if t.frequency != "once" else ""
        due = f" (due {t.due_date})" if t.due_date else ""
        print(f"  ○ {t.title}{freq}{due}")

    print()


if __name__ == "__main__":
    main()
