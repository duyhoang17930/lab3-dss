# AGENT HANDOFF — LAB DSS: WEBSITE RECSYS GỢI Ý VIỆC LÀM

> **Tài liệu bàn giao ngữ cảnh và đặc tả tác vụ cho coding/research agent.**  
> Ngôn ngữ làm việc: **Tiếng Việt**.  
> Phiên bản tài liệu: **1.0 — 28/10/2026**.  
> Phạm vi: **chỉ bài LabDSS WebsiteRECSYS**; không trộn với các đồ án/nghiên cứu khác.  
> Trạng thái: **chưa có CSV Template của chức năng Nhà tuyển dụng, chưa có MEDAJob CSV thật, chưa có kết quả gợi ý của website; chưa được coi là hoàn thành lab**.

---

## 0. CÁCH AGENT PHẢI ĐỌC TÀI LIỆU NÀY

**Đọc toàn bộ tài liệu trước khi thao tác.** Đây là hướng dẫn triển khai công việc, không phải báo cáo kết quả đã làm.

Phân biệt bốn loại thông tin:

- **[GỐC]**: yêu cầu được nêu trong tài liệu `LabDSS WebsiteRECSYS.docx` do người dùng cung cấp. Các mục/tên thuật toán từ tài liệu gốc được giữ nguyên.
- **[CHỐT]**: phân công trách nhiệm và phạm vi do người dùng quyết định trong hội thoại.
- **[ĐÃ KIỂM TRA]**: thông tin đã kiểm tra trực tiếp trên tệp hoặc chạy thử trong môi trường trước khi viết handoff.
- **[ĐỀ XUẤT]**: thiết kế kỹ thuật/học thuật để thực hiện lab tốt hơn; **không** được tuyên bố là yêu cầu chính thức của giảng viên hay cách website triển khai.
- **[CHƯA XÁC MINH]**: chi tiết phải đợi website/CSV/screenshot thật mới kết luận được.

**Nguyên tắc nguồn sự thật:** (1) tài liệu gốc, (2) yêu cầu và quyết định của người dùng, (3) dữ liệu thực sự xuất từ website và CSV Template, (4) giao diện/ảnh chụp website thật, (5) mã nguồn và kết quả thực nghiệm có thể tái lập, (6) các giả định của agent. Khi có mâu thuẫn, nêu rõ thay vì tự lấp chỗ trống.

**Nghiêm cấm:** bịa tin tuyển dụng, bịa URL, tự điền kết quả website chưa nhận, tạo ảnh chụp màn hình giả, ghi số liệu demo thành số liệu MEDAJob thật, nói đã import khi người dùng chưa xác nhận, lặng lẽ sửa dữ liệu để đạt chỉ số đẹp, tự động commit/push hoặc sửa/xóa dữ liệu người dùng khi chưa được yêu cầu.

### 0.1. Yêu cầu trả lời của agent

- Viết **tiếng Việt, rõ ràng, có cấu trúc, kỹ thuật đủ sâu nhưng không dài dòng vô ích**.
- Tiến hành phần việc có đủ đầu vào; không liên tục hỏi những thông tin chưa cần cho giai đoạn hiện tại.
- Nêu tiến độ theo các trạng thái: `TODO`, `IN_PROGRESS`, `BLOCKED_USER`, `BLOCKED_EXTERNAL`, `DONE`, `VERIFIED`.
- `DONE` nghĩa là có tệp hoặc output; `VERIFIED` nghĩa là đã kiểm tra tiêu chí nghiệm thu và có bằng chứng.
- Nếu thiếu CSV Template, vẫn có thể nghiên cứu 10 tin tuyển dụng và tạo **bảng trung gian**; **không đoán schema CSV import**.
- Nếu thiếu MEDAJob, vẫn có thể viết module, unit tests, notebook demo; **không báo đã chạy đánh giá dữ liệu thật**.
- Kết thúc mỗi giai đoạn phải bàn giao file thực tế, chỉ ra việc người dùng cần làm tiếp theo, và liệt kê điều chưa xác minh.

---

# PHẦN I — BỐI CẢNH, MỤC TIÊU, PHÂN CÔNG

## 1. Thông tin chính của bài lab

**[GỐC]**

- Tên tài liệu: `LabDSS WebsiteRECSYS.docx`.
- Tiêu đề tài liệu: **HỆ THỐNG RECSYS GỢI Ý VIỆC LÀM**.
- Môn/ngữ cảnh: bài thực hành hệ hỗ trợ ra quyết định (DSS) liên quan gợi ý việc làm.
- Website thực hành: <http://wandertour.ddns.net:8020/>.
- Tài liệu mô tả website tổng hợp thông tin việc làm tại các tỉnh thành Việt Nam theo thời gian thực; mô tả này **là phát biểu trong đề**, không phải xác nhận độc lập về chất lượng hay độ cập nhật của website.
- Tài liệu yêu cầu SV điền thông tin nhóm học phần, mã sinh viên và họ tên thành viên.
- Tài liệu ghi đăng nhập theo mẫu `svMaSinhVien`, có ví dụ về mã số sinh viên và mật khẩu khởi tạo; **không lưu lại mật khẩu thực tế, cookie hoặc token vào repo/báo cáo**. Sinh viên tự đăng nhập và đổi mật khẩu.

**[CHỐT]** Người dùng muốn hoàn thành lab bằng cách giao tối đa các khâu có thể tự động cho agent. Danh mục tuyển dụng tập trung vào **Công nghệ thông tin (CNTT/IT)**. Người dùng **tự chịu trách nhiệm các thao tác tài khoản và website** được liệt kê ở mục 3.1.

**[CHƯA XÁC MINH]** Trước khi tạo tài liệu này, môi trường duyệt web không mở được URL ở trên; **chưa xác thực giao diện, nội dung, selector, trạng thái website, định dạng export, thuật toán backend**. Agent không được tự giả định rằng website hiện sẵn hoạt động hoặc có đúng các tên nút ngoài những mục được mô tả trong đề.

## 2. Mục tiêu đầu ra cuối cùng

Hoàn thành một bộ nộp bài gồm:

1. **Phần thao tác website**: bằng chứng người dùng đã đăng nhập, cập nhật hồ sơ/skills, kiểm tra tin cũ, đăng ít nhất 10 tin CNTT thật, tìm việc, tạo rating, chạy chức năng gợi ý và lưu kết quả.
2. **Phần dữ liệu**: bảng 10+ tin IT nguồn thật + URL kiểm chứng; CSV import **đúng template thật**, hồ sơ nguồn tin, ảnh/danh sách đã import; MEDAJob export thật được lưu nguyên trạng.
3. **Phần thuật toán**: code Python triển khai **9 phương pháp** theo danh sách trong đề, với mô tả rõ phiên bản học thuật do agent chọn; chạy và tạo Top-N bằng dữ liệu thật khi có thể.
4. **Phần kiểm chứng**: bảng so sánh kết quả Python với gợi ý trên website cho cùng user/thuật toán/dữ liệu/điều kiện, kèm độ lệch và phân tích nguyên nhân.
5. **Phần báo cáo**: báo cáo `.docx` bằng tiếng Việt, định dạng học thuật tự nhiên, ưu tiên Times New Roman, giữ sát cấu trúc/bố cục tài liệu lab nếu nó là mẫu phải điền; có hình từ dữ liệu thật, kết quả thực nghiệm, bảng biểu và tài liệu tham khảo.
6. **Bộ mã nguồn nộp kèm**: `.py`/`.ipynb`, `requirements.txt`, README hướng dẫn chạy, dữ liệu mẫu an toàn, tests, CSV kết quả, manifest nguồn và minh chứng.

Điều kiện thành công: **không chỉ có chương trình chạy được**, mà còn chứng minh được kết quả thực hành theo các mục 1–7 của đề, không đánh tráo demo với dữ liệu thật.

## 3. Phân công CHỐT giữa người dùng và agent

### 3.1. NGƯỜI DÙNG TỰ LÀM — KHÔNG giao agent trừ khi quyết định lại

1. **Đăng nhập website** bằng tài khoản sinh viên, đổi mật khẩu và quản lý phiên đăng nhập.
2. **Cập nhật hồ sơ ứng viên**, thông tin tài khoản và kỹ năng trên web; agent chỉ chuẩn bị nội dung skills nếu được yêu cầu.
3. **Kiểm tra** tin tuyển dụng hiện có, đặc biệt trùng lặp/hết hạn/quyền đóng tin; tự quyết định đóng tin nếu phù hợp.
4. **Import CSV tuyển dụng** do agent chuẩn bị, đối chiếu thông báo import và danh sách tin sau import.
5. **Tìm việc và đánh giá rating** theo mong muốn thật để tạo lịch sử tương tác.
6. **Chạy gợi ý trên website**, chọn thuật toán/độ đo nếu giao diện hỗ trợ, **chụp hình và lưu kết quả gợi ý**.
7. **Tải dữ liệu và cung cấp dữ liệu từ website**: CSV Template tuyển dụng, MEDAJob CSV và các kết quả/ảnh cần để đối sánh.

**Không yêu cầu người dùng cung cấp mật khẩu, mã 2FA, cookie, token, session hoặc quyền truy cập hệ thống cho agent.** Không hướng dẫn vô hiệu hóa cơ chế bảo vệ tài khoản.

### 3.2. AGENT PHẢI LÀM

1. Phân tích đề lab, lập kế hoạch gắn với yêu cầu và đầu ra.
2. **Tìm tối thiểu 10 tin tuyển dụng IT thực**, ưu tiên tin còn hiệu lực, có link gốc kiểm chứng; trích xuất trường dữ liệu và đánh dấu độ tin cậy.
3. Tạo **bảng dữ liệu trung gian** và chuyển thành CSV import **sau khi có template thật**; kiểm tra schema, encoding, dấu phân cách, định dạng ngày, trường bắt buộc, trùng lặp.
4. Chuẩn bị hướng dẫn để người dùng nhập/import và xác nhận kết quả, không thao tác trên tài khoản của họ.
5. Thiết kế pipeline đọc và chuẩn hóa **MEDAJob CSV thật** (tùy cấu trúc thực tế); không đoán schema như sự thật.
6. Lập trình/hoàn thiện và kiểm thử đầy đủ 9 phương pháp được liệt kê trong đề.
7. Chạy thực nghiệm có log, seed, phiên bản, thời điểm, điều kiện thí nghiệm, CSV Top-N và bảng đo lường.
8. Đối sánh với kết quả từ website khi người dùng cung cấp; không có kết quả website thì để trạng thái `BLOCKED_USER`.
9. Viết báo cáo Word và bàn giao đầy đủ code/output/minh chứng, **chỉ dùng ảnh chụp thật** do người dùng cung cấp hoặc ảnh chụp thực tế từ phiên được cho phép.
10. Kiểm tra chất lượng, khả năng chạy lại, tính toàn vẹn và bảo mật dữ liệu trước khi nộp.

