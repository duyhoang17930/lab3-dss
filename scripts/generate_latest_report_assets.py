"""Build the report figures for the 2026-10-31 MEDAJob CSV export."""
from pathlib import Path
import json
import shutil

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/shared/medajob_csv_20261031"
RESULTS = ROOT / "outputs/notebook/medajob_csv_20261031"
OUT = ROOT / "outputs/report_medajob_20261031/figures"
OUT.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
navy, blue, teal, gold = "#183b56", "#3478a8", "#27a39a", "#e0a43b"
muted, red = "#607487", "#b65a55"


def pipeline():
    quality = json.loads((RESULTS / "data_quality.json").read_text(encoding="utf-8"))
    split = json.loads((RESULTS / "split_manifest.json").read_text(encoding="utf-8"))
    manifest = json.loads((RESULTS / "run_manifest.json").read_text(encoding="utf-8"))
    boxes = [
        (0.25, "01  DỮ LIỆU", "5 tệp CSV\n466 tài khoản • 1.241 tin", navy),
        (2.75, "02  TIỀN XỬ LÝ", "Nối theo ID\nChuẩn hóa kỹ năng", blue),
        (5.25, "03  CHIA TẬP", f"Seed 42\n{split['train_ratings']} train • {split['test_users']} test", teal),
        (7.75, "04  MÔ HÌNH", "9 thuật toán\nGợi ý Top-10", gold),
        (10.25, "05  ĐÁNH GIÁ", "HitRate • NDCG\nCoverage • RMSE/MAE", blue),
        (12.75, "06  ĐỐI CHIẾU", "Website\ntheo mã việc làm", navy),
    ]
    fig, ax = plt.subplots(figsize=(15, 4.2))
    ax.set(xlim=(0, 15), ylim=(0, 4.2))
    ax.axis("off")
    for x, title, body, color in boxes:
        ax.add_patch(FancyBboxPatch((x, 1.3), 2.0, 1.65,
                                    boxstyle="round,pad=.04,rounding_size=.14",
                                    fc="white", ec=color, lw=2))
        ax.text(x + .13, 2.55, title, fontsize=9.2, fontweight="bold",
                color=color, va="center")
        ax.text(x + .13, 1.82, body, fontsize=9.1, color=navy,
                va="center", linespacing=1.45)
    for i in range(len(boxes) - 1):
        x = boxes[i][0]
        ax.add_patch(FancyArrowPatch((x + 2.05, 2.1), (boxes[i + 1][0] - .06, 2.1),
                                     arrowstyle="-|>", mutation_scale=14,
                                     color=muted, lw=1.5))
    ax.text(.25, 3.65, "QUY TRÌNH THỰC NGHIỆM", fontsize=12,
            fontweight="bold", color=muted)
    ax.text(.25, .52,
            f"Snapshot {manifest['dataset_snapshot_id']} • Kết quả tính từ MEDAJob cập nhật ngày 31/10/2026",
            fontsize=10, color=muted)
    fig.tight_layout()
    fig.savefig(OUT / "report_pipeline.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def source_chart():
    jobs = pd.read_csv(DATA / "job.csv", dtype=str, keep_default_na=False)
    ratings = pd.read_csv(DATA / "ratings.csv", dtype=str, keep_default_na=False)
    order = ["career.vn", "test", "other/blank"]
    labels = ["career.vn", "test", "Khác hoặc\nchưa phân nhóm"]
    job_counts = jobs.source_group.value_counts().reindex(order, fill_value=0)
    joined = ratings.merge(jobs[["id", "source_group"]], left_on="job_id", right_on="id", how="left")
    rating_counts = joined.source_group.value_counts().reindex(order, fill_value=0)

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 5), gridspec_kw={"wspace": .32})
    panels = [
        (axes[0], "SỐ TIN THEO NHÃN GHI CHÚ", job_counts.to_list(), "Số việc làm"),
        (axes[1], "SỐ RATING THEO NHÃN GHI CHÚ", rating_counts.to_list(), "Số rating"),
    ]
    colors = [blue, gold, teal]
    for ax, title, values, ylabel in panels:
        bars = ax.bar(labels, values, color=colors, width=.58)
        ax.set_title(title, loc="left", pad=16, color=navy, fontsize=12)
        ax.set_ylabel(ylabel)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.spines["bottom"].set_color("#d6e0e8")
        ax.grid(axis="y", alpha=.18)
        ax.set_axisbelow(True)
        ax.bar_label(bars, padding=5, fontsize=11, fontweight="bold", color=navy)
        ax.margins(y=.2)
    fig.suptitle("PHÂN NHÓM THEO TRƯỜNG NOTE TRONG BẢN CSV",
                 x=.08, y=1.02, ha="left", fontsize=16,
                 fontweight="bold", color=navy)
    fig.text(.08, -.02,
             "Nhóm khác/chưa phân nhóm gồm note trống và các giá trị khác career.vn, test; hai panel dùng thang riêng.",
             fontsize=9.2, color=muted)
    fig.savefig(OUT / "source_job_rating_counts.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def copy_model_figures():
    for filename in ("rating_distribution.png", "offline_metrics.png", "training_loss.png"):
        shutil.copy2(RESULTS / "figures" / filename, OUT / filename)


def profile_status():
    fig, ax = plt.subplots(figsize=(10, 5.2))
    ax.set(xlim=(0, 10), ylim=(0, 5.2))
    ax.axis("off")
    ax.add_patch(FancyBboxPatch((.15, .15), 9.7, 4.9,
                                boxstyle="round,pad=.02,rounding_size=.18",
                                fc="white", ec="#d6e0e8", lw=1.4))
    ax.add_patch(FancyBboxPatch((.15, 4.35), 9.7, .7,
                                boxstyle="round,pad=.02,rounding_size=.18",
                                fc=navy, ec=navy))
    ax.text(.48, 4.7, "TÌNH TRẠNG HỒ SƠ TRONG BẢN CSV NGÀY 31/10",
            fontsize=10.3, fontweight="bold", color="white", va="center")
    ax.text(.55, 3.55, "sv102230343 • ID 458", fontsize=20,
            fontweight="bold", color=navy, va="center")
    ax.text(.55, 2.85, "role: employer  |  user_profiles: chưa có bản ghi",
            fontsize=12.5, color=blue, va="center")
    ax.plot([.55, 9.35], [2.35, 2.35], color="#dce5ec", lw=1.2)
    ax.text(.55, 1.65,
            "Lần khảo sát website ngày 28/10 chưa ghi nhận kỹ năng trên hồ sơ.\n"
            "CSV mới có tài khoản này nhưng không có dữ liệu kỹ năng để cá nhân hóa CBF.",
            fontsize=11.5, color=muted, va="center", linespacing=1.55)
    ax.text(.55, .55,
            "Hình minh họa tóm tắt CSV; không phải ảnh chụp giao diện website.",
            fontsize=9.8, color=red, va="center")
    fig.savefig(OUT / "placeholder_profile.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    pipeline()
    source_chart()
    copy_model_figures()
    profile_status()
    print(f"Created report figures in {OUT}")
