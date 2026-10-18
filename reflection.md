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

- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