### 3.3. Ranh giới phụ thuộc

| Công việc agent | Có thể bắt đầu ngay? | Phụ thuộc | Trạng thái ban đầu |
|---|---:|---|---|
| Nghiên cứu 10+ tin CNTT thật | Có | Internet và nguồn tin còn truy cập | `TODO` |
| Tạo bảng trung gian `jobs_verified.csv` | Có | Tin tuyển dụng đã kiểm chứng | `TODO` |
| Tạo **CSV import cuối cùng** | Chưa | Người dùng cung cấp CSV Template | `BLOCKED_USER` |
| Viết cơ sở thuật toán, tests, notebook demo | Có | Python/runtime | `TODO` / có notebook khởi đầu |
| Chuẩn hóa MEDAJob **thật** | Chưa | Người dùng xuất MEDAJob CSV | `BLOCKED_USER` |
| Chạy thực nghiệm MEDAJob thật | Chưa | MEDAJob CSV, schema đúng | `BLOCKED_USER` |
| Đối sánh website–Python | Chưa | Screenshot/Top-N và điều kiện web | `BLOCKED_USER` |
| Viết phần lý thuyết/khung báo cáo | Có | Đề lab | `TODO` |
| Chốt báo cáo kết quả thực nghiệm | Chưa | Output thật, minh chứng website | `BLOCKED_USER` |

---

# PHẦN II — TRÍCH XUẤT ĐÚNG YÊU CẦU GỐC

## 4. Cấu trúc chính thức từ file Word (không thay đổi ý nghĩa)

**[GỐC]** Tài liệu có các mục:

1. **Giới thiệu**.
2. **Chức năng [Hồ sơ]**.
3. **Chức năng [Nhà tuyển dụng]**.
4. **Chức năng [Tìm việc]**.
5. **Chức năng [Tìm việc]/[Gợi ý việc làm]**.
6. **Tải bộ dữ liệu MEDAJob, lập trình tính toán và đối sánh kết quả**.
   1. `6.1. CBF - Theo kỹ năng`.
   2. `6.2. CF - Theo hành vi`.
   3. `6.3. Hybrid - Kết hợp`.
   4. `6.4. User-KNN`.
   5. `6.5. Item-KNN`.
   6. `6.6. Popularity - Phổ biến`.
   7. `6.7. Model-based CF - SGD`.
   8. `6.8. Model-based CF - ALS Explicit`.
   9. `6.9. Model-based CF - ALS Implicit`.
7. **Tham khảo**.

**Yêu cầu nguyên văn về nghiệp vụ (diễn giải sát nguồn):**

### 4.1. Giới thiệu
- Sinh viên đăng nhập website bằng tài khoản được cấp.
- Đổi mật khẩu sau đăng nhập.

### 4.2. Hồ sơ
- Cập nhật thông tin tài khoản.
- Cập nhật hồ sơ ứng viên.
- Trường kỹ năng mô tả bằng các từ khóa ngăn cách bằng dấu phẩy; đề cho ví dụ `python, fastapi, sql, data engineering`.

### 4.3. Nhà tuyển dụng
- Xem và tìm kiếm tin theo **từ khóa, tên công ty, địa điểm, loại hình, ...**.
- Đóng vai trò nhà tuyển dụng kiểm tra các tin đã có; đóng tin hết hạn.
- **Mỗi nhóm đăng ít nhất 10 tin tuyển dụng thật, có link kiểm chứng**.
- Chú ý **kiểm tra trùng lặp** với tin sẵn có.
- Có thể tải CSV Template rồi Import CSV.
- Có **hình ảnh liệt kê các tin mới của nhóm**.
- Website nguồn được đề gợi ý: TopCV, VietnamWorks, CareerViet, Vieclam24h, JobsGO, ITviec, LinkedIn, Cake.

### 4.4. Tìm việc
- Tìm tin theo từ khóa, tên công ty, địa điểm, loại hình.
- Tìm một số việc làm phù hợp.
- Đánh giá rating **theo đúng mong muốn** để tạo hồ sơ người dùng.

### 4.5. Gợi ý việc làm
- Chọn thuật toán và cách tính độ đo (nếu giao diện cung cấp).
- Xem kết quả website.
- Kiểm tra độ phù hợp với hồ sơ kỹ năng và rating.
- Phân tích, đánh giá.

### 4.6. MEDAJob
- Vào **[Hồ sơ] → [Tải MEDAJob CSV]**.
- Tải CSV mới nhất.
- **Lập trình tính toán và đối sánh kết quả** bằng các phương pháp 6.1–6.9 ở trên.

### 4.7. Điểm tài liệu gốc KHÔNG nêu

Tài liệu **không cung cấp**:

- Cấu trúc CSV Template import, tên cột, kiểu dữ liệu và validation.
- Schema thực tế của MEDAJob CSV, số file khi export, quan hệ giữa các bảng, mã user/job.
- Cách website tính mỗi thuật toán, công thức chuẩn hóa, hyperparameters, chọn `k`, `alpha`, seed, xử lý cold-start.
- Thang rating, có/không rating implicit, timestamp, logging API, cách tie-break.
- Độ đo similarity cụ thể nào website hỗ trợ và ý nghĩa của các tùy chọn UI.
- Số tin tối thiểu cần người dùng rating, số lượng Top-N cố định, phương pháp đánh giá bắt buộc như Recall/NDCG.
- Tiêu chí chấm điểm cụ thể; template báo cáo kết quả đầy đủ hay cấu trúc file mã nguồn bắt buộc.
- Số lượng trang/hình/độ dài báo cáo.

Tất cả nội dung kỹ thuật bổ sung trong phần sau là **đề xuất của agent**, không ghi thành quy định của giảng viên.

---

# PHẦN III — QUY TRÌNH CỤ THỂ TỪNG GIAI ĐOẠN

## 5. Giai đoạn A — Tìm nguồn và chuẩn bị ít nhất 10 tin tuyển dụng CNTT

**Mục tiêu:** xây dựng tập dữ liệu có nguồn rõ ràng để người dùng kiểm tra rồi import.

### 5.1. Tiêu chuẩn từng tin

- Thuộc lĩnh vực **IT/CNTT**. Ưu tiên Backend Developer, Frontend Developer, Full-stack Developer, Software Engineer, QA/Test Engineer, DevOps, Data Engineer, Data Analyst, AI/ML Engineer, Mobile Developer, System/Network Engineer, Database Engineer; có thể có Internship/Juniors nếu tin thật.
- Là tin tuyển dụng thật của đơn vị có thể xác định, hoặc đăng trên nền tảng tuyển dụng có thông tin công ty/nguồn gốc.
- Có **URL cụ thể dẫn đến trang tin**, không chỉ URL trang chủ của website tuyển dụng.
- Ưu tiên tin còn hiển thị tuyển dụng tại thời điểm kiểm tra, ghi rõ `checked_at` và trạng thái.
- Không dùng nguồn sao chép không rõ, tin tuyển dụng đã hết hạn mà giả là mới, hoặc URL tưởng tượng.
- Không tự suy ra lương, địa điểm, hình thức, kinh nghiệm, email liên hệ, hạn ứng tuyển khi không hiển thị; để trống hoặc `not_specified` theo quy tắc của template thực tế.
- Tránh tin trùng trong **chính danh sách 10+ tin**; người dùng sẽ kiểm tra trùng với database website.
- Chuẩn bị **12–15 ứng viên tin nếu có thể**, chọn tối thiểu 10 sau kiểm tra trùng/hết hạn. Số 12–15 là **đề xuất** để có dự phòng; không phải yêu cầu của đề.

### 5.2. Nguồn tham khảo theo đề

- <https://www.topcv.vn>
- <https://www.vietnamworks.com>
- <https://careerviet.vn>
- <https://vieclam24h.vn>
- <https://jobsgo.vn>
- <https://itviec.com>
- <https://www.linkedin.com>
- <https://www.cake.me>

Ưu tiên trang tuyển dụng chính thức của công ty nếu tin có cả link nguồn và link gốc, đồng thời giữ URL trang mà agent thực sự đọc. Không tự động thực hiện crawling vi phạm điều khoản truy cập; dùng công cụ tìm kiếm hoặc đọc trang công khai phù hợp.

### 5.3. Bảng dữ liệu trung gian **trước khi có CSV Template**

Đề xuất `data/processed/job_candidates.csv` với tối thiểu các trường:

| Cột trung gian | Ý nghĩa |
|---|---|
| `candidate_id` | ID nội bộ của tin trong danh sách dự kiến, không giả là job_id website |
| `job_title` | Chức danh ghi trên nguồn |
| `company_name` | Tên công ty |
| `location` | Thành phố/vùng/remote nếu có |
| `employment_type` | Full-time/part-time/internship/contract nếu nguồn nêu |
| `work_mode` | On-site/hybrid/remote nếu nguồn nêu |
| `experience` | Yêu cầu kinh nghiệm nếu có |
| `salary` | Chỉ ghi khi nguồn cung cấp, không tự bịa |
| `job_description` | Mô tả ngắn gọn, trung thực; không copy nguyên văn quá dài |
| `skills` | Danh sách kỹ năng suy ra từ tin, có thể được chuẩn hóa |
| `source_site` | Nền tảng hoặc website công ty |
| `source_url` | Link cụ thể đến tin thật |
| `checked_at` | ISO 8601 với múi giờ, ví dụ `2026-10-28T14:20:00+07:00` |
| `source_status` | `active`, `expired`, `uncertain`, `inaccessible` |
| `verification_note` | Căn cứ kiểm chứng và phần chưa chắc chắn |
| `duplicate_key` | Khóa chuẩn hóa chống trùng nội bộ |
| `approved_for_import` | `true/false`, chỉ true khi đã xác minh và người dùng duyệt nếu cần |

