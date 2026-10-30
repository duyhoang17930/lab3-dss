# Định nghĩa thực nghiệm

## Dữ liệu

users.csv cần id, username; user_profiles.csv cần user_id,user_skills; job.csv hoặc jobs.csv cần id,job_title,job_skills; ratings.csv cần user_id,job_id,rating; job_views.csv cần user_id,job_id,view_duration. Cột tùy chọn: company_name,job_location,status,deadline. Khi không có status, adapter mặc định open và metadata schema thể hiện việc thiếu cột. Các snapshot thực đều có status.

Kỹ năng không đồng nhất từ vựng (ví dụ JS/JavaScript) không được tự quy đồng; chỉ NFC, lowercase, trim, loại lặp. Đây là hạn chế cần lưu ý của CBF.

## Chín biến thể Python

1. CBF: cosine/Jaccard/Pearson trên multi-hot kỹ năng. Pearson trừ trung bình trên cùng vocabulary của metadata.
2. CF hành vi: item-item cosine trên B; bỏ đường chéo; affinity tổng có trọng số.
3. Hybrid: 0.55 min-max CBF + 0.45 min-max CF; các nhánh thiếu có nhãn và không trộn prior rating vào affinity.
4. User-KNN: top5 cosine user, weighted mean rating với mẫu số theo mask.
5. Item-KNN: top5 cosine item, weighted mean rating với mẫu số theo mask.
6. Popularity: (tổng rating +5×global mean)/(số rating +5), không phải số lượt xem.
7. SGD: global mean + bias user/item + tích vô hướng nhân tố,45 epoch,lr0.012,reg0.04.
8. ALS Explicit: rating trừ global mean, ridge theo rating quan sát,12 vòng,reg0.4.
9. ALS Implicit: P=1[B>0],C=1+16B,confidence-weighted ALS,10 vòng,reg0.7.

Các MF dùng12 nhân tố,seed42. Rating≥4 tạo B=rating/5; lượt xem dương chỉ với cặp chưa rating tạo B=0.25. Không dùng rating thấp làm thích. CBF không học từ rating, nên dữ liệu kỹ năng static được phép có mặt khi holdout; không có lịch sử profile để tái tạo trạng thái quá khứ.

## Đánh giá và fallback

Chỉ lấy một test positive/user đủ điều kiện; mỗi test item còn rating train. Holdout random này thiên về nhóm đã tương tác và không đo cold-start thực tế toàn hệ thống. Không lấy metric trên full snapshot làm test. Không tune tham số trên test.

Fallback có thể làm metric xếp hạng cao dù thuật toán bản thân thiếu tín hiệu; luôn đọc fallback_fraction cùng metric. Trường rating_prediction_fallback_fraction nói riêng về dự đoán rating của cặp test. RMSE không so với điểm cosine hoặc implicit affinity.

Các danh sách model-supported được xếp trước prior fallback; việc này là chính sách công khai của thực nghiệm và không được giả định là chính sách website. Source `job_recsys/models.py` là căn cứ tái lập.

## Nguồn thuật toán

- Hu, Koren, Volinsky (2008), Collaborative Filtering for Implicit Feedback Datasets: https://yifanhu.net/PUB/cf.pdf. Tham khảo phân biệt preference và confidence; tham số và chuyển đổi tín hiệu cụ thể do notebook quy định.
- Koren, Bell, Volinsky (2009), Matrix Factorization Techniques for Recommender Systems, Computer42(8),30–37: https://doi.org/10.1109/MC.2009.263. Tham khảo mô hình nhân tố; không khẳng định bản cài đặt trùng tất cả biến thể trong bài.
- Nguồn website/tin tuyển dụng được lưu trong data/import và từng capture JSON, truy cập ngày28/10/2026.
