import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler


def test_mark_complete_changes_status():
    task = Task(description="Morning walk", duration_minutes=30, frequency="daily")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Mochi", species="dog", age=3)
    assert len(pet.tasks) == 0
    pet.add_task(Task(description="Feed breakfast", duration_minutes=10, frequency="daily"))
    assert len(pet.tasks) == 1
    pet.add_task(Task(description="Grooming", duration_minutes=25, frequency="weekly"))
    assert len(pet.tasks) == 2


# ============================================================================
# REQUIREMENT 1: SORTING CORRECTNESS
# Verify tasks are returned in chronological order
# ============================================================================

def test_sort_by_time_single_task():
    """Single task should return as-is."""
    owner = Owner(name="Alice", available_minutes=120)
    pet = Pet(name="Mochi", species="dog", age=3)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    
    task = Task(description="Morning walk", duration_minutes=30, frequency="daily", time="09:00")
    pet.add_task(task)
    
    sorted_tasks = scheduler.sort_by_time([(pet, task)])
    assert len(sorted_tasks) == 1
    assert sorted_tasks[0][1].time == "09:00"


def test_sort_by_time_multiple_tasks_ascending_order():
    """Multiple tasks should be sorted in chronological order."""
    owner = Owner(name="Alice", available_minutes=240)
    pet = Pet(name="Mochi", species="dog", age=3)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    
    # Create tasks in non-chronological order
    task_morning = Task(description="Morning walk", duration_minutes=30, frequency="daily", time="07:00")
    task_noon = Task(description="Lunch feeding", duration_minutes=15, frequency="daily", time="12:00")
    task_evening = Task(description="Evening walk", duration_minutes=30, frequency="daily", time="18:00")
    task_night = Task(description="Bedtime treat", duration_minutes=5, frequency="daily", time="20:30")
    
    # Add in random order (not sorted)
    unsorted_tasks = [(pet, task_evening), (pet, task_morning), (pet, task_night), (pet, task_noon)]
    
    sorted_tasks = scheduler.sort_by_time(unsorted_tasks)
    
    # Verify they are in chronological order
    assert sorted_tasks[0][1].time == "07:00"  # Morning
    assert sorted_tasks[1][1].time == "12:00"  # Noon
    assert sorted_tasks[2][1].time == "18:00"  # Evening
    assert sorted_tasks[3][1].time == "20:30"  # Night


def test_sort_by_time_same_time_multiple_pets():
    """Tasks at the same time should remain grouped (tests stability)."""
    owner = Owner(name="Alice", available_minutes=120)
    pet1 = Pet(name="Mochi", species="dog", age=3)
    pet2 = Pet(name="Luna", species="cat", age=2)
    owner.add_pet(pet1)
    owner.add_pet(pet2)
    scheduler = Scheduler(owner)
    
    task1 = Task(description="Dog walk", duration_minutes=30, frequency="daily", time="08:00")
    task2 = Task(description="Cat playtime", duration_minutes=15, frequency="daily", time="08:00")
    
    unsorted_tasks = [(pet1, task1), (pet2, task2)]
    sorted_tasks = scheduler.sort_by_time(unsorted_tasks)
    
    # Both should still be at 08:00 and should maintain their order
    assert len(sorted_tasks) == 2
    assert sorted_tasks[0][1].time == "08:00"
    assert sorted_tasks[1][1].time == "08:00"


def test_sort_by_time_edge_case_midnight_and_late_night():
    """Verify midnight (00:00) and late times (23:59) sort correctly."""
    owner = Owner(name="Alice", available_minutes=120)
    pet = Pet(name="Mochi", species="dog", age=3)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    
    task_midnight = Task(description="Midnight check", duration_minutes=5, frequency="daily", time="00:00")
    task_late = Task(description="Late night care", duration_minutes=5, frequency="daily", time="23:59")
    task_noon = Task(description="Noon feeding", duration_minutes=10, frequency="daily", time="12:00")
    
    unsorted_tasks = [(pet, task_late), (pet, task_midnight), (pet, task_noon)]
    sorted_tasks = scheduler.sort_by_time(unsorted_tasks)
    
    assert sorted_tasks[0][1].time == "00:00"
    assert sorted_tasks[1][1].time == "12:00"
    assert sorted_tasks[2][1].time == "23:59"


# ============================================================================
# REQUIREMENT 2: RECURRENCE LOGIC
# Confirm that marking a daily task complete creates a new task for the following day
# ============================================================================

def test_mark_task_complete_creates_next_occurrence_daily():
    """Marking a daily task complete should create a new task for the next day."""
    owner = Owner(name="Alice", available_minutes=120)
    pet = Pet(name="Mochi", species="dog", age=3)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    
    today = date.today()
    task = Task(
        description="Morning walk",
        duration_minutes=30,
        frequency="daily",
        priority="high",
        time="07:00",
        due_date=today
    )
    pet.add_task(task)
    
    initial_count = len(pet.tasks)
    assert initial_count == 1
    
    # Mark task complete
    scheduler.mark_task_complete(pet, task)
    
    # Should now have 2 tasks: original (completed) and new one
    assert len(pet.tasks) == initial_count + 1
    assert task.completed is True
    
    # Find the new task
    new_task = [t for t in pet.tasks if not t.completed][0]
    
    # Verify new task is for the next day
    assert new_task.due_date == today + timedelta(days=1)
    assert new_task.description == task.description
    assert new_task.duration_minutes == task.duration_minutes
    assert new_task.frequency == task.frequency
    assert new_task.priority == task.priority
    assert new_task.time == task.time


