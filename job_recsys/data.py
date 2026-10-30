"""Read-only MEDAJob adapter. Raw files are never edited."""
from __future__ import annotations

from dataclasses import dataclass, replace
from hashlib import sha256
from pathlib import Path
import json
import re
import unicodedata

import numpy as np
import pandas as pd


def split_skills(value) -> list[str]:
    if isinstance(value, (list, tuple, set)):
        parts = value
    elif value is None or (not isinstance(value, str) and pd.isna(value)):
        return []
    else:
        text = str(value).strip()
        if not text:
            return []
        if text.startswith("["):
            try:
                parts = json.loads(text)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON skill array: {text[:80]}") from exc
            if not isinstance(parts, list):
                raise ValueError("Skills JSON must be an array")
        else:
            parts = re.split(r"[,;|\n]+", text)
    return sorted({re.sub(r"\s+", " ", unicodedata.normalize("NFC", str(x))).strip().lower()
                   for x in parts if x is not None and str(x).strip()})


def id_key(value: str):
    value = str(value)
    return (0, int(value), value) if value.isdecimal() else (1, 0, value)


@dataclass
class Dataset:
    users: pd.DataFrame
    jobs: pd.DataFrame
    ratings: pd.DataFrame
    views: pd.DataFrame
    snapshot_id: str
    quality: dict
    raw_hashes: dict

    def with_interactions(self, ratings, views):
        return replace(self, ratings=ratings.copy(), views=views.copy())


def _read(root: Path, names: tuple[str, ...], required: list[str]):
    found = [root / n for n in names if (root / n).is_file()]
    if len(found) != 1:
        raise ValueError(f"Expected exactly one of {names} under {root}, found {len(found)}")
    p = found[0]
    df = pd.read_csv(p, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    missing = set(required) - set(df.columns)
    if missing:
        raise ValueError(f"{p.name}: missing columns {sorted(missing)}")
    for col in ("id", "user_id", "job_id"):
        if col in df:
            df[col] = df[col].str.strip()
    if "id" in df and (df.id.eq("").any() or df.id.duplicated().any()):
        raise ValueError(f"{p.name}: empty or duplicate id")
    return df, {p.name: sha256(p.read_bytes()).hexdigest()}


def load_dataset(directory: str | Path) -> Dataset:
    root = Path(directory)
    specifications = {
        "users": (("users.csv",), ["id", "username"]),
        "profiles": (("user_profiles.csv",), ["user_id", "user_skills"]),
        "jobs": (("jobs.csv", "job.csv"), ["id", "job_title", "job_skills"]),
        "ratings": (("ratings.csv",), ["user_id", "job_id", "rating"]),
        "views": (("job_views.csv",), ["user_id", "job_id", "view_duration"]),
    }
    raw, hashes = {}, {}
    for name, (names, cols) in specifications.items():
        raw[name], h = _read(root, names, cols)
        hashes.update(h)
    if raw["profiles"].user_id.duplicated().any():
        raise ValueError("user_profiles.csv: duplicate user_id; no silent first-row selection")
    if raw["users"].username.duplicated().any():
        raise ValueError("users.csv: duplicate username")
    orphan_counts = {}
    for table in ("profiles", "ratings", "views"):
        orphan_counts[f"{table}_unknown_user"] = int((~raw[table].user_id.isin(raw["users"].id)).sum())
    for table in ("ratings", "views"):
        orphan_counts[f"{table}_unknown_job"] = int((~raw[table].job_id.isin(raw["jobs"].id)).sum())
    if any(orphan_counts.values()):
        raise ValueError(f"Foreign-key violations (not silently dropped): {orphan_counts}")
    users = raw["users"][["id", "username"]].rename(columns={"id": "user_id"})
    profiles = raw["profiles"][["user_id", "user_skills"]].rename(columns={"user_skills": "skills"})
    users = users.merge(profiles, on="user_id", how="left", validate="one_to_one")
    users["skills"] = users.skills.fillna("")
    users["skill_list"] = users.skills.map(split_skills)
    jobs = raw["jobs"].rename(columns={"id": "job_id", "job_title": "title", "job_skills": "skills",
                                       "job_location": "location"}).copy()
    for col in ("company_name", "location", "link", "deadline", "status"):
        if col not in jobs:
            jobs[col] = "open" if col == "status" else ""
    jobs["skill_list"] = jobs.skills.map(split_skills)
    jobs = jobs[["job_id", "title", "skills", "skill_list", "company_name", "location", "link", "status", "deadline"]]
    ratings = raw["ratings"][["user_id", "job_id", "rating"]].copy()
    ratings["rating"] = pd.to_numeric(ratings.rating, errors="coerce")
    invalid = ratings.rating.isna() | ~ratings.rating.between(1, 5)
    if invalid.any():
        raise ValueError(f"ratings.csv: {int(invalid.sum())} invalid ratings; verified website scale is 1..5")
    if ratings.duplicated(["user_id", "job_id"]).any():
        raise ValueError("Duplicate user/job ratings without reliable timestamps; resolve explicitly")
    views = raw["views"][["user_id", "job_id", "view_duration"]].copy()
    views["view_duration"] = pd.to_numeric(views.view_duration, errors="coerce")
    if not np.isfinite(views.view_duration).all() or (views.view_duration < 0).any():
        raise ValueError("job_views.csv: invalid or negative view_duration")
    # One binary exposure per pair. Repeated page openings must not dominate the signal.
    original_view_rows = len(views)
    views = views.groupby(["user_id", "job_id"], as_index=False).view_duration.sum()
    for name, frame, key in (("users", users, "user_id"), ("jobs", jobs, "job_id")):
        order = sorted(range(len(frame)), key=lambda i: id_key(frame.iloc[i][key]))
        if name == "users": users = frame.iloc[order].reset_index(drop=True)
        else: jobs = frame.iloc[order].reset_index(drop=True)
    quality = {
        "raw_counts": {n: len(d) for n, d in raw.items()},
        "users": len(users), "jobs": len(jobs), "ratings": len(ratings), "views_raw": original_view_rows,
        "view_pairs": len(views), "rating_users": ratings.user_id.nunique(), "rated_jobs": ratings.job_id.nunique(),
        "rating_distribution": {str(k): int(v) for k, v in ratings.rating.value_counts().sort_index().items()},
        "users_without_skills": int(users.skill_list.map(len).eq(0).sum()),
        "jobs_without_skills": int(jobs.skill_list.map(len).eq(0).sum()),
        "status_counts": jobs.status.value_counts().to_dict(), "foreign_key_violations": orphan_counts,
        "sparsity_all_users": 1 - len(ratings) / max(1, len(users) * len(jobs)),
        "sparsity_rating_users": 1 - len(ratings) / max(1, ratings.user_id.nunique() * len(jobs)),
        "rating_timestamps_available": False,
        "view_timestamp_unique": int(raw["views"].get("viewed_at", pd.Series(dtype=str)).nunique()),
        "skill_format": "JSON arrays and comma/semicolon/pipe-separated strings; NFC; lowercase; preserve phrases",
        "raw_columns": {n: list(d.columns) for n, d in raw.items()},
    }
    snapshot = sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest()[:16]
    return Dataset(users, jobs, ratings, views, snapshot, quality, hashes)
