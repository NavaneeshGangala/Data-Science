"""
Generate a small MovieLens-100K-shaped sample dataset.

This produces files that match the MovieLens 100K column layout exactly so the
notebook code path is identical whether the user has the real dataset or the
bundled sample. The sample is intentionally small (a few thousand ratings) but
preserves realistic structure:

  - Heavy popularity skew (Zipf-like item popularity)
  - User activity heterogeneity (most users rate a handful of items, a few rate
    many)
  - Genre-conditioned preferences so content features actually carry signal
  - Rating scale 1-5, integer

Output files (written to ./data/sample/):
  u.data        user_id\titem_id\trating\ttimestamp
  u.item        item_id|title|release|video_release|imdb|<19 genre flags>
  u.user        user_id|age|gender|occupation|zip
  u.genre       genre|id (19 genres)
  u.occupation  one per line

Run from the project root:

    python scripts/make_sample.py
"""
from __future__ import annotations

import math
import random
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = PROJECT_ROOT / "data" / "sample"

# --- Configuration -----------------------------------------------------------
# These defaults produce a ~10x-smaller-than-real dataset that runs in seconds
# but still has enough signal for the notebook's A/B comparison.
N_USERS = 600
N_ITEMS = 500
N_RATINGS_TARGET = 30_000
SEED = 7
# How strongly user genre affinity (vs raw popularity) drives an item's
# probability of being rated. Higher = more personalization signal in the data.
TASTE_WEIGHT = 4.0
POP_WEIGHT = 1.0

GENRES = [
    "unknown", "Action", "Adventure", "Animation", "Children", "Comedy",
    "Crime", "Documentary", "Drama", "Fantasy", "Film-Noir", "Horror",
    "Musical", "Mystery", "Romance", "Sci-Fi", "Thriller", "War", "Western",
]
OCCUPATIONS = [
    "administrator", "artist", "doctor", "educator", "engineer", "entertainment",
    "executive", "healthcare", "homemaker", "lawyer", "librarian", "marketing",
    "none", "other", "programmer", "retired", "salesman", "scientist",
    "student", "technician", "writer",
]

rng = np.random.default_rng(SEED)
random.seed(SEED)


def _zipf_choices(n_items: int, size: int, alpha: float = 1.15) -> np.ndarray:
    """Draw item indices with a Zipfian popularity distribution."""
    weights = 1.0 / np.power(np.arange(1, n_items + 1), alpha)
    weights /= weights.sum()
    return rng.choice(n_items, size=size, replace=True, p=weights)


def build_items() -> list[dict]:
    """Each item gets 1-3 genres + a title + a release year."""
    items = []
    for i in range(1, N_ITEMS + 1):
        n_genres = rng.choice([1, 2, 3], p=[0.5, 0.35, 0.15])
        genre_idx = rng.choice(len(GENRES), size=n_genres, replace=False)
        flags = [0] * len(GENRES)
        for g in genre_idx:
            flags[g] = 1
        year = int(rng.integers(1970, 1999))
        title = f"Movie_{i:04d} ({year})"
        items.append({
            "item_id": i,
            "title": title,
            "release": f"01-Jan-{year}",
            "video_release": "",
            "imdb": f"http://example.com/movie/{i}",
            "genres": flags,
        })
    return items


def build_users() -> list[dict]:
    """Synthesize user demographics."""
    users = []
    for u in range(1, N_USERS + 1):
        age = int(rng.integers(15, 65))
        gender = "M" if rng.random() < 0.7 else "F"
        occupation = random.choice(OCCUPATIONS)
        zipc = f"{rng.integers(10000, 99999)}"
        users.append({
            "user_id": u,
            "age": age,
            "gender": gender,
            "occupation": occupation,
            "zip": zipc,
        })
    return users


def assign_user_genre_affinity() -> np.ndarray:
    """Each user has a soft, peaky preference vector over genres."""
    # Smaller alpha => more peaked Dirichlet => users with sharper taste.
    aff = rng.dirichlet(alpha=np.ones(len(GENRES)) * 0.25, size=N_USERS)
    return aff


def build_ratings(items: list[dict], user_aff: np.ndarray) -> list[tuple]:
    """Generate (user, item, rating, ts) triples with realistic structure.

    Each (user, item) is sampled with probability proportional to
        pop(item)^POP_WEIGHT * affinity(user, item)^TASTE_WEIGHT
    so user taste -- not raw popularity -- is the dominant signal in held-out
    interactions. This is closer to the real MovieLens dynamics than a pure
    Zipfian sampler.
    """
    item_genres = np.array([it["genres"] for it in items], dtype=np.float32)  # (N_ITEMS, |G|)
    # Base item popularity follows Zipf
    pop = 1.0 / np.power(np.arange(1, N_ITEMS + 1), 1.05)
    rng.shuffle(pop)  # decouple popularity rank from item id

    # User activity: lognormal so a small fraction of users rate a lot.
    activity = np.clip(rng.lognormal(mean=3.2, sigma=0.7, size=N_USERS), 8, None)
    activity = (activity / activity.sum() * N_RATINGS_TARGET).round().astype(int)
    activity = np.clip(activity, 8, 400)

    triples = set()
    ratings: list[tuple] = []
    base_ts = 875_000_000

    for u in range(N_USERS):
        n = activity[u]
        affinity = item_genres @ user_aff[u]            # (N_ITEMS,)
        affinity = np.clip(affinity, 1e-6, None)
        probs = (pop ** POP_WEIGHT) * (affinity ** TASTE_WEIGHT)
        probs = probs / probs.sum()

        # Sample without replacement
        chosen = rng.choice(N_ITEMS, size=min(n, N_ITEMS), replace=False, p=probs)
        for item_idx in chosen:
            if (u, item_idx) in triples:
                continue
            triples.add((u, item_idx))
            aff = float(affinity[item_idx])
            mean = 3.0 + 2.5 * (aff / max(affinity.max(), 1e-6))
            score = int(np.clip(round(rng.normal(mean, 0.7)), 1, 5))
            ts = base_ts + int(rng.integers(0, 60 * 60 * 24 * 365))
            ratings.append((u + 1, item_idx + 1, score, ts))
    return ratings


def write_files(items, users, ratings):
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # u.data
    with (OUT_DIR / "u.data").open("w") as f:
        for u, i, r, t in ratings:
            f.write(f"{u}\t{i}\t{r}\t{t}\n")

    # u.item
    with (OUT_DIR / "u.item").open("w", encoding="latin-1") as f:
        for it in items:
            row = [
                str(it["item_id"]), it["title"], it["release"],
                it["video_release"], it["imdb"],
                *[str(g) for g in it["genres"]],
            ]
            f.write("|".join(row) + "\n")

    # u.user
    with (OUT_DIR / "u.user").open("w") as f:
        for u in users:
            f.write(f"{u['user_id']}|{u['age']}|{u['gender']}|{u['occupation']}|{u['zip']}\n")

    # u.genre
    with (OUT_DIR / "u.genre").open("w") as f:
        for idx, name in enumerate(GENRES):
            f.write(f"{name}|{idx}\n")

    # u.occupation
    with (OUT_DIR / "u.occupation").open("w") as f:
        for o in OCCUPATIONS:
            f.write(o + "\n")


def main() -> None:
    items = build_items()
    users = build_users()
    affinity = assign_user_genre_affinity()
    ratings = build_ratings(items, affinity)
    write_files(items, users, ratings)
    print(f"Wrote {len(ratings):,} ratings, {len(users)} users, {len(items)} items -> {OUT_DIR}")


if __name__ == "__main__":
    main()
