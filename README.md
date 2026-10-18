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

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

Output from running `python main.py`:
Today's Schedule
----------------------------------------
  [ ] 08:00  Breakfast      Mochi    high
  [ ] 09:00  Vet visit      Mochi    high
  [ ] 09:00  Litter box     Biscuit  low
  [ ] 18:00  Evening walk   Mochi    medium

Sorted by priority
----------------------------------------
  [ ] 08:00  Breakfast      Mochi    high
  [ ] 09:00  Vet visit      Mochi    high
  [ ] 18:00  Evening walk   Mochi    medium
  [ ] 09:00  Litter box     Biscuit  low

Mochi's tasks only
----------------------------------------
  [ ] 18:00  Evening walk   Mochi    medium
  [ ] 08:00  Breakfast      Mochi    high
  [ ] 09:00  Vet visit      Mochi    high

Conflicts
----------------------------------------
  ⚠ Conflict on 2026-10-18 at 09:00: Vet visit (Mochi), Litter box (Biscuit)

Completed 'Breakfast'. Next one created for 2026-10-19.

Pending tasks
----------------------------------------
  [ ] 18:00  Evening walk   Mochi    medium
  [ ] 09:00  Vet visit      Mochi    high
  [ ] 08:00  Breakfast      Mochi    high
  [ ] 09:00  Litter box     Biscuit  low










## 🧪 Testing PawPal+

Run the test suite from the project folder:

```bash
python -m pytest
```

The tests in `tests/test_pawpal.py` cover:

- **Basics:** marking a task complete, and adding a task to a pet
- **Sorting:** tasks added out of order come back in chronological order
- **Recurring tasks:** a daily task creates a new task for the next day; one-time tasks don't repeat; completing a task twice doesn't create duplicates
- **Conflict detection:** two tasks at the same date and time are flagged; the same time on different days isn't; completed tasks don't count
- **Edge cases:** a pet with no tasks gives an empty schedule without crashing

Sample test output:

```
====================================== test session starts =======================================
platform win32 -- Python 3.13.0, pytest-9.1.1, pluggy-1.7.0
rootdir: C:\Users\khang\CodePath\week 5\ai110-module2show-pawpal-starter
plugins: anyio-4.15.1
collected 10 items

tests\test_pawpal.py ..........                                                             [100%]

======================================= 10 passed in 0.05s =======================================
```

