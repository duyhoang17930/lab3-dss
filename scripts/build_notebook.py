"""Generate the teaching notebook from shared source modules, without duplicated math."""
from pathlib import Path
import nbformat as nbf

ROOT=Path(__file__).resolve().parents[1]
nb=nbf.v4.new_notebook()
cells=[]
def md(text): cells.append(nbf.v4.new_markdown_cell(text))
def code(text): cells.append(nbf.v4.new_code_cell(text))

md('''# LabDSS Website RECSYS
Nguyễn Hoàng Hà · MSSV 102230343 · Báo cáo cá nhân · 28/10/2026

Notebook này đọc MEDAJob thật, chạy chín thuật toán và phân biệt hai mục tiêu: đối sánh một snapshot đầy đủ với website, và đánh giá ngoại tuyến trên train/test. Không dùng dữ liệu demo, không đăng nhập hoặc ghi lên website.

**Kết luận về tài khoản:** `sv102230343` vắng mặt trong dữ liệu gốc. Bản xuất website có user `458`, chưa có hồ sơ kỹ năng và rating. Không thay bằng người dùng khác. Kết quả dự phòng không được diễn giải như sở thích của sinh viên.

Chạy từ đầu bằng `python scripts/execute_notebook.py` trong môi trường đã cài `requirements.txt`. Dữ liệu gốc được ưu tiên; gói chia sẻ chỉ có các bản đã lược bỏ thông tin cá nhân, có provenance và mã snapshot riêng. Không sửa nguồn CSV trong notebook.''')
code('''from pathlib import Path
import json
from dataclasses import asdict, replace
import pandas as pd
import numpy as np
from IPython.display import display, Markdown, Image
from job_recsys.data import load_dataset, split_skills
from job_recsys.models import ALGORITHMS, Config, RecommenderSuite, content_scores
from job_recsys.evaluation import positive_holdout, compare_website
from job_recsys.run import run

ROOT = Path.cwd()
assert (ROOT / "job_recsys").is_dir(), "Mở notebook từ thư mục Lab3"
cfg_values = json.loads((ROOT / "configs/experiment.json").read_text(encoding="utf-8"))
config = Config(**{k:v for k,v in cfg_values.items() if k in Config.__dataclass_fields__})
target_username = cfg_values["target_username"]
data_paths = {
    "provided_snapshot": Path("data_MEDAJOB"),
    "website_before": Path("data/raw/website_before/csv"),
    "website_after_capture": Path("data/raw/website_after_capture/csv"),
}
for label, path in list(data_paths.items()):
    if not path.is_dir():
        data_paths[label] = Path("data/shared") / label
    assert data_paths[label].is_dir(), f"Thiếu dữ liệu thật: {label}"
display(pd.DataFrame([{"snapshot":k,"path":str(v),"privacy_reduced":"shared" in v.parts} for k,v in data_paths.items()]))
display(pd.DataFrame(asdict(config).items(), columns=["Tham số", "Giá trị"]))''')
md('''## 1 Đọc dữ liệu và kiểm tra chất lượng
Nối `users.id = user_profiles.user_id`. ID đọc dạng chuỗi, không làm mất số 0 đầu. Kỹ năng JSON array hoặc chuỗi phân cách bằng dấu phẩy/chấm phẩy/dấu gạch đứng được chuẩn hóa Unicode NFC và chữ thường; không cắt cụm như `machine learning` theo khoảng trắng.

Pipeline dừng khi có ID trùng, khóa ngoại sai, cặp rating trùng không có thời gian đáng tin cậy, rating ngoài 1–5 hoặc thời lượng xem không hữu hạn/âm. Giữ toàn bộ user và job, kể cả job chưa được rating. `status=open` là quy tắc ứng viên chung; chưa suy diễn hạn nộp lịch sử từ metadata không hoàn chỉnh.''')
code('''datasets = {label: load_dataset(path) for label,path in data_paths.items()}
quality = []
for label,d in datasets.items():
    q = d.quality
    quality.append({"snapshot":label,"hash":d.snapshot_id,"users":len(d.users),"jobs":len(d.jobs),
                    "ratings":len(d.ratings),"view_pairs":len(d.views),"rating_users":q["rating_users"],
                    "users_without_skills":q["users_without_skills"],"sparsity":q["sparsity_all_users"]})
display(pd.DataFrame(quality))
print(split_skills('["Python", "machine learning", "SQL"]'))
for label,d in datasets.items():
    t=d.users[d.users.username.eq(target_username)]
    print(label, "target absent" if t.empty else {"user_id":t.iloc[0].user_id,"skills":t.iloc[0].skill_list,
          "ratings":int(d.ratings.user_id.eq(t.iloc[0].user_id).sum())})''')
