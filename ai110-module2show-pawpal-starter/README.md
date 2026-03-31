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

The scheduler goes beyond a basic priority sort with three additions built directly into `pawpal_system.py`:

**Scheduled start times & chronological sorting**
Every `Task` now carries a `time` field in `"HH:MM"` format. `Scheduler.sort_by_time()` orders any task list chronologically using Python's `sorted()` with a lambda key — zero-padded strings sort correctly without any datetime parsing.

**Auto-rescheduling on completion**
When `Scheduler.mark_task_complete()` is called, it marks the task done *and* calls `task.next_occurrence()` to create a fresh copy with the next due date already calculated using `timedelta`:
- `"daily"` tasks → due date + 1 day
- `"weekly"` tasks → due date + 7 days

The new task is added back to the pet automatically, so recurring care never falls off the schedule.

**Conflict detection**
`Scheduler.detect_conflicts()` scans the plan for tasks that share the exact same start time. It groups tasks by `time` using a `defaultdict`, then returns a plain-language warning string for each overlap (e.g. `⚠ Conflict at 07:00 — 2 tasks overlap: Mochi: Morning walk, Luna: Morning feeding`). It never crashes the program — an empty list means no conflicts.

---

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

---

## Testing PawPal+

### Run Tests

```bash
python -m pytest
```

### Test Coverage

The test suite verifies three core scheduling requirements:

**1. Sorting Correctness** — Tasks are returned in chronological order
- Single task returns correctly
- Multiple tasks sort in ascending time order
- Tasks at same time maintain stability across pets
- Edge cases (midnight 00:00, late night 23:59) handled properly

**2. Recurrence Logic** — Marking a daily/weekly task complete creates a new task for the next occurrence
- Daily tasks create new task for next day
- Weekly tasks create new task for 7 days later
- All task properties (description, duration, priority, time) are preserved
- Multiple pets' recurring tasks all generate correctly

**3. Conflict Detection** — The Scheduler flags duplicate times
- No conflicts detected when tasks have different times
- Single conflicts identified with proper warning format
- Multiple conflicts at same time grouped correctly
- Multiple conflict times all reported
- Cross-pet conflicts detected
- Edge case: midnight (00:00) conflicts handled

Additionally, the suite includes basic validation tests for `Task` and `Pet` classes to ensure core functionality.

### Confidence Level

⭐⭐⭐⭐ **4/5 stars**

**Reasoning:**
- ✅ All three core scheduler behaviors well-tested with 30+ test cases
- ✅ Edge cases covered (midnight, late night, multiple pets, empty plans)
- ✅ Tests verify both happy path and boundary conditions
- ⚠️ Integration testing with Streamlit UI not yet included
- ⚠️ Performance testing for very large task lists not included

The core scheduling logic is reliable. The system correctly sorts tasks, creates recurring tasks on completion, and detects scheduling conflicts. Further testing should focus on UI integration and stress-testing with edge-case data volumes.