**Confidence Level:** ⭐⭐⭐⭐☆ (4/5)
All 10 tests pass, including the required sorting, recurrence and conflict tests and several edge cases. I'm not giving 5 stars because conflict detection only checks exact start times, not overlapping durations, and the Streamlit UI is only tested by hand.

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

 Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_tasks(tasks, by)` | Sorts by `"time"` (default), `"priority"` (high → low, ties broken by time), or `"duration"`. |
| Filtering | `Scheduler.filter_tasks(pet_name, completed, day)` | Filter by pet, completion status, and/or date, in any combination. |
| Conflict handling | `Scheduler.detect_conflicts()` | Warns when two or more unfinished tasks (same or different pets) share the same date and start time. Returns warnings instead of crashing. |
| Recurring tasks | `Scheduler.mark_task_complete(task)` | When a daily or weekly task is completed, creates a new one for the next day (`+1 day`) or week (`+7 days`) using `timedelta`. |


## ✨ Features

- **Multi-pet tracking:** add several pets and schedule care tasks for each one.
- **Daily schedule:** today's tasks for all pets in one plan, sorted by time.
- **Flexible sorting:** sort by time, by priority (high → low, ties broken by time), or by duration.
- **Filtering:** show tasks for one pet, hide completed tasks, or view a specific day.
- **Conflict warnings:** flags unfinished tasks booked at the same date and time, for the same pet or different pets.
- **Daily and weekly recurrence:** completing a repeating task automatically creates the next one (+1 day or +7 days).
- **Duplicate protection:** completing a task twice doesn't create extra copies.
- **Time validation:** rejects times that aren't 24-hour `HH:MM` (like `9:00` or `25:00`) with a clear error.
- **Safe editing:** `update()` only allows editable fields, so a task can't be moved to the wrong pet by accident.

Run the app with `streamlit run app.py`.

### Main UI features

- **Owner:** set the owner's name.
- **Add a Pet:** enter a name and species. Blank or duplicate names are rejected.
- **Schedule a Task:** pick a pet, then enter the task, time, duration, priority, and whether it repeats (once, daily, weekly).
- **Today's Schedule:** a summary line (tasks, done, pending), conflict warnings, and a table of today's tasks with **Sort by**, **Pet**, and **Show completed** controls.
- **Mark a Task Complete:** choose a pending task from the dropdown and click **Done**.

### Example workflow

1. Add two pets: **Mochi** (dog) and **Biscuit** (cat).
2. Schedule **Breakfast** for Mochi at 08:00, repeating **daily**, priority high.
3. Schedule **Vet visit** for Mochi at 09:00 and **Litter box** for Biscuit at 09:00.
4. Schedule **Evening walk** for Mochi at 18:00.
5. Look at **Today's Schedule**: the tasks appear in time order, and a yellow warning says Vet visit and Litter box clash at 09:00.
6. Change **Sort by** to *priority*: high-priority tasks move to the top.
7. Set **Pet** to *Biscuit*: only Litter box is shown.
8. Mark **Breakfast** as done: a green message confirms it, and the next Breakfast is scheduled for tomorrow.

### Key Scheduler behaviors shown

- **Sorting:** `Scheduler.sort_tasks()` orders tasks by time, priority, or duration.
- **Filtering:** `Scheduler.filter_tasks()` narrows by pet, completion status, and date.
- **Conflict warnings:** `Scheduler.detect_conflicts()` returns warnings, shown with `st.warning`.
- **Recurrence:** `Scheduler.mark_task_complete()` creates the next daily or weekly task.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
### Sample CLI output (`python main.py`)

```
Today's Schedule
-------------------------------------------------------
  [ ] 2026-10-18  08:00  Breakfast      Mochi    high
  [ ] 2026-10-18  09:00  Vet visit      Mochi    high
  [ ] 2026-10-18  09:00  Litter box     Biscuit  low
  [ ] 2026-10-18  18:00  Evening walk   Mochi    medium

All tasks (as added)
-------------------------------------------------------
  [ ] 2026-10-18  18:00  Evening walk   Mochi    medium
  [ ] 2026-10-18  08:00  Breakfast      Mochi    high
  [ ] 2026-10-18  09:00  Vet visit      Mochi    high
  [ ] 2026-10-18  09:00  Litter box     Biscuit  low

Sorted by time
-------------------------------------------------------
  [ ] 2026-10-18  08:00  Breakfast      Mochi    high
  [ ] 2026-10-18  09:00  Vet visit      Mochi    high
  [ ] 2026-10-18  09:00  Litter box     Biscuit  low
  [ ] 2026-10-18  18:00  Evening walk   Mochi    medium

Sorted by priority
-------------------------------------------------------
  [ ] 2026-10-18  08:00  Breakfast      Mochi    high
  [ ] 2026-10-18  09:00  Vet visit      Mochi    high
  [ ] 2026-10-18  18:00  Evening walk   Mochi    medium
  [ ] 2026-10-18  09:00  Litter box     Biscuit  low

Mochi's tasks only
-------------------------------------------------------
  [ ] 2026-10-18  18:00  Evening walk   Mochi    medium
  [ ] 2026-10-18  08:00  Breakfast      Mochi    high
  [ ] 2026-10-18  09:00  Vet visit      Mochi    high

Conflicts
-------------------------------------------------------
  ⚠ Conflict on 2026-10-18 at 09:00: Vet visit (Mochi), Litter box (Biscuit)

Completed 'Breakfast'. Next one created for 2026-10-19.

Pending tasks
-------------------------------------------------------
  [ ] 2026-10-18  18:00  Evening walk   Mochi    medium
  [ ] 2026-10-18  09:00  Vet visit      Mochi    high
  [ ] 2026-10-19  08:00  Breakfast      Mochi    high
  [ ] 2026-10-18  09:00  Litter box     Biscuit  low

Time format validation
-------------------------------------------------------
  ✗ Invalid time '9:00'. Use 24-hour HH:MM format, e.g. '09:00'.
  ✗ Invalid time '25:00'. Use 24-hour HH:MM format, e.g. '09:00'.
  ✗ Invalid time '9am'. Use 24-hour HH:MM format, e.g. '09:00'.
```