md('''## 2 Tín hiệu và quy tắc chung
Rating explicit dùng riêng ma trận $R$ và mask quan sát $M$. Không xem số 0 bị thiếu là rating thật.

Tín hiệu hành vi $B_{ui}=r_{ui}/5$ nếu rating ≥4; $B_{ui}=0.25$ nếu cặp chưa rating nhưng có thời lượng xem dương; các trường hợp còn lại bằng 0. Rating thấp luôn chặn lượt xem của cùng cặp. Lượt xem lặp được gộp, không tăng trọng số tùy số lần mở trang.

Top-N=10, seed=42; loại việc đã rating và việc không mở. Khi đồng điểm, sắp ID tăng dần. Điểm model và điểm dự phòng có thang khác nhau: các ứng viên có bằng chứng model được xếp trước dự phòng Popularity. Mọi fallback có nhãn, không clip các điểm rating để tránh tạo đồng hạng giả.''')
md('''## 3 Chạy snapshot đầy đủ và holdout độc lập
`fit(dataset)` học trên dữ liệu truyền vào; `recommend(user_id, top_n, algorithms)` trả thuật toán, user/job ID, hạng, điểm, loại điểm, fallback và snapshot ID. Không tự chọn user đầu tiên.

Hàm `run` vừa xuất đối sánh full-snapshot, vừa tạo mô hình train riêng cho đánh giá. Bản gốc và các lần xuất website chạy độc lập, không trộn rating giữa snapshot.''')
code('''web_path = Path("data/website/verified_baseline/recommendations.csv")
capture_path = Path("data/website/verified_baseline/capture_manifest.json")
web = pd.read_csv(web_path, dtype={"user_id":str,"job_id":str})
captures = json.loads(capture_path.read_text(encoding="utf-8"))
runs = {}
for label,path in data_paths.items():
    runs[label] = run(path, Path("outputs/notebook")/label, target_username, config,
                      web_path if label != "provided_snapshot" else None,
                      capture_path if label != "provided_snapshot" else None)
data, suite, recs, metrics, manifest = runs["website_before"]
target_id = manifest["target_user_id"]
display(recs.groupby(["algorithm","score_type","status"], dropna=False).size().rename("count").reset_index())''')

