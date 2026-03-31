import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

st.title("🐾 PawPal+")
st.markdown("*Your smart pet task scheduler*")

st.divider()

# --- Owner & Pet Setup ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("👤 Owner & Pet Info")
    owner_name = st.text_input("Owner name", value="Jordan")
    pet_name = st.text_input("Pet name", value="Mochi")

with col2:
    st.subheader("⏱️ Available Time")
    available_minutes = st.number_input("Available minutes today", min_value=10, max_value=480, value=90)
    species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("✅ Save owner & pet", use_container_width=True):
    pet = Pet(name=pet_name, species=species, age=0)
    owner = Owner(name=owner_name, available_minutes=int(available_minutes))
    owner.add_pet(pet)
    st.session_state.owner = owner
    st.session_state.scheduler = None
    st.session_state.tasks = []
    st.success(f"✓ Saved! {owner_name} with pet {pet_name} ({species}) — {available_minutes} min available")

st.divider()

# --- Add Tasks ---
st.subheader("📋 Add a Task")

if "owner" not in st.session_state:
    st.info("👆 Save an owner & pet above before adding tasks.")
else:
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        task_title = st.text_input("Task", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
    with col3:
        task_time = st.time_input("Start time", value="08:00")
    with col4:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    with col5:
        frequency = st.selectbox("Frequency", ["daily", "weekly"])

    if st.button("➕ Add task", use_container_width=True):
        task = Task(
            description=task_title,
            duration_minutes=int(duration),
            frequency=frequency,
            priority=priority,
            time=task_time.strftime("%H:%M"),  # Convert time object to HH:MM format
        )
        st.session_state.owner.pets[0].add_task(task)
        st.session_state.scheduler = None  # Reset scheduler when tasks change
        st.success(f"✓ Added: {task} at {task_time.strftime('%H:%M')}")

    # Show current tasks in a professional table
    all_tasks = st.session_state.owner.get_all_tasks()
    if all_tasks:
        st.markdown("**Current Tasks:**")
        rows = [
            {
                "🐾": pet.name,
                "📝 Task": task.description,
                "🕐 Time": task.time,
                "⏱️ Duration (min)": task.duration_minutes,
                "⭐ Priority": task.priority.upper(),
                "🔄 Frequency": task.frequency.capitalize(),
                "✓ Status": "✅ Done" if task.completed else "⏳ Pending"
            }
            for pet, task in all_tasks
        ]
        st.table(rows)
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

# --- Generate & Display Schedule ---
st.subheader("📅 Today's Smart Schedule")

if "owner" not in st.session_state:
    st.info("👆 Save an owner & pet above to generate a schedule.")
else:
    col_gen, col_complete = st.columns(2)
    with col_gen:
        generate_btn = st.button("🚀 Generate Schedule", use_container_width=True)
    with col_complete:
        complete_all_btn = st.button("✨ Mark All Complete", use_container_width=True)

    if generate_btn:
        scheduler = Scheduler(st.session_state.owner)
        st.session_state.scheduler = scheduler
        st.session_state.plan = scheduler.generate_plan()

    if complete_all_btn and "scheduler" in st.session_state and st.session_state.scheduler:
        st.session_state.scheduler.mark_all_complete()
        st.success("✓ All tasks marked complete! Next occurrences queued.")
        st.session_state.scheduler = None
        st.rerun()

    # Display the schedule if it exists
    if "plan" in st.session_state and st.session_state.plan:
        plan = st.session_state.plan
        scheduler = st.session_state.scheduler

        # --- Check for conflicts FIRST (before displaying) ---
        conflicts = scheduler.detect_conflicts(plan)
        
        # Build conflict metadata for highlighting
        conflicted_times = set()
        if conflicts:
            for conflict in conflicts:
                # Extract time slot from conflict string (e.g., "Conflict at 14:30")
                if "at " in conflict:
                    try:
                        time_slot = conflict.split("at ")[1].split(" ")[0]
                        conflicted_times.add(time_slot)
                    except:
                        pass

        # --- Display Scheduled Tasks ---
        st.success(f"✓ Schedule Generated for {st.session_state.owner.name}")
        
        # Sort tasks chronologically and prepare display data
        sorted_tasks = scheduler.sort_by_time(plan)
        
        schedule_rows = []
        total_time = 0
        for i, (pet, task) in enumerate(sorted_tasks, 1):
            is_conflicted = task.time in conflicted_times
            conflict_badge = "🚨 CONFLICT" if is_conflicted else "✓ OK"
            
            schedule_rows.append({
                "🎯 #": i,
                "🐾": pet.name,
                "📝": task.description,
                "⏱️": f"{task.duration_minutes} min",
                "⭐": task.priority.upper(),
                "🕐": task.time if task.time else "TBD",
                "Status": conflict_badge
            })
            total_time += task.duration_minutes
        
        st.markdown("**Scheduled Tasks (sorted by time):**")
        st.markdown("*🚨 = Conflict detected | ✓ = No conflicts*")
        st.table(schedule_rows)
        
        # Show time summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Scheduled", f"{total_time} min")
        with col2:
            st.metric("Available", f"{st.session_state.owner.available_minutes} min")
        with col3:
            remaining = st.session_state.owner.available_minutes - total_time
            st.metric("Remaining", f"{remaining} min")

        # --- Display Conflicts with Detailed UX ---
        st.markdown("---")
        conflicts = scheduler.detect_conflicts(plan)
        
        if conflicts:
            # Count conflicts for summary
            num_conflicts = len(conflicts)
            st.error(f"⚠️ **{num_conflicts} Scheduling Conflict{'s' if num_conflicts > 1 else ''} Detected**")
            
            # Create an expandable section for detailed conflict info
            with st.expander("🔍 View Conflict Details & Solutions", expanded=True):
                for idx, conflict in enumerate(conflicts, 1):
                    # Parse the conflict string to extract time and task info
                    st.markdown(f"**Conflict #{idx}:**")
                    st.error(conflict)
                    
                    # Provide actionable suggestions
                    st.markdown("""
                    **Possible Solutions:**
                    - 🕐 **Reschedule**: Change the time of one task (click 'Edit' if available)
                    - ⏱️ **Shorten Task**: Reduce duration of lower-priority task(s)
                    - 🐾 **Split by Pet**: Assign tasks to different time windows per pet
                    - 📅 **Move to Tomorrow**: Mark lower-priority tasks for next day
                    """)
                    st.divider()
        else:
            st.success("✅ **No Scheduling Conflicts!** All tasks fit their assigned times.")

        # --- Display Unscheduled Tasks ---
        unscheduled = scheduler.get_unscheduled_tasks(plan)
        if unscheduled:
            st.warning("**Tasks That Didn't Fit:**")
            unscheduled_rows = [
                {
                    "🐾": pet.name,
                    "📝": task.description,
                    "⏱️": f"{task.duration_minutes} min",
                    "⭐": task.priority.upper(),
                    "📌": "Couldn't fit in time"
                }
                for pet, task in unscheduled
            ]
            st.table(unscheduled_rows)
        
        # Plan explanation
        st.markdown("---")
        st.markdown("**Plan Summary:**")
        st.info(scheduler.explain_plan())

    elif "plan" in st.session_state and not st.session_state.plan:
        st.warning("❌ No tasks fit within the available time, or no tasks have been added.")
