# Reflection on User Profile Comparisons

## Profile Pairs and Observations

### 1. Happy Pop vs. Intense Pop
- The "Gym Hero" song keeps showing up for both profiles, but it scores highest for users who want high energy and happy pop. This is because "Gym Hero" is a pop song with very high energy, so it matches both the genre and energy preferences. For users who just want "Happy Pop" but with lower energy, other songs like "Sunrise City" or "Lemon Drop Summer" may appear, but "Gym Hero" still ranks high due to its strong genre and energy match.

### 2. Lofi Chill vs. Lofi Focused
- The system recommends different lofi songs depending on the mood. "Library Rain" and "Midnight Coding" are suggested for "chill" moods, while "Focus Flow" and "Rainy Window" are picked for "focused" moods. This makes sense because the mood filter is binary—only songs with the exact mood get full points, so the top results shift when the mood changes.

### 3. Acoustic Jazz vs. Non-Acoustic Jazz
- For users who like acoustic jazz, songs like "Coffee Shop Stories" and "Sunday Afternoon" (with high acousticness) are recommended. If the user does not like acoustic, the system prefers jazz songs with lower acousticness, but since most jazz songs in the dataset are acoustic, the recommendations are similar. This shows how the acoustic preference can shift the ranking, but only if the dataset has enough variety.

### 4. High Energy Electronic vs. Low Energy Ambient
- The EDM profile (high energy, electronic) gets songs like "Electric Dreams" and "Neon Jungle" because they have high energy and match the genre. The ambient profile (low energy, ambient) gets "Spacewalk Thoughts" and "Frozen Lake"—these have low energy and high acousticness. The difference in energy and genre causes a big shift in the top results, which matches expectations.

### 5. Folk Relaxed vs. Rock Intense
- Folk relaxed users get songs like "Desert Wind" and "Mountain Echo" (folk, relaxed, mid/low energy). Rock intense users get "Storm Runner" and "Chasing Thunder" (rock, intense, high energy). This shows the system is sensitive to both genre and mood, and the energy gap helps separate profiles with different activity levels.

---

These comparisons show that the recommender is most sensitive to genre, mood, and energy. Songs like "Gym Hero" appear often for pop/high energy profiles because they fit the scoring rules. If a user's preferences are rare in the dataset, their recommendations may not be as strong or relevant.