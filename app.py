import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("A pet care planning assistant: track tasks for all your pets and see today's plan.")

with st.expander("Scenario", expanded=False):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.
"""
    )

# --- App memory: create the Owner once and keep it across reruns ---
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")
owner = st.session_state.owner
scheduler = Scheduler(owner)

st.divider()

# --- Owner ---
st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name)

# --- Add a pet ---
st.subheader("Add a Pet")
with st.form("add_pet_form", clear_on_submit=True):
    new_pet_name = st.text_input("Pet name")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    if st.form_submit_button("Add pet"):
        name = new_pet_name.strip()
        if not name:
            st.error("Please enter a pet name.")
        elif owner.get_pet(name):
            st.warning(f"A pet named {name} already exists.")
        else:
            owner.add_pet(Pet(name, species))
            st.success(f"Added {name}!")

if owner.pets:
    st.write("Your pets: " + ", ".join(f"{p.name} ({p.species})" for p in owner.pets))

# --- Schedule a task ---
st.subheader("Schedule a Task")
if not owner.pets:
    st.info("Add a pet first.")
else:
    with st.form("add_task_form", clear_on_submit=True):
        pet_choice = st.selectbox("Pet", [p.name for p in owner.pets])
        description = st.text_input("Task", value="Morning walk")
        task_time = st.time_input("Time")
        col1, col2, col3 = st.columns(3)
        with col1:
            duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
        with col2:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=1)
        with col3:
            frequency = st.selectbox("Repeats", ["once", "daily", "weekly"])
        if st.form_submit_button("Add task"):
            if not description.strip():
                st.error("Please enter a task description.")
            else:
                task = Task(
                    description.strip(),
                    task_time.strftime("%H:%M"),
                    frequency=frequency,
                    duration=int(duration),
                    priority=priority,
                )
                owner.get_pet(pet_choice).add_task(task)
                st.success(f"Added '{task.description}' for {pet_choice} at {task.time}.")

st.divider()

# --- Today's schedule ---
st.subheader("Today's Schedule")
schedule = scheduler.get_todays_schedule()
if schedule:
    st.table(
        [
            {
                "Time": t.time,
                "Task": t.description,
                "Pet": t.pet_name,
                "Duration (min)": t.duration,
                "Priority": t.priority,
                "Repeats": t.frequency,
                "Done": "✅" if t.completed else "",
            }
            for t in schedule
        ]
    )
else:
    st.info("No tasks scheduled for today.")
