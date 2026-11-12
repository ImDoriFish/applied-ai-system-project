from datetime import date

import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler
from ai_assistant import ask_ai, logger

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
    species = st.selectbox("Species", ["dog", "cat", "rabbit", "guinea pig", "hamster",
                                    "fish", "bird", "reptile", "turtle", "other"])
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
# --- Ask the AI ---
st.subheader("🤖 Ask the AI")
if not owner.pets:
    st.info("Add a pet first.")
else:
    with st.form("ai_form"):
        ai_pet_name = st.selectbox("Pet", [p.name for p in owner.pets], key="ai_pet_select")
        question = st.text_area("Question", placeholder="What should my 3-month-old puppy's daily routine be?")
        if st.form_submit_button("Ask"):
            pet = owner.get_pet(ai_pet_name)
            with st.spinner("Looking up pet care notes and asking Gemini..."):
                st.session_state.ai_result = ask_ai(question, pet.name, pet.species)
            st.session_state.ai_pet = pet.name
            st.session_state.ai_round = st.session_state.get("ai_round", 0) + 1

    result = st.session_state.get("ai_result")
    if result:
        # 1. The answer (red if it's an emergency)
        if result["emergency"]:
            st.error(f"🚨 {result['answer']}")
        else:
            st.info(result["answer"])
        if result["sources"]:
            st.caption("Sources: " + ", ".join(result["sources"]))

        # 2. Suggestions our guardrails rejected
        if result["rejected"]:
            st.warning(f"{len(result['rejected'])} AI suggestion(s) were rejected by validation:")
            for reason in result["rejected"]:
                st.caption(f"✗ {reason}")

        # 3. Valid suggestions: the human edits, picks, then approves
        if result["suggestions"]:
            st.write(f"**Suggested tasks for {st.session_state.ai_pet}** "
                     "(edit anything, untick what you don't want, then approve):")
            rows = [
                {
                    "Keep": True,
                    "Time": s["task"].time,
                    "Task": s["task"].description,
                    "Repeats": s["task"].frequency,
                    "Priority": s["task"].priority,
                    "Duration (min)": s["task"].duration,
                    "Source": s["source"],
                }
                for s in result["suggestions"]
            ]
            edited = st.data_editor(
                rows,
                key=f"ai_editor_{st.session_state.ai_round}",
                hide_index=True,
                disabled=["Source"],
                column_config={
                    "Keep": st.column_config.CheckboxColumn(),
                    "Time": st.column_config.TextColumn(help="24-hour HH:MM, e.g. 07:00"),
                    "Repeats": st.column_config.SelectboxColumn(options=["once", "daily", "weekly"], required=True),
                    "Priority": st.column_config.SelectboxColumn(options=["low", "medium", "high"], required=True),
                    "Duration (min)": st.column_config.NumberColumn(min_value=1, max_value=240, step=1),
                },
            )
            kept = [row for row in edited if row["Keep"]]

            # Conflict preview, using the EDITED times
            busy_times = {t.time for t in owner.get_all_tasks()
                          if not t.completed and t.due_date == date.today()}
            kept_times = [row["Time"] for row in kept]
            for row in kept:
                if row["Time"] in busy_times:
                    st.warning(f"⚠️ {row['Task']} at {row['Time']} clashes with an existing task.")
                elif kept_times.count(row["Time"]) > 1:
                    st.warning(f"⚠️ {row['Task']} at {row['Time']} clashes with another suggestion.")

            col1, col2 = st.columns(2)
            if col1.button("✅ Approve selected"):
                new_tasks = []
                error_message = None
                for row in kept:
                    try:
                        if not str(row["Task"]).strip():
                            raise ValueError("Task name can't be empty.")
                        new_tasks.append(Task(
                            str(row["Task"]).strip(),
                            str(row["Time"]).strip(),          # validate_time() runs here
                            frequency=row["Repeats"],
                            duration=int(row["Duration (min)"]),
                            priority=row["Priority"],
                        ))
                    except (ValueError, TypeError) as error:
                        error_message = f"{row['Task']}: {error}"
                        break

                if error_message:
                    st.error(f"Please fix the table first. {error_message}")  # nothing is added
                else:
                    pet = owner.get_pet(st.session_state.ai_pet)
                    for t in new_tasks:
                        pet.add_task(t)
                    edited_count = sum(1 for before, after in zip(rows, edited)
                                       if after["Keep"] and after != before)
                    logger.info("Human approved %d of %d AI suggestions for %s (%d edited)",
                                len(new_tasks), len(rows), pet.name, edited_count)
                    st.session_state.flash = f"Added {len(new_tasks)} AI-suggested task(s) for {pet.name}."
                    del st.session_state.ai_result
                    st.rerun()
            if col2.button("Discard"):
                logger.info("Human discarded all %d AI suggestions", len(result["suggestions"]))
                del st.session_state.ai_result
                st.rerun()

