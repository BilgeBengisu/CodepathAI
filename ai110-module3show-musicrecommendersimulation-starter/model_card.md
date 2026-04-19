# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  **Music Matcher**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for.  

The Music Matcher suggests songs based on what the user likes. It uses a small list of songs. The user picks their favorite genre, mood, energy, and if they like acoustic songs. The system tries to find songs that match these choices.

It assumes users know what they like and can pick simple options. It also assumes there are enough songs to find a good match.

This is for classroom learning, not for real music fans. It helps show how recommenders work and how changing the rules changes the results.

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
