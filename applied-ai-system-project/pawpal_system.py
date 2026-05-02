# logic layer where the backend classes live

from datetime import date, timedelta
from collections import defaultdict


class Task:
    def __init__(self, description: str, duration_minutes: int, frequency: str, priority: str = "medium", time: str = "00:00", due_date: date = None):
        self.description = description
        self.duration_minutes = duration_minutes
        self.frequency = frequency        # e.g. "daily", "weekly"
        self.priority = priority          # "low", "medium", "high"
        self.time = time                  # scheduled start time in "HH:MM" format (24-hour clock)
        self.due_date = due_date or date.today()  # defaults to today if not provided
        self.completed = False

    def mark_complete(self):
        """Marks the task as completed."""
        self.completed = True

    def next_occurrence(self) -> "Task":
        """Returns a new pending Task due on the next occurrence date.

        Defaults to +1 day for any unrecognised frequency so unknown values
        never silently stall the schedule.
        """
        days_ahead = {"daily": 1, "weekly": 7}.get(self.frequency, 1)
        next_due = self.due_date + timedelta(days=days_ahead)
        return Task(
            description=self.description,
            duration_minutes=self.duration_minutes,
            frequency=self.frequency,
            priority=self.priority,
            time=self.time,
            due_date=next_due,
        )

    def reset(self):
        """Resets the task back to incomplete."""
        self.completed = False

    def __repr__(self) -> str:
        """Returns a readable string showing task status, name, time, and priority."""
        status = "done" if self.completed else "pending"
        return f"[{status}] {self.description} ({self.duration_minutes} min, {self.priority} priority)"


class Pet:
    def __init__(self, name: str, species: str, age: int):
        self.name = name
        self.species = species
        self.age = age
        self.tasks: list[Task] = []

    def add_task(self, task: Task):
        """Adds a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, description: str):
        """Removes a task from this pet's list by its description."""
        self.tasks = [t for t in self.tasks if t.description != description]

    def get_pending_tasks(self) -> list[Task]:
        """Returns only tasks that have not been completed yet."""
        return [t for t in self.tasks if not t.completed]

    def get_info(self) -> str:
        """Returns a summary string of the pet's name, species, age, and task count."""
        return f"{self.name} ({self.species}, age {self.age}) — {len(self.tasks)} task(s)"


class Owner:
    def __init__(self, name: str, available_minutes: int):
        self.name = name
        self.available_minutes = available_minutes
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet):
        """Adds a pet to this owner's list of pets."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Returns all tasks across all pets as (pet, task) pairs."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]

    def get_all_pending_tasks(self) -> list[tuple[Pet, Task]]:
        """Returns all incomplete tasks across every pet the owner has."""
        return [(pet, task) for pet in self.pets for task in pet.tasks if not task.completed]

    def filter_tasks(self, status: str = None, pet_name: str = None) -> list[tuple[Pet, Task]]:
        """Filters tasks by completion status and/or pet name.
        
        Args:
            status: "completed" or "pending" (or None for all)
            pet_name: Name of the pet to filter by (or None for all pets)
        
        Returns:
            A list of (pet, task) tuples matching the filter criteria
        """
        return [
            pt for pt in self.get_all_tasks()
            if (status is None or (status == "completed") == pt[1].completed)
            and (pet_name is None or pt[0].name == pet_name)
        ]


class Scheduler:
    PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}

    def __init__(self, owner: Owner):
        self.owner = owner

    def generate_plan(self) -> list[tuple[Pet, Task]]:
        """Sorts pending tasks by priority and fits them within available time."""
        pending = self.owner.get_all_pending_tasks()
        sorted_tasks = sorted(pending, key=lambda pt: self.PRIORITY_ORDER.get(pt[1].priority, 1))

        plan = []
        time_remaining = self.owner.available_minutes
        for pet, task in sorted_tasks:
            if task.duration_minutes <= time_remaining:
                plan.append((pet, task))
                time_remaining -= task.duration_minutes

        return plan

    def explain_plan(self) -> str:
        """Returns a human-readable explanation of the generated plan."""
        plan = self.generate_plan()
        if not plan:
            return "No tasks fit within the available time."

        lines = [f"Plan for {self.owner.name} ({self.owner.available_minutes} min available):\n"]
        total = 0
        for i, (pet, task) in enumerate(plan, 1):
            lines.append(f"  {i}. [{pet.name}] {task.description} — {task.duration_minutes} min ({task.priority} priority)")
            total += task.duration_minutes

        lines.append(f"\nTotal time scheduled: {total} min")
        return "\n".join(lines)

    def mark_task_complete(self, pet: "Pet", task: "Task"):
        """Marks a task done and appends its next occurrence to the pet's task list."""
        task.mark_complete()
        pet.add_task(task.next_occurrence())

    def mark_all_complete(self):
        """Marks every task in the generated plan complete and queues next occurrences."""
        for pet, task in self.generate_plan():
            self.mark_task_complete(pet, task)

    def sort_by_time(self, tasks: list[tuple]) -> list[tuple]:
        """Returns tasks sorted chronologically by start time.

        "HH:MM" zero-padded strings sort correctly with plain string comparison.
        """
        return sorted(tasks, key=lambda pt: pt[1].time)

    def detect_conflicts(self, plan: list[tuple] = None) -> list[str]:
        """Returns a warning string for every time slot shared by more than one task.

        Returns an empty list when there are no conflicts — never raises.
        """
        if plan is None:
            plan = self.generate_plan()

        time_slots: dict[str, list] = defaultdict(list)
        for pet, task in plan:
            time_slots[task.time].append((pet, task))

        return [
            f"⚠ Conflict at {time_str} — {len(entries)} tasks overlap: "
            + ", ".join(f"{pet.name}: {task.description}" for pet, task in entries)
            for time_str, entries in time_slots.items()
            if len(entries) > 1
        ]

    def get_unscheduled_tasks(self, plan: list[tuple] = None) -> list[tuple[Pet, Task]]:
        """Returns pending tasks that didn't make it into the plan."""
        if plan is None:
            plan = self.generate_plan()
        plan_tasks = {id(task) for _, task in plan}
        return [(pet, task) for pet, task in self.owner.get_all_pending_tasks()
                if id(task) not in plan_tasks]