st.divider()

# --- Today's schedule ---
st.subheader("Today's Schedule")

# Message saved from the last "Done" click (shown once after the page reruns)
if "flash" in st.session_state:
    st.success(st.session_state.pop("flash"))

todays = scheduler.get_todays_schedule()
done_count = len([t for t in todays if t.completed])
st.caption(f"{len(todays)} tasks today · {done_count} done · {len(todays) - done_count} pending")

# Conflict warnings come first so the owner sees them before the schedule
conflicts = scheduler.detect_conflicts()
if conflicts:
    for warning in conflicts:
        st.warning(f"⚠️ {warning}  \nConsider moving one of these tasks to a different time.")
elif todays:
    st.success("✅ No scheduling conflicts.")

# View controls: sort and filter using the Scheduler's methods
col1, col2, col3 = st.columns(3)
with col1:
    sort_by = st.selectbox("Sort by", ["time", "priority", "duration"])
with col2:
    pet_filter = st.selectbox("Pet", ["All"] + [p.name for p in owner.pets])
with col3:
    show_completed = st.checkbox("Show completed", value=True)

view = scheduler.filter_tasks(
    pet_name=None if pet_filter == "All" else pet_filter,
    completed=None if show_completed else False,
    day=date.today(),
)
view = scheduler.sort_tasks(view, by=sort_by)

if view:
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
            for t in view
        ]
    )
elif todays:
    st.info("No tasks match these filters.")
else:
    st.info("No tasks scheduled for today.")


# --- Mark a task complete ---
st.subheader("Mark a Task Complete")
pending = scheduler.sort_tasks(scheduler.filter_tasks(completed=False, day=date.today()), by="time")
if not pending:
    st.info("Nothing left to do today. 🎉" if todays else "No tasks to complete yet.")
else:
    labels = [f"{t.time}  {t.description} ({t.pet_name})" for t in pending]
    choice = st.selectbox("Task", range(len(pending)), format_func=lambda i: labels[i])
    if st.button("Done"):
        task = pending[choice]
        next_task = scheduler.mark_task_complete(task)
        message = f"✅ {task.description} for {task.pet_name} is done!"
        if next_task is not None:
            message += f" Next one scheduled for {next_task.due_date}."
        st.session_state.flash = message
        st.rerun()


# --- Remove a task ---
st.subheader("Remove a Task")
all_tasks = scheduler.sort_tasks(owner.get_all_tasks(), by="time")
if not all_tasks:
    st.info("No tasks to remove.")
else:
    remove_labels = [f"{t.due_date}  {t.time}  {t.description} ({t.pet_name})" for t in all_tasks]
    remove_choice = st.selectbox(
        "Task to remove", range(len(all_tasks)), format_func=lambda i: remove_labels[i]
    )
    if st.button("Remove"):
        task = all_tasks[remove_choice]
        owner.get_pet(task.pet_name).remove_task(task)
        st.session_state.flash = f"🗑️ Removed {task.description} for {task.pet_name}."
        st.rerun()
