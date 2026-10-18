# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
My initial UML design has four classes: Task, Pet, Owner and Scheduler. They connect in a chain: an Owner has many Pets, and each Pet has many Tasks. The Scheduler sits on top and uses the Owner to reach all tasks across every pet
- What classes did you include, and what responsibilities did you assign to each?

- Scheduler: The “brain” of the app. It gets all tasks through the Owner and organizes them by sorting, filtering, detecting conflicts and handling recurring tasks. It’s the only class with real scheduling logic. The other three mainly hold data.

- Owner: Represents the person using the app. It stores the owner’s name and their pets, and it can add a pet and return every task from all pets in one list.

- Pet: Represents one pet. It stores the pet’s name, species and its list of tasks, and it can add a task to that list.

- Task: Represents one care activity, such as a feeding, walk or medication. It stores a description, time, frequency and completion status, and it can mark itself complete.

**b. Design changes**

- Did your design change during implementation?
Yes

- If yes, describe at least one change and why you made it.
1) Redesigned filtering and sorting (my idea). Instead of separate methods for each kind of filter or sort, I used one filter_tasks(pet_name, completed, day) that can combine filters and one sort_tasks(tasks, by) that can sort by time, priority or duration. I kept get_todays_schedule() as a shortcut that filters by today and then sorts by time.
2) Added pet_name to Task (from the AI review). In my first design, a task didn’t know which pet it belonged to. Once Owner.get_all_tasks() merges every pet’s tasks into one list, the scheduler couldn’t filter by pet or show which pet a task was for. I considered returning (pet_name, task) tuples instead, but chose to store pet_name on the task so every Scheduler method could work with plain Task objects. Pet.add_task() sets it automatically.
3) Added Owner.get_pet() for easier lookup.
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
My scheduler mainly looks at the time of each task. It sorts tasks by their start time so the daily plan shows what needs to happen first, and it warns me if two unfinished tasks are at the same time. It also uses the due date so the daily schedule only shows today’s tasks, and so daily or weekly tasks get created again after I complete them. Other things it considers are priority, completion status, and which pet the task is for.
- How did you decide which constraints mattered most?
I decided time mattered the most because pet care is very time-based. Feeding or giving medication needs to happen at a certain time, so the default schedule is sorted by time. Priority is more of a second option for when the day gets busy. I kept the scheduler simple, so it doesn’t try to fit tasks into how much free time the owner has or follow owner preferences. Those would be good features to add next.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
One tradeoff I made is that the conflict detection only checks if two tasks have the exact same start time. It does not check their duration, so for example if I have a 60-minute vet appointment at 9:00 and another task at 9:30, the system would not detect that as a conflict even though they overlap. 
- Why is that tradeoff reasonable for this scenario?
I think this is reasonable for this project because most pet care tasks like feeding, walking, or giving medication are usually pretty short. Checking only the exact time also keeps the logic simple and easy to understand instead of having to compare every task with every other task.
---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
I used Claude as my AI assistant for plan out my approach. I asked it to explain things I didn’t understand like, dataclasses, what the imports do, lambda, and timedelta. I also used it to review my class skeleton, write method code, draft tests, and check that everything ran.
- What kinds of prompts or questions were most helpful?
The most helpful prompts were when I questioned its design instead of just accepting it. For example, I asked why we needed both filter_tasks and get_todays_schedule if filtering can already do it, and why get_pet was needed if I can just access the pet. Those questions helped me understand how the classes connect and made the design simpler.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
One AI suggestion I changed was the update() method. The AI first wrote it with **changes, which I thought was too advanced, so I changed it to update(field_name, value). Then it used hasattr and setattr, which was shorter but harder to understand and allowed any field to be changed, even pet_name, which could put a task under the wrong pet. I rewrote it with explicit if/elif branches so I control which fields can change. Later I also removed the “completed” option, because completing a daily task through update() would skip creating tomorrow’s copy.

Another time, I asked the AI to simplify detect_conflicts(). It gave a shorter “Pythonic” version with defaultdict and a list comprehension, but the speed was the same, so I kept my version because it’s easier to read and debug.
- How did you evaluate or verify what the AI suggested?
To verify suggestions, I ran main.py to see the output in the terminal, tested the app in the browser, and ran python -m pytest.
---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
I have 10 tests. They check that marking a task complete works, adding a task to a pet increases the count, tasks get sorted in time order, completing a daily task creates a new task for the next day, and two tasks at the same time get flagged as a conflict. I also tested edge cases: a one-time task doesn’t repeat, completing a task twice doesn’t make duplicates, the same time on different days isn’t a conflict, a completed task isn’t a conflict, and a pet with no tasks gives an empty schedule without crashing.
- Why were these tests important?
These tests were important because sorting, recurring tasks, and conflicts are the “smart” parts of the app, and the edge cases are where bugs usually hide. For example, without the “completing twice” test, clicking Done twice could create two copies for tomorrow.
**b. Confidence**

- How confident are you that your scheduler works correctly?
I’m about 4 out of 5 confident. All 10 tests pass and the app works when I use it. I’m not at 5 because conflict detection only checks exact times, not overlapping durations, and I only tested the Streamlit UI by hand.
- What edge cases would you test next if you had more time?
If I had more time, I would test overlapping tasks, weekly recurrence, a daily task at the end of the month (like Oct 31 to Nov 1), sorting by priority with ties, filtering with multiple filters at once, and invalid times through update().
---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
I’m most satisfied with how the Scheduler works with the Owner. Every method goes through Owner.get_all_tasks(), so it works for any number of pets. I’m also happy that I questioned the AI’s design a lot, because it made me actually understand my approach.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
I would add overlap-aware conflict detection using each task’s duration, and save the data to a JSON file so pets and tasks don’t disappear when the page refreshes. I would also let the app support more than one owner, and add a way to edit or delete tasks from the UI.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
The most important thing I learned is that being the “lead architect” means I make the final decisions, not the AI. The AI can write code fast, but it sometimes suggests things that are too complicated, overlaps with other methods, or edits files I didn’t ask it to. I learned to ask why, check where its claims come from, and only accept changes I understand and can explain.

## 6. Implementation Summary
Task: one care activity (description, time, frequency, duration, priority, due date, completion status).
Pet: a pet and its list of tasks. Adding a task stamps it with the pet’s name.
Owner: the owner’s pets. get_all_tasks() returns every pet’s tasks in one list.
Scheduler: the “brain.” It reads tasks through Owner.get_all_tasks(), then filters, sorts, detects conflicts and creates the next copy of recurring tasks.
Task, Pet and Owner only store data, while Scheduler holds all the scheduling logic. Because the Scheduler always goes through the Owner, it works across every pet, not just one.
    filter_tasks() keeps tasks matching any combination of pet name, completion status and day.
    sort_tasks() orders tasks by time, priority (ties broken by time) or duration.
    get_todays_schedule() combines the two: today’s tasks, sorted by time.
    detect_conflicts() returns warning messages when unfinished tasks share the same date and time.
    mark_task_complete() completes a task. For daily or weekly tasks, it creates a new task for the next date and adds it to the same pet.