# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the secret number kept changing" or "the hints were backwards").

---
- Looked like a normal guessing game and I started to make guesses and view hints.
- New Game button doesn't work on win/loss
- history doesn't reset
- attempts left is off by 1

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).

--
- chatgpt
- setting the range for difficulty levels, i reviewed the code and saw it was implemented correctly now.
- it gave me repeated code instead of fixing the issue. i looked over the code and provided the tasks it needs to create in a more specific manner. It also moved UI around to fix something and I prompted again to apply fixes without changing position.

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
- Did AI help you design or understand any tests? How?

---
- I decided by reviewing over the code myself, testing on the UI and for some bugs, adding test cases to target the bug fix.
- I used test cases to check for difficulty level fix. It assured that the number range was set correctly.
- Yes, I used AI to write the test by describing the bug fix and then looked over the test case it wrote and executed it.

## 4. What did you learn about Streamlit and state?

- In your own words, explain why the secret number kept changing in the original app.
- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?
- What change did you make that finally gave the game a stable secret number?

---

- The secret number kept changing because Streamlit reruns the whole script on every interaction (typing, clicking, changing widgets). In the original version, the app generated a new random secret during each rerun, so the target moved between guesses.
- I’d explain it like this: Streamlit is like replaying the app from top to bottom every time you touch the UI. session_state is the app’s memory between those replays. Without session_state, variables reset each rerun; with it, values persist for that user session.
- The key fix was storing the secret in st.session_state and only creating it once:
if "secret" not in st.session_state: st.session_state.secret = random.randint(low, high).
After that, the secret stayed stable until explicitly reset with New Game.

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.
---
- the biggest skill was to consider writing tests and moving step by step witth each bug rather than rushing to the result. Taking step by step and absorbing each change made me learn better. I have been using AI for projects for some time and have come up with many complex applications but I do see it is much more valuable to take the process slowly so that it has more depth.