**Không ép schema trên thành schema của CSV Template website.** Khi có template, phải viết một adapter chuyển cột, không phá hủy thông tin nguồn trong bảng trung gian.

### 5.4. Kiểm tra trùng nội bộ

Các tầng kiểm tra đề xuất:

1. Chuẩn hóa URL (bỏ tracking parameters không cần thiết, đồng nhất slash/case khi an toàn).
2. Chuẩn hóa tên công ty/chức danh: lowercase, chuẩn hóa khoảng trắng, Unicode, các hậu tố pháp lý khi phù hợp.
3. So trùng cặp `(company_name, job_title, location)` và URL.
4. Nếu cùng công ty + vai trò nhưng khác địa điểm/mã requisition, coi là **nghi ngờ trùng**, không tự xóa.
5. Người dùng kiểm tra trực tiếp tin đã tồn tại trên web trước khi import; không tuyên bố 'không trùng database' chỉ từ danh sách CSV của agent.

### 5.5. Chuyển sang CSV import **sau khi nhận template**

1. Đọc CSV Template **nguyên bản dưới dạng bytes** để nhận encoding (`utf-8-sig`/`utf-8`/khác), delimiter, quote, tên cột, thứ tự cột; không thay đổi template bằng trực giác.
2. Xác định trường bắt buộc, kiểu dữ liệu và ví dụ hợp lệ từ hàng mẫu/nội dung UI; nếu không biết, lập bảng câu hỏi/đánh dấu chưa xác minh.
3. Tạo mapping `intermediate_column -> template_column` trong file cấu hình, có giải thích mọi chuyển đổi.
4. Giữ tiêu đề cột và thứ tự cột đúng như template; kiểm tra Unicode tiếng Việt và dấu phẩy/dấu xuống dòng trong mô tả.
5. Xuất `data/exports/job_import_ready.csv` bằng writer có quoting phù hợp; đọc ngược file bằng `pandas.read_csv`/`csv.DictReader` để kiểm chứng.
6. Tạo `reports/import_preview.md` mô tả số dòng, số thiếu trường, trùng nội bộ, URL nguồn và những giá trị chưa xác minh.
7. Người dùng tự **kiểm tra trùng trên website và import**; chỉ khi đã nhận được ảnh/thông báo từ website mới ghi nhận import hoàn tất.
8. Nếu website trả về lỗi theo từng dòng, sửa **những dòng bị lỗi** và xuất bản `v2`; tránh import lại mọi dòng đã thành công gây trùng.

### 5.6. Nghiệm thu giai đoạn A

- [ ] Tối thiểu **10 tin IT thật và có URL kiểm chứng**.
- [ ] Tại thời điểm trích xuất, tình trạng từng tin được ghi rõ; tin không thể xác minh không bị âm thầm đưa vào nhóm 'đã xác minh'.
- [ ] Không có URL giả, công ty giả, lương/địa điểm bịa.
- [ ] Có tệp nguồn trung gian, log kiểm tra và thời điểm tra cứu.
- [ ] Nếu đã có template: import CSV khớp cột, đọc lại được, số dòng hợp lệ.
- [ ] Có hướng dẫn người dùng kiểm tra trùng trước khi import.
- [ ] **Chỉ người dùng xác nhận** số tin import thực sự thành công trên hệ thống.

## 6. Giai đoạn B — Hồ sơ, rating và thu thập kết quả website (người dùng thao tác)

### 6.1. Hồ sơ

Người dùng đăng nhập, đổi mật khẩu, cập nhật hồ sơ. Agent có thể gợi ý chuỗi kỹ năng dạng CSV-style. Ví dụ minh họa:

```text
python, fastapi, sql, postgresql, rest api, docker, git
```

**Chú ý:** đây là chuỗi **gợi ý**, không phải kỹ năng thật đã được xác minh của người dùng. Người dùng quyết định nội dung phù hợp với hồ sơ cá nhân.

### 6.2. Rating

**[GỐC]** Sinh viên phải rating theo đúng mong muốn để tạo dữ liệu người dùng.

**[ĐỀ XUẤT]** Để thấy khác biệt giữa thuật toán, nên rating đa dạng các loại công việc và ghi lại thang điểm website nếu có. Ví dụ nếu web dùng 1–5 sao thì chọn điểm theo sở thích thực, không cần đạt một quota rating cố định. Có thể thử 8–15 rating **nếu thời gian và giao diện cho phép**, đây không phải yêu cầu của đề.

Vì gợi ý có thể phụ thuộc vào rating, người dùng **nên chụp hoặc xuất danh sách rating trước khi chạy gợi ý** để đóng băng bối cảnh; sau đó tránh thay đổi rating trong loạt đối sánh nếu mục tiêu là so sánh công bằng.

### 6.3. Phiếu ghi nhận mỗi lượt website gợi ý

Agent chuẩn bị form/bảng CSV để người dùng hoặc agent điền từ screenshot:

| Cột | Ý nghĩa |
|---|---|
| `capture_id` | Mã lượt chạy |
| `captured_at` | Thời điểm chụp kết quả (Asia/Ho_Chi_Minh) |
| `website_user_id` | Mã user tương ứng, nếu có và phù hợp bảo mật |
| `algorithm_ui_name` | **Chính xác chuỗi tên thuật toán** hiển thị |
| `similarity_ui_name` | Độ đo được chọn hoặc `not_visible` |
| `top_n_ui` | Số kết quả thực hiển thị |
| `rank` | Thứ hạng từ website |
| `website_job_id` | ID job nếu thực sự hiển thị/truy xuất hợp lệ |
| `job_title` | Tên việc |
| `company_name` | Công ty |
| `location` | Địa điểm nếu có |
| `displayed_score` | Score nếu có, không tự tính rồi gán là score web |
| `source_screenshot` | Tên ảnh thật làm bằng chứng |
| `note` | Điều kiện lọc, phân trang, điều chưa rõ |

**[CHƯA XÁC MINH]** Không biết website có hiển thị `job_id`, `score`, `company` hoặc `similarity_ui_name` đầy đủ hay không. Chỉ điền trường nào thực sự nhìn thấy hoặc có trong dữ liệu được phép dùng.

### 6.4. Danh sách ảnh người dùng nên cung cấp

Đặt tên gợi ý (không bắt buộc):

```text
evidence/website/
  01_profile_skills.png
  02_existing_jobs_search.png
  03_import_result.png
  04_imported_jobs_list.png
  05_job_search_results.png
  06_ratings_before_recommendation.png
  07_recs_cbf.png
  08_recs_cf.png
  09_recs_hybrid.png
  10_recs_user_knn.png
  11_recs_item_knn.png
  12_recs_popularity.png
  13_recs_sgd.png
  14_recs_als_explicit.png
  15_recs_als_implicit.png
```

Nếu giao diện có các biến thể độ đo (Cosine/Pearson/Jaccard, v.v.), dùng tên thể hiện thuật toán+độ đo, ví dụ `07_recs_cbf_cosine.png`; **không khẳng định giao diện có tùy chọn này**.

Ảnh phải giữ nguyên nội dung có ích và đủ rõ (đặc biệt tên thuật toán, Top-N, thời gian nếu có), nhưng che các dữ liệu không phục vụ lab như mật khẩu, email cá nhân, token, thông tin nhạy cảm. Không cắt ghép nội dung để làm tăng kết quả.

### 6.5. Nghiệm thu giai đoạn B

- [ ] Có thông tin profile/skills đầu vào dùng cho đối sánh.
- [ ] Có bằng chứng 10 tin mới sau import hoặc thống kê tin được website xác nhận.
- [ ] Có dữ liệu rating/ảnh trước lúc chụp Top-N.
- [ ] Có screenshot kết quả gợi ý với tên thuật toán tương ứng.
- [ ] Có ghi thời điểm, biến thể độ đo và bộ lọc (nếu website hiển thị).
- [ ] Không chứa thông tin đăng nhập trong artifact được nộp.

## 7. Giai đoạn C — Tiếp nhận MEDAJob CSV thật và kiểm toán dữ liệu

### 7.1. Cách người dùng lấy dữ liệu

**[GỐC]** Vào **[Hồ sơ] → [Tải MEDAJob CSV]** và chọn tải CSV mới nhất. Người dùng sẽ cung cấp file tải được cho agent.

### 7.2. Agent tuyệt đối KHÔNG đoán định dạng

MEDAJob có thể là một file ghép hoặc nhiều file; tài liệu gốc không xác định. Những tên `users.csv`, `jobs.csv`, `ratings.csv` **chỉ là các bảng logic trong notebook minh họa**, không phải tên thật chắc chắn của bộ export.

Bước xử lý:

1. Lưu **snapshot gốc bất biến** vào `data/raw/` và hash SHA-256.
2. Ghi log: tên file, kích thước, số dòng, encoding, delimiter, danh sách cột, dtype suy đoán, thời điểm nhận và thời điểm export do người dùng cung cấp (nếu có).
3. Đếm null, duplicate, giá trị rating khác thường, ngày không hợp lệ, user/job không có đối tượng tương ứng, skills rỗng.
4. Kiểm tra liệu có ID ổn định hay chỉ có tên công việc/công ty; cần mapping thống nhất cho đối sánh.
5. Kiểm tra dữ liệu người dùng thật có nằm trong export hay không; nếu không thì không giả định có thể tái tạo riêng gợi ý tài khoản đó.
6. Kiểm tra dataset có đủ tương tác cho CF, mô hình latent factors và đánh giá hold-out không.
7. Tạo tài liệu `reports/data_dictionary.md` và `reports/data_quality.md` với số liệu thực tế.
8. Nếu thiếu trường quan trọng, báo blocker cụ thể; đề xuất cách thay thế **chỉ nếu hợp lệ**, không tự tạo thông tin trông như dữ liệu thật.

### 7.3. Lược đồ logic mục tiêu (không phải schema export chắc chắn)

```text
users:
  user_id: str
  skills: str | list[str]

jobs:
  job_id: str
  title: str
  company_name: str | optional
  skills: str | list[str]
  location: str | optional
  employment_type: str | optional

interactions:
  user_id: str
  job_id: str
  rating: float | optional
  event_type: str | optional
  event_time: datetime | optional
```

**Có thể** cần thêm table quan hệ hoặc adapter từ CSV xuất. Ghi rõ luật `mapping`, bảng nào được sinh từ dữ liệu nào và vì sao. Không được dùng ID hàng dataframe làm `user_id` thật nếu làm mất khả năng đối sánh.

