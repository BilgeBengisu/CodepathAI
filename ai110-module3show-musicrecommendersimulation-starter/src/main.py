"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


PROFILES = {
    "chill_studier": {
        "favorite_genre": "lofi",
        "favorite_mood": "focused",
        "target_energy": 0.35,
        "likes_acoustic": True,
    },
    "workout_hype": {
        "favorite_genre": "electronic",
        "favorite_mood": "intense",
        "target_energy": 0.92,
        "likes_acoustic": False,
    },
    "happy_indie_pop": {
        "favorite_genre": "indie pop",
        "favorite_mood": "happy",
        "target_energy": 0.78,
        "likes_acoustic": False,
    },
    # --- Adversarial/Edge Case Profiles ---
    "conflicting_preferences": {
        "favorite_genre": "pop",
        "favorite_mood": "sad",
        "target_energy": 0.9,
        "likes_acoustic": True,
    },
    "impossible_acoustic_energy": {
        "favorite_genre": "jazz",
        "favorite_mood": "happy",
        "target_energy": 0.1,
        "likes_acoustic": False,
    },
    "all_maximums": {
        "favorite_genre": "rock",
        "favorite_mood": "angry",
        "target_energy": 1.0,
        "likes_acoustic": False,
    },
    "all_minimums": {
        "favorite_genre": "classical",
        "favorite_mood": "calm",
        "target_energy": 0.0,
        "likes_acoustic": True,
    },
    "genre_mood_mismatch": {
        "favorite_genre": "hiphop",
        "favorite_mood": "relaxed",
        "target_energy": 0.8,
        "likes_acoustic": True,
    },
}


def main() -> None:
    import os
    # Use an absolute path to ensure the CSV is found regardless of working directory
    csv_path = os.path.join(os.path.dirname(__file__), "../data/songs.csv")
    songs = load_songs(csv_path)

    for profile_name, user_prefs in PROFILES.items():
        print(f"\n{'='*50}")
        print(f"Profile: {profile_name.replace('_', ' ').title()}")
        print(f"{'='*50}")

        recommendations = recommend_songs(user_prefs, songs, k=5)

        print("\nTop recommendations:\n")
        for rec in recommendations:
            # You decide the structure of each returned item.
            # A common pattern is: (song, score, explanation)
            song, score, explanation = rec
            print(f"{song['title']} - Score: {score:.2f}")
            print(f"Because: {explanation}")
            print()


if __name__ == "__main__":
    main()
