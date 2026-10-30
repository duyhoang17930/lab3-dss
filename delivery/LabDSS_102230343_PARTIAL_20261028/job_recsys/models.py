"""Nine transparent CPU recommenders. No claim of website implementation parity."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MultiLabelBinarizer

from .data import Dataset, id_key

ALGORITHMS = {
    "cbf": "CBF - Theo kỹ năng", "cf": "CF - Theo hành vi", "hybrid": "Hybrid - Kết hợp",
    "user_knn": "User-KNN", "item_knn": "Item-KNN", "popularity": "Popularity - Phổ biến",
    "sgd": "Model-based CF - SGD", "als_explicit": "Model-based CF - ALS Explicit",
    "als_implicit": "Model-based CF - ALS Implicit",
}
EXPLICIT = {"user_knn", "item_knn", "popularity", "sgd", "als_explicit"}
RESULT_COLUMNS = ["algorithm", "algorithm_name", "user_id", "job_id", "rank", "title", "company_name",
                  "score", "score_type", "status", "fallback", "reason", "matched_skills", "dataset_snapshot_id", "config_id"]


@dataclass(frozen=True)
class Config:
    top_n: int = 10
    seed: int = 42
    similarity: str = "cosine"
    positive_threshold: float = 4.0
    view_weight: float = 0.25
    hybrid_alpha: float = 0.55
    knn_k: int = 5
    popularity_prior: float = 5.0
    factors: int = 12
    sgd_epochs: int = 45
    sgd_lr: float = 0.012
    sgd_reg: float = 0.04
    als_explicit_epochs: int = 12
    als_explicit_reg: float = 0.4
    als_implicit_epochs: int = 10
    als_implicit_alpha: float = 16.0
    als_implicit_reg: float = 0.7
    exclude_rated: bool = True
    active_only: bool = True

    def __post_init__(self):
        if self.similarity not in {"cosine", "jaccard", "pearson"}:
            raise ValueError("Unsupported content similarity")
        if not 0 <= self.hybrid_alpha <= 1 or self.view_weight < 0 or not 1 <= self.positive_threshold <= 5:
            raise ValueError("Invalid mixture/interaction weights")
        if min(self.knn_k, self.factors, self.top_n) < 1 or min(self.popularity_prior, self.sgd_reg,
                 self.als_explicit_reg, self.als_implicit_reg) <= 0:
            raise ValueError("k, factors, top_n and regularization must be positive")

    @property
    def config_id(self):
        return hashlib.sha256(json.dumps(asdict(self), sort_keys=True).encode()).hexdigest()[:12]


def normalize_rows(a):
    if not a.shape[1]: return a.copy()
    return (a - a.min(axis=1, keepdims=True)) / np.maximum(np.ptp(a, axis=1, keepdims=True), 1e-12)


def content_scores(user_skills, job_skills, similarity="cosine"):
    # Item metadata are available before holdout; no ratings enter this vocabulary.
    mlb = MultiLabelBinarizer()
    x = mlb.fit_transform(list(user_skills) + list(job_skills)).astype(float)
    a, b = x[:len(user_skills)], x[len(user_skills):]
    if not x.shape[1]: return np.zeros((len(a), len(b))), mlb.classes_.tolist()
    if similarity == "cosine": scores = cosine_similarity(a, b)
    elif similarity == "jaccard":
        intersection = a @ b.T
        union = a.sum(axis=1)[:, None] + b.sum(axis=1)[None, :] - intersection
        scores = np.divide(intersection, union, out=np.zeros_like(intersection), where=union > 0)
    elif similarity == "pearson":
        scores = cosine_similarity(a - a.mean(axis=1, keepdims=True), b - b.mean(axis=1, keepdims=True))
    else: raise ValueError(similarity)
    return scores, mlb.classes_.tolist()


class RecommenderSuite:
    def __init__(self, config=None):
        self.config = config or Config()

    def fit(self, dataset: Dataset):
        self.data = dataset
        self.users, self.jobs = dataset.users, dataset.jobs
        self.uidx = {v: i for i, v in enumerate(self.users.user_id)}
        self.jidx = {v: i for i, v in enumerate(self.jobs.job_id)}
        n, m = len(self.users), len(self.jobs)
        if not n or not m:
            raise ValueError("Need a nonempty user table and job catalog")
        if n * m > 5_000_000:
            raise ValueError("Dataset exceeds documented dense CPU budget; no silent sampling")
        self.R = np.zeros((n, m))
        self.mask = np.zeros((n, m), dtype=bool)
        for r in dataset.ratings.itertuples():
            u, j = self.uidx[r.user_id], self.jidx[r.job_id]
            self.R[u, j], self.mask[u, j] = r.rating, True
        self.B = np.where(self.mask & (self.R >= self.config.positive_threshold), self.R / 5.0, 0.0)
        for r in dataset.views.itertuples():
            u, j = self.uidx[r.user_id], self.jidx[r.job_id]
            if not self.mask[u, j] and r.view_duration > 0:
                self.B[u, j] = self.config.view_weight
        self.loss_history = []
        count = self.mask.sum(axis=0)
        self.mu = float(self.R[self.mask].mean()) if self.mask.any() else 3.0
        prior = self.config.popularity_prior
        self.pop = (self.R.sum(axis=0) + prior * self.mu) / (count + prior)
        self.scores = {"popularity": np.broadcast_to(self.pop, (n, m)).copy()}
        self.fallback = {"popularity": np.full((n, m), "", dtype=object)}
        if not self.mask.any(): self.fallback["popularity"][:] = "neutral_prior_no_ratings"
        cbf, self.vocabulary = content_scores(self.users.skill_list, self.jobs.skill_list, self.config.similarity)
        self.scores["cbf"] = cbf
        self.fallback["cbf"] = np.full((n, m), "", dtype=object)
        empty = self.users.skill_list.map(len).eq(0).to_numpy()
        self._fill("cbf", np.broadcast_to(empty[:, None], (n, m)), "popularity_missing_profile")
        # Only behavior-supported items participate in co-occurrence; keep catalog cold items for other models.
        observed_items = np.flatnonzero(self.B.any(axis=0))
        self._pairwise_guard(len(observed_items))
        cf = np.zeros((n, m))
        if len(observed_items):
            behavior = self.B[:, observed_items]
            sim = cosine_similarity(behavior.T)
            np.fill_diagonal(sim, 0.0)
            cf[:, observed_items] = (behavior @ sim) / np.maximum(behavior.sum(axis=1, keepdims=True), 1.0)
        self.scores["cf"], self.fallback["cf"] = cf, np.full((n, m), "", dtype=object)
        self._fill("cf", cf <= 0, "popularity_no_behavior_support")
        raw_cbf, _ = content_scores(self.users.skill_list, self.jobs.skill_list, self.config.similarity)
        # Normalize supported raw scores before combining; fallback is never mixed in as CF evidence.
        pure_cf = np.where(self.fallback["cf"] == "", self.scores["cf"], 0.0)
        a = self.config.hybrid_alpha
        hybrid = a * normalize_rows(raw_cbf) + (1 - a) * normalize_rows(pure_cf)
        self.scores["hybrid"], self.fallback["hybrid"] = hybrid, np.full((n, m), "", dtype=object)
        no_behavior = ~self.B.any(axis=1)
        for u in range(n):
            if empty[u] and no_behavior[u]:
                self.scores["hybrid"][u] = self.pop
                self.fallback["hybrid"][u] = "popularity_no_profile_or_behavior"
            elif no_behavior[u]:
                self.scores["hybrid"][u] = raw_cbf[u]
                self.fallback["hybrid"][u] = "cbf_only_no_behavior"
            elif empty[u]:
                self.scores["hybrid"][u] = self.scores["cf"][u]
                self.fallback["hybrid"][u] = np.where(self.fallback["cf"][u] == "",
                    "cf_only_missing_profile", "popularity_no_behavior_support_missing_profile")
        self._knn()
        self._sgd()
        self._als_explicit()
        self._als_implicit()
        for name, scores in self.scores.items():
            if not np.isfinite(scores).all(): raise FloatingPointError(f"Nonfinite scores: {name}")
        return self

    @staticmethod
    def _pairwise_guard(size):
        if size * size * 8 > 256_000_000:
            raise ValueError("Pairwise similarity exceeds CPU memory budget; use sparse implementation")

    def _fill(self, method, unsupported, reason):
        self.scores[method][unsupported] = np.broadcast_to(self.pop, self.R.shape)[unsupported]
        self.fallback[method][unsupported] = reason

    def _knn(self):
        n, m = self.R.shape
        for name in ("user_knn", "item_knn"):
            pred, denominator = np.zeros_like(self.R), np.zeros_like(self.R)
            if name == "user_knn":
                active = np.flatnonzero(self.mask.any(axis=1))
                self._pairwise_guard(len(active))
                if len(active):
                    sims = cosine_similarity(self.R[active])
                    np.fill_diagonal(sims, 0)
                    for pos, u in enumerate(active):
                        selected = np.argsort(-sims[pos], kind="stable")[:self.config.knn_k]
                        near, w = active[selected], sims[pos, selected]
                        denominator[u] = w @ self.mask[near]
                        pred[u] = (w @ self.R[near]) / np.maximum(denominator[u], 1e-12)
            else:
                active = np.flatnonzero(self.mask.any(axis=0))
                self._pairwise_guard(len(active))
                if len(active):
                    sims = cosine_similarity(self.R[:, active].T)
                    np.fill_diagonal(sims, 0)
                    for pos, j in enumerate(active):
                        selected = np.argsort(-sims[pos], kind="stable")[:self.config.knn_k]
                        near, w = active[selected], sims[pos, selected]
                        denominator[:, j] = self.mask[:, near] @ w
                        pred[:, j] = (self.R[:, near] @ w) / np.maximum(denominator[:, j], 1e-12)
            self.scores[name], self.fallback[name] = pred, np.full(self.R.shape, "", dtype=object)
            self._fill(name, denominator <= 0, "popularity_no_neighbors")

    def _sgd(self):
        c, (n, m) = self.config, self.R.shape
        rng = np.random.default_rng(c.seed)
        u = rng.normal(0, .12, (n, c.factors)); v = rng.normal(0, .12, (m, c.factors))
        bu, bi = np.zeros(n), np.zeros(m)
        observed = np.argwhere(self.mask)
        for epoch in range(c.sgd_epochs):
            for i, j in observed[rng.permutation(len(observed))]:
                error = self.R[i, j] - (self.mu + bu[i] + bi[j] + u[i] @ v[j])
                old = u[i].copy()
                bu[i] += c.sgd_lr * (error - c.sgd_reg * bu[i])
                bi[j] += c.sgd_lr * (error - c.sgd_reg * bi[j])
                u[i] += c.sgd_lr * (error * v[j] - c.sgd_reg * u[i])
                v[j] += c.sgd_lr * (error * old - c.sgd_reg * v[j])
            if len(observed):
                ii, jj = observed.T
                error = self.R[ii, jj] - (self.mu + bu[ii] + bi[jj] + np.sum(u[ii] * v[jj], axis=1))
                self.loss_history.append({"algorithm": "sgd", "epoch": epoch + 1, "observed_mse": float(np.mean(error**2))})
        self.scores["sgd"] = self.mu + bu[:, None] + bi[None, :] + u @ v.T
        self.fallback["sgd"] = np.full((n, m), "", dtype=object)
        unsupported = (~self.mask.any(axis=1))[:, None] | (~self.mask.any(axis=0))[None, :]
        self._fill("sgd", unsupported, "popularity_untrained_user_or_item")

    def _als_explicit(self):
        c, (n, m) = self.config, self.R.shape
        rng = np.random.default_rng(c.seed)
        u = rng.normal(0, .15, (n, c.factors)); v = rng.normal(0, .15, (m, c.factors))
        eye, centered = np.eye(c.factors), self.R - self.mu
        for epoch in range(c.als_explicit_epochs):
            for i in range(n):
                observed = self.mask[i]; y = v[observed]
                u[i] = np.linalg.solve(y.T @ y + c.als_explicit_reg * eye, y.T @ centered[i, observed]) if observed.any() else 0
            for j in range(m):
                observed = self.mask[:, j]; x = u[observed]
                v[j] = np.linalg.solve(x.T @ x + c.als_explicit_reg * eye, x.T @ centered[observed, j]) if observed.any() else 0
            if self.mask.any():
                mse = float(np.mean((self.R - (self.mu + u @ v.T))[self.mask]**2))
                self.loss_history.append({"algorithm": "als_explicit", "epoch": epoch + 1, "observed_mse": mse})
        self.scores["als_explicit"] = self.mu + u @ v.T
        self.fallback["als_explicit"] = np.full((n, m), "", dtype=object)
        self._fill("als_explicit", (~self.mask.any(axis=1))[:, None] | (~self.mask.any(axis=0))[None, :],
                   "popularity_untrained_user_or_item")

    def _als_implicit(self):
        c, (n, m) = self.config, self.R.shape
        rng = np.random.default_rng(c.seed)
        x = rng.normal(0, .08, (n, c.factors)); y = rng.normal(0, .08, (m, c.factors))
        eye = np.eye(c.factors)
        for _ in range(c.als_implicit_epochs):
            gram = y.T @ y
            for i in range(n):
                idx = np.flatnonzero(self.B[i] > 0); yi = y[idx]; diff = c.als_implicit_alpha * self.B[i, idx]
                x[i] = np.linalg.solve(gram + yi.T @ (diff[:, None] * yi) + c.als_implicit_reg * eye,
                                       yi.T @ (1 + diff))
            gram = x.T @ x
            for j in range(m):
                idx = np.flatnonzero(self.B[:, j] > 0); xj = x[idx]; diff = c.als_implicit_alpha * self.B[idx, j]
                y[j] = np.linalg.solve(gram + xj.T @ (diff[:, None] * xj) + c.als_implicit_reg * eye,
                                       xj.T @ (1 + diff))
        self.scores["als_implicit"] = x @ y.T
        self.fallback["als_implicit"] = np.full((n, m), "", dtype=object)
        self._fill("als_implicit", (~self.B.any(axis=1))[:, None] | (~self.B.any(axis=0))[None, :],
                   "popularity_no_positive_signal")

    def recommend(self, user_id, top_n=None, algorithms=None, eligible_job_ids=None):
        user_id = str(user_id)
        if user_id not in self.uidx: raise ValueError(f"Unknown target user_id {user_id}; no substitute user")
        if top_n is not None and top_n < 1: raise ValueError("top_n must be positive")
        u, rows = self.uidx[user_id], []
        eligible = np.ones(len(self.jobs), dtype=bool)
        if self.config.active_only: eligible &= self.jobs.status.eq("open").to_numpy()
        if self.config.exclude_rated: eligible &= ~self.mask[u]
        if eligible_job_ids is not None: eligible &= self.jobs.job_id.isin(eligible_job_ids).to_numpy()
        ids = np.flatnonzero(eligible)
        for name in (algorithms if algorithms is not None else ALGORITHMS):
            # Native-supported recommendations precede labeled fallback candidates.
            # Never compare affinity scores with fallback rating-scale scores.
            order = sorted(ids, key=lambda j: (str(self.fallback[name][u, j]).startswith(("popularity", "neutral")),
                                               -self.scores[name][u, j], id_key(self.jobs.iloc[j].job_id)))
            for rank, j in enumerate(order[:top_n or self.config.top_n], 1):
                job = self.jobs.iloc[j]; fallback = str(self.fallback[name][u, j])
                score_type = "predicted_rating" if name in EXPLICIT else (self.config.similarity if name == "cbf" else "affinity")
                if fallback.startswith("popularity") or fallback.startswith("neutral"): score_type = "bayesian_rating_prior"
                elif fallback.startswith("cbf_only"): score_type = self.config.similarity
                matched = sorted(set(self.users.iloc[u].skill_list) & set(job.skill_list))
                rows.append(dict(algorithm=name, algorithm_name=ALGORITHMS[name], user_id=user_id, job_id=job.job_id,
                                 rank=rank, title=job.title, company_name=job.company_name, score=float(self.scores[name][u, j]),
                                 score_type=score_type, status="fallback" if fallback else "model", fallback=fallback,
                                 reason=fallback or "model_supported", matched_skills=", ".join(matched),
                                 dataset_snapshot_id=self.data.snapshot_id, config_id=self.config.config_id))
        return pd.DataFrame(rows, columns=RESULT_COLUMNS)
