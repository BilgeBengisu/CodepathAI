# logic layer where the backend classes live


class Task:
    def __init__(self, description: str, duration_minutes: int, frequency: str, priority: str = "medium"):
        self.description = description
        self.duration_minutes = duration_minutes
        self.frequency = frequency        # e.g. "daily", "weekly"
        self.priority = priority          # "low", "medium", "high"
        self.completed = False

    def mark_complete(self):
        """Marks the task as completed."""
        self.completed = True

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
        result = []
        for pet in self.pets:
            for task in pet.tasks:
                result.append((pet, task))
        return result

    def get_all_pending_tasks(self) -> list[tuple[Pet, Task]]:
        """Returns all incomplete tasks across every pet the owner has."""
        return [(pet, task) for pet, task in self.get_all_tasks() if not task.completed]


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

    def mark_all_complete(self):
        """Marks every task in the generated plan as complete."""
        for _, task in self.generate_plan():
            task.mark_complete()

    def get_unscheduled_tasks(self) -> list[tuple[Pet, Task]]:
        """Returns pending tasks that didn't make it into the plan."""
        plan_tasks = {id(task) for _, task in self.generate_plan()}
        return [(pet, task) for pet, task in self.owner.get_all_pending_tasks()
                if id(task) not in plan_tasks]
