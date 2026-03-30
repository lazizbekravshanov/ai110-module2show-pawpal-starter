# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The initial UML design uses five classes, each with a single clear responsibility:

- **Owner** (dataclass) — Holds the owner's name and their daily time budget (`available_time_minutes`). This is the primary constraint the scheduler works within.
- **Pet** (dataclass) — Stores the pet's name, species, age, and a list of special needs. Provides context so the scheduler or explanation can reference pet-specific details.
- **Task** (dataclass) — Represents one care activity with a title, duration, priority level, and category. Includes `priority_value()` to convert the priority string into a numeric weight for sorting.
- **Scheduler** (regular class) — The central engine. It receives an Owner, Pet, and list of Tasks, then `generate_plan()` sorts tasks by priority, fits them within the time budget, and returns a DailyPlan.
- **DailyPlan** (dataclass) — The output. Separates tasks into `scheduled_tasks` (what fits) and `skipped_tasks` (what didn't), and `get_explanation()` produces a human-readable rationale.

Relationships: Owner and Pet feed into Scheduler as constraints/context. Tasks are the inputs. Scheduler produces a DailyPlan, which references Tasks.

**Core user actions identified from the scenario:**

1. **Enter owner and pet info** — A user can register basic details about themselves (name, available time per day) and their pet (name, species, any special needs). This information provides the constraints the scheduler needs to build a realistic plan.

2. **Add or edit care tasks** — A user can create, modify, and remove pet care tasks such as walks, feeding, medication, enrichment, and grooming. Each task has at minimum a duration and a priority level, which feed directly into the scheduling logic.

3. **Generate a daily care plan** — A user can request a daily schedule that fits their available time. The system prioritizes tasks by importance, respects time constraints, and displays the resulting plan along with an explanation of why it chose that particular ordering (e.g., high-priority medication before optional enrichment).

**Building blocks (classes, attributes, and methods):**

1. **Owner** — Represents the pet owner and their constraints.
   - Attributes: `name` (str), `available_time_minutes` (int — total time budget per day)
   - Methods: `get_summary()` — returns a readable description of the owner's profile

2. **Pet** — Represents the pet being cared for.
   - Attributes: `name` (str), `species` (str — dog, cat, or other), `age` (int), `special_needs` (list[str] — e.g., "needs daily medication")
   - Methods: `get_summary()` — returns a readable description of the pet

3. **Task** — A single care activity that can be scheduled.
   - Attributes: `title` (str), `duration_minutes` (int), `priority` (str — low, medium, or high), `category` (str — walk, feeding, meds, enrichment, grooming)
   - Methods: `priority_value()` — converts the priority string to a numeric weight (high=3, medium=2, low=1) so the scheduler can sort and compare tasks

4. **Scheduler** — The engine that builds a plan from tasks and constraints.
   - Attributes: `owner` (Owner), `pet` (Pet), `tasks` (list[Task])
   - Methods: `generate_plan()` — sorts tasks by priority (highest first), fits them into the owner's available time budget, and returns a DailyPlan object

5. **DailyPlan** — The output schedule for a given day.
   - Attributes: `scheduled_tasks` (list[Task] — ordered tasks that fit), `skipped_tasks` (list[Task] — tasks that didn't fit in the time budget), `total_duration` (int — sum of scheduled task durations)
   - Methods: `get_explanation()` — produces a human-readable rationale for why each task was included or skipped and why they appear in that order

**b. Design changes**

Yes, two changes were made after reviewing the skeleton against the starter app and potential edge cases:

1. **Added a default value for `Task.category`** — The original UML required a category for every task, but the starter app's UI doesn't collect one. Changed `category` to default to `"general"` so tasks can be created without specifying a category, matching the existing UI contract.

2. **Added `__post_init__` validation on `Task.priority`** — The priority field accepted any string, but `priority_value()` depends on it being "low", "medium", or "high". Added a validation step that raises a `ValueError` for invalid priorities. This catches bad input at construction time rather than letting it silently produce wrong scheduling results downstream.

**c. Screenshots**

UML class diagram (rendered from Mermaid):

![UML Diagram](screenshots/uml_diagram.png)

CLI demo output (`python main.py`):

![CLI Demo Output](screenshots/main_output.png)

Pytest results (`python -m pytest tests/test_pawpal.py -v`):

![Pytest Results](screenshots/pytest_results.png)

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three constraints:

1. **Time budget** — The owner's `available_time_minutes` is the hard ceiling. Tasks are added greedily until the budget is exhausted; remaining tasks are skipped.
2. **Priority** — Tasks are sorted high → medium → low before filling the budget, so critical tasks (medication, feeding) are always scheduled before optional ones (enrichment).
3. **Duration as tiebreaker** — Within the same priority level, shorter tasks are scheduled first, maximizing the number of tasks that fit.

Priority was ranked above duration because a pet owner would rather complete one critical 30-minute task than three optional 10-minute tasks. Time budget is the ultimate constraint since it cannot be exceeded.

**b. Tradeoffs**

**Conflict detection checks for time overlap but does not resolve it.** The scheduler warns that two tasks overlap (e.g., "Morning walk 07:00-07:30 overlaps with Litter box cleanup 07:15-07:25") but still schedules both. It does not automatically shift one task.

This is reasonable because: (1) a pet owner may intentionally overlap tasks they can multitask (e.g., supervising a pet while food heats up), and (2) automatically rearranging times adds complexity and assumptions the scheduler shouldn't make — the owner is better positioned to resolve the conflict once warned.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
