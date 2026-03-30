# PawPal+ (Module 2 Project)

**PawPal+** is a Streamlit app that helps a pet owner plan daily care tasks for their pets. It considers time constraints, task priority, and scheduling conflicts to produce an optimized daily plan with clear reasoning.

## Features

- **Owner & pet management** — Register an owner with a daily time budget, add multiple pets with species, age, and special needs
- **Task management** — Create tasks with title, duration, priority (high/medium/low), category, scheduled time (HH:MM), and frequency (once/daily/weekly)
- **Priority-based scheduling** — Greedy algorithm packs highest-priority tasks first within the time budget; shorter duration breaks ties
- **Time-based sorting** — View tasks in chronological order via timeline view
- **Filtering** — Filter tasks by pet name, completion status, or category
- **Recurring tasks** — Daily and weekly tasks auto-generate the next occurrence (with correct due date) when marked complete
- **Conflict detection** — Warns when tasks overlap in time without silently ignoring them
- **Next available slot finder** — Scans the day for the earliest gap that fits a new task of a given duration
- **Data persistence** — Save/load all owner, pet, and task data to `data.json` so nothing is lost between sessions
- **Professional UI** — Emoji indicators for priority (🔴🟡🟢) and category (🚶💊🧩✂️), progress bar for time budget usage, sidebar data management
- **Plan explanation** — Every generated plan includes a rationale for what was scheduled, what was skipped, and why

## Demo

![PawPal+ App Screenshot](screenshots/app_screenshot.png)

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the app

```bash
streamlit run app.py
```

### Run the CLI demo

```bash
python main.py
```

## Testing PawPal+

```bash
python -m pytest tests/test_pawpal.py -v
```

The suite includes **39 tests** covering:

| Category | Tests | What they verify |
|---|---|---|
| Basics | 5 | task completion, add/remove, pet name tagging |
| Validation | 4 | invalid priority, zero duration, bad frequency, malformed time |
| Sorting | 3 | chronological order, priority order, duration tiebreak |
| Filtering | 5 | by pet, status, category, combined, no-match |
| Recurring | 4 | daily/weekly creation, one-time returns none, Scheduler integration |
| Conflicts | 5 | overlap, no overlap, exact same time, cross-pet, plan includes conflicts |
| Edge cases | 4 | no tasks, all exceed budget, completed excluded, exact fill |
| Next slot | 4 | empty schedule, between tasks, full schedule, after last task |
| Persistence | 3 | task round-trip, owner save/load, missing file |
| Formatting | 2 | priority emoji, category emoji |

**Confidence level: 5/5**

## Optional extensions implemented

- **Challenge 1: Next available slot** — `Scheduler.find_next_available_slot()` scans between occupied time blocks to find the earliest gap that fits a given duration. Exposed in the UI under "Find Next Available Slot."
- **Challenge 2: Data persistence** — `Owner.save_to_json()` and `Owner.load_from_json()` serialize the full object graph (Owner -> Pets -> Tasks) using custom `to_dict()`/`from_dict()` methods. The Streamlit app auto-loads on startup and saves on every mutation.
- **Challenge 4: Professional UI** — Priority-coded emojis (🔴 High, 🟡 Medium, 🟢 Low), category emojis (🚶 Walk, 💊 Meds, 🧩 Enrichment, etc.), progress bar for budget usage, and sidebar data management controls.

## Project structure

```
pawpal_system.py     — Logic layer (Owner, Pet, Task, Scheduler, DailyPlan)
app.py               — Streamlit UI with all features wired up
main.py              — CLI demo script
tests/test_pawpal.py — Automated test suite (39 tests)
uml_diagram.md       — Mermaid.js class diagram (final)
reflection.md        — Design decisions and project reflection
data.json            — Persisted session data (auto-generated)
```
