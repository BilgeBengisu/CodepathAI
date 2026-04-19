# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders


This project is a simple music recommender. It helps users find songs they might like. The system looks at what kind of music the user enjoys and scores each song. It then shows the best matches. The code is easy to read and change.

---
## Screenshots
![Screenshot 2026-04-18 at 10.13.43 PM](Screenshot%202026-04-18%20at%2010.13.43%E2%80%AFPM.png)
![Screenshot 2026-04-18 at 10.13.35 PM](Screenshot%202026-04-18%20at%2010.13.35%E2%80%AFPM.png)
![Screenshot 2026-04-18 at 10.13.29 PM](Screenshot%202026-04-18%20at%2010.13.29%E2%80%AFPM.png)
![Screenshot 2026-04-18 at 10.13.21 PM](Screenshot%202026-04-18%20at%2010.13.21%E2%80%AFPM.png)
![Screenshot 2026-04-18 at 10.13.11 PM](Screenshot%202026-04-18%20at%2010.13.11%E2%80%AFPM.png)
![Screenshot 2026-04-18 at 10.13.02 PM](Screenshot%202026-04-18%20at%2010.13.02%E2%80%AFPM.png)
![Screenshot 2026-04-18 at 10.12.53 PM](Screenshot%202026-04-18%20at%2010.12.53%E2%80%AFPM.png)
![Screenshot 2026-04-18 at 10.12.21 PM](Screenshot%202026-04-18%20at%2010.12.21%E2%80%AFPM.png)
![Screenshot 2026-04-15 at 11.16.06 PM](Screenshot%202026-04-15%20at%2011.16.06%E2%80%AFPM.png)

## How The System Works


**How it works:**

- Each `Song` has a genre, mood, energy, and acousticness.
- The `UserProfile` stores what genre and mood the user likes, their target energy, and if they like acoustic songs.
- The `Recommender` gives each song a score. It checks if the song matches the user's favorite genre and mood. It also checks how close the energy is and if the acoustic style fits. Each part has a weight. Genre is most important, then mood, energy, and acousticness.
- The system sorts the songs by score and shows the top ones.

| Feature | Weight |
|---------|--------|
| genre | 0.35 |
| mood | 0.25 |
| energy | 0.25 |
| acoustic | 0.15 |

### Data Flow

```
INPUT — User Preference Profile
  favorite_genre, favorite_mood, target_energy, likes_acoustic
          │
          ▼
PROCESS — score_song() runs once for every song in the catalog
  ┌─────────────────────────────────────────────────────────┐
  │  genre match?     → 1.0 or 0.0        × weight 0.35    │
  │  mood match?      → 1.0 or 0.0        × weight 0.25    │
  │  energy closeness → 1 - |song - target| × weight 0.25  │
  │  acoustic fit?    → 0.0 – 1.0         × weight 0.15    │
  │                   ─────────────────────────────────     │
  │                   total score (0.0 – 1.0)               │
  └─────────────────────────────────────────────────────────┘
          │
          ▼
OUTPUT — recommend_songs() ranks and returns top k
  all scored songs → sort by score (descending) → top k
  returns: [(song, score, explanation), ...]
```


---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried


**Experiments I tried:**

- I changed the weight for genre to see if it made a big difference. When genre had a lower weight, mood and energy mattered more.
- I tried adding tempo to the score, but it did not help much with my small song list.
- I tested with users who like different genres and moods. The system worked best for common genres like pop and lofi.

---

## Limitations and Risks


**Limitations and Risks:**

- The system only works with a small list of songs.
- It does not know about lyrics or the meaning of songs.
- It can favor popular genres and ignore rare ones.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)


**Reflection:**

I learned that recommenders use simple rules to match users and songs. Changing the weights can change the results a lot. I saw that small datasets can make the system less fair. Bias can happen if some genres or moods are missing. Real recommenders need more data and careful design to be fair.


---

## 7. `model_card_template.md`

Combines reflection and model card framing from the Module 3 guidance. :contentReference[oaicite:2]{index=2}  

```markdown
# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  **Music Matcher**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for.  

The Music Matcher suggests songs based on what the user likes. It uses a small list of songs. The user picks their favorite genre, mood, energy, and if they like acoustic songs. The system tries to find songs that match these choices.

It assumes users know what they like and can pick simple options. It also assumes there are enough songs to find a good match.


---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

The Music Matcher checks each song to see how well it matches the user's choices. It looks at genre, mood, energy, and acousticness. If a song matches the user's favorite genre or mood, it gets a higher score. Songs with the right energy or acoustic style also score higher. Genre matters most, then mood, energy, and acousticness.

I changed the weights so genre is most important. The system sorts the songs and shows the best matches at the top.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

The dataset for Music Matcher consists of 20 songs. These songs cover a range of genres, including pop, lofi, rock, ambient, jazz, synthwave, indie pop, folk, and electronic. The moods represented in the catalog include happy, chill, intense, relaxed, moody, and focused.

I added 10 songs to the original starter dataset to increase variety and better test the recommender. However, the catalog is still quite small compared to real-world music libraries, and some genres or moods may be missing or underrepresented. For example, there may not be enough songs for every possible combination of genre and mood, and certain styles like classical, metal, or world music are not included. This means the system might not work as well for users with tastes outside the catalog's main genres and moods.

---

## 5. Strengths  

The system works well for users who have clear preferences for genre and mood. If a user likes popular genres like pop or lofi, the recommendations usually make sense. The scoring does a good job matching songs with the right energy and acoustic style. When I tested it, the top songs often fit what I expected for each profile. The system is simple, so it's easy to understand why a song was recommended.

---

## 6. Limitations and Bias 


One weakness I discovered is that the system over-prioritizes songs with energy levels close to the user's target, due to the high weight on energy. This means users whose preferred energy is very low or very high may get few or no strong recommendations if the catalog doesn't have matching songs. Also, since genre and mood are binary and the dataset is small, users who like rare genres or moods are often ignored. The system tends to recommend songs from the most common genres (like pop and lofi), creating a filter bubble. As a result, users with less typical tastes or those outside the main catalog genres may not get satisfying recommendations.

---

## 7. Evaluation  

I tested the recommender with a variety of user profiles, such as "Happy Pop," "Intense Pop," "Lofi Chill," "Lofi Focused," "Acoustic Jazz," "High Energy Electronic," "Low Energy Ambient," "Folk Relaxed," and "Rock Intense." For each profile, I checked if the top songs matched the user's preferences for genre, mood, energy, and acousticness. Sometimes the same song, like "Gym Hero," appeared for both "Happy Pop" and "Intense Pop" profiles because it matches both genre and high energy. I was surprised how much the energy and mood weights changed the top results, and how users with rare preferences got weaker recommendations. Comparing profiles showed that the system is most sensitive to genre and energy, and that the dataset size limits diversity in recommendations.

---

## 8. Future Work  

I would add more features, like tempo or artist. I want to explain recommendations in more detail. I would try to make the top results more diverse. I would also add support for more complex user tastes, like people who like more than one genre or mood.

---

## 9. Personal Reflection  

I learned that recommenders use simple math to match users and items. I was surprised how much the weights changed the results. I realized that small datasets can make recommenders less fair. Now I see why real music apps need lots of data and careful design to work well.
