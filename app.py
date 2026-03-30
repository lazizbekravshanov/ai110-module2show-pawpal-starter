import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# ── Session state: keep the Owner alive across reruns ────────────────────
if "owner" not in st.session_state:
    st.session_state.owner = Owner("", available_time_minutes=60)

owner: Owner = st.session_state.owner

# ── Header ───────────────────────────────────────────────────────────────
st.title("🐾 PawPal+")
st.caption("A pet care planning assistant — sort, filter, detect conflicts, and handle recurring tasks")

# ── 1. Owner info ────────────────────────────────────────────────────────
st.subheader("Owner Info")
col_name, col_time = st.columns(2)
with col_name:
    owner.name = st.text_input("Your name", value=owner.name or "Jordan")
with col_time:
    owner.available_time_minutes = st.number_input(
        "Available time today (minutes)",
        min_value=1,
        max_value=480,
        value=owner.available_time_minutes,
    )

st.divider()

# ── 2. Add a pet ─────────────────────────────────────────────────────────
st.subheader("Add a Pet")
with st.form("add_pet_form", clear_on_submit=True):
    pc1, pc2, pc3 = st.columns(3)
    with pc1:
        pet_name = st.text_input("Pet name")
    with pc2:
        species = st.selectbox("Species", ["dog", "cat", "other"])
    with pc3:
        age = st.number_input("Age", min_value=0, max_value=30, value=1)
    special_needs = st.text_input("Special needs (comma-separated)", value="")
    add_pet = st.form_submit_button("Add pet")

    if add_pet and pet_name:
        needs = [s.strip() for s in special_needs.split(",") if s.strip()]
        new_pet = Pet(pet_name, species, age, special_needs=needs)
        owner.add_pet(new_pet)
        st.success(f"Added {pet_name} the {species}!")

# Show current pets
if owner.pets:
    st.markdown("**Your pets:**")
    for pet in owner.pets:
        st.write(f"- {pet.get_summary()}")
else:
    st.info("No pets yet. Add one above.")

st.divider()

# ── 3. Add tasks to a pet ────────────────────────────────────────────────
st.subheader("Add a Task")

if owner.pets:
    with st.form("add_task_form", clear_on_submit=True):
        pet_choice = st.selectbox(
            "For which pet?",
            options=[p.name for p in owner.pets],
        )
        tc1, tc2 = st.columns(2)
        with tc1:
            task_title = st.text_input("Task title")
            task_category = st.selectbox(
                "Category",
                ["walk", "feeding", "meds", "enrichment", "grooming", "general"],
            )
            task_frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])
        with tc2:
            task_duration = st.number_input(
                "Duration (minutes)", min_value=1, max_value=240, value=15
            )
            task_priority = st.selectbox("Priority", ["high", "medium", "low"])
            task_time = st.text_input("Scheduled time (HH:MM, optional)", value="")
        add_task = st.form_submit_button("Add task")

        if add_task and task_title:
            try:
                target_pet = next(p for p in owner.pets if p.name == pet_choice)
                new_task = Task(
                    task_title,
                    int(task_duration),
                    task_priority,
                    task_category,
                    scheduled_time=task_time,
                    frequency=task_frequency,
                )
                target_pet.add_task(new_task)
                st.success(f"Added '{task_title}' for {pet_choice}!")
            except ValueError as e:
                st.error(str(e))

    # Show tasks per pet with status
    for pet in owner.pets:
        if pet.tasks:
            st.markdown(f"**{pet.name}'s tasks:**")
            st.table(
                [
                    {
                        "Task": t.title,
                        "Duration": f"{t.duration_minutes} min",
                        "Priority": t.priority,
                        "Category": t.category,
                        "Time": t.scheduled_time or "—",
                        "Frequency": t.frequency,
                        "Status": "Done" if t.completed else "Pending",
                    }
                    for t in pet.tasks
                ]
            )
else:
    st.info("Add a pet first, then you can assign tasks.")

st.divider()

# ── 4. Filter tasks ─────────────────────────────────────────────────────
st.subheader("Filter Tasks")