### 7.4. Kiểm soát chất lượng dữ liệu

- Chuẩn hóa Unicode tiếng Việt (NFC), khoảng trắng, case ở trường so khớp; giữ bản gốc để hiển thị.
- Chuẩn hóa skills: tách dấu phẩy/chấm phẩy phù hợp dữ liệu thực, loại rỗng, dedup; **không tự tách các cụm nhiều từ như `machine learning`, `spring boot`, `data engineering` thành các skill đơn lẻ** nếu không có tokenizer thiết kế rõ.
- Giữ provenance cột/nguồn; nếu kỹ năng chỉ lấy từ tiêu đề/mô tả thì đánh dấu `derived`.
- Không coi `rating=0` hoặc ô trống là đánh giá tiêu cực nếu dữ liệu xuất định nghĩa chúng là **chưa quan sát**.
- Rating trùng của cùng user/job: kiểm tra timestamp và quy tắc lấy rating mới nhất hoặc tổng hợp; nêu rõ quy tắc.
- Tách interaction implicit và explicit; không trộn click/đã xem với 5 sao nếu không có quy đổi giải thích.
- Giữ seed và cấu hình tiền xử lý trong file máy đọc được để tái lập.
- Chỉ thống kê kết quả *thật* khi đã áp dụng mapping và kiểm tra dữ liệu thành công.

### 7.5. Định danh phiên dữ liệu

Mỗi lần chạy cần `dataset_snapshot_id`, ví dụ hash rút gọn của các CSV gốc + thời gian export. Ghi bảng:

```text
dataset_snapshot_id
raw_files_sha256
exported_at (nếu biết)
received_at
number_of_users
number_of_jobs
number_of_interactions
number_of_explicit_ratings
sparsity
number_of_missing_skills
```

Không so sánh thẳng một website lấy dữ liệu realtime với MEDAJob export khác thời điểm mà không nêu giới hạn này.

---

# PHẦN IV — CÀI ĐẶT 9 THUẬT TOÁN: ĐẶC TẢ CHO AGENT

## 8. Nguyên tắc chung của bộ recommender

**[GỐC]** Đề chỉ nêu **tên 9 phương pháp**, không công bố công thức hoặc tham số. Vì thế cần ghi rõ thuật toán Python là **phiên bản cài đặt học thuật có thể tái lập**, không được khẳng định giống backend website.

### 8.1. Giao diện đầu vào/đầu ra chung — [ĐỀ XUẤT]

```python
class Recommender:
    def fit(self, users, jobs, interactions, config): ...
    def recommend(self, user_id: str, top_n: int = 10) -> list[dict]: ...
```

Record output tối thiểu:

```json
{
  "algorithm": "CBF",
  "user_id": "user_x",
  "job_id": "job_y",
  "rank": 1,
  "score": 0.73,
  "score_type": "cosine_similarity",
  "dataset_snapshot_id": "...",
  "config_id": "..."
}
```

`score` khác thang đo giữa các phương pháp, vì vậy **không lấy điểm tuyệt đối của CBF so với ALS để kết luận cái nào tốt hơn**. Dùng thứ hạng và metric đánh giá thống nhất.

### 8.2. Baseline chung

- Chọn cùng người dùng và cùng snapshot.
- Top-N chỉ gồm công việc đủ điều kiện theo cấu hình; nếu muốn loại công việc đã rating, áp dụng **giống nhau** giữa thuật toán và ghi rõ.
- Nếu dữ liệu không đủ, trả về `insufficient_data` và fallback có nhãn; không gán fallback là kết quả thuần của CF.
- Dùng `seed = 42` làm mặc định minh họa; ghi seed thực trong kết quả.
- Tie-break phải xác định trước (ví dụ `score desc`, `job_id asc`).
- Nếu tính similarity trên ma trận sparse, tránh xây dựng ma trận dense khổng lồ khi không cần.

## 9. `6.1. CBF — Theo kỹ năng`

### Ý tưởng

So khớp skills của ứng viên với skills/yêu cầu của job. Cách minh họa đơn giản: biểu diễn vector skills nhị phân hoặc TF–IDF, sau đó tính cosine similarity.

### Triển khai đề xuất

1. Tách skills ứng viên và từng việc làm.
2. Chuẩn hóa skills; xây vocabulary trên **train** nếu có chia tập.
3. Dùng `MultiLabelBinarizer` hoặc TF–IDF tùy bản chất dữ liệu; mặc định ưu tiên MultiLabelBinarizer khi có danh sách tag chuẩn.
4. Cosine similarity:

   `sim(u, j) = dot(x_u, x_j) / (||x_u|| * ||x_j||)`.

5. Xử lý vector rỗng → điểm bằng 0 và ghi nguyên nhân; không tính NaN.
6. Loại trừ việc đã đánh giá khi cấu hình yêu cầu.
7. Xuất top-N và **giải thích skill khớp/skill thiếu** để báo cáo.

**Cần lưu**: phương pháp vector hóa, vocabulary size, preprocess, ví dụ cặp user-job và cách tính điểm.

## 10. `6.2. CF — Theo hành vi`

### Điểm cần lưu ý

**[CHƯA XÁC MINH]** `CF - Theo hành vi` là tên rất rộng; tài liệu không định nghĩa CF cụ thể và còn liệt kê User-KNN, Item-KNN riêng. **Agent không được âm thầm tuyên bố nó là một thuật toán nhất định của website.**

### Phiên bản minh họa hợp lý — [ĐỀ XUẤT]

Có thể xây `behavioral CF` dựa trên đồng tương tác tích cực:

- Tạo ma trận tương tác quan sát `B[user, job]` (binary hoặc trọng số từ click/apply/rating tùy dữ liệu thật).
- Tính job–job co-occurrence hoặc item similarity từ hành vi người dùng.
- Chấm điểm job chưa tương tác bằng mức độ đồng xuất hiện với tập job user tương tác tích cực.
- Ghi rõ **khác Item-KNN** (Item-KNN dùng lân cận có kích thước k và rating thực/điều chỉnh), nếu thiết kế này được sử dụng.

Nếu dữ liệu/website cho phép xác định CF chính xác hơn, hãy thay bằng bản đúng có giải thích thay đổi. Không đếm một triển khai trùng y hệt Item-KNN hai lần mà không giải thích.

## 11. `6.3. Hybrid — Kết hợp`

### Ý tưởng

Kết hợp một thành phần content-based và một thành phần hành vi.

### Công thức minh họa

`S_hybrid(u,j) = alpha * norm(S_CBF(u,j)) + (1-alpha) * norm(S_CF(u,j))`

- `alpha` có thể mặc định 0.5 nếu không có bằng chứng khác, nhưng phải khai báo là tham số **do agent chọn**.
- Phải chuẩn hóa phù hợp trước khi trộn; ghi rõ phạm vi và công thức `norm`.
- Nếu user mới chưa rating, có thể fallback CBF, **đánh dấu rõ**.
- Thử `alpha ∈ {0.25, 0.5, 0.75}` chỉ nếu thời gian/dữ liệu cho phép; không cần làm thành yêu cầu bắt buộc.

## 12. `6.4. User-KNN`

### Ý tưởng

Tìm nhóm người dùng có rating/hành vi tương tự và dự đoán các job họ đánh giá tốt.

### Triển khai đề xuất

- Tạo ma trận user × job từ **rating đã quan sát**.
- Chọn similarity: Cosine hoặc Pearson; **ghi đúng độ đo dùng khi chạy**.
- Chỉ tính similarity hợp lệ khi đủ đồng tương tác; tránh coi hàng chưa quan sát như rating 0 tiêu cực.
- Chọn `k` (ví dụ 20) và số người dùng láng giềng thực có dữ liệu; xử lý khi ít hơn `k`.
- Dự đoán bằng trung bình rating có trọng số tương đồng hoặc điều chỉnh mean-center; ghi công thức.
- Với dữ liệu sparse, cần cân nhắc shrinkage/min-overlap.
- Không đưa job user đã đánh giá vào danh sách top-N nếu config loại trừ.

## 13. `6.5. Item-KNN`

### Ý tưởng

Xác định job tương tự dựa trên các mẫu rating, rồi gợi ý job mới giống những job mà người dùng đã quan tâm.

### Triển khai đề xuất

- Similarity trên cột của ma trận tương tác (job × user), không phải trên vector skills nếu đang báo là Collaborative Filtering.
- `k` lân cận với từng job; cosine/Pearson điều chỉnh theo dữ liệu.
- Dự đoán rating bằng trọng số tương đồng với job user đã đánh giá.
- Giải quyết cold-start job chưa rating: đánh dấu không đủ dữ liệu hoặc fallback; không lặng lẽ sử dụng CBF rồi gán nhãn Item-KNN.

## 14. `6.6. Popularity — Phổ biến`

### Ý tưởng

Ưu tiên job có nhiều tương tác tốt hoặc được đánh giá cao trong toàn bộ hệ thống.

### Triển khai đề xuất

- Baseline 1: số lượt tương tác tích cực.
- Baseline 2: mean rating có Bayesian smoothing để tránh 1 rating 5 sao áp đảo 100 rating trung bình 4.5 sao.
- Chọn **một phương pháp chính** và giải thích, ví dụ:

  `bayes_score(j) = (n_j*mean_j + m*C) / (n_j + m)`;

  `n_j`: số rating job; `mean_j`: rating trung bình job; `C`: mean toàn hệ thống; `m`: prior strength do agent chọn.

- Popularity thường có tính không cá nhân hóa; đánh giá đúng giới hạn đó.

## 15. `6.7. Model-based CF — SGD`

### Ý tưởng

Matrix factorization tối ưu bằng stochastic gradient descent trên **rating đã quan sát**.

### Mô hình minh họa

`r_hat(u,j) = mu + b_u + b_j + p_u^T q_j`.

Minimize trên tập observed:

`sum((r_uj-r_hat_uj)^2) + lambda*(||P||²+||Q||²+||b||²)`.

- Chọn factors, epochs, learning rate, regularization, seed; lưu trong config.
- Shuffle theo seed, report train loss và (nếu có) validation loss; tránh chỉ chọn số epochs vì output đẹp.
- Không coi missing rating là zero observed.
- Có thể clip dự đoán về thang rating thật để diễn giải, nhưng **chỉ ở bước hiển thị**; giữ raw prediction khi cần đánh giá.

