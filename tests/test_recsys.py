from dataclasses import replace
import json

import numpy as np
import pandas as pd
import pytest

from job_recsys.data import Dataset, load_dataset, split_skills
from job_recsys.models import ALGORITHMS, Config, RecommenderSuite, content_scores
from job_recsys.evaluation import compare_rankings, compare_website, positive_holdout, ranking_metrics


@pytest.fixture
def tiny():
    users = pd.DataFrame({"user_id": ["01", "02", "03", "04"], "username": ["u1", "u2", "u3", "new"],
                          "skills": ["python, sql", "python, git", "java", ""]})
    jobs = pd.DataFrame({"job_id": ["001", "002", "003", "004", "005", "006"],
                         "title": ["Python", "Data", "Java", "DevOps", "Cold", "Closed"],
                         "skills": ["python", "sql", "java", "git", "python, sql", "python"],
                         "company_name": ["Example"] * 6, "status": ["open"] * 5 + ["closed"]})
    users["skill_list"] = users.skills.map(split_skills); jobs["skill_list"] = jobs.skills.map(split_skills)
    ratings = pd.DataFrame([("01", "001", 5), ("01", "002", 4), ("01", "003", 1),
                            ("02", "001", 4), ("02", "002", 5), ("02", "004", 4),
                            ("03", "001", 2), ("03", "003", 5), ("03", "004", 3)],
                           columns=["user_id", "job_id", "rating"])
    views = pd.DataFrame([("01", "003", 10), ("01", "004", 20), ("02", "002", 20)],
                         columns=["user_id", "job_id", "view_duration"])
    return Dataset(users, jobs, ratings, views, "synthetic_test_only", {}, {})


@pytest.fixture
def fast():
    return Config(factors=3, sgd_epochs=3, als_explicit_epochs=3, als_implicit_epochs=3)


@pytest.mark.parametrize("value,expected", [
    ('["Python", "SQL", "machine learning"]', ["machine learning", "python", "sql"]),
    ("python; SQL|spring boot, python", ["python", "spring boot", "sql"]),
    (["C++", "c#", "rest api"], ["c#", "c++", "rest api"]),
    (None, []), (float("nan"), []), ("", []),
])
def test_skills(value, expected):
    assert split_skills(value) == expected


def test_bad_json_skills():
    with pytest.raises(ValueError, match="Invalid JSON"): split_skills('["python"')


@pytest.mark.parametrize("metric", ["cosine", "jaccard", "pearson"])
def test_content_scores(metric):
    scores, vocab = content_scores([["python", "sql"], []], [["python", "sql"], ["java"]], metric)
    assert scores[0, 0] == pytest.approx(1)
    assert scores[1, 0] == 0
    assert np.isfinite(scores).all()


def test_no_skills():
    scores, _ = content_scores([[]], [[]])
    assert scores.tolist() == [[0]]


def test_all_methods_shapes_and_filters(tiny, fast):
    suite = RecommenderSuite(fast).fit(tiny)
    rec = suite.recommend("01")
    assert set(rec.algorithm) == set(ALGORITHMS)
    assert np.isfinite(rec.score).all()
    assert set(rec.job_id) == {"004", "005"}
    assert rec.groupby("algorithm").size().eq(2).all()
    assert all(x.shape == (4, 6) for x in suite.scores.values())


def test_low_rating_is_not_positive(tiny, fast):
    suite = RecommenderSuite(fast).fit(tiny)
    assert suite.B[0, 2] == 0  # low explicit rating overrides the view
    assert suite.B[0, 3] == fast.view_weight
    assert suite.B[0, 0] == 1


def test_unknown_user(tiny, fast):
    suite = RecommenderSuite(fast).fit(tiny)
    with pytest.raises(ValueError, match="Unknown target"): suite.recommend("unknown")


def test_cold_start_labels(tiny, fast):
    rec = RecommenderSuite(fast).fit(tiny).recommend("04")
    assert rec.loc[~rec.algorithm.eq("popularity"), "status"].eq("fallback").all()
    assert rec.loc[rec.algorithm.eq("cbf"), "fallback"].eq("popularity_missing_profile").all()


def test_empty_ratings(tiny, fast):
    empty = tiny.with_interactions(tiny.ratings.iloc[:0], tiny.views.iloc[:0])
    suite = RecommenderSuite(fast).fit(empty)
    assert np.isfinite(suite.recommend("01").score).all()
    assert suite.recommend("04").status.eq("fallback").all()