all_tasks = owner.get_all_tasks()
if all_tasks:
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        filter_pet = st.selectbox(
            "By pet", ["All"] + [p.name for p in owner.pets], key="filter_pet"
        )
    with fc2:
        filter_status = st.selectbox(
            "By status", ["All", "Pending", "Completed"], key="filter_status"
        )
    with fc3:
        categories = sorted({t.category for t in all_tasks})
        filter_cat = st.selectbox(
            "By category", ["All"] + categories, key="filter_cat"
        )

    filtered = owner.filter_tasks(
        pet_name=filter_pet if filter_pet != "All" else None,
        completed={"All": None, "Pending": False, "Completed": True}[filter_status],
        category=filter_cat if filter_cat != "All" else None,
    )

    if filtered:
        st.caption(f"Showing {len(filtered)} of {len(all_tasks)} tasks")
        st.table(
            [
                {
                    "Pet": t.pet_name,
                    "Task": t.title,
                    "Duration": f"{t.duration_minutes} min",
                    "Priority": t.priority,
                    "Status": "Done" if t.completed else "Pending",
                }
                for t in filtered
            ]
        )
    else:
        st.info("No tasks match the selected filters.")

st.divider()

# ── 5. Generate the daily plan ───────────────────────────────────────────
st.subheader("Build Schedule")

if st.button("Generate schedule"):
    pending = owner.get_all_pending_tasks()
    if not pending:
        st.warning("No pending tasks to schedule. Add some tasks above first.")
    else:
        scheduler = Scheduler(owner)
        plan = scheduler.generate_plan()

        # Conflict warnings
        if plan.conflicts:
            for warning in plan.conflicts:
                st.warning(f"Schedule conflict: {warning}")

        st.markdown(
            f"**{owner.name}'s Daily Plan** "
            f"({plan.total_duration}/{owner.available_time_minutes} min used)"
        )

        # Scheduled tasks table
        if plan.scheduled_tasks:
            st.success(f"{len(plan.scheduled_tasks)} tasks scheduled")
            st.table(
                [
                    {
                        "#": i,
                        "Pet": t.pet_name,
                        "Task": t.title,
                        "Duration": f"{t.duration_minutes} min",
                        "Time": t.scheduled_time or "—",
                        "Priority": t.priority,
                        "Category": t.category,
                    }
                    for i, t in enumerate(plan.scheduled_tasks, 1)
                ]
            )

        # Skipped tasks
        if plan.skipped_tasks:
            st.error(f"{len(plan.skipped_tasks)} tasks skipped (not enough time)")
            for t in plan.skipped_tasks:
                st.write(f"- {t.title} — {t.duration_minutes} min ({t.priority})")

        # Sorted timeline view
        timed_tasks = [t for t in plan.scheduled_tasks if t.scheduled_time]
        if timed_tasks:
            with st.expander("Timeline view (sorted by time)"):
                for t in scheduler.sort_by_time(timed_tasks):
                    st.write(
                        f"**{t.scheduled_time}** — {t.title} [{t.pet_name}] "
                        f"({t.duration_minutes} min)"
                    )

        # Full explanation
        with st.expander("Why this plan?"):
            st.text(plan.get_explanation())

st.divider()

# ── 6. Mark tasks complete ───────────────────────────────────────────────
st.subheader("Complete a Task")

pending_tasks = owner.get_all_pending_tasks()
if pending_tasks:
    task_options = [f"{t.pet_name}: {t.title}" for t in pending_tasks]
    selected = st.selectbox("Select task to complete", task_options)

    if st.button("Mark complete"):
        pet_name, task_title = selected.split(": ", 1)
        scheduler = Scheduler(owner)
        next_task = scheduler.complete_task(pet_name, task_title)

        st.success(f"Completed '{task_title}'!")
        if next_task:
            st.info(
                f"Recurring task: next '{next_task.title}' created, "
                f"due {next_task.due_date}"
            )
else:
    st.info("No pending tasks to complete.")
