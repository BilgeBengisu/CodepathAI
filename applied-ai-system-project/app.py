import os
import streamlit as st
from dotenv import load_dotenv
from pawpal_system import Task, Pet, Owner, Scheduler
from nutrition_advisor import DogProfile, NutritionRAG, MealAdvisor
from pathlib import Path

load_dotenv()

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

st.title("🐾 PawPal+")
st.markdown("*Your smart pet task scheduler & nutrition advisor*")

st.divider()

tab_scheduler, tab_nutrition = st.tabs(["📅 Task Scheduler", "🥗 Nutrition Advisor"])

# ── TASK SCHEDULER TAB ────────────────────────────────────────────────────────
with tab_scheduler:
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
                time=task_time.strftime("%H:%M"),
            )
            st.session_state.owner.pets[0].add_task(task)
            st.session_state.scheduler = None
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
                    if "at " in conflict:
                        try:
                            time_slot = conflict.split("at ")[1].split(" ")[0]
                            conflicted_times.add(time_slot)
                        except Exception:
                            pass

            # --- Display Scheduled Tasks ---
            st.success(f"✓ Schedule Generated for {st.session_state.owner.name}")

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

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Scheduled", f"{total_time} min")
            with col2:
                st.metric("Available", f"{st.session_state.owner.available_minutes} min")
            with col3:
                remaining = st.session_state.owner.available_minutes - total_time
                st.metric("Remaining", f"{remaining} min")

            st.markdown("---")
            conflicts = scheduler.detect_conflicts(plan)

            if conflicts:
                num_conflicts = len(conflicts)
                st.error(f"⚠️ **{num_conflicts} Scheduling Conflict{'s' if num_conflicts > 1 else ''} Detected**")

                with st.expander("🔍 View Conflict Details & Solutions", expanded=True):
                    for idx, conflict in enumerate(conflicts, 1):
                        st.markdown(f"**Conflict #{idx}:**")
                        st.error(conflict)
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

            st.markdown("---")
            st.markdown("**Plan Summary:**")
            st.info(scheduler.explain_plan())

        elif "plan" in st.session_state and not st.session_state.plan:
            st.warning("❌ No tasks fit within the available time, or no tasks have been added.")


# ── NUTRITION ADVISOR TAB ─────────────────────────────────────────────────────
with tab_nutrition:
    st.subheader("🥗 Personalized Dog Meal Advisor")
    st.markdown(
        "Enter your dog's profile and get a tailored meal plan powered by AI "
        "and a curated nutrition knowledge base."
    )

    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        st.warning("⚠️ Set the `GROQ_API_KEY` environment variable to enable AI recommendations.")

    with st.form("nutrition_form"):
        col_a, col_b = st.columns(2)
        with col_a:
            breed_input = st.text_input(
                "Dog Breed", value="Golden Retriever", placeholder="e.g. Labrador, Chihuahua"
            )
            age_input = st.number_input("Age (years)", min_value=0.1, max_value=20.0, value=3.0, step=0.5)
            weight_input = st.number_input(
                "Weight (lbs)", min_value=2.0, max_value=220.0, value=65.0, step=1.0
            )

        with col_b:
            activity_input = st.selectbox(
                "Activity Level",
                options=["low", "moderate", "high", "very_high"],
                format_func=lambda x: {
                    "low": "🛋️ Low — mostly resting",
                    "moderate": "🚶 Moderate — daily walks",
                    "high": "🏃 High — vigorous exercise",
                    "very_high": "🏅 Very High — sporting / working dog",
                }[x],
                index=1,
            )
            concerns_input = st.multiselect(
                "Dietary Concerns (optional)",
                options=[
                    "weight_management",
                    "joint_health",
                    "sensitive_stomach",
                    "coat_skin",
                    "dental_health",
                    "heart_health",
                ],
                format_func=lambda x: {
                    "weight_management": "⚖️ Weight Management",
                    "joint_health": "🦴 Joint Health",
                    "sensitive_stomach": "🍃 Sensitive Stomach / Allergies",
                    "coat_skin": "✨ Coat & Skin Health",
                    "dental_health": "🦷 Dental Health",
                    "heart_health": "❤️ Heart Health",
                }[x],
            )

        submitted = st.form_submit_button(
            "🔍 Get My Dog's Meal Plan", use_container_width=True, disabled=not api_key
        )

    if submitted and api_key:
        profile = DogProfile(
            breed=breed_input,
            age_years=age_input,
            weight_lbs=weight_input,
            activity_level=activity_input,
            dietary_concerns=concerns_input,
        )

        facts_path = Path(__file__).parent / "dog_nutrition_facts.json"
        rag = NutritionRAG(facts_path)
        advisor = MealAdvisor(rag)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Life Stage", profile.age_group.title())
        with col2:
            st.metric("Breed Size", profile.size_category.title())
        with col3:
            st.metric("Est. Daily Calories", f"~{profile.daily_calories_estimate} kcal")

        st.markdown("---")

        relevant_facts = rag.retrieve(profile)
        with st.expander("📚 Retrieved Nutrition Knowledge (RAG context)", expanded=False):
            context_md = rag.format_context(relevant_facts)
            st.text(context_md)

        with st.spinner("Generating personalized recommendation..."):
            try:
                st.caption(f"Model: `{MealAdvisor._MODEL}`")
                recommendation = advisor.advise(profile)
                st.markdown("### Your Personalized Meal Plan")
                st.markdown(recommendation)
            except Exception as e:
                st.error(f"API error: {e}")