methods=[
 ('cbf','CBF theo kỹ năng',r'$s(u,j)=x_u^T x_j/(\|x_u\|\|x_j\|)$ trên vector nhị phân kỹ năng. Jaccard = giao/hợp; Pearson = cosine của vector đã trừ trung bình. Hồ sơ rỗng dùng Popularity có nhãn; job rỗng có nội dung bằng 0. CBF này chỉ dùng kỹ năng, không giả định backend website dùng cùng đặc trưng.'),
 ('cf','CF theo hành vi',r'Tính cosine giữa các cột của $B$, bỏ đường chéo. Điểm job là tổng có trọng số các tương đồng với hành vi dương của user, chia cho $\max(\sum_i B_{ui},1)$. Không có hỗ trợ đồng xuất hiện thì dùng dự phòng.'),
 ('hybrid','Hybrid kết hợp',r'$s=0.55\,norm(s_{CBF})+0.45\,norm(s_{CF})$, với norm là min-max theo user. Không trộn điểm rating dự phòng vào affinity CF. Thiếu một nhánh thì dùng nhánh còn lại có nhãn; thiếu cả hai dùng Popularity.'),
 ('user_knn','User KNN',r'Chọn tối đa 5 user có cosine cao nhất trên vector rating, loại chính user. $\hat r_{uj}=\sum_v sim(u,v)r_{vj}/\sum_v sim(u,v)M_{vj}$. Mẫu số chỉ gồm người đã rating job. Không có láng giềng hợp lệ dùng Popularity.'),
 ('item_knn','Item KNN',r'Chọn tối đa 5 job có cosine cao nhất trên cột rating, bỏ chính job. $\hat r_{uj}=\sum_i sim(j,i)r_{ui}/\sum_i sim(j,i)M_{ui}$. Giữ mask quan sát; không coi missing là đánh giá 0.'),
 ('popularity','Popularity',r'Baseline dùng trung bình Bayes $s_j=(\sum_u r_{uj}+5\mu)/(n_j+5)$. Đây là biến thể chất lượng rating có prior, không phải bộ đếm lượt xem. Khi không có rating toàn bộ dữ liệu, prior trung tính =3 và có nhãn.'),
 ('sgd','Model based CF SGD',r'$\hat r_{uj}=\mu+b_u+b_j+p_u^Tq_j$. Tối thiểu hóa sai số bình phương trên rating quan sát cùng regularization; cập nhật SGD 45 epoch, 12 nhân tố, learning rate 0.012, reg 0.04. User/job chưa huấn luyện dùng prior, không dùng vector ngẫu nhiên để xếp hạng.'),
 ('als_explicit','ALS Explicit',r'$\hat r_{uj}=\mu+p_u^Tq_j$. Luân phiên giải ridge trên các rating quan sát sau khi trừ trung bình; 12 nhân tố, 12 vòng, reg=0.4. Không áp dụng loss cho các ô thiếu; không clip dự đoán.'),
 ('als_implicit','ALS Implicit',r'$P_{uj}=1[B_{uj}>0]$, $C_{uj}=1+16B_{uj}$. Tối thiểu hóa $\sum_{u,j} C_{uj}(P_{uj}-p_u^Tq_j)^2+0.7(\|p_u\|^2+\|q_j\|^2)$; 12 nhân tố, 10 vòng. Rating thấp không tạo preference dương. Đây là affinity, không phải rating và không tính RMSE cho nó.')
]
for ix,(key,title,explain) in enumerate(methods,1):
    md(f'## 4 {ix} {title}\n{explain}\n\nBảng sau là Top-10 của đúng user 458 trong snapshot trước thu ảnh. Ảnh là kết quả website có nhãn thuật toán đã kiểm tra; hai bên không có cam kết đồng nhất backend hoặc snapshot.')
    code(f'''display(recs[recs.algorithm.eq("{key}")][["rank","job_id","title","score","score_type","fallback"]])
display(metrics[metrics.algorithm.eq("{key}")][["k","test_users","hit_rate","recall","ndcg","catalog_coverage","fallback_fraction","rmse_positive_holdout","mae_positive_holdout"]])
cap=next(c for c in captures if c["algorithm"]=="{key}" and c["similarity"]=="cosine")
display(Markdown(f"Website trả **{{cap['n_items']}}** kết quả, HTTP {{cap['http_status']}}; thời điểm UTC {{cap['captured_at']}}."))
display(Image(filename=cap["screenshot"],width=1000))''')
md('''## 5 Đánh giá ngoại tuyến không rò rỉ
Do rating không có thời gian đáng tin cậy, dùng random positive leave-one-out với seed 42. User cần ít nhất 3 rating; giữ một rating ≥4 cho test, job test phải mở và còn ít nhất một rating train từ user khác. Xóa mọi lượt xem của chính cặp test khỏi train.

HitRate là tỷ lệ user tìm được ít nhất một mục đúng; Recall là tỷ lệ mục relevant được thu hồi. Mỗi user chỉ có một test item nên HR=Recall. NDCG dùng chiết khấu log2 theo hạng. Coverage là số job được gợi ý / số job mở. Báo cáo tỷ lệ fallback và số mẫu cùng metrics. RMSE/MAE chỉ cho phương pháp dự đoán rating, trên **holdout tích cực**, không suy ra chất lượng trên toàn thang rating hoặc độ phù hợp cá nhân hiện tại.''')
code('''train,test,split = positive_holdout(data,config)
held=set(zip(test.user_id,test.job_id))
assert not held.intersection(zip(train.ratings.user_id,train.ratings.job_id))
assert not held.intersection(zip(train.views.user_id,train.views.job_id))
print({k:v for k,v in split.items() if k not in ["exclusions"]})
all_metrics=pd.concat([r[3].assign(source=label) for label,r in runs.items()],ignore_index=True)
display(all_metrics[["source","algorithm","k","test_users","hit_rate","recall","ndcg","catalog_coverage","fallback_fraction"]])
display(Image(filename="outputs/notebook/website_before/figures/offline_metrics.png"))
display(Image(filename="outputs/notebook/provided_snapshot/figures/training_loss.png"))''')
md('''## 6 Đối sánh website và Python
So theo job ID, không theo tiêu đề hoặc thang điểm. Có số kết quả thực, giao nhau, Jaccard và chênh lệch hạng của job chung. `Overlap@10` không tính khi một bên ít hơn 10. HTTP lỗi hoặc thiếu capture là unavailable, không phải danh sách rỗng thành công. Website trả 0 kết quả với 6 phương pháp khi tài khoản chưa có tương tác; không kết luận backend sai.

`candidate_count` website và số job mở trong CSV có thể khác; diagnostics chỉ xuất 50 dòng mẫu nên không đủ chứng minh cùng tập ứng viên. Các bảng này là đối chiếu tham khảo, không phải phép kiểm chứng tái tạo backend. CBF Pearson được chụp ở phiên khôi phục muộn hơn, có timestamp riêng.''')
code('''comparison,ranks=compare_website(web,recs,captures=captures,target_user_id=target_id)
display(comparison)
display(ranks.head(20))
display(pd.DataFrame(captures)[["algorithm","similarity","n_items","candidate_count","captured_at"]])
cbf_results=[]
for similarity in ["cosine","jaccard","pearson"]:
    s=RecommenderSuite(replace(config,similarity=similarity)).fit(data)
    r=s.recommend(target_id,algorithms=["cbf"])
    r["similarity"]=similarity
    cbf_results.append(r)
    c,_=compare_website(web,r,captures=captures,similarity=similarity,target_user_id=target_id)
    display(c[c.algorithm.eq("cbf")])
cbf_results=pd.concat(cbf_results,ignore_index=True)
cbf_results.to_csv("outputs/notebook/cbf_similarity.csv",index=False,encoding="utf-8-sig")
display(cbf_results[["similarity","rank","job_id","score_type","fallback"]])
for similarity in ["jaccard","pearson"]:
    c=next(c for c in captures if c["algorithm"]=="cbf" and c["similarity"]==similarity)
    display(Image(filename=c["screenshot"],width=1000))''')