def test_mark_task_complete_creates_next_occurrence_weekly():
    """Marking a weekly task complete should create a new task for the following week."""
    owner = Owner(name="Alice", available_minutes=120)
    pet = Pet(name="Mochi", species="dog", age=3)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    
    today = date.today()
    task = Task(
        description="Grooming",
        duration_minutes=60,
        frequency="weekly",
        priority="medium",
        time="10:00",
        due_date=today
    )
    pet.add_task(task)
    
    # Mark task complete
    scheduler.mark_task_complete(pet, task)
    
    # Find the new task
    new_task = [t for t in pet.tasks if not t.completed][0]
    
    # Verify new task is for 7 days later (next week)
    assert new_task.due_date == today + timedelta(days=7)
    assert new_task.description == task.description
    assert new_task.frequency == task.frequency


def test_mark_task_complete_preserves_task_properties():
    """All task properties should be preserved when creating next occurrence."""
    owner = Owner(name="Alice", available_minutes=120)
    pet = Pet(name="Mochi", species="dog", age=3)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    
    task = Task(
        description="Medication",
        duration_minutes=5,
        frequency="daily",
        priority="high",
        time="09:30",
        due_date=date.today()
    )
    pet.add_task(task)
    
    scheduler.mark_task_complete(pet, task)
    new_task = [t for t in pet.tasks if not t.completed][0]
    
    assert new_task.description == "Medication"
    assert new_task.duration_minutes == 5
    assert new_task.priority == "high"
    assert new_task.time == "09:30"


def test_mark_multiple_tasks_complete_all_recur():
    """Marking multiple tasks complete should create new occurrences for all."""
    owner = Owner(name="Alice", available_minutes=240)
    pet1 = Pet(name="Mochi", species="dog", age=3)
    pet2 = Pet(name="Luna", species="cat", age=2)
    owner.add_pet(pet1)
    owner.add_pet(pet2)
    scheduler = Scheduler(owner)
    
    today = date.today()
    task1 = Task(description="Dog walk", duration_minutes=30, frequency="daily", time="07:00", due_date=today)
    task2 = Task(description="Cat feeding", duration_minutes=10, frequency="daily", time="08:00", due_date=today)
    
    pet1.add_task(task1)
    pet2.add_task(task2)
    
    # Mark both complete
    scheduler.mark_task_complete(pet1, task1)
    scheduler.mark_task_complete(pet2, task2)
    
    # Both pets should now have new pending tasks
    pet1_pending = pet1.get_pending_tasks()
    pet2_pending = pet2.get_pending_tasks()
    
    assert len(pet1_pending) == 1
    assert len(pet2_pending) == 1
    assert pet1_pending[0].due_date == today + timedelta(days=1)
    assert pet2_pending[0].due_date == today + timedelta(days=1)


# ============================================================================
# REQUIREMENT 3: CONFLICT DETECTION
# Verify that the Scheduler flags duplicate times
# ============================================================================

def test_detect_conflicts_no_conflicts():
    """When tasks have different times, detect_conflicts should return empty list."""
    owner = Owner(name="Alice", available_minutes=120)
    pet = Pet(name="Mochi", species="dog", age=3)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    
    task1 = Task(description="Morning walk", duration_minutes=30, frequency="daily", time="07:00")
    task2 = Task(description="Evening walk", duration_minutes=30, frequency="daily", time="18:00")
    
    pet.add_task(task1)
    pet.add_task(task2)
    
    plan = [(pet, task1), (pet, task2)]
    conflicts = scheduler.detect_conflicts(plan)
    
    assert conflicts == []


def test_detect_conflicts_single_conflict_two_tasks():
    """When two tasks share the same time, detect_conflicts should flag it."""
    owner = Owner(name="Alice", available_minutes=120)
    pet = Pet(name="Mochi", species="dog", age=3)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    
    task1 = Task(description="Morning walk", duration_minutes=30, frequency="daily", time="07:00")
    task2 = Task(description="Morning feeding", duration_minutes=15, frequency="daily", time="07:00")
    
    pet.add_task(task1)
    pet.add_task(task2)
    
    plan = [(pet, task1), (pet, task2)]
    conflicts = scheduler.detect_conflicts(plan)
    
    assert len(conflicts) == 1
    assert "07:00" in conflicts[0]
    assert "2 tasks overlap" in conflicts[0]


