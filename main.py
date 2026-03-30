"""CLI demo script — verifies PawPal+ logic before connecting to Streamlit."""

from pawpal_system import Owner, Pet, Task, Scheduler


def main() -> None:
    # --- Setup owner ---
    owner = Owner("Jordan", available_time_minutes=90)

    # --- Setup pets ---
    mochi = Pet("Mochi", "dog", 3, special_needs=["needs daily medication"])
    whiskers = Pet("Whiskers", "cat", 7, special_needs=["indoor only"])

    owner.add_pet(mochi)
    owner.add_pet(whiskers)

    # --- Add tasks for Mochi (dog) ---
    mochi.add_task(Task("Morning walk", 30, "high", "walk"))
    mochi.add_task(Task("Medication", 5, "high", "meds"))
    mochi.add_task(Task("Brush coat", 15, "medium", "grooming"))
    mochi.add_task(Task("Puzzle toy", 20, "low", "enrichment"))

    # --- Add tasks for Whiskers (cat) ---
    whiskers.add_task(Task("Feed breakfast", 10, "high", "feeding"))
    whiskers.add_task(Task("Litter box cleanup", 10, "medium", "grooming"))
    whiskers.add_task(Task("Play with laser pointer", 15, "low", "enrichment"))

    # --- Generate schedule ---
    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()

    # --- Display ---
    print("=" * 50)
    print("  PawPal+ — Today's Schedule")
    print("=" * 50)
    print()
    print(f"Owner: {owner.get_summary()}")
    print()
    for pet in owner.pets:
        print(f"  {pet.get_summary()}")
    print()
    print("-" * 50)
    print(plan.get_explanation())
    print("-" * 50)


if __name__ == "__main__":
    main()
