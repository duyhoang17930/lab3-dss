# LabDSS Website RECSYS

Nguyễn Hoàng Hà — MSSV 102230343. Bài cá nhân, không tự điền nhóm học phần.

Notebook dùng dữ liệu MEDAJob thật, đủ 9 thuật toán, có kiểm tra dữ liệu, tách full-snapshot và train/test, đối sánh website theo ID. Xem [STATUS.md](STATUS.md) trước khi dùng làm bài nộp: phần hồ sơ/rating/import còn chờ xác nhận, báo cáo chưa qua render từng trang.

## Chạy từ đầu trên Windows

Python 3.13, PowerShell, đứng tại thư mục Lab3:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -X utf8 scripts/execute_notebook.py
```

Lệnh cuối chạy lại toàn bộ notebook bằng kernel mới của đúng interpreter, không cần đăng ký kernel hệ thống. Mất khoảng vài phút tùy máy. Không cần kết nối website để tái lập kết quả đã lưu. Không có mật khẩu hoặc phiên đăng nhập trong mã nguồn.

Notebook ưu tiên `data_MEDAJOB`, `data/raw/website_before/csv`, `data/raw/website_after_capture/csv`. Nếu không có các thư mục riêng tư, nó dùng các bản dữ liệu thật đã giảm thông tin cá nhân trong `data/shared/`; luôn in đường dẫn, snapshot ID và cờ privacy_reduced. Không fallback sang dữ liệu demo. Hash file thay đổi sau lược bỏ cột, nên snapshot ID của bản chia sẻ khác bản raw; nội dung mô hình được kiểm tra tương đương.

## Chạy một snapshot bằng CLI

```powershell
.\.venv\Scripts\python.exe -X utf8 -m job_recsys.run --data data_MEDAJOB --output outputs/provided_snapshot
.\.venv\Scripts\python.exe -X utf8 -m job_recsys.run --data data/shared/website_before --output outputs/shared_replay --website-csv data/website/verified_baseline/recommendations.csv --capture-manifest data/website/verified_baseline/capture_manifest.json
```

Không thay `--target` bằng tài khoản khác khi user không tồn tại. Bản gốc thiếu `sv102230343` nên gợi ý cho tài khoản đó rỗng có chủ đích, nhưng đánh giá toàn dataset vẫn chạy.

## Cấu trúc

- `LabDSS_RECSYS_9_thuat_toan.ipynb`: notebook đã chạy, 30 cell, công thức và giải thích tiếng Việt.
- `job_recsys/`: adapter dữ liệu, 9 thuật toán, holdout/metrics, pipeline.
- `configs/experiment.json`: cấu hình chung, seed42, Top10, k5, factors12.
- `tests/`: kiểm thử dữ liệu, cold-start, score, ranking, tái lập, rò rỉ và trạng thái capture.
- `outputs/notebook/`: kết quả raw đã chạy; mỗi snapshot có manifest, CSV và biểu đồ.
- `data/shared/`: bản giảm thông tin cá nhân, không phải dữ liệu tổng hợp; provenance kèm hash nguồn.
- `data/website/verified_baseline/`: 11 capture JSON, manifest và CSV kết quả thực.
- `evidence/website/verified_baseline/`: 9 ảnh Cosine và CBF Jaccard/Pearson.
- `data/import/`: nguồn tuyển dụng, kiểm tra trùng và CSV 19 cột **chưa import**.
- `reports/`: báo cáo Word và bản Markdown.
- `verification/`: kết quả kiểm thử và kiểm tra tính toàn vẹn.

Đã giải nén ZIP sang thư mục riêng và chạy lại notebook từ kernel sạch chỉ bằng dữ liệu `data/shared`: 14 cell mã,0 lỗi; kết quả gợi ý, metrics và phân chia train/test của cả3 snapshot khớp bản raw (ngoại trừ mã snapshot do lược bỏ cột). Chi tiết trong `verification/package_replay.json`.

Không dùng `evidence/website/baseline` hoặc `data/website/baseline`: đây là lần thu thử có ảnh cũ khi HTTP429, không đưa vào gói nộp. Dữ liệu raw, backups và môi trường `.venv` cũng không đóng gói.

## Định nghĩa và giới hạn

CBF dùng vector nhị phân kỹ năng. CF hành vi dùng tương đồng item trên tín hiệu tích cực. Hybrid trộn min-max CBF/CF với alpha0.55. KNN dự đoán rating với mask quan sát. Popularity là trung bình Bayes có prior5. SGD có bias, ALS Explicit dùng rating đã trừ trung bình, ALS Implicit dùng preference/confidence. Xem notebook và [METHODS.md](METHODS.md).

Điểm giữa các phương pháp không cùng thang. Giữ score thô, loại rated job và job không mở; đồng điểm theo ID. Điểm model xếp trước dự phòng Popularity. `status`, `fallback`, `score_type` giải thích nhánh sử dụng. Giới hạn bộ nhớ dense được báo lỗi rõ, không tự cắt 300 user/600 job.

Holdout ngẫu nhiên một rating ≥4/user, user có ≥3 rating và item test còn dữ liệu train. Loại cả view của cặp test. HR=Recall vì mỗi user một relevant item. RMSE/MAE chỉ cho dự đoán rating và chỉ trên holdout tích cực. Chưa có đánh giá theo thời gian, repeated split hoặc tuning độc lập.

Website trả danh sách rỗng thành công khác với thiếu capture/HTTP lỗi. `Overlap@10` để trống nếu thiếu số lượng; chênh hạng chỉ tính trên ID chung. Diagnostics chỉ chứa 50 dòng mẫu, không phải tập ứng viên đầy đủ. Chưa biết tham số backend và website thay đổi trong lúc thu ảnh, nên không tuyên bố Python tái tạo backend.

## Cập nhật phần website sau khi có xác nhận

1. Người dùng cung cấp kỹ năng thật, nghề và địa điểm mong muốn; duyệt hồ sơ/rating cụ thể trước khi ghi.
2. Duyệt J01–J10 trong `data/import/IMPORT_PREVIEW.md`. Kiểm tra lại nguồn, danh mục website và quyền import ngay trước ghi; J03 có loại `intern` cần xác minh template/backend hỗ trợ, không tự đổi thành full-time.
3. Import một lô đã kiểm tra. Ghi ID và số thành công, chỉ thử lại dòng lỗi. Không ứng tuyển và không đóng tin của người khác.
4. Xuất snapshot mới, chụp lại 9 phương pháp cùng điều kiện và các thao tác cập nhật. Không thay baseline bằng ảnh hậu cập nhật không ghi timestamp.
5. Người dùng tự đổi mật khẩu. Không ghi mật khẩu mới vào code hoặc báo cáo.
6. Chạy lại notebook, cập nhật báo cáo và render kiểm tra từng trang trước khi gắn VERIFIED.

`scripts/prepare_import.py` chỉ tạo preview, không gửi lên website. `scripts/capture_browser_helpers.mjs` chỉ dùng với phiên đã xác thực trong bộ nhớ; không có chức năng đăng nhập, import hoặc apply.

## Báo cáo Word

Builder `scripts/build_report.py` dùng python-docx của runtime đi kèm và cần đề gốc đặt cạnh notebook để dựng lại báo cáo. Các lệnh chạy notebook/tests không cần đề gốc hoặc python-docx. Tài liệu theo 7 mục của đề, giữ khổ A4 và lề nguồn. Không nhúng đề gốc chứa mật khẩu vào gói. Báo cáo hiện là `DRAFT_NOT_VERIFIED`: canonical renderer thiếu `soffice.exe`; kiểm tra OOXML không thay thế render. Không nên nộp như bản hoàn tất.

## Riêng tư

Gói chỉ giữ user ID giả danh và tín hiệu cần tính toán; loại tên/email/điện thoại/địa chỉ/CV của người khác, token và raw export. ID vẫn có thể liên kết với hệ thống gốc; đây là giảm thiểu dữ liệu, không khẳng định ẩn danh không thể đảo ngược. Chỉ chia sẻ gói cho phạm vi học phần cần thiết.