## 16. `6.8. Model-based CF — ALS Explicit`

### Ý tưởng

Factorize explicit rating với alternating least squares, tối ưu xen kẽ user factors và item factors trên rating **có quan sát**.

### Điểm bắt buộc

- Mô hình hóa mask quan sát tách biệt ma trận rating; missing != rating 0.
- Có `regularization`, `latent_dim`, `iterations`, seed.
- Tránh inverse trực tiếp khi có thể dùng `solve` ổn định; xử lý ma trận suy biến bằng regularization.
- Kiểm tra loss/error qua iteration; so sánh với SGD trong cùng split.
- Lưu ý mô hình explicit này **không giống** implicit ALS.

## 17. `6.9. Model-based CF — ALS Implicit`

### Ý tưởng

Dùng `preference p_ui` và `confidence c_ui` theo cách implicit collaborative filtering.

### Công thức minh họa

`p_ui = 1` khi tồn tại tín hiệu tích cực, `0` khi chưa có tín hiệu phù hợp;

`c_ui = 1 + alpha * strength_ui`.

Tối ưu luân phiên dạng weighted least squares. Cần **phân biệt preference với confidence** và nhấn mạnh zero chưa quan sát không có nghĩa dislike rõ ràng.

- Nếu CSV chỉ có rating, agent phải **nêu luật chuyển rating → implicit signal** (ví dụ điểm cao là tương tác tích cực) và đây là giả định phân tích.
- Nếu có click/save/apply thật thì ưu tiên tín hiệu phù hợp hơn với ngữ nghĩa implicit.
- Ghi cấu hình: `confidence_alpha`, `latent_dim`, `regularization`, `iterations`, conversion threshold.
- Output là điểm affinity/độ phù hợp, không phải sao dự đoán trực tiếp.

## 18. Tình huống dữ liệu thiếu và các bẫy kỹ thuật

| Trường hợp | Hành vi agent cần có |
|---|---|
| Không có `skills` trong MEDAJob | Nêu CBF không thể chạy đúng biến thể theo skills nếu chưa có nguồn skills hợp lệ; chỉ suy từ mô tả khi nêu rõ phương pháp. |
| Không có `ratings`/interactions | CF/KNN/MF không đủ dữ liệu; không tự tạo rating thật. |
| User không xuất hiện trong snapshot | Không nhận là đã tái tạo gợi ý user đó; chỉ có thể minh họa với user khác và nêu giới hạn. |
| Một job mới chưa từng được rated | Giải thích cold-start item, dự kiến CF yếu/không xếp hạng được. |
| Nhiều item bằng điểm | Tie-break deterministic và ghi rõ. |
| Dữ liệu lớn | Dùng sparse matrices và batch/ANN nếu cần; tránh dense O(users × jobs) vượt RAM. |
| Rating theo thang khác 1–5 | Kiểm tra từ dữ liệu/UI rồi chuẩn hóa đúng; không hardcode giả định. |
| Rating 0 | Kiểm tra nghĩa 0 trước khi chọn mask. |
| Website hiển thị score khác | So sánh ranking, không quy điểm các thuật toán khác thang. |
| Website realtime và CSV snapshot khác thời điểm | Ghi mismatched snapshot, không kết luận lỗi thuật toán. |
| Web dùng similarity/hyperparameter không biết | Nêu giới hạn tái lập và thực hiện sensitivity analysis nếu hữu ích. |

---

# PHẦN V — THỰC NGHIỆM, ĐỐI SÁNH VÀ ĐÁNH GIÁ

## 19. Thiết kế thực nghiệm tối thiểu

### 19.1. Baseline chạy được

**[ĐỀ XUẤT]**

- Nhập dữ liệu thật và thống kê snapshot.
- Chọn một hoặc vài `target_user_id` có đủ thông tin; nếu có thể, ưu tiên user đang dùng website, **chỉ khi user xuất hiện trong export**.
- Chạy 9 thuật toán trên **cùng dữ liệu, cùng điều kiện lọc, cùng Top-N**.
- Lưu Top-5 hoặc Top-10 tùy dữ liệu/screenshot. Top-5 **không phải yêu cầu bắt buộc**.
- Lưu từng thuật toán thành CSV riêng hoặc một CSV có `algorithm`.
- Ghi `run_id`, `dataset_snapshot_id`, `algorithm`, `algorithm_config`, `target_user_id`, seed, thời điểm, thư viện.

### 19.2. Đánh giá ngoại tuyến (nếu dữ liệu đủ)

Chọn cách tách dữ liệu không làm lộ kết quả:

1. Nếu có timestamp đáng tin cậy: ưu tiên chronological split (train cũ, test mới) theo user.
2. Nếu thiếu timestamp: dùng hold-out random có seed cố định, bảo đảm user có đủ interactions trong train và test; thừa nhận giới hạn.
3. Tất cả phương pháp dùng **cùng split**, cùng tập users/jobs có thể đánh giá.
4. `fit()` (bao gồm xây vocabulary, popularity, normalize statistics, latent factors) chỉ nhìn thấy train, không vô tình đưa test vào train.
5. Đánh giá trên **user đủ điều kiện**; thống kê bao nhiêu user bị loại và vì sao.
6. Đừng chọn k/hyperparameter theo test; nếu tuning thì cần validation riêng.

Metrics đề xuất (chọn theo dữ liệu và yêu cầu):

- `HitRate@K`: tỷ lệ user có ít nhất một job dương trong test nằm trong Top-K.
- `Recall@K`: tổng số item dương test được truy hồi trong Top-K chia cho số item dương test.
- `Precision@K`: số item dương test trong Top-K chia K, cần chú ý giả định item không quan sát là không liên quan.
- `NDCG@K`: quan tâm thứ hạng, dùng relevance hợp lệ.
- `Coverage@K`: tỷ lệ item có cơ hội được gợi ý trong tập ứng viên.
- `RMSE/MAE`: chỉ hợp lý với mô hình dự đoán **explicit ratings** trên tập observed test; không buộc dùng để so score của implicit/CBF.

Cần ghi **metric formula, đối tượng đánh giá, số lượng user/items test, biến thể negative sampling** (nếu có). Không dùng điểm chính xác 100% trên tập demo rất nhỏ để tuyên bố hiệu năng tổng quát.

## 20. Đối sánh website ↔ Python

### 20.1. Tiền điều kiện so sánh hợp lệ

Kiểm tra:

- Cùng `target_user_id` hay không.
- Cùng phiên MEDAJob với dữ liệu website tại lúc capture hay không.
- Có dùng cùng hồ sơ skills, ratings, filter job, trạng thái job active và địa điểm không.
- Cùng thuật toán theo tên; mức chắc chắn về implementation backend.
- Cùng `K` hoặc số lượng gợi ý thực tế hiển thị.
- Có thể đối sánh `job_id` thật hoặc chỉ theo composite title+company+location.
- Có trường hợp website **đã loại job đã rated** hay đã đăng ký hay không.

Nếu không đồng nhất, kết quả chỉ là **so sánh tham khảo có giới hạn**, không phải phép thử tái lập tuyệt đối.

### 20.2. Metric đơn giản cho tập Top-K

**Overlap@K**:

`Overlap@K = |TopK_website ∩ TopK_python| / K`.

K chỉ dùng khi hai danh sách cùng đủ K item. Khi bên nào có ít hơn, phải ghi `N_web`/`N_python` và chọn quy tắc so sánh minh bạch; **không đổi mẫu số lặng lẽ**.

Có thể bổ sung:

- `Jaccard = |A ∩ B| / |A ∪ B|`.
- Thứ tự khác nhau dù tập item trùng: đánh giá `rank_delta` cho item chung, hoặc rank correlation chỉ trên intersection (ghi giới hạn).
- `Top1_match` để có thông tin đơn giản, không thay thế phân tích toàn bộ danh sách.
- Mô tả định tính: tương ứng kỹ năng, khả năng cold-start, thiên lệch popularity, ảnh hưởng sparse ratings.

### 20.3. Bảng đối sánh mẫu (chỉ schema, không phải dữ liệu thật)

| Thuật toán | K | Website Top-N | Python Top-N | Overlap@K | Ghi chú |
|---|---:|---|---|---:|---|
| CBF | — | `PENDING` | `PENDING_REAL_DATA` | — | Cần web screenshot + MEDAJob |
| CF | — | `PENDING` | `PENDING_REAL_DATA` | — | Cần định nghĩa CF backend |
| Hybrid | — | `PENDING` | `PENDING_REAL_DATA` | — | Cần hệ số phối hợp |
| User-KNN | — | `PENDING` | `PENDING_REAL_DATA` | — | Cần k/similarity |
| Item-KNN | — | `PENDING` | `PENDING_REAL_DATA` | — | Cần k/similarity |
| Popularity | — | `PENDING` | `PENDING_REAL_DATA` | — | Dữ liệu popularity có thể thay đổi |
| SGD | — | `PENDING` | `PENDING_REAL_DATA` | — | Seed/latent factors |
| ALS Explicit | — | `PENDING` | `PENDING_REAL_DATA` | — | Regularization |
| ALS Implicit | — | `PENDING` | `PENDING_REAL_DATA` | — | Định nghĩa confidence |

### 20.4. Giải thích khi kết quả không khớp

Không gán nguyên nhân duy nhất. Kiểm tra có thứ tự:

1. Mismatch dữ liệu/time snapshot.
2. Khác cách lọc item đã đánh giá, active job, địa điểm.
3. Khác mapping ID, normalization skills.
4. Khác similarity, thông số `k`, `alpha`, factors, số epochs.
5. Khác negative sampling/khái niệm implicit.
6. Khác cold-start/fallback và cách xử lý đồng điểm.
7. Khác phiên bản dữ liệu/mã nguồn.
8. Có thể website dùng thuật toán khác tên gọi phổ quát; chưa biết backend thì không được khẳng định bug.

---

# PHẦN VI — KIẾN TRÚC MÃ NGUỒN VÀ CHUẨN HÓA PROJECT

## 21. Tận dụng notebook đã có

**[ĐÃ KIỂM TRA]** Có notebook khởi đầu:

```text
LabDSS_RECSYS_9_thuat_toan.ipynb
```

Notebook này:

