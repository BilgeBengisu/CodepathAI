from pawpal_system import Task, Pet, Owner, Scheduler


# --- Setup ---
owner = Owner(name="Jordan", available_minutes=90)

dog = Pet(name="Mochi", species="dog", age=3)
cat = Pet(name="Luna", species="cat", age=5)

# --- Tasks for Mochi (dog) - added OUT OF ORDER with different times ---
dog.add_task(Task(description="Evening playtime",   duration_minutes=15, frequency="daily",  priority="medium", time="18:30"))
dog.add_task(Task(description="Feed breakfast",     duration_minutes=10, frequency="daily",  priority="high", time="08:00"))
dog.add_task(Task(description="Grooming session",   duration_minutes=25, frequency="weekly", priority="low", time="15:00"))
dog.add_task(Task(description="Morning walk",       duration_minutes=30, frequency="daily",  priority="high", time="07:00"))

# --- Tasks for Luna (cat) - added OUT OF ORDER with different times ---
cat.add_task(Task(description="Dinner time",        duration_minutes=10, frequency="daily",  priority="high", time="19:00"))
cat.add_task(Task(description="Afternoon playtime", duration_minutes=20, frequency="daily",  priority="medium", time="14:00"))
cat.add_task(Task(description="Clean litter box",   duration_minutes=10, frequency="daily",  priority="high", time="09:00"))
# Intentional conflict: same time as Mochi's "Morning walk" (07:00) → should trigger a warning
cat.add_task(Task(description="Morning feeding",    duration_minutes=10, frequency="daily",  priority="high", time="07:00"))

owner.add_pet(dog)
owner.add_pet(cat)

# --- Mark some tasks as completed ---
dog.tasks[1].mark_complete()  # Feed breakfast
cat.tasks[2].mark_complete()  # Clean litter box

# --- Schedule ---
scheduler = Scheduler(owner)

print("=" * 60)
print("                  TODAY'S SCHEDULE — PawPal+")
print("=" * 60)
print(scheduler.explain_plan())

unscheduled = scheduler.get_unscheduled_tasks()
if unscheduled:
    print("\nNot scheduled (out of time):")
    for pet, task in unscheduled:
        print(f"  - [{pet.name}] {task.description} ({task.duration_minutes} min)")

# --- FILTERING DEMO ---
print("\n" + "=" * 60)
print("            FILTERING BY COMPLETION STATUS")
print("=" * 60)

print("\n✓ ALL COMPLETED TASKS:")
completed = owner.filter_tasks(status="completed")
for pet, task in completed:
    print(f"  [{pet.name}] {task.description}")

print("\n⏳ ALL PENDING TASKS:")
pending = owner.filter_tasks(status="pending")
for pet, task in pending:
    print(f"  [{pet.name}] {task.description}")

# --- FILTERING BY PET ---
print("\n" + "=" * 60)
print("            FILTERING BY PET NAME")
print("=" * 60)

print("\n🐕 MOCHI'S TASKS:")
mochi_tasks = owner.filter_tasks(pet_name="Mochi")
for pet, task in mochi_tasks:
    status = "✓" if task.completed else "⏳"
    print(f"  {status} {task.description}")

print("\n🐱 LUNA'S TASKS:")
luna_tasks = owner.filter_tasks(pet_name="Luna")
for pet, task in luna_tasks:
    status = "✓" if task.completed else "⏳"
    print(f"  {status} {task.description}")

# --- COMBINED FILTERING ---
print("\n" + "=" * 60)
print("            COMBINED FILTERING")
print("=" * 60)

print("\n🐕 MOCHI'S PENDING TASKS:")
mochi_pending = owner.filter_tasks(pet_name="Mochi", status="pending")
for pet, task in mochi_pending:
    print(f"  ⏳ {task.description}")

print("\n🐱 LUNA'S COMPLETED TASKS:")
luna_completed = owner.filter_tasks(pet_name="Luna", status="completed")
for pet, task in luna_completed:
    print(f"  ✓ {task.description}")

# --- SORTING BY TIME ---
print("\n" + "=" * 60)
print("         ALL TASKS SORTED BY TIME (Chronological)")
print("=" * 60)

all_tasks = owner.get_all_tasks()
sorted_tasks = scheduler.sort_by_time(all_tasks)
for pet, task in sorted_tasks:
    status = "✓" if task.completed else "⏳"
    print(f"  {status} {task.time} — [{pet.name}] {task.description}")

# --- CONFLICT DETECTION ---
print("\n" + "=" * 60)
print("              CONFLICT DETECTION")
print("=" * 60)

# generate_plan() builds the scheduled task list; pass it to detect_conflicts()
# so both methods work on the exact same set of tasks
plan = scheduler.generate_plan()
conflicts = scheduler.detect_conflicts(plan)

if conflicts:
    print(f"\n{len(conflicts)} conflict(s) found:")
    for warning in conflicts:
        print(f"  {warning}")
else:
    print("\nNo scheduling conflicts detected.")

print("\n" + "=" * 60)
