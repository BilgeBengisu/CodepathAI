# PawPal+ Project Reflection

## 1. System Design
the user should be able to add a pet with name and pet tasks.
the user should be able to able to enter constraints such as available time, priority, owner preferences.
the user should be able to display the tasks of the day.

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
I used four classes: Owner, Pet, CareTask, and Scheduler
Owner owns Pet; Scheduler has Owner and manages CareTask.
the Pet has get_info responsibility. CareTask has task information. Scheduler has the responsiblity to add tasks, generate a plan to carry out the tasks as well as to explain the plan.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes, the CareTask had no link to pet. Scheduler never uses Pet directly.
The pet is buried inside Owner (owner.pet). When generate_plan() needs to check pet-specific constraints (e.g. a cat doesn't need walks, a senior dog needs shorter sessions), it has to do self.owner.pet.species — that's a Law of Demeter violation. Switched to direct reference.
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

`detect_conflicts()` flags a conflict only when two tasks share the **exact same start time** (`task.time`). It does not check whether one task's duration causes it to *run into* another task's start time. For example, a 30-minute walk at 07:00 and a feeding at 07:20 are treated as conflict-free, even though the walk is still in progress when the feeding is supposed to begin.

This is a reasonable tradeoff for a pet scheduling app at this scale because:
1. **Simplicity** — comparing two `"HH:MM"` strings is O(1) per task pair. Overlap detection would require converting every time to minutes and checking whether `[start, start + duration]` intervals intersect, which adds complexity without much benefit for a small daily task list.
2. **Owner flexibility** — pet care tasks rarely need to be back-to-back. A 10-minute buffer between a walk and a feeding is realistic; the owner naturally knows the walk must finish before feeding starts.
3. **Good enough for the problem** — the scheduler's primary job is to fit tasks within a daily time budget, not to produce a minute-by-minute timeline. Exact-time conflict detection catches the most obvious mistake (scheduling two things at literally the same moment) without over-engineering the solution.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?
I find the brainstorming and the uml diagram generation very helpful as they tend to be the steps that I used to do alone. Debugging is also a big help because it can just find the place to correct and show it for review.
**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?
It suggested to have no relationship between owner and pet and I prompted it to fix it, after brainstorming and reasoning why there should be a relationship between them.
---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?
I tested adding pet, owner, and tasks, as well as tested edge cases such as conflicting times. The tests were important to be able to easily check if everything is functioning even after adding or refactoring code.
However the confliction test passed not because the test was flawed but because the times were always entered as 00:00 by default and that had to be fixed on the UI end.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?
I am confident that it does its basic functionality as I tested the functions via code and the UI manually.
I would keep testing the connections between functions that rely on each other. i think functions individually then to work fine but as they start relying on each other and the logic gets more complicated, crashes happen.
---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
I am satisfied with the thinking I was encouraged to do on my end. I think it is very easy to want to put everything on AI but I was motivated to be an active thinker in the process andtreat ai as a tool.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
I would improve the UI and come with some more creative design decisions.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
It is important to make system decisions before starting to build and to come back to check if those decisons remain correct. I also learn to build functions step-by-step rather than asking ai for a complete feature right off the bat.
