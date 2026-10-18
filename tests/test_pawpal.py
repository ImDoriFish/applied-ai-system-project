from datetime import date, timedelta

from pawpal_system import Owner, Pet, Task, Scheduler


# ---------------------------------------------------------------------------
# Helper: builds an owner with two pets and a scheduler, used by many tests
# ---------------------------------------------------------------------------
def make_scheduler():
    owner = Owner("Jordan")
    mochi = Pet("Mochi", "dog")
    biscuit = Pet("Biscuit", "cat")
    owner.add_pet(mochi)
    owner.add_pet(biscuit)
    return owner, mochi, biscuit, Scheduler(owner)


# ===========================================================================
# Phase 2 tests (basic behavior)
# ===========================================================================

# HAPPY PATH: mark_complete() flips a task from not done to done
def test_mark_complete_changes_status():
    task = Task("Walk", "09:00")
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


# HAPPY PATH: adding a task to a pet increases that pet's task count
def test_add_task_increases_pet_task_count():
    pet = Pet("Mochi", "dog")
    assert len(pet.get_tasks()) == 0

    pet.add_task(Task("Feed", "08:00"))

    assert len(pet.get_tasks()) == 1


# ===========================================================================
# Sorting
# ===========================================================================

# REQUIRED - SORTING CORRECTNESS (happy path):
# tasks added out of order come back in chronological order
def test_sort_by_time_returns_chronological_order():
    owner, mochi, biscuit, scheduler = make_scheduler()
    mochi.add_task(Task("Evening walk", "18:00"))
    mochi.add_task(Task("Breakfast", "08:00"))
    biscuit.add_task(Task("Litter box", "09:30"))

    result = scheduler.sort_tasks(owner.get_all_tasks(), by="time")

    assert [t.time for t in result] == ["08:00", "09:30", "18:00"]


# ===========================================================================
# Recurring tasks
# ===========================================================================

# REQUIRED - RECURRENCE LOGIC (happy path):
# completing a daily task creates a new, unfinished task for the next day
def test_completing_daily_task_creates_task_for_next_day():
    owner, mochi, biscuit, scheduler = make_scheduler()
    today = date(2026, 10, 18)
    breakfast = Task("Breakfast", "08:00", frequency="daily", due_date=today)
    mochi.add_task(breakfast)

    next_task = scheduler.mark_task_complete(breakfast)

    assert breakfast.completed is True
    assert next_task is not None
    assert next_task.due_date == today + timedelta(days=1)
    assert next_task.completed is False
    assert next_task in mochi.get_tasks()       # added to the same pet
    assert len(mochi.get_tasks()) == 2          # original + tomorrow's copy


# EDGE CASE: a one-time task should NOT create a new copy
def test_completing_one_time_task_creates_no_new_task():
    owner, mochi, biscuit, scheduler = make_scheduler()
    vet = Task("Vet visit", "10:00", frequency="once")
    mochi.add_task(vet)

    next_task = scheduler.mark_task_complete(vet)

    assert vet.completed is True
    assert next_task is None
    assert len(mochi.get_tasks()) == 1


# EDGE CASE: completing the same daily task twice should NOT make two copies
def test_completing_task_twice_does_not_duplicate():
    owner, mochi, biscuit, scheduler = make_scheduler()
    breakfast = Task("Breakfast", "08:00", frequency="daily")
    mochi.add_task(breakfast)

    scheduler.mark_task_complete(breakfast)
    second = scheduler.mark_task_complete(breakfast)

    assert second is None
    assert len(mochi.get_tasks()) == 2          # original + one copy, not two


# ===========================================================================
# Conflict detection
# ===========================================================================

# REQUIRED - CONFLICT DETECTION (happy path):
# two tasks at the same date and time (different pets) are flagged
def test_detect_conflicts_flags_same_time():
    owner, mochi, biscuit, scheduler = make_scheduler()
    mochi.add_task(Task("Vet visit", "09:00"))
    biscuit.add_task(Task("Litter box", "09:00"))

    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 1
    assert "09:00" in warnings[0]
    assert "Vet visit" in warnings[0]
    assert "Litter box" in warnings[0]


# EDGE CASE: same time on DIFFERENT days is not a conflict
def test_same_time_on_different_days_is_not_a_conflict():
    owner, mochi, biscuit, scheduler = make_scheduler()
    today = date(2026, 10, 18)
    mochi.add_task(Task("Breakfast", "08:00", due_date=today))
    mochi.add_task(Task("Breakfast", "08:00", due_date=today + timedelta(days=1)))

    assert scheduler.detect_conflicts() == []


# EDGE CASE: a completed task no longer counts as a conflict
def test_completed_task_is_not_a_conflict():
    owner, mochi, biscuit, scheduler = make_scheduler()
    vet = Task("Vet visit", "09:00")
    mochi.add_task(vet)
    biscuit.add_task(Task("Litter box", "09:00"))

    scheduler.mark_task_complete(vet)

    assert scheduler.detect_conflicts() == []


# ===========================================================================
# Empty data
# ===========================================================================

# EDGE CASE: a pet with no tasks gives an empty schedule and no crash
def test_pet_with_no_tasks_gives_empty_schedule():
    owner, mochi, biscuit, scheduler = make_scheduler()

    assert scheduler.get_todays_schedule() == []
    assert scheduler.filter_tasks(pet_name="Mochi") == []
    assert scheduler.detect_conflicts() == []