- Dùng Python, `numpy`, `pandas`, `scikit-learn`.
- Có `DEMO_MODE = True`, bộ dữ liệu minh họa, lược đồ logic `users`, `jobs`, `ratings`.
- Có mã chấm điểm 9 phương pháp (bản **minh họa học thuật**), xuất Top-N và ví dụ hold-out `HitRate@5`.
- Có ô đối sánh `WEBSITE_TOP_JOB_IDS` (ban đầu rỗng) và các file CSV xuất kết quả.
- Không khẳng định là phiên bản đúng với công thức website.

**[ĐÃ KIỂM TRA]** Notebook đã được thực thi toàn bộ ở chế độ demo trong môi trường chuẩn bị handoff, không báo lỗi; sinh `recommendation_comparison.csv` gồm **45 dòng cho 9 thuật toán × Top-5**, và `evaluation_hit_rate.csv` gồm **9 dòng thuật toán**. Đó là bằng chứng chạy **dữ liệu giả lập**, **không phải** MEDAJob thực tế và **không phải** ảnh/kết quả website. Trạng thái hoàn thành dữ liệu thật vẫn `BLOCKED_USER`.

**Chỉ dẫn agent:** dùng notebook làm tham khảo/startup, không coi đó là mã final đã được review. Xem kỹ logic splitting, tính toán score, nửa chừng thiếu dữ liệu, sự khác nhau của `CF` và `Item-KNN`, hạn chế của demo trước khi mở rộng. Khi có CSV thật, chạy toàn bộ tests và thí nghiệm lại; không tái sử dụng số liệu demo trong báo cáo kết luận.

## 22. Cấu trúc repo khuyến nghị (không overengineering)

```text
LabDSS_Job_Recommender/
├── README.md
├── AGENT_HANDOFF_LABDSS_RECSYS.md
├── requirements.txt
├── pyproject.toml                 # tùy chọn; không bắt buộc nếu chỉ cần pip
├── .gitignore
├── configs/
│   ├── experiment.yaml
│   └── column_mapping.yaml       # bổ sung khi có MEDAJob/Template thật
├── data/
│   ├── raw/                      # snapshot nguyên bản, có thể không commit
│   ├── interim/                  # các bảng sau mapping
│   ├── processed/                # dataset kiểm chứng, split
│   └── exports/                  # CSV import, các bảng output
├── src/
│   └── job_recsys/
│       ├── __init__.py
│       ├── io.py
│       ├── validate.py
│       ├── preprocess.py
│       ├── metrics.py
│       ├── evaluation.py
│       ├── run_experiment.py
│       ├── compare_website.py
│       ├── algorithms/
│       │   ├── cbf.py
│       │   ├── cf_behavior.py
│       │   ├── hybrid.py
│       │   ├── user_knn.py
│       │   ├── item_knn.py
│       │   ├── popularity.py
│       │   ├── sgd.py
│       │   ├── als_explicit.py
│       │   └── als_implicit.py
│       └── jobs_import/
│           ├── collect.py
│           ├── dedupe.py
│           └── build_csv.py
├── notebooks/
│   ├── LabDSS_RECSYS_9_thuat_toan.ipynb
│   └── 02_experiment_real_data.ipynb
├── tests/
│   ├── test_import_mapping.py
│   ├── test_data_validity.py
│   ├── test_algorithms.py
│   ├── test_recommendation_filters.py
│   └── test_metrics.py
├── evidence/
│   └── website/                  # do người dùng cung cấp, phân loại ảnh
├── reports/
│   ├── data_dictionary.md
│   ├── data_quality.md
│   ├── sources_jobs.csv
│   ├── import_preview.md
│   ├── screenshots_manifest.csv
│   ├── run_manifest.json
│   ├── algorithm_results.csv
│   ├── website_results.csv
│   ├── website_python_comparison.csv
│   ├── offline_metrics.csv
│   └── LabDSS_WebsiteRECSYS_Report.docx
└── logs/
    └── run_*.log
```

Đây là **đề xuất tổ chức**, được phép rút gọn nếu bài lab nhỏ. Không biến bài thực hành thành hệ thống microservice, không thêm database/server/backend riêng nếu không cần.

## 23. Môi trường và lệnh chạy gợi ý

Người dùng làm việc trên **Windows/VS Code**; ưu tiên các lệnh PowerShell, notebook hỗ trợ chạy cả local và Colab khi phù hợp.

```powershell
# Trong thư mục dự án
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pytest -q
```

**Agent chịu trách nhiệm** tạo README ghi lệnh cụ thể theo repo thật; không sao chép lệnh CLI chưa triển khai vào mục hướng dẫn nộp như thể chạy được.

Nếu dùng notebook:

```powershell
python -m pip install notebook jupyter nbconvert
jupyter notebook
```

Hoặc mở `.ipynb` trực tiếp trong VS Code với Python/Jupyter extension. Nếu buộc cài package mới, đưa vào `requirements.txt` với phiên bản hoặc khoảng phiên bản có thể tái lập.

## 24. Kiểm thử bắt buộc

### 24.1. Dữ liệu và CSV

- Nạp dữ liệu hợp lệ; từ chối schema thiếu cột bắt buộc.
- CSV có dấu phẩy trong mô tả, Unicode tiếng Việt, newline/quote, trường rỗng.
- Detect duplicate ID và duplicate jobs theo quy tắc có giải thích.
- Trường ID là chuỗi giữ số 0 đầu nếu có.
- Rating missing != rating 0, tránh row/column alignment bug.
- Ratings tham chiếu `user_id`/`job_id` không có trong tables phải được thống kê, không silently drop mà không log.

### 24.2. Các thuật toán

- Đảm bảo 9 phương pháp đều trả Top-N và score hữu hạn trong tình huống đủ dữ liệu.
- Reproducibility cùng seed: output deterministic trong môi trường tương đương.
- Không gợi ý job đã tương tác nếu bật exclude.
- Xử lý user/job cold-start bằng `status` và fallback có nhãn.
- Không lộ test interactions vào fit/training.
- Không dùng unknown user làm user đã có ratings.
- Kiểm tra thiếu dữ liệu: `empty ratings`, `empty skills`, `all items rated`, `one user`, `one item`, `no positive interactions`, `ties`.
- Kiểm tra `Top-N` số item thực (không thêm fake row nếu thiếu candidates).
- Đánh giá `Overlap@K`, `HitRate@K` bằng ví dụ số nhỏ tính tay.

### 24.3. Chất lượng bằng chứng

- Mỗi biểu đồ/số liệu trong báo cáo liên kết đến file output thật hoặc mã tái lập.
- Screenshot website có filename và thuật toán đúng với mô tả.
- Không có ảnh sinh ra bằng thao tác vẽ đồ họa giả giao diện website.
- Phân biệt **kết quả chạy code** và **kết quả website**.

---

# PHẦN VII — BÁO CÁO WORD VÀ CÁCH THỂ HIỆN MINH CHỨNG

## 25. Phong cách báo cáo

**[CHỐT]** Người dùng muốn báo cáo tiếng Việt tự nhiên, có thể nộp học phần, giữ cấu trúc đề gốc nếu dùng chính tài liệu đó làm mẫu, ưu tiên Times New Roman. Không trang trí rườm rà.

**Đừng xóa đề, trang bìa, mục lục hoặc câu hỏi gốc để thay bằng một báo cáo hoàn toàn khác** nếu người dùng mong muốn giữ bố cục. Bổ sung phần kết quả ở vị trí thích hợp. Nếu cần làm file Word mới, vẫn bám các mục 1–7 của tài liệu.

### 25.1. Đề cương báo cáo (mức chi tiết mong muốn)

**Trang đầu**
- Tên trường/khoa, tên học phần/bài lab (dựa trên tài liệu gốc), nhóm học phần, sinh viên, mã số SV (do người dùng cung cấp).
- Tiêu đề `HỆ THỐNG RECSYS GỢI Ý VIỆC LÀM`.
- Mục lục.

**1. Giới thiệu**
- Mục tiêu bài lab: trải nghiệm chức năng nhà tuyển dụng/tìm việc, tạo dữ liệu hồ sơ và đánh giá 9 thuật toán.
- Giới thiệu website theo đề và phạm vi thực hiện.
- Công cụ sử dụng (Python, pandas, numpy, scikit-learn; bổ sung thư viện thật).
- Lưu ý rằng chưa có dữ liệu backend/cấu hình bên trong nếu không có.

**2. Chức năng [Hồ sơ]**
- Các trường đã cập nhật; skills cụ thể (không lộ thông tin nhạy cảm).
- Ảnh thật trước/sau nếu có.
- Nhận xét vai trò của skills đối với CBF và Hybrid.

**3. Chức năng [Nhà tuyển dụng]**
- Quy trình kiểm tra trùng, tin hết hạn.
- Quy trình thu thập 10+ tin IT và nguồn.
- Bảng 10 tin: tiêu đề, công ty, địa điểm nếu có, source URL (không copy full mô tả quá dài).
- CSV Template được dùng, kiểm tra schema, kết quả import.
- Ảnh danh sách tin nhóm sau import.
- Phân biệt số tin chuẩn bị và số tin thực tế import thành công.

**4. Chức năng [Tìm việc]**
- Từ khóa tìm kiếm, lọc địa điểm/loại hình (nếu dùng).
- Một số job phù hợp và căn cứ đánh giá.
- Rating thật đã tạo (bảng nhỏ + ảnh minh chứng).

**5. Chức năng [Tìm việc]/[Gợi ý việc làm]**
- Ghi nguyên tên thuật toán và độ đo trên giao diện, nếu có.
- Screenshot kết quả thuật toán.
- Nhận xét định tính kỹ năng, lịch sử rating và mức phù hợp.
- Không nhận xét độ chính xác theo cảm giác như số liệu đo định lượng.

**6. MEDAJob, lập trình và đối sánh**
- Mô tả MEDAJob thực tế: cấu trúc, tổng số bản ghi, số user/job/rating nếu truy xuất được.
- Pipeline xử lý dữ liệu, sơ đồ luồng CSV → chuẩn hóa → recommender → Top-N → so sánh.
- Với mỗi trong **9 mục 6.1–6.9**:
  - Mục đích và giải thích ngắn.
  - Công thức/cách tính được agent lựa chọn.
  - Cấu hình/hyperparameters.
  - Code chính hoặc giải thích code, path source tương ứng.
  - Kết quả thực nghiệm thật ở dạng bảng/terminal/screenshot output Python.
  - Bảng đối sánh website–Python (nếu đủ đầu vào).
  - Nhận xét nguyên nhân khác biệt và giới hạn.
