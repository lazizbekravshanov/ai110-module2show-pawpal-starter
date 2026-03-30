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

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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