def test_all_items_rated(tiny, fast):
    ratings = pd.DataFrame([("01", jid, 4) for jid in tiny.jobs.job_id], columns=["user_id", "job_id", "rating"])
    suite = RecommenderSuite(fast).fit(tiny.with_interactions(ratings, tiny.views.iloc[:0]))
    assert suite.recommend("01").empty


def test_single_user_single_item(tiny, fast):
    one = replace(tiny, users=tiny.users.iloc[:1], jobs=tiny.jobs.iloc[:1], ratings=tiny.ratings.iloc[:1], views=tiny.views.iloc[:0])
    suite = RecommenderSuite(fast).fit(one)
    assert suite.recommend("01").empty
    assert all(np.isfinite(s).all() for s in suite.scores.values())


def test_seed_reproducible(tiny, fast):
    a, b = RecommenderSuite(fast).fit(tiny), RecommenderSuite(fast).fit(tiny)
    pd.testing.assert_frame_equal(a.recommend("01"), b.recommend("01"))


def test_ties_sorted_by_id(tiny, fast):
    empty = tiny.with_interactions(tiny.ratings.iloc[:0], tiny.views.iloc[:0])
    rec = RecommenderSuite(fast).fit(empty).recommend("04", algorithms=["popularity"])
    assert rec.job_id.tolist() == ["001", "002", "003", "004", "005"]


def test_exclude_rated_toggle(tiny, fast):
    config = replace(fast, exclude_rated=False)
    rec = RecommenderSuite(config).fit(tiny).recommend("01", algorithms=["cbf"])
    assert "001" in set(rec.job_id)


def test_split_removes_views_and_retains_train_support(tiny, fast):
    train, test, meta = positive_holdout(tiny, fast)
    pairs = set(zip(test.user_id, test.job_id))
    assert not pairs.intersection(zip(train.ratings.user_id, train.ratings.job_id))
    assert not pairs.intersection(zip(train.views.user_id, train.views.job_id))
    assert set(test.job_id).issubset(set(train.ratings.job_id))
    assert train.ratings.groupby("user_id").size().ge(2).all()
    train2, test2, _ = positive_holdout(tiny, fast)
    pd.testing.assert_frame_equal(test, test2)


def test_holdout_insufficient(tiny, fast):
    empty = tiny.with_interactions(tiny.ratings.iloc[:1], tiny.views.iloc[:0])
    _, test, _ = positive_holdout(empty, fast)
    assert test.empty


def test_metrics_hand_calculated():
    got = ranking_metrics(["a", "b", "c"], ["b"], 3)
    assert got["hit_rate"] == 1 and got["recall"] == 1
    assert got["ndcg"] == pytest.approx(1 / np.log2(3))
    assert ranking_metrics(["a"], ["b"], 5)["recall"] == 0
    with pytest.raises(ValueError): ranking_metrics([], [], 5)


def test_overlap_short_list_is_not_zero():
    got = compare_rankings(["1", "2"], ["2", "3"], 10)
    assert got["overlap_at_k"] is None and got["jaccard"] == pytest.approx(1 / 3)
    assert got["mean_absolute_rank_delta_common"] == 1
    assert compare_rankings([], [], 10)["jaccard"] is None


def test_overlap_full_list():
    assert compare_rankings(["1", "2"], ["2", "3"], 2)["overlap_at_k"] == .5


@pytest.fixture
def raw_files(tmp_path):
    pd.DataFrame([{"id": "001", "username": "u"}]).to_csv(tmp_path / "users.csv", index=False)
    pd.DataFrame([{"user_id": "001", "user_skills": '["python", "machine learning"]'}]).to_csv(tmp_path / "user_profiles.csv", index=False)
    pd.DataFrame([{"id": "010", "job_title": 'Lập trình, "Python"\nAPI', "job_skills": '["python", "sql"]', "status": "open"}]).to_csv(tmp_path / "job.csv", index=False)
    pd.DataFrame([{"user_id": "001", "job_id": "010", "rating": 5}]).to_csv(tmp_path / "ratings.csv", index=False)
    pd.DataFrame(columns=["user_id", "job_id", "view_duration"]).to_csv(tmp_path / "job_views.csv", index=False)
    return tmp_path


def test_loader_roundtrip_unicode_json_leading_zero(raw_files):
    data = load_dataset(raw_files)
    assert data.users.iloc[0].user_id == "001"
    assert data.jobs.iloc[0].job_id == "010"
    assert data.jobs.iloc[0].title == 'Lập trình, "Python"\nAPI'
    assert data.users.iloc[0].skill_list == ["machine learning", "python"]
    assert len(data.raw_hashes) == 5


