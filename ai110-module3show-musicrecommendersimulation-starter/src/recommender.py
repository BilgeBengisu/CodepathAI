from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Returns the top k songs ranked by score for the given user profile."""
        user_dict = asdict(user)
        ranked = sorted(self.songs, key=lambda s: score_song(user_dict, asdict(s))[0], reverse=True)
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Returns a plain-language explanation of why a song was recommended."""
        user_dict = asdict(user)
        score, reasons = score_song(user_dict, asdict(song))
        return f"Score {score:.2f} — " + " | ".join(reasons)


# Experimental: Double energy, half genre
WEIGHTS = {
    "genre":    0.175,   # Halved from 0.35
    "mood":     0.25,
    "energy":   0.50,    # Doubled from 0.25
    "acoustic": 0.15,
}


def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    import csv
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Cast numeric fields from strings to the right types
            row["id"]            = int(row["id"])
            row["energy"]        = float(row["energy"])
            row["tempo_bpm"]     = float(row["tempo_bpm"])
            row["valence"]       = float(row["valence"])
            row["danceability"]  = float(row["danceability"])
            row["acousticness"]  = float(row["acousticness"])
            songs.append(row)
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences using weighted components.

    Data flow:
      user_prefs + song → four component scores × weights → total score + reasons

    Returns (score, reasons) where score is in [0.0, 1.0].
    """
    reasons = []
    total   = 0.0

    # --- Genre (binary: full credit or none) ---
    if song["genre"] == user_prefs["favorite_genre"]:
        total += WEIGHTS["genre"]
        reasons.append(f"genre matches '{song['genre']}'")

    # --- Mood (binary: full credit or none) ---
    if song["mood"] == user_prefs["favorite_mood"]:
        total += WEIGHTS["mood"]
        reasons.append(f"mood matches '{song['mood']}'")

    # --- Energy (continuous: closer to target = higher score) ---
    energy_score = 1.0 - abs(song["energy"] - user_prefs["target_energy"])
    total += WEIGHTS["energy"] * energy_score
    reasons.append(f"energy score {energy_score:.2f} (song {song['energy']} vs target {user_prefs['target_energy']})")

    # --- Acousticness (directional: likes_acoustic favors high values, else low) ---
    acoustic_score = song["acousticness"] if user_prefs["likes_acoustic"] else 1.0 - song["acousticness"]
    total += WEIGHTS["acoustic"] * acoustic_score
    reasons.append(f"acoustic fit {acoustic_score:.2f}")

    return total, reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Scores every song, ranks by score descending, returns top k.

    Data flow:
      songs list → score each → sort → slice top k → format output
    """
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = " | ".join(reasons)
        scored.append((song, score, explanation))

    # Ranking: sort by score descending, then take the top k
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]