def test_detect_conflicts_single_conflict_multiple_tasks():
    """When three tasks share the same time, detect_conflicts should flag all three."""
    owner = Owner(name="Alice", available_minutes=120)
    pet = Pet(name="Mochi", species="dog", age=3)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    
    task1 = Task(description="Walk", duration_minutes=30, frequency="daily", time="08:00")
    task2 = Task(description="Feeding", duration_minutes=15, frequency="daily", time="08:00")
    task3 = Task(description="Enrichment", duration_minutes=20, frequency="daily", time="08:00")
    
    pet.add_task(task1)
    pet.add_task(task2)
    pet.add_task(task3)
    
    plan = [(pet, task1), (pet, task2), (pet, task3)]
    conflicts = scheduler.detect_conflicts(plan)
    
    assert len(conflicts) == 1
    assert "08:00" in conflicts[0]
    assert "3 tasks overlap" in conflicts[0]


def test_detect_conflicts_multiple_conflicts():
    """When multiple time slots have conflicts, all should be flagged."""
    owner = Owner(name="Alice", available_minutes=240)
    pet1 = Pet(name="Mochi", species="dog", age=3)
    pet2 = Pet(name="Luna", species="cat", age=2)
    owner.add_pet(pet1)
    owner.add_pet(pet2)
    scheduler = Scheduler(owner)
    
    # Conflict at 07:00
    task1 = Task(description="Dog walk", duration_minutes=30, frequency="daily", time="07:00")
    task2 = Task(description="Cat feeding", duration_minutes=15, frequency="daily", time="07:00")
    
    # Conflict at 12:00
    task3 = Task(description="Dog play", duration_minutes=20, frequency="daily", time="12:00")
    task4 = Task(description="Cat play", duration_minutes=15, frequency="daily", time="12:00")
    
    pet1.add_task(task1)
    pet2.add_task(task2)
    pet1.add_task(task3)
    pet2.add_task(task4)
    
    plan = [(pet1, task1), (pet2, task2), (pet1, task3), (pet2, task4)]
    conflicts = scheduler.detect_conflicts(plan)
    
    assert len(conflicts) == 2
    assert any("07:00" in c for c in conflicts)
    assert any("12:00" in c for c in conflicts)


def test_detect_conflicts_across_multiple_pets():
    """Conflicts should be detected across different pets."""
    owner = Owner(name="Alice", available_minutes=120)
    pet1 = Pet(name="Mochi", species="dog", age=3)
    pet2 = Pet(name="Luna", species="cat", age=2)
    owner.add_pet(pet1)
    owner.add_pet(pet2)
    scheduler = Scheduler(owner)
    
    task1 = Task(description="Dog walk", duration_minutes=30, frequency="daily", time="09:00")
    task2 = Task(description="Cat feeding", duration_minutes=10, frequency="daily", time="09:00")
    
    pet1.add_task(task1)
    pet2.add_task(task2)
    
    plan = [(pet1, task1), (pet2, task2)]
    conflicts = scheduler.detect_conflicts(plan)
    
    assert len(conflicts) == 1
    assert "09:00" in conflicts[0]
    assert "Mochi: Dog walk" in conflicts[0]
    assert "Luna: Cat feeding" in conflicts[0]


def test_detect_conflicts_returns_formatted_warning_string():
    """Conflict message should be properly formatted."""
    owner = Owner(name="Alice", available_minutes=120)
    pet = Pet(name="Mochi", species="dog", age=3)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    
    task1 = Task(description="Morning walk", duration_minutes=30, frequency="daily", time="07:00")
    task2 = Task(description="Breakfast", duration_minutes=15, frequency="daily", time="07:00")
    
    pet.add_task(task1)
    pet.add_task(task2)
    
    plan = [(pet, task1), (pet, task2)]
    conflicts = scheduler.detect_conflicts(plan)
    
    assert len(conflicts) == 1
    conflict_msg = conflicts[0]
    
    # Verify format
    assert conflict_msg.startswith("⚠")
    assert "07:00" in conflict_msg
    assert "2 tasks overlap" in conflict_msg
    assert "Morning walk" in conflict_msg
    assert "Breakfast" in conflict_msg


def test_detect_conflicts_no_error_on_empty_plan():
    """detect_conflicts should handle empty plan gracefully."""
    owner = Owner(name="Alice", available_minutes=120)
    scheduler = Scheduler(owner)
    
    conflicts = scheduler.detect_conflicts([])
    assert conflicts == []


def test_detect_conflicts_edge_case_midnight():
    """Conflicts at midnight (00:00) should be detected correctly."""
    owner = Owner(name="Alice", available_minutes=120)
    pet = Pet(name="Mochi", species="dog", age=3)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    
    task1 = Task(description="Midnight check 1", duration_minutes=5, frequency="daily", time="00:00")
    task2 = Task(description="Midnight check 2", duration_minutes=5, frequency="daily", time="00:00")
    
    pet.add_task(task1)
    pet.add_task(task2)
    
    plan = [(pet, task1), (pet, task2)]
    conflicts = scheduler.detect_conflicts(plan)
    
    assert len(conflicts) == 1
    assert "00:00" in conflicts[0]
