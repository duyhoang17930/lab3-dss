"""Run all nine methods; persist exact inputs, settings, counts and limitations."""
from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime
from hashlib import sha256
from importlib.metadata import version
from pathlib import Path
from time import perf_counter
from zoneinfo import ZoneInfo
import json
import platform

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from .data import load_dataset
from .evaluation import compare_website, evaluate
from .models import ALGORITHMS, Config, RecommenderSuite


def save_json(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def make_figures(data, metrics, suite, directory):
    directory = Path(directory); directory.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
    fig, ax = plt.subplots(figsize=(8, 4))
    counts = data.ratings.rating.value_counts().sort_index()
    ax.bar(counts.index.astype(str), counts.values, color="#32678b")
    ax.set(xlabel="Rating", ylabel="Số đánh giá", title="Phân bố rating trong snapshot MEDAJob")
    for i, val in enumerate(counts.values): ax.text(i, val, str(val), ha="center", va="bottom")
    fig.tight_layout(); fig.savefig(directory / "rating_distribution.png", dpi=160); plt.close(fig)
    if not metrics.empty:
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        sub = metrics[metrics.k.eq(10)].set_index("algorithm").reindex(ALGORITHMS)
        sub[["hit_rate", "ndcg"]].plot.bar(ax=axes[0], color=["#32678b", "#a25e2a"])
        axes[0].set(title="Positive hold-out tại K=10", xlabel="", ylabel="Giá trị")
        sub["fallback_fraction"].plot.bar(ax=axes[1], color="#626d76")
        axes[1].set(title="Tỷ lệ gợi ý dùng fallback", xlabel="", ylabel="Tỷ lệ")
        fig.tight_layout(); fig.savefig(directory / "offline_metrics.png", dpi=160); plt.close(fig)
    loss = pd.DataFrame(suite.loss_history)
    if not loss.empty:
        fig, ax = plt.subplots(figsize=(8, 4))
        for name, group in loss.groupby("algorithm"):
            ax.plot(group.epoch, group.observed_mse, label=name)
        ax.set(xlabel="Vòng lặp", ylabel="MSE trên rating train", title="Sai số huấn luyện không phải độ chính xác kiểm thử")
        ax.legend(); fig.tight_layout(); fig.savefig(directory / "training_loss.png", dpi=160); plt.close(fig)


def run(data_dir, output_dir, target_username="sv102230343", config=None, website_csv=None, capture_manifest=None):
    start = perf_counter(); config = config or Config(); output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    data = load_dataset(data_dir)
    save_json(output / "data_quality.json", data.quality)
    target = data.users[data.users.username.eq(target_username)]
    suite = RecommenderSuite(config).fit(data)
    if len(target) == 1:
        target_id = target.iloc[0].user_id
        recs = suite.recommend(target_id)
        target_status = "profile_missing" if not target.iloc[0].skill_list else "available"
    else:
        target_id, target_status = None, "absent_from_snapshot"
        recs = pd.DataFrame(columns=["algorithm", "rank", "user_id", "job_id", "title", "score"])
    recs.to_csv(output / "recommendations.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(suite.loss_history).to_csv(output / "training_loss.csv", index=False, encoding="utf-8-sig")
    metrics, individual, train, test, split = evaluate(data, config)
    metrics.to_csv(output / "offline_metrics.csv", index=False, encoding="utf-8-sig")
    individual.to_csv(output / "per_user_metrics.csv", index=False, encoding="utf-8-sig")
    train.ratings.to_csv(output / "train_ratings.csv", index=False, encoding="utf-8-sig")
    test.to_csv(output / "test_ratings.csv", index=False, encoding="utf-8-sig")
    train.views.to_csv(output / "train_views.csv", index=False, encoding="utf-8-sig")
    save_json(output / "split_manifest.json", split)
    web = pd.read_csv(website_csv, dtype={"user_id": str, "job_id": str}) if website_csv else pd.DataFrame()
    captures = json.loads(Path(capture_manifest).read_text(encoding="utf-8")) if capture_manifest else []
    summary, ranks = compare_website(web, recs, config.top_n, captures, config.similarity, target_id)
    summary.to_csv(output / "website_comparison.csv", index=False, encoding="utf-8-sig")
    ranks.to_csv(output / "website_rank_details.csv", index=False, encoding="utf-8-sig")
    make_figures(data, metrics, suite, output / "figures")
    artifacts = {str(p.relative_to(output)): sha256(p.read_bytes()).hexdigest() for p in output.rglob("*") if p.is_file() and p.name != "run_manifest.json"}
    manifest = {
        "run_at": datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).isoformat(),
        "data_dir": str(Path(data_dir)), "dataset_snapshot_id": data.snapshot_id, "raw_sha256": data.raw_hashes,
        "target_username": target_username, "target_user_id": target_id, "target_status": target_status,
        "target_rating_count": int(data.ratings.user_id.eq(target_id).sum()), "config": asdict(config),
        "website_csv": str(website_csv) if website_csv else None,
        "capture_manifest": str(capture_manifest) if capture_manifest else None,
        "config_id": config.config_id, "recommendation_rows": len(recs), "algorithm_count": len(ALGORITHMS),
        "source_sha256": {p.name: sha256(p.read_bytes()).hexdigest() for p in Path(__file__).parent.glob("*.py")},
        "test_users": len(test), "python": platform.python_version(),
        "libraries": {n: version(n) for n in ("numpy", "pandas", "scipy", "scikit-learn", "matplotlib")},
        "duration_seconds": round(perf_counter() - start, 3), "artifact_sha256": artifacts,
        "limitations": ["Website backend parameters and exact live snapshot parity are not known.",
                         "Scores from different algorithms are not directly comparable.",
                         "Holdout uses positive ratings; HR equals recall because one item is held out per user.",
                         "Profile metadata are treated as static snapshot metadata; no historical profile versions.",
                         "Native-supported candidates rank before explicitly labeled fallback candidates.",
                         "Open status controls candidates; no inferred historical deadline filter."],
    }
    save_json(output / "run_manifest.json", manifest)
    print(json.dumps({k: manifest[k] for k in ("dataset_snapshot_id", "target_user_id", "target_status", "recommendation_rows", "test_users", "duration_seconds")}, ensure_ascii=False))
    return data, suite, recs, metrics, manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data_MEDAJOB")
    parser.add_argument("--output", default="outputs/provided_snapshot")
    parser.add_argument("--target", default="sv102230343")
    parser.add_argument("--config", default="configs/experiment.json")
    parser.add_argument("--website-csv")
    parser.add_argument("--capture-manifest")
    args = parser.parse_args()
    values = json.loads(Path(args.config).read_text(encoding="utf-8"))
    config = Config(**{k: v for k, v in values.items() if k in Config.__dataclass_fields__})
    run(args.data, args.output, args.target, config, args.website_csv, args.capture_manifest)


if __name__ == "__main__":
    main()
