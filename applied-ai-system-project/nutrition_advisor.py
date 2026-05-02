import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path

from groq import Groq

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
_log = logging.getLogger("pawpal.nutrition")

_BREED_SIZE_MAP = {
    "toy": ["chihuahua", "yorkie", "yorkshire terrier", "pomeranian", "maltese", "shih tzu",
            "toy poodle", "miniature pinscher", "papillon", "italian greyhound", "affenpinscher"],
    "small": ["miniature", "dachshund", "beagle", "cocker spaniel", "pug", "french bulldog",
              "boston terrier", "cavalier", "bichon", "corgi", "scottish terrier", "west highland",
              "jack russell", "miniature schnauzer", "basenji"],
    "large": ["labrador", "golden retriever", "german shepherd", "husky", "rottweiler", "boxer",
              "doberman", "weimaraner", "dalmatian", "setter", "pointer", "airedale",
              "standard poodle", "collie", "samoyed", "chow chow", "akita"],
    "giant": ["great dane", "saint bernard", "mastiff", "newfoundland", "leonberger",
              "irish wolfhound", "greater swiss", "tibetan mastiff", "anatolian shepherd",
              "great pyrenees", "bernese mountain"],
}

_ACTIVITY_MULTIPLIERS = {
    "low": 1.2,
    "moderate": 1.6,
    "high": 2.0,
    "very_high": 2.5,
}


@dataclass
class DogProfile:
    breed: str
    age_years: float
    weight_lbs: float
    activity_level: str
    dietary_concerns: list[str] = field(default_factory=list)

    @property
    def weight_kg(self) -> float:
        return self.weight_lbs / 2.205

    @property
    def size_category(self) -> str:
        breed_lower = self.breed.lower()
        for size, keywords in _BREED_SIZE_MAP.items():
            if any(k in breed_lower for k in keywords):
                return size
        if self.weight_lbs < 12:
            return "toy"
        if self.weight_lbs < 25:
            return "small"
        if self.weight_lbs < 55:
            return "medium"
        if self.weight_lbs < 100:
            return "large"
        return "giant"

    @property
    def age_group(self) -> str:
        if self.age_years < 1:
            return "puppy"
        if self.age_years < 2:
            return "junior"
        if self.age_years < 7:
            return "adult"
        return "senior"

    @property
    def daily_calories_estimate(self) -> int:
        rer = 70 * (self.weight_kg ** 0.75)
        multiplier = _ACTIVITY_MULTIPLIERS.get(self.activity_level, 1.6)
        if self.age_group == "puppy":
            multiplier *= 2.0
        elif self.age_group == "senior":
            multiplier *= 0.8
        return int(rer * multiplier)


class NutritionRAG:
    def __init__(self, facts_path: Path):
        with open(facts_path) as f:
            self._facts: list[dict] = json.load(f)["nutrition_facts"]

    def retrieve(self, profile: DogProfile, top_k: int = 4) -> list[dict]:
        concern_tags = {c.lower().replace(" ", "_") for c in profile.dietary_concerns}
        profile_tags = {profile.size_category, profile.age_group, profile.activity_level} | concern_tags

        scored = sorted(
            self._facts,
            key=lambda f: len(profile_tags & set(f.get("tags", []))),
            reverse=True,
        )
        matched = [f for f in scored if len(profile_tags & set(f.get("tags", []))) > 0]
        results = matched[:top_k] if matched else scored[:top_k]

        confidence = self.retrieval_confidence(profile, results)
        _log.info(
            "RAG retrieve | breed=%s size=%s age=%s activity=%s concerns=%s "
            "| top_k=%d matched=%d confidence=%.2f | facts=%s",
            profile.breed, profile.size_category, profile.age_group,
            profile.activity_level, profile.dietary_concerns,
            top_k, len(matched), confidence,
            [f["id"] for f in results],
        )
        return results

    def retrieval_confidence(self, profile: DogProfile, facts: list[dict]) -> float:
        """Returns 0.0-1.0: fraction of profile tags covered by the retrieved facts."""
        concern_tags = {c.lower().replace(" ", "_") for c in profile.dietary_concerns}
        profile_tags = {profile.size_category, profile.age_group, profile.activity_level} | concern_tags
        if not profile_tags:
            return 0.0
        covered = set()
        for f in facts:
            covered |= profile_tags & set(f.get("tags", []))
        return round(len(covered) / len(profile_tags), 2)

    def format_context(self, facts: list[dict]) -> str:
        sections = ["NUTRITION KNOWLEDGE:"]
        for fact in facts:
            lines = [f"[{fact['title']}]"] + [f"• {p}" for p in fact["facts"][:3]]
            if fact.get("good_ingredients"):
                lines.append(f"Good ingredients: {', '.join(fact['good_ingredients'][:6])}")
            sections.append("\n".join(lines))
        return "\n\n".join(sections)


class MealAdvisor:
    _SYSTEM = (
        "You are a friendly, evidence-based canine nutritionist. "
        "Be concise, practical, and specific. Always connect advice to the individual dog's profile."
    )
    _MODEL = "llama-3.3-70b-versatile"

    def __init__(self, rag: NutritionRAG):
        self.rag = rag
        self._client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    def advise(self, profile: DogProfile) -> str:
        relevant_facts = self.rag.retrieve(profile)
        confidence = self.rag.retrieval_confidence(profile, relevant_facts)
        _log.info(
            "advise | breed=%s age=%.1f weight=%.1flbs activity=%s "
            "calories=%d confidence=%.2f",
            profile.breed, profile.age_years, profile.weight_lbs,
            profile.activity_level, profile.daily_calories_estimate, confidence,
        )
        context = self.rag.format_context(relevant_facts)

        concerns_str = (
            ", ".join(profile.dietary_concerns) if profile.dietary_concerns else "None specified"
        )

        prompt = f"""Using the dog profile and retrieved nutrition knowledge below, generate a personalized meal plan.

DOG PROFILE:
- Breed: {profile.breed} ({profile.size_category} breed)
- Age: {profile.age_years} year(s) — life stage: {profile.age_group}
- Weight: {profile.weight_lbs} lbs ({profile.weight_kg:.1f} kg)
- Activity Level: {profile.activity_level.replace("_", " ").title()}
- Dietary Concerns: {concerns_str}
- Estimated Daily Calories Needed: ~{profile.daily_calories_estimate} kcal/day

{context}

Respond with the following three sections exactly. Be specific, practical, and tie every recommendation back to this dog's profile.

## 🍽️ Personalized Meal Recommendation
Recommend 1-2 concrete meal options (homemade recipes or specific commercial food categories). List ingredients and brief preparation notes.

## 📏 Portion Guidance
State the daily feeding amount in cups (dry) or grams, number of meals per day, and any timing tips (e.g., post-exercise vs. pre-exercise).

## 🌿 Ingredient Spotlight
Choose 3-4 key ingredients from your recommendation. For each, write 1-2 sentences explaining WHY it benefits THIS specific dog — reference their breed size, age, activity level, or dietary concern.
"""

        try:
            response = self._client.chat.completions.create(
                model=self._MODEL,
                messages=[
                    {"role": "system", "content": self._SYSTEM},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=1024,
            )
            result = response.choices[0].message.content
            _log.info("LLM call succeeded | model=%s tokens_in_prompt=%d", self._MODEL, len(prompt))
            return result
        except Exception as exc:
            _log.error("LLM call failed | model=%s error=%s", self._MODEL, exc, exc_info=True)
            raise
