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

The suite includes **30 tests** covering:

| Category | Tests | What they verify |
|---|---|---|
| Basics | 5 | task completion, add/remove, pet name tagging |
| Validation | 4 | invalid priority, zero duration, bad frequency, malformed time |
| Sorting | 3 | chronological order, priority order, duration tiebreak |
| Filtering | 5 | by pet, status, category, combined, no-match |
| Recurring | 4 | daily/weekly creation, one-time returns none, Scheduler integration |
| Conflicts | 4 | overlap, no overlap, exact same time, cross-pet |
| Edge cases | 5 | no tasks, all exceed budget, completed excluded, exact fill, plan includes conflicts |

**Confidence level: 4/5**

## Project structure

```
pawpal_system.py    — Logic layer (Owner, Pet, Task, Scheduler, DailyPlan)
app.py              — Streamlit UI
main.py             — CLI demo script
tests/test_pawpal.py — Automated test suite (30 tests)
uml_diagram.md      — Mermaid.js class diagram (final)
reflection.md       — Design decisions and project reflection
```
