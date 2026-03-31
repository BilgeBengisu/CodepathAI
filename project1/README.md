# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

- [x] Describe the game's purpose.
The game's purpose is to offer a number guessing game for the user with different difficulty levels and score display at the end. The user guesses between a range of numbers and receives hints to go lower or higher based on their guess.

- [x] Detail which bugs you found.
* After a win/loss, New Game does not reset status, so the app stops.
* Attempts is initialized as 1 instead of 0, causing attempts left to be off by 1 throughout the game.
* Difficulty level ranges is not implemented correctly and the number is always between 1 and 0.
* history doesn't update in real time correctly and doesn't reset in a new game. 
* score is not being updated correctly.

- [x] Explain what fixes you applied.
* fixed broken submit flow by resetting all required session fields on New Game.
* fixed initalization to be at 0 instead of 1
* implemented logic for difficulty levels in logic_utils so that the low and high number range can be set correctly.
* History was displayed before if submit: ran, so it always lagged by one interaction.
* Updated the score logic to be correct: "Win": + (100 - 10 * attempt_number), with a floor of +10
"Too High" / "Too Low": -5 consistently

## 📸 Demo

- [x] [Insert a screenshot of your fixed, winning game here]
![alt text](<Screenshot 2026-03-05 at 3.29.56 PM.png>)

## 🚀 Stretch Features

- [ ] [If you choose to complete Challenge 4, insert a screenshot of your Enhanced Game UI here]

# CodepathAI
