import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pathlib import Path
import pytest
from nutrition_advisor import DogProfile, NutritionRAG

FACTS_PATH = Path(__file__).parent.parent / "dog_nutrition_facts.json"


# ============================================================================
# DogProfile — size_category
# ============================================================================

def test_size_category_known_breed_large():
    p = DogProfile(breed="Golden Retriever", age_years=3, weight_lbs=65, activity_level="moderate")
    assert p.size_category == "large"


def test_size_category_known_breed_toy():
    p = DogProfile(breed="Chihuahua", age_years=2, weight_lbs=6, activity_level="low")
    assert p.size_category == "toy"


def test_size_category_known_breed_small():
    p = DogProfile(breed="Dachshund", age_years=4, weight_lbs=18, activity_level="moderate")
    assert p.size_category == "small"


def test_size_category_weight_fallback_toy():
    """Unknown breed under 12 lbs → toy."""
    p = DogProfile(breed="Mixed Breed", age_years=1, weight_lbs=8, activity_level="moderate")
    assert p.size_category == "toy"


def test_size_category_weight_fallback_medium():
    """Unknown breed 25-54 lbs → medium."""
    p = DogProfile(breed="Mixed Breed", age_years=3, weight_lbs=40, activity_level="moderate")
    assert p.size_category == "medium"


def test_size_category_weight_fallback_giant():
    """Unknown breed 100+ lbs → giant."""
    p = DogProfile(breed="Unknown Giant", age_years=2, weight_lbs=130, activity_level="low")
    assert p.size_category == "giant"


# ============================================================================
# DogProfile — age_group
# ============================================================================

def test_age_group_puppy():
    p = DogProfile(breed="Labrador", age_years=0.5, weight_lbs=20, activity_level="high")
    assert p.age_group == "puppy"


def test_age_group_junior():
    p = DogProfile(breed="Labrador", age_years=1.5, weight_lbs=50, activity_level="high")
    assert p.age_group == "junior"


def test_age_group_adult():
    p = DogProfile(breed="Labrador", age_years=4, weight_lbs=70, activity_level="moderate")
    assert p.age_group == "adult"


def test_age_group_senior():
    p = DogProfile(breed="Labrador", age_years=9, weight_lbs=65, activity_level="low")
    assert p.age_group == "senior"


# ============================================================================
# DogProfile — daily_calories_estimate
# ============================================================================

def test_daily_calories_positive():
    p = DogProfile(breed="Beagle", age_years=3, weight_lbs=22, activity_level="moderate")
    assert p.daily_calories_estimate > 0


def test_daily_calories_puppy_higher_than_adult():
    """Puppy multiplier (×2) should produce more calories than same dog as adult."""
    puppy = DogProfile(breed="Labrador", age_years=0.5, weight_lbs=30, activity_level="moderate")
    adult = DogProfile(breed="Labrador", age_years=3, weight_lbs=30, activity_level="moderate")
    assert puppy.daily_calories_estimate > adult.daily_calories_estimate


def test_daily_calories_senior_lower_than_adult():
    """Senior multiplier (×0.8) should produce fewer calories than the same dog as adult."""
    senior = DogProfile(breed="Labrador", age_years=9, weight_lbs=65, activity_level="moderate")
    adult = DogProfile(breed="Labrador", age_years=4, weight_lbs=65, activity_level="moderate")
    assert senior.daily_calories_estimate < adult.daily_calories_estimate


def test_daily_calories_high_activity_higher_than_low():
    """More active dogs should need more calories at the same weight."""
    active = DogProfile(breed="Husky", age_years=3, weight_lbs=55, activity_level="very_high")
    lazy = DogProfile(breed="Husky", age_years=3, weight_lbs=55, activity_level="low")
    assert active.daily_calories_estimate > lazy.daily_calories_estimate


# ============================================================================
# NutritionRAG — retrieve
# ============================================================================

def test_retrieve_returns_top_k(tmp_path):
    rag = NutritionRAG(FACTS_PATH)
    p = DogProfile(breed="Golden Retriever", age_years=3, weight_lbs=65, activity_level="moderate")
    results = rag.retrieve(p, top_k=3)
    assert len(results) <= 3


def test_retrieve_large_breed_gets_large_fact():
    """A large-breed profile should retrieve the large-breed nutrition entry."""
    rag = NutritionRAG(FACTS_PATH)
    p = DogProfile(breed="Labrador", age_years=4, weight_lbs=70, activity_level="moderate")
    ids = [f["id"] for f in rag.retrieve(p)]
    assert "large_breed_basics" in ids


def test_retrieve_joint_concern_gets_joint_fact():
    """A dog with joint_health concern should retrieve the joint-health entry."""
    rag = NutritionRAG(FACTS_PATH)
    p = DogProfile(
        breed="Golden Retriever", age_years=9, weight_lbs=70,
        activity_level="low", dietary_concerns=["joint_health"]
    )
    ids = [f["id"] for f in rag.retrieve(p)]
    assert any("joint" in fid for fid in ids)


def test_retrieve_senior_dog_gets_senior_fact():
    """A senior dog should retrieve a senior-specific fact entry."""
    rag = NutritionRAG(FACTS_PATH)
    p = DogProfile(breed="Labrador", age_years=9, weight_lbs=65, activity_level="low")
    ids = [f["id"] for f in rag.retrieve(p)]
    assert any("senior" in fid for fid in ids)


def test_retrieve_never_returns_empty():
    """retrieve() should always return at least one fact."""
    rag = NutritionRAG(FACTS_PATH)
    p = DogProfile(breed="Unknown Alien Dog", age_years=3, weight_lbs=40, activity_level="moderate")
    results = rag.retrieve(p)
    assert len(results) >= 1


# ============================================================================
# NutritionRAG — retrieval_confidence
# ============================================================================

def test_confidence_between_zero_and_one():
    rag = NutritionRAG(FACTS_PATH)
    p = DogProfile(breed="Golden Retriever", age_years=4, weight_lbs=65, activity_level="moderate")
    facts = rag.retrieve(p)
    score = rag.retrieval_confidence(p, facts)
    assert 0.0 <= score <= 1.0


def test_confidence_higher_with_more_matched_concerns():
    """Profile with matching concerns should have higher confidence than profile without."""
    rag = NutritionRAG(FACTS_PATH)
    p_with = DogProfile(
        breed="Golden Retriever", age_years=9, weight_lbs=70,
        activity_level="low", dietary_concerns=["joint_health"]
    )
    p_without = DogProfile(
        breed="Golden Retriever", age_years=9, weight_lbs=70, activity_level="low"
    )
    facts_with = rag.retrieve(p_with)
    facts_without = rag.retrieve(p_without)
    score_with = rag.retrieval_confidence(p_with, facts_with)
    score_without = rag.retrieval_confidence(p_without, facts_without)
    assert score_with >= score_without


def test_confidence_zero_on_empty_facts():
    rag = NutritionRAG(FACTS_PATH)
    p = DogProfile(breed="Labrador", age_years=3, weight_lbs=65, activity_level="moderate")
    score = rag.retrieval_confidence(p, [])
    assert score == 0.0