@pytest.mark.parametrize("rating", ["", "0", "6", "bad"])
def test_bad_ratings_rejected(raw_files, rating):
    pd.DataFrame([{"user_id": "001", "job_id": "010", "rating": rating}]).to_csv(raw_files / "ratings.csv", index=False)
    with pytest.raises(ValueError, match="invalid ratings"): load_dataset(raw_files)


def test_orphan_not_silent(raw_files):
    pd.DataFrame([{"user_id": "bad", "job_id": "010", "rating": 5}]).to_csv(raw_files / "ratings.csv", index=False)
    with pytest.raises(ValueError, match="Foreign-key"): load_dataset(raw_files)


def test_duplicate_ids(raw_files):
    pd.DataFrame([{"id": "001", "username": "u"}] * 2).to_csv(raw_files / "users.csv", index=False)
    with pytest.raises(ValueError, match="duplicate id"): load_dataset(raw_files)


def test_duplicate_ratings(raw_files):
    pd.DataFrame([{"user_id": "001", "job_id": "010", "rating": 5}] * 2).to_csv(raw_files / "ratings.csv", index=False)
    with pytest.raises(ValueError, match="Duplicate user/job"): load_dataset(raw_files)


def test_missing_schema(raw_files):
    pd.DataFrame([{"wrong": "x"}]).to_csv(raw_files / "users.csv", index=False)
    with pytest.raises(ValueError, match="missing columns"): load_dataset(raw_files)


def test_model_no_random_factor_cold_item(tiny, fast):
    suite = RecommenderSuite(fast).fit(tiny)
    for name in ("sgd", "als_explicit", "als_implicit"):
        assert suite.fallback[name][0, 4].startswith("popularity")


def test_hybrid_missing_profile_preserves_cf_support_priority(tiny, fast):
    users = tiny.users.copy()
    users.at[0, "skill_list"] = []
    suite = RecommenderSuite(fast).fit(replace(tiny, users=users))
    rec = suite.recommend("01", algorithms=["hybrid"])
    assert rec.iloc[0].job_id == "004"
    assert rec.iloc[-1].fallback.startswith("popularity")


def test_comparison_success_empty_is_distinct_from_missing(tiny, fast):
    rec = RecommenderSuite(fast).fit(tiny).recommend("04")
    cap = {"capture_id": "cf_cosine", "algorithm": "cf", "returned_algorithm": "cf",
           "similarity": "cosine", "user_id": "04", "n_items": 0,
           "http_status": 200, "capture_status": "success"}
    summary, details = compare_website(pd.DataFrame(), rec, captures=[cap])
    summary = summary.set_index("algorithm")
    assert summary.loc["cf", "n_web"] == 0
    assert summary.loc["cf", "comparison_status"].startswith("reference_only")
    assert summary.loc["cbf", "comparison_status"] == "missing_capture"
    assert pd.isna(summary.loc["cbf", "jaccard"])
    assert pd.isna(summary.loc["cf", "overlap_at_k"])


def test_comparison_error_is_not_zero(tiny, fast):
    rec = RecommenderSuite(fast).fit(tiny).recommend("04")
    cap = {"algorithm": "cbf", "similarity": "cosine", "user_id": "04",
           "http_status": 429, "capture_status": "error"}
    summary, _ = compare_website(pd.DataFrame(), rec, captures=[cap])
    row = summary.set_index("algorithm").loc["cbf"]
    assert row.comparison_status == "capture_error"
    assert pd.isna(row.n_web) and pd.isna(row.intersection)


def test_comparison_user_mismatch_and_similarity_filter(tiny, fast):
    rec = RecommenderSuite(fast).fit(tiny).recommend("04")
    cap = {"algorithm": "cbf", "returned_algorithm": "cbf", "similarity": "cosine",
           "user_id": "other", "http_status": 200, "capture_status": "success", "n_items": 0}
    summary, _ = compare_website(pd.DataFrame(), rec, captures=[cap])
    assert summary.set_index("algorithm").loc["cbf", "comparison_status"] == "target_absent_or_user_mismatch"


@pytest.mark.parametrize("value", ["inf", "nan", "-1"])
def test_invalid_view_duration(raw_files, value):
    pd.DataFrame([{"user_id": "001", "job_id": "010", "view_duration": value}]).to_csv(raw_files / "job_views.csv", index=False)
    with pytest.raises(ValueError, match="view_duration"): load_dataset(raw_files)
