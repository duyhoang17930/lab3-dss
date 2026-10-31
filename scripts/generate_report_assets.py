"""Create the report's illustrative diagrams and source-count chart."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
from matplotlib import font_manager
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


FONT = Path("C:/Windows/Fonts/arial.ttf")
font_manager.fontManager.addfont(str(FONT))
family = font_manager.FontProperties(fname=str(FONT)).get_name()
OUT = Path("outputs/report_medajob_20261030/figures")
OUT.mkdir(parents=True, exist_ok=True)

plt.rcParams.update(
    {
        "font.family": family,
        "font.size": 11,
        "axes.titlesize": 17,
        "axes.titleweight": "bold",
        "figure.facecolor": "#f7f9fc",
        "axes.facecolor": "#ffffff",
        "savefig.facecolor": "#f7f9fc",
        "text.color": "#243447",
        "axes.labelcolor": "#526477",
        "xtick.color": "#526477",
        "ytick.color": "#526477",
    }
)
navy, blue, teal, gold = "#183b56", "#3478a8", "#27a39a", "#e0a43b"
muted, red = "#607487", "#b65a55"


def pipeline():
    fig, ax = plt.subplots(figsize=(15, 4.2))
    ax.set(xlim=(0, 15), ylim=(0, 4.2))
    ax.axis("off")
    boxes = [
        (0.25, 1.32, 2.1, 1.65, "01  DỮ LIỆU", "5 tệp CSV\nMEDAJob", navy),
        (2.8, 1.32, 2.15, 1.65, "02  XỬ LÝ", "Nối khóa\nChuẩn hóa kỹ năng", blue),
        (5.4, 1.32, 2.15, 1.65, "03  CHIA DỮ LIỆU", "Train/test\nseed 42 • 34 test", teal),
        (8, 1.32, 2.15, 1.65, "04  MÔ HÌNH", "9 thuật toán\nTop-10", gold),
        (10.6, 1.32, 2, 1.65, "05  ĐÁNH GIÁ", "HR • NDCG\nCoverage\nRMSE", blue),
        (13, 1.32, 1.75, 1.65, "06  SO SÁNH", "Website\ntheo job ID", navy),
    ]
    for x, y, w, h, title, body, color in boxes:
        ax.add_patch(
            FancyBboxPatch(
                (x, y), w, h, boxstyle="round,pad=.04,rounding_size=.14",
                fc="white", ec=color, lw=2
            )
        )
        ax.text(x + 0.14, y + h - 0.42, title, fontsize=9.5,
                fontweight="bold", color=color, va="center")
        ax.text(x + 0.14, y + 0.58, body, fontsize=9.5, color=navy,
                va="center", linespacing=1.45)
    for i in range(len(boxes) - 1):
        x, y, w, h, *_ = boxes[i]
        ax.add_patch(
            FancyArrowPatch((x + w + 0.06, 2.15), (boxes[i + 1][0] - 0.08, 2.15),
                            arrowstyle="-|>", mutation_scale=15, color=muted, lw=1.7)
        )
    ax.text(0.25, 3.65, "QUY TRÌNH THỰC NGHIỆM", fontsize=12,
            fontweight="bold", color=muted)
    ax.text(
        0.25, 0.48,
        "Snapshot 7b33ca0861b04b83  •  Kết quả ngoại tuyến tính từ MEDAJob; "
        "capture website là tư liệu ngày 28/10/2026",
        fontsize=10.5, color=muted,
    )
    fig.tight_layout()
    fig.savefig(OUT / "report_pipeline.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def source_chart():
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 5), gridspec_kw={"wspace": 0.32})
    panels = [
        (axes[0], "SỐ TIN TRONG DANH MỤC", [741, 50], [blue, gold], "Số job"),
        (axes[1], "SỐ RATING QUAN SÁT", [1, 103], [teal, red], "Số rating"),
    ]
    for ax, title, values, colors, ylabel in panels:
        bars = ax.bar(["career.vn", "test"], values, color=colors, width=0.58)
        ax.set_title(title, loc="left", pad=16, color=navy, fontsize=13)
        ax.set_ylabel(ylabel)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.spines["bottom"].set_color("#d6e0e8")
        ax.grid(axis="y", alpha=0.18)
        ax.set_axisbelow(True)
        ax.bar_label(bars, padding=5, fontsize=12, fontweight="bold", color=navy)
        ax.margins(y=0.22)
    fig.suptitle("NHÃN NGUỒN VÀ MỨC ĐỘ TƯƠNG TÁC", x=0.08, y=1.03,
                 ha="left", fontsize=17, fontweight="bold", color=navy)
    fig.text(0.08, -0.02,
             "Trong 104 rating, 103 thuộc nhóm test và 1 thuộc career.vn. Hai panel dùng thang riêng.",
             fontsize=10, color=muted)
    fig.savefig(OUT / "source_job_rating_counts.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def placeholder(filename, title, subtitle, detail):
    fig, ax = plt.subplots(figsize=(10, 5.2))
    fig.subplots_adjust(0.04, 0.06, 0.96, 0.94)
    ax.set(xlim=(0, 10), ylim=(0, 5.2))
    ax.axis("off")
    ax.add_patch(
        FancyBboxPatch((0.15, 0.15), 9.7, 4.9,
                       boxstyle="round,pad=.02,rounding_size=.18",
                       fc="white", ec="#d6e0e8", lw=1.4)
    )
    ax.add_patch(
        FancyBboxPatch((0.15, 4.35), 9.7, 0.7,
                       boxstyle="round,pad=.02,rounding_size=.18",
                       fc=navy, ec=navy)
    )
    ax.text(0.48, 4.7, "TÌNH TRẠNG THAO TÁC TRÊN WEBSITE",
            fontsize=10.5, fontweight="bold", color="white", va="center")
    ax.text(0.55, 3.55, title, fontsize=21, fontweight="bold", color=navy, va="center")
    ax.text(0.55, 2.84, subtitle, fontsize=13, color=blue, va="center")
    ax.plot([0.55, 9.35], [2.35, 2.35], color="#dce5ec", lw=1.2)
    ax.text(0.55, 1.75, detail, fontsize=12, color=muted,
            va="center", linespacing=1.6, wrap=True)
    ax.text(0.55, 0.65,
            "Hình minh họa tình trạng thực hiện; chưa có ảnh chụp giao diện website.",
            fontsize=10, color=red, va="center")
    fig.savefig(OUT / filename, dpi=220, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    pipeline()
    source_chart()
    placeholder("placeholder_profile.png", "Hồ sơ ứng viên",
                "Kỹ năng • chức danh • địa điểm mong muốn",
                "Hồ sơ ứng viên chưa được cập nhật trên website. Tài khoản sv102230343 không có trong dữ liệu MEDAJob.")
    placeholder("placeholder_employer_import.png", "Danh sách tin tuyển dụng đã nhập",
                "Cần ảnh danh sách tin thành công trên website",
                "Đã chuẩn bị 10 tin trong tệp CSV. Các tin chưa được nhập lên website.")
    placeholder("placeholder_user_ratings.png", "Rating việc làm của sinh viên",
                "Cần ảnh các tin và mức sao đã chọn",
                "Chưa có rating cá nhân được ghi nhận trên website.")
    print(f"Created report assets using {family}.")