md('''## 7 Nhận xét và công việc cần dữ liệu bổ sung
Chín thuật toán chạy trên cùng quy tắc và train/test trong từng snapshot. Các mô hình cộng tác bị giới hạn bởi độ thưa, ít user có rating và cold-start. Tài khoản sinh viên chưa có hồ sơ/rating, nên 80/90 dòng Python của snapshot website là fallback (Popularity là baseline model). Không có căn cứ khẳng định các việc này phù hợp sở thích cá nhân.

Đăng 10 tin, chuẩn hóa hồ sơ và tạo rating còn chờ xác nhận nội dung thật. Không đưa kỹ năng suy đoán hoặc rating do hệ thống tự bịa vào dữ liệu. Mật khẩu do người dùng tự đổi. Xem `STATUS.md` cho trạng thái hoàn thành và `data/import/IMPORT_PREVIEW.md` cho danh sách chờ duyệt.

Nguồn: đề LabDSS WebsiteRECSYS do giảng viên cung cấp; website RECSYS; nguồn tuyển dụng gốc Bosch/KMS trong danh sách import; source Python của gói này là định nghĩa chính xác các biến thể đã chạy.''')
nb.cells=cells
nb.metadata={'kernelspec':{'display_name':'Python (LabDSS)','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.13'}}
path=ROOT/'LabDSS_RECSYS_9_thuat_toan.ipynb'
nbf.write(nb,path)
print(f'{len(cells)} cells written to {path.name}')
