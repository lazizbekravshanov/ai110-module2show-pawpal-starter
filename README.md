# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

PawPal+ includes several algorithmic features beyond basic task listing:

- **Priority-based scheduling** — Tasks are sorted high → medium → low and packed into the owner's available time budget using a greedy algorithm. Shorter tasks win ties within the same priority.
- **Time-based sorting** — Tasks with a scheduled time (HH:MM) can be sorted chronologically. Unscheduled tasks sort last.
- **Filtering** — Tasks can be filtered by pet name, completion status, or category across all pets.
- **Recurring tasks** — Daily and weekly tasks automatically generate a new occurrence (with the correct next due date) when marked complete.
- **Conflict detection** — The scheduler detects overlapping tasks based on start time and duration, and includes warnings in the daily plan without crashing or silently ignoring them.

## Testing PawPal+

Run the full test suite with:

```bash
python -m pytest tests/test_pawpal.py -v
```

The suite includes 30 tests covering:

- **Basics** — task completion, add/remove tasks, pet name tagging
- **Validation** — invalid priority, zero duration, bad frequency, malformed time
- **Sorting** — chronological ordering, priority ordering, duration tiebreaker
- **Filtering** — by pet name, completion status, category, combined filters, no-match
- **Recurring tasks** — daily/weekly next-occurrence creation, one-time returns none, Scheduler integration
- **Conflict detection** — overlapping times, exact same time, cross-pet conflicts
- **Scheduling edge cases** — pet with no tasks, all tasks exceed budget, completed tasks excluded, exact budget fill

**Confidence level: 4/5** — All happy paths and key edge cases are covered. Remaining gaps: stress testing with large task counts, and testing the Streamlit UI integration layer.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
