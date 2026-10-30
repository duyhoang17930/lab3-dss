"""Positive leave-one-out evaluation and evidence-bounded website comparisons."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .data import Dataset, id_key
from .models import ALGORITHMS, EXPLICIT, Config, RecommenderSuite


def positive_holdout(data: Dataset, config: Config):
    rng = np.random.default_rng(config.seed)
    remaining = data.ratings.job_id.value_counts().to_dict()
    active = set(data.jobs.loc[data.jobs.status.eq("open"), "job_id"]) if config.active_only else set(data.jobs.job_id)
    selected, exclusions = [], {}
    for uid in sorted(data.ratings.user_id.unique(), key=id_key):
        rows = data.ratings[data.ratings.user_id.eq(uid)]
        if len(rows) < 3:
            exclusions[uid] = "fewer_than_3_ratings"
            continue
        eligible = rows[(rows.rating >= config.positive_threshold) & rows.job_id.isin(active)]
        eligible = eligible[eligible.job_id.map(remaining).ge(2)]
        if eligible.empty:
            exclusions[uid] = "no_positive_active_item_with_training_support"
            continue
        chosen = rng.choice(eligible.index.to_numpy())
        selected.append(chosen)
        remaining[data.ratings.loc[chosen, "job_id"]] -= 1
    test = data.ratings.loc[selected].copy().reset_index(drop=True)
    train = data.ratings.drop(index=selected).copy().reset_index(drop=True)
    held_pairs = set(zip(test.user_id, test.job_id))
    keep = [(r.user_id, r.job_id) not in held_pairs for r in data.views.itertuples()]
    train_views = data.views.loc[keep].copy().reset_index(drop=True)
    return data.with_interactions(train, train_views), test, {
        "strategy": "positive_leave_one_out_random",
        "seed": config.seed, "test_users": len(test), "test_ratings": len(test),
        "train_ratings": len(train), "excluded_users": len(exclusions),
        "exclusions": exclusions, "removed_view_pairs": len(data.views) - len(train_views),
        "limitation": "No trustworthy rating time. Positive-only holdout; RMSE/MAE are not all-rating accuracy. Static catalog/profile metadata available at snapshot.",
    }


def ranking_metrics(recommended, relevant, k):
    if k < 1: raise ValueError("k must be positive")
    truth = set(relevant)
    if not truth: raise ValueError("Need at least one held-out relevant item")
    top = list(recommended)[:k]
    hits = [int(j in truth) for j in top]
    dcg = sum(v / np.log2(rank + 2) for rank, v in enumerate(hits))
    ideal = sum(1 / np.log2(rank + 2) for rank in range(min(k, len(truth))))
    return {"hit_rate": float(any(hits)), "recall": sum(hits) / len(truth), "ndcg": dcg / ideal}


def evaluate(data: Dataset, config: Config):
    train, test, split = positive_holdout(data, config)
    rows, individual = [], []
    if test.empty:
        return pd.DataFrame(), pd.DataFrame(), train, test, split
    suite = RecommenderSuite(config).fit(train)
    active = set(data.jobs.loc[data.jobs.status.eq("open"), "job_id"]) if config.active_only else set(data.jobs.job_id)
    for algorithm in ALGORITHMS:
        predictions, rating_truth, rating_fallback = [], [], []
        for row in test.itertuples():
            u, j = suite.uidx[row.user_id], suite.jidx[row.job_id]
            predictions.append(suite.scores[algorithm][u, j])
            rating_truth.append(row.rating)
            rating_fallback.append(bool(suite.fallback[algorithm][u, j]))
        for k in (5, 10):
            metrics, catalog, output_rows, fallback_rows = [], set(), 0, 0
            short_lists = 0
            for row in test.itertuples():
                rec = suite.recommend(row.user_id, k, [algorithm])
                value = ranking_metrics(rec.job_id, [row.job_id], k)
                metrics.append(value); catalog.update(rec.job_id)
                output_rows += len(rec); fallback_rows += int(rec.status.eq("fallback").sum())
                short_lists += int(len(rec) < k)
                individual.append({"algorithm": algorithm, "k": k, "user_id": row.user_id, "test_job_id": row.job_id,
                                   **value, "returned": len(rec), "fallback_count": int(rec.status.eq("fallback").sum())})
            error = np.asarray(predictions) - np.asarray(rating_truth)
            rows.append({"algorithm": algorithm, "k": k, "test_users": len(test),
                         **{key: float(np.mean([v[key] for v in metrics])) for key in ("hit_rate", "recall", "ndcg")},
                         "catalog_coverage": len(catalog) / max(len(active), 1), "unique_recommended_jobs": len(catalog),
                         "eligible_catalog_jobs": len(active), "fallback_fraction": fallback_rows / max(output_rows, 1),
                         "short_lists": short_lists,
                         "rmse_positive_holdout": float(np.sqrt(np.mean(error**2))) if algorithm in EXPLICIT else None,
                         "mae_positive_holdout": float(np.mean(np.abs(error))) if algorithm in EXPLICIT else None,
                         "rating_prediction_fallback_fraction": float(np.mean(rating_fallback)) if algorithm in EXPLICIT else None,
                         "dataset_snapshot_id": data.snapshot_id, "config_id": config.config_id})
    return pd.DataFrame(rows), pd.DataFrame(individual), train, test, split


def compare_rankings(web, python, k=10):
    a, b = list(dict.fromkeys(map(str, web)))[:k], list(dict.fromkeys(map(str, python)))[:k]
    common, union = set(a) & set(b), set(a) | set(b)
    return {"requested_k": k, "n_web": len(a), "n_python": len(b), "intersection": len(common),
            "overlap_at_k": len(common) / k if len(a) == k and len(b) == k else None,
            "jaccard": len(common) / len(union) if union else None,
            "top1_match": a[0] == b[0] if a and b else None,
            "mean_absolute_rank_delta_common": float(np.mean([abs(a.index(j) - b.index(j)) for j in common])) if common else None}


def compare_website(website: pd.DataFrame, recommendations: pd.DataFrame, k=10,
                    captures=None, similarity="cosine", target_user_id=None):
    """A successful empty response differs from absent/error evidence.

    Capture metadata is mandatory for numerical comparisons. No inferred backend
    parity: frontend diagnostics expose only a sample, not the complete candidates.
    """
    summaries, rank_rows = [], []
    captures = captures or []
    for algorithm in ALGORITHMS:
        a = website[website.algorithm.eq(algorithm)].sort_values("rank") if not website.empty else pd.DataFrame()
        if not a.empty and "similarity" in a:
            a = a[a.similarity.eq(similarity)]
        b = recommendations[recommendations.algorithm.eq(algorithm)].sort_values("rank")
        matching = [c for c in captures if c.get("algorithm") == algorithm and c.get("similarity") == similarity]
        cap = matching[0] if len(matching) == 1 else None
        web_ids = a.job_id.astype(str).head(k).tolist() if not a.empty else []
        py_ids = b.job_id.astype(str).head(k).tolist()
        py_users = set(b.user_id.astype(str)) if not b.empty else ({str(target_user_id)} if target_user_id is not None else set())
        same_user = bool(cap and py_users == {str(cap.get("user_id"))})
        status = "missing_capture" if not matching else "ambiguous_capture" if cap is None else "capture_error"
        valid = bool(cap and cap.get("capture_status") == "success" and cap.get("http_status") == 200
                     and cap.get("returned_algorithm") == algorithm)
        if valid:
            if not same_user: status = "target_absent_or_user_mismatch"
            elif int(cap.get("n_items", -1)) != len(a): status = "capture_row_count_mismatch"
            elif not a.empty and set(a.user_id.astype(str)) != py_users: status = "row_user_mismatch"
            elif not a.empty and a.job_id.duplicated().any(): status = "duplicate_web_ids"
            else: status = "reference_only_backend_and_snapshot_not_proven"
        comparable = status == "reference_only_backend_and_snapshot_not_proven"
        metrics = compare_rankings(web_ids, py_ids, k) if comparable else {
            "requested_k": k, "n_web": len(a) if valid else None, "n_python": len(py_ids),
            "intersection": None, "overlap_at_k": None, "jaccard": None,
            "top1_match": None, "mean_absolute_rank_delta_common": None}
        summaries.append({"algorithm": algorithm, "similarity": similarity, **metrics, "same_user": same_user,
                          "capture_id": cap.get("capture_id") if cap else None,
                          "captured_at": cap.get("captured_at") if cap else None,
                          "comparison_status": status})
        if not comparable: continue
        for job in sorted(set(web_ids) | set(py_ids), key=id_key):
            wr = web_ids.index(job) + 1 if job in web_ids else None
            pr = py_ids.index(job) + 1 if job in py_ids else None
            rank_rows.append({"algorithm": algorithm, "job_id": job, "web_rank": wr, "python_rank": pr,
                              "rank_delta": pr - wr if wr is not None and pr is not None else None})
    return pd.DataFrame(summaries), pd.DataFrame(rank_rows)