- Bảng tổng hợp 9 phương pháp, cùng dữ liệu/split.
- Nếu có offline metric: mô tả train/test, seed, K, số mẫu và metric.

**7. Tham khảo**
- Tài liệu lab.
- Link tin tuyển dụng thật đã tham chiếu.
- Tài liệu/hướng dẫn chính thức của thư viện thuật toán nếu sử dụng.
- Paper phương pháp (nếu agent thực sự tra cứu và dùng, trích dẫn đầy đủ).

**Kết luận (nếu bố cục cho phép)**
- Thành quả đã kiểm chứng, hạn chế, bài học về CBF vs CF vs Hybrid/Cold-start/sparsity.
- Không nêu `mô hình X tốt nhất` nếu thiếu bằng chứng đánh giá công bằng.

### 25.2. Tiêu chuẩn bảng/ảnh

- Mỗi hình có caption số thứ tự và nguồn (`Ảnh chụp hệ thống ...` hoặc `Kết quả chạy Python ...`).
- Cắt ảnh đủ rõ phần cần minh chứng, không lẫn mật khẩu/session.
- Bảng có tiêu đề, đơn vị, diễn giải cách tạo và nguồn dữ liệu.
- Báo cáo ghi rõ **thời điểm truy xuất nguồn**, nhất là tin việc làm và dataset biến động.
- Dùng ảnh terminal/output thật khi được yêu cầu; có thể tạo bảng Word sạch kèm log đầy đủ ở phụ lục.
- Mọi kết luận gắn với output/citation; tránh lặp phần code dài vào nhiều chỗ nếu có source đính kèm.

### 25.3. Điều kiện không đủ dữ liệu

Khi chưa có screenshot/MEDAJob, agent **được soạn bản nháp** với placeholder rõ như:

```text
[CHỜ DỮ LIỆU MEDAJOB THẬT]
[CHỜ ẢNH CHỤP WEBSITE: USER-KNN]
[CHỜ BẢNG XÁC NHẬN IMPORT 10 TIN]
```

Tuyệt đối không thay placeholder bằng số liệu tưởng tượng. Trước khi bàn giao **bản báo cáo cuối** phải xác nhận các placeholder bắt buộc đã được giải quyết hoặc ghi thẳng phần chưa hoàn thành.

---

# PHẦN VIII — QUẢN LÝ DỮ LIỆU, BẢO MẬT, PHẠM VI

## 26. An toàn và quyền riêng tư

- Không tự đăng nhập, lưu mật khẩu, nhận OTP/2FA, lấy cookie/token qua screenshot/chat.
- Không nhúng thông tin bí mật vào `.py`, `.ipynb`, `.env` được commit, báo cáo hoặc log.
- Không ghi các ID cá nhân, email, số điện thoại của user khác nếu không cần thiết. Nếu dữ liệu export chứa PII, xử lý tối thiểu, ẩn danh khi báo cáo.
- Không vượt captcha/anti-bot, không bypass hạn chế của website, không quét/cào dữ liệu trái phép.
- Không nộp/đẩy dataset cá nhân lên dịch vụ bên ngoài nếu chưa có sự cho phép phù hợp.
- Không tự xóa, sửa hoặc đóng tin tuyển dụng trên website. Việc đó thuộc người dùng.
- Không tự động commit/push/gắn tên co-author hay tác động Git history trừ khi người dùng yêu cầu.
- Không thêm phụ thuộc nặng/GPU nếu dữ liệu vừa phải và CPU đáp ứng. Kiến trúc tối giản, dễ chạy bằng máy sinh viên.

## 27. Quy trình khi gặp blocker

Mỗi blocker phải trình bày theo mẫu:

```text
BLOCKER-ID:
Giai đoạn:
Thiếu đầu vào hoặc lỗi:
Ảnh hưởng trực tiếp đến yêu cầu nào:
Phần vẫn làm được ngay:
Một hành động ngắn gọn người dùng cần làm:
Đầu ra dự kiến sau khi nhận dữ liệu:
```

Ví dụ:

```text
BLOCKER-ID: B-MEDAJOB-01
Giai đoạn: C/D/E
Thiếu: MEDAJob CSV thật từ [Hồ sơ] → [Tải MEDAJob CSV]
Ảnh hưởng: Chưa thể chạy/đối sánh 9 thuật toán trên dữ liệu thật
Phần vẫn làm được: unit tests, module nhập liệu, demo minh họa
Người dùng cần làm: tải CSV và đính kèm các tệp nhận được
Đầu ra sau khi nhận: data dictionary, validation, 9 thuật toán và bảng Top-N thật
```

---

# PHẦN IX — KẾ HOẠCH THỰC HIỆN VÀ NGHIỆM THU

## 28. Thứ tự thực hiện tối ưu

### Phase 0 — Kiểm kê

1. Kiểm tra file gốc `LabDSS WebsiteRECSYS.docx`, notebook có sẵn và các file người dùng đính kèm.
2. Đọc yêu cầu và viết task board cùng trạng thái; không hỏi lại dữ liệu đã có.
3. Kiểm tra môi trường Python và chạy notebook demo/pytest nếu có.
4. Tạo skeleton repo vừa đủ, README và `.gitignore` phù hợp.

**Output:** task board, directory, logs kiểm tra demo, danh sách blocker ban đầu.

### Phase 1 — Nguồn tin tuyển dụng

1. Tìm 12–15 tin dự phòng (nếu có nguồn), lọc ≥10 tin IT thực.
2. Kiểm tra URL riêng từng tin, trang tuyển dụng, công ty, ngày kiểm tra.
3. Tạo bảng ứng viên và nguồn kiểm chứng.
4. Kiểm tra trùng nội bộ.
5. **Nếu chưa nhận CSV Template:** bàn giao nguồn tin trước, chờ template để xuất import-ready.
6. **Nếu đã có CSV Template:** parse template, map cột, xuất file import-ready, kiểm tra đọc lại.

**Output:** `job_candidates.csv`, `sources_jobs.csv`, `job_import_ready.csv` (khi đủ template), `import_preview.md`.

### Phase 2 — Hạ tầng phân tích thuật toán

1. Đọc/kiểm thử notebook hiện có.
2. Tách chức năng đọc/mapping dữ liệu, công thức các thuật toán, đo metric, xuất output.
3. Viết unit tests trên synthetic mini dataset minh bạch.
4. Chạy và xuất output demo được gắn `DEMO` rõ ràng.
5. Viết phần lý thuyết và công thức 9 thuật toán cho báo cáo.

**Output:** code, notebook, requirements, unit tests, demo logs. Chưa được tính là kết quả thật.

### Phase 3 — Người dùng thao tác website

1. Người dùng cập nhật hồ sơ và rating; agent chuẩn bị hướng dẫn/phiếu ghi nhận.
2. Người dùng kiểm tra trùng tin trên website và import file agent đã tạo.
3. Người dùng chụp bằng chứng danh sách tin sau import.
4. Người dùng chạy gợi ý website và chụp output (thuật toán, độ đo, Top-N).
5. Người dùng tải MEDAJob CSV và gửi file cho agent.

**Output:** `evidence/website/`, `website_results.csv`, CSV Template/MEDAJob snapshots. Phần này do người dùng xác nhận.

### Phase 4 — Thực nghiệm dữ liệu thật

1. Hash, kiểm toán và chuẩn hóa MEDAJob.
2. Chốt cách mapping, chọn `target_user_id`, `K`, train/test split và config.
3. Fit/recommend cả 9 phương pháp.
4. Chạy metric hợp lệ; tạo bảng output + log.
5. Nếu có đủ snapshot website: đối sánh, tính overlap, phân tích.
6. Rà soát chênh lệch và tính tái lập.

**Output:** dữ liệu sạch, Top-N, metric, comparison, manifests, logs.

### Phase 5 — Báo cáo & bàn giao

1. Điền Word theo đúng cấu trúc file lab.
2. Chèn ảnh thật, bảng, mã nguồn/đường dẫn source phù hợp.
3. Chạy kiểm tra văn bản, bảng, số liệu so với nguồn; kiểm tra không còn placeholder bắt buộc.
4. Kiểm thử chạy lại từ README trên môi trường sạch.
5. Nộp `.docx`, code, CSV hợp lệ, tài liệu hướng dẫn, toàn bộ minh chứng liên quan.

**Output:** bộ bài nộp hoàn chỉnh, có manifest những gì đã hoàn tất.

## 29. Checklist nghiệm thu cuối cho agent

### Yêu cầu theo đề
- [ ] Đề gốc và các mục chính được giữ đúng ý nghĩa.
- [ ] Người dùng có bằng chứng cập nhật hồ sơ.
- [ ] Có **ít nhất 10 tin tuyển dụng IT thật + URL kiểm chứng**, được người dùng xác nhận trên hệ thống khi đã import.
- [ ] Có bước kiểm tra trùng và tin hết hạn.
- [ ] Có minh chứng tìm việc và rating.
- [ ] Có minh chứng trang gợi ý website và phân tích.
- [ ] Có MEDAJob CSV mới nhất (nếu người dùng đã cung cấp) với snapshot/metadata.
- [ ] Cài đặt/đánh giá đủ **9 thuật toán**.
- [ ] Có phần đối sánh website–Python hoặc ghi trung thực blocker còn thiếu.
- [ ] Có danh mục tài liệu tham khảo.

### Kỹ thuật
- [ ] Source có thể chạy lại bằng hướng dẫn README.
- [ ] Unit tests và smoke tests chạy qua.
- [ ] Không hardcode path cá nhân hoặc credential.
- [ ] Không trộn dữ liệu train/test và không biến missing rating thành dislike.
- [ ] Không gọi demo là số liệu thật.
- [ ] Có provenance từng file CSV, kết quả và ảnh minh chứng.
- [ ] Khớp số liệu giữa CSV kết quả, log, bảng báo cáo.
- [ ] Nếu phải chạy lâu, có cache/checkpoint thích hợp và log trạng thái.

### File nộp
- [ ] `.docx` trình bày hoàn chỉnh bằng tiếng Việt, Times New Roman khi phù hợp.
- [ ] `.py`/`.ipynb`, `requirements.txt`, `README.md`.
- [ ] CSV import + danh sách URL tuyển dụng có nguồn thật.
- [ ] CSV kết quả 9 thuật toán, bảng metric và bảng so sánh.
- [ ] Screenshot website thật và output chạy code.
- [ ] Các giới hạn và phần chưa xác minh được nêu rõ.

