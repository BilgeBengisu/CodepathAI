import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.divider()

# --- Owner & Pet Setup ---
st.subheader("Owner & Pet Info")

owner_name = st.text_input("Owner name", value="Jordan")
available_minutes = st.number_input("Available minutes today", min_value=10, max_value=480, value=90)
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Save owner & pet"):
    pet = Pet(name=pet_name, species=species, age=0)
    owner = Owner(name=owner_name, available_minutes=int(available_minutes))
    owner.add_pet(pet)
    st.session_state.owner = owner
    st.session_state.tasks = []
    st.success(f"Saved! {owner_name} with pet {pet_name} ({species}).")

st.divider()

# --- Add Tasks ---
st.subheader("Add a Task")

if "owner" not in st.session_state:
    st.info("Save an owner & pet above before adding tasks.")
else:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        task_title = st.text_input("Task", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    with col4:
        frequency = st.selectbox("Frequency", ["daily", "weekly"])

    if st.button("Add task"):
        task = Task(
            description=task_title,
            duration_minutes=int(duration),
            frequency=frequency,
            priority=priority,
        )
        # add to the first pet
        st.session_state.owner.pets[0].add_task(task)
        st.success(f"Added: {task}")

    # Show current tasks
    all_tasks = st.session_state.owner.get_all_tasks()
    if all_tasks:
        st.markdown("**Current tasks:**")
        rows = [
            {"pet": pet.name, "task": task.description,
             "duration (min)": task.duration_minutes,
             "priority": task.priority, "frequency": task.frequency}
            for pet, task in all_tasks
        ]
        st.table(rows)
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

# --- Generate Schedule ---
st.subheader("Today's Schedule")

if "owner" not in st.session_state:
    st.info("Save an owner & pet above to generate a schedule.")
else:
    if st.button("Generate schedule"):
        scheduler = Scheduler(st.session_state.owner)
        plan = scheduler.generate_plan()

        if not plan:
            st.warning("No tasks fit within the available time, or no tasks have been added.")
        else:
            st.success(scheduler.explain_plan())

            unscheduled = scheduler.get_unscheduled_tasks()
            if unscheduled:
                st.markdown("**Not scheduled (out of time):**")
                for pet, task in unscheduled:
                    st.markdown(f"- [{pet.name}] {task.description} ({task.duration_minutes} min)")
