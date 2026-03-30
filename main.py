from pawpal_system import Task, Pet, Owner, Scheduler


# --- Setup ---
owner = Owner(name="Jordan", available_minutes=90)

dog = Pet(name="Mochi", species="dog", age=3)
cat = Pet(name="Luna", species="cat", age=5)

# --- Tasks for Mochi (dog) ---
dog.add_task(Task(description="Morning walk",      duration_minutes=30, frequency="daily",  priority="high"))
dog.add_task(Task(description="Feed breakfast",    duration_minutes=10, frequency="daily",  priority="high"))
dog.add_task(Task(description="Grooming session",  duration_minutes=25, frequency="weekly", priority="low"))

# --- Tasks for Luna (cat) ---
cat.add_task(Task(description="Clean litter box",  duration_minutes=10, frequency="daily",  priority="high"))
cat.add_task(Task(description="Playtime",          duration_minutes=20, frequency="daily",  priority="medium"))

owner.add_pet(dog)
owner.add_pet(cat)

# --- Schedule ---
scheduler = Scheduler(owner)

print("=" * 45)
print("        TODAY'S SCHEDULE — PawPal+")
print("=" * 45)
print(scheduler.explain_plan())

unscheduled = scheduler.get_unscheduled_tasks()
if unscheduled:
    print("\nNot scheduled (out of time):")
    for pet, task in unscheduled:
        print(f"  - [{pet.name}] {task.description} ({task.duration_minutes} min)")
print("=" * 45)