---

# PHẦN X — MẪU GIAO TIẾP NGẮN GIỮA AGENT VÀ NGƯỜI DÙNG

## 30. Khi agent đã chuẩn bị tin tuyển dụng

```text
Đã kiểm chứng [N] tin IT công khai. Đã loại [X] tin trùng nội bộ và [Y]
tin không còn truy cập/hết hạn. File nguồn: [...].

Bạn giúp tôi 2 việc:
1. Gửi CSV Template tải từ mục Nhà tuyển dụng để tôi xuất đúng định dạng import.
2. Trên website, rà soát các tin theo bảng `import_preview.md` để tránh trùng.

Tôi chưa báo đã import thành công vì bạn chưa thực hiện bước đó.
```

## 31. Khi agent chờ MEDAJob

```text
Phần code 9 thuật toán đã chạy thử bằng synthetic data và có tests.
Để thực nghiệm chính thức, bạn vào [Hồ sơ] → [Tải MEDAJob CSV]
rồi gửi các file đã tải. Tôi sẽ phân tích schema thực tế, chạy lại và
xuất Top-N + bảng so sánh, không sử dụng số liệu demo làm kết quả thật.
```

## 32. Khi agent chờ screenshot website

```text
Tôi đã có Top-N Python từ snapshot [ID]. Để đối sánh trực tiếp, vui lòng
gửi ảnh hoặc danh sách Top-N gợi ý của website, kèm tên thuật toán và
độ đo bạn chọn. Nếu không có job_id, cần ít nhất tên job + công ty để
đối chiếu; độ tin cậy thấp hơn sẽ được ghi rõ.
```

## 33. Khi báo hoàn thành

Phải dùng bảng trạng thái:

| Yêu cầu | Trạng thái | Bằng chứng/tệp | Giới hạn |
|---|---|---|---|
| 10 tin IT có nguồn | `VERIFIED` / ... | path thực tế | ... |
| CSV import | `DONE` / `BLOCKED_USER` | path | chưa biết import web hay chưa |
| 9 thuật toán demo | `VERIFIED` / ... | notebook/log | demo không phải dataset thật |
| 9 thuật toán MEDAJob thật | `VERIFIED` / `BLOCKED_USER` | CSV/log | ... |
| So sánh website | `VERIFIED` / `BLOCKED_USER` | comparison/screenshot | ... |
| Báo cáo Word | `VERIFIED` / ... | `.docx` | ... |

Không thông báo 'hoàn thành 100%' nếu còn phần tài liệu gốc bắt buộc chưa có dữ liệu/bằng chứng.

---

# PHẦN XI — PROMPT TỔNG ĐỂ DÁN VÀO CODING AGENT

> Khối bên dưới được viết để **dán nguyên văn** vào Claude Code, Codex hoặc agent tương tự, cùng file Markdown này và tài liệu gốc. Có thể sử dụng làm `AGENTS.md`/project instructions nhưng không che lấp yêu cầu của người dùng.

```text
Bạn là coding/research agent chịu trách nhiệm hỗ trợ hoàn thành bài thực hành
Lab DSS — Website RECSYS gợi ý việc làm.

HÃY ĐỌC TOÀN BỘ các tệp đầu vào sau:
1. AGENT_HANDOFF_LABDSS_RECSYS.md (source of instructions cho dự án lab).
2. LabDSS WebsiteRECSYS.docx (đề bài chính thức, authoritative cho yêu cầu).
3. LabDSS_RECSYS_9_thuat_toan.ipynb (notebook minh họa đã có, KHÔNG phải kết quả thật).
4. CSV Template, MEDAJob CSV và screenshot — CHỈ nếu người dùng đã cung cấp.

MỤC TIÊU:
- Tìm ≥10 tin tuyển dụng CNTT thật, có URL kiểm chứng và lưu dấu vết nguồn.
- Chuẩn hóa dữ liệu, tạo file CSV import đúng template do người dùng gửi.
- Triển khai đủ 9 phương pháp: CBF, CF theo hành vi, Hybrid, User-KNN,
  Item-KNN, Popularity, SGD, ALS Explicit, ALS Implicit.
- Chạy thực nghiệm có log và có thể tái lập trên MEDAJob THẬT khi có file.
- Đối sánh kết quả Python với output website khi có screenshot/dữ liệu web.
- Xuất source đầy đủ, kết quả CSV, checklist và báo cáo Word tiếng Việt
  theo cấu trúc đề gốc, định dạng tự nhiên/Times New Roman.

PHÂN CÔNG KHÔNG THAY ĐỔI:
Người dùng tự đăng nhập, cập nhật hồ sơ, kiểm tra trùng website, import CSV,
rating công việc, chạy gợi ý và chụp output website, tải/cung cấp MEDAJob.
Bạn KHÔNG yêu cầu mật khẩu/OTP/token, không thao tác tài khoản thay người dùng,
không tuyên bố import/rating hoàn tất khi chưa có xác nhận.

NGUYÊN TẮC KỸ THUẬT:
- Bắt đầu ngay các phần không cần chờ người dùng: kiểm kê code, kiểm thử notebook,
  khảo sát nguồn tuyển dụng công khai, tạo bảng trung gian, xây modules/tests,
  chuẩn bị khung báo cáo.
- Không đoán schema CSV Template/MEDAJob; chờ đọc file thực tế rồi mapping.
- Không bịa dữ liệu, citation, link việc làm, ảnh chụp, output terminal,
  kết quả website hoặc số đo trên dataset thật.
- Gắn nhãn DEMO cho kết quả synthetic; chỉ gắn REAL khi có dữ liệu thật.
- Không giả định biết công thức/siêu tham số backend website; ghi rõ lựa chọn
  học thuật do bạn triển khai và giới hạn đối sánh.
- Không overengineering. Dùng Python, pandas/numpy/scikit-learn và thư viện
  cần thiết, ưu tiên CPU. Viết README chạy được trên Windows/VS Code.
- Có unit tests, data validation, deterministic seed và manifest nguồn.
- Không tự commit/push, xóa dữ liệu, sửa tài khoản hoặc xuất bản dữ liệu riêng tư.

ĐẦU RA THEO GIAI ĐOẠN:
A. 10+ jobs IT có nguồn và trạng thái xác minh; file trung gian, dedup.
B. Import-ready CSV khi có template; validation và preview cho người dùng.
C. Code đủ 9 thuật toán + tests + notebook demo minh bạch.
D. Pipeline MEDAJob real CSV + thống kê/snapshot + Top-N/metric khi có file.
E. Đối sánh website–Python khi có output web từ người dùng.
F. Báo cáo Word có bằng chứng thật, code/output và tài liệu tham khảo.

QUY TRÌNH:
1. Lập task board với DONE/VERIFIED/BLOCKED_USER rõ ràng.
2. Triển khai toàn bộ phần có thể triển khai ngay, không trì hoãn vô ích.
3. Chạy tests và kiểm chứng artifacts trước khi tuyên bố hoàn tất.
4. Cuối mỗi giai đoạn cung cấp đường dẫn các file thật đã tạo,
   số liệu kiểm chứng, blocker cụ thể và DUY NHẤT những thao tác người dùng
   phải thực hiện tiếp theo.
5. Đừng kết thúc bằng những tuyên bố chưa có bằng chứng.

ƯU TIÊN HOÀN THÀNH:
Bảo đảm đáp ứng yêu cầu gốc trước, sau đó mới bổ sung tối ưu hóa/tuning.
Nếu tài liệu gốc không chỉ rõ phương pháp đánh giá, đề xuất quy trình thực
nghiệm hợp lý và ghi là đề xuất, không tự gọi là bắt buộc của giảng viên.
```

---

# PHẦN XII — DANH SÁCH ĐẦU VÀO NGƯỜI DÙNG SẼ CUNG CẤP

## 34. Danh sách đầu vào còn thiếu tại thời điểm bàn giao

| Đầu vào | Người cung cấp | Dùng để làm gì | Tình trạng |
|---|---|---|---|
| `LabDSS WebsiteRECSYS.docx` | Đã có trong hội thoại | Yêu cầu gốc | `AVAILABLE` |
| `LabDSS_RECSYS_9_thuat_toan.ipynb` | Đã có trong hội thoại | Code minh họa | `AVAILABLE`, chạy demo OK |
| CSV Template Nhà tuyển dụng | Người dùng | Tạo CSV import thật | `PENDING` |
| Xác nhận tin trùng trên website | Người dùng | Lọc tin trước import | `PENDING` |
| Ảnh/trạng thái import 10 tin | Người dùng | Minh chứng mục 3 | `PENDING` |
| Thông tin skills và rating sau khi cập nhật | Người dùng | Gắn ngữ cảnh gợi ý | `PENDING` |
| Screenshot Top-N trên website | Người dùng | Đối sánh thuật toán | `PENDING` |
| MEDAJob CSV thật | Người dùng | Phân tích/đánh giá 9 thuật toán | `PENDING` |
| Thông tin nhóm học phần, MSSV, họ tên cho trang bìa | Người dùng | Điền báo cáo | `PENDING`, không chặn code |

**Lưu ý:** Nếu agent làm việc trong thư mục/phiên khác, các tệp đính kèm của hội thoại này có thể không tự xuất hiện. Người dùng cần chuyển **tài liệu Markdown này và các tệp đầu vào liên quan** sang workspace của agent. Không giả định agent có thể đọc được đường dẫn sandbox của một phiên khác.

## 35. Kết luận phạm vi giao việc

**Người dùng sẽ làm thủ công**: đăng nhập và quản lý tài khoản; cập nhật hồ sơ; rà soát tin trên website; import CSV; tạo rating; chụp kết quả gợi ý; tải và chuyển file MEDAJob/ảnh/số liệu website.

**Agent phải chủ động làm**: tìm tin IT thật và nguồn, xây CSV hợp template, lập trình/kiểm thử 9 thuật toán, xử lý MEDAJob thật, chạy/đo lường, đối sánh, viết báo cáo Word, làm bộ source + minh chứng có thể kiểm chứng.

Trọng tâm là **làm đúng đề, trung thực với chứng cứ, tự động hóa tối đa những gì có thể mà không tự nhận đã làm các thao tác website thuộc người dùng**.

---

**Hết tài liệu bàn giao.**
