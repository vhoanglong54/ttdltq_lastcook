# Model card — cảnh báo tỷ lệ hoàn thành thấp

## Mục tiêu

Dự báo cơ sở/nhóm cơ sở có tỷ lệ hoàn thành trong 150% thời gian chuẩn dưới 40%.
Mô hình không dự báo danh tính hay kết quả của từng sinh viên.

## Thuật toán

Hai kịch bản đều dùng Logistic Regression với trọng số cân bằng lớp. Mô hình nền tảng
dùng bối cảnh tài chính, nguồn lực và loại hình; mô hình sau năm nhất bổ sung tỷ lệ
tiếp tục học. Biến số liên tục được biến đổi bằng spline trước Logistic Regression;
bộ phân loại cuối cùng vẫn đúng thuật toán rubric.

## Chia dữ liệu

- Chiến lược: `temporal_last_year_holdout`
- Train: 27,887 dòng
- Test: 5,359 dòng

## Kết quả trên test

- Mô hình nền tảng — Accuracy: **0.801**, ROC-AUC: **0.847**
- Mô hình sau năm nhất — Accuracy: **0.813**, ROC-AUC: **0.876**

Chỉ số chi tiết của mô hình sau năm nhất:

- Accuracy: **0.813**
- Balanced Accuracy: **0.798**
- Recall nhóm rủi ro: **0.764**
- Precision: **0.644**
- F1: **0.699**
- ROC-AUC: **0.876**
- Brier score: **0.133**

Ngưỡng nghiệm thu bắt buộc của dự án là Accuracy >= 0,80 và không dùng biến 
rò rỉ mục tiêu. Balanced Accuracy và Recall >= 0,80 là mục tiêu chẩn đoán bổ sung, 
được công bố trung thực ngay cả khi chưa đạt.

Accuracy đo tỷ lệ dự báo đúng tổng thể; Balanced Accuracy cân bằng giữa hai lớp; 
Recall đo tỷ lệ nhóm hoàn thành thấp được phát hiện; Precision cho biết mức đúng 
của các cảnh báo; F1 cân bằng Precision–Recall; ROC-AUC đo khả năng xếp hạng rủi ro; 
Brier score đo chất lượng xác suất (càng thấp càng tốt).

## Yếu tố có giá trị dự báo lớn

- `tuition_in_state`: permutation importance 0.0988
- `retention_rate`: permutation importance 0.0543
- `predominant_degree`: permutation importance 0.0517
- `full_time_faculty_share`: permutation importance 0.0058
- `control`: permutation importance 0.0040
- `pell_share`: permutation importance 0.0019
- `average_faculty_salary`: permutation importance 0.0004
- `locale_group`: permutation importance 0.0000

## Giới hạn

- Dữ liệu quan sát chỉ chứng minh mối liên hệ, không chứng minh nguyên nhân.
- Một số chỉ số chỉ đại diện người nhận hỗ trợ Title IV.
- Ô có cỡ mẫu nhỏ có thể bị privacy suppression.
- Retention là chỉ báo sớm ở cấp cơ sở, không phải đặc điểm cá nhân.
- Kết quả hiện đã được đánh giá theo thời gian (test 2022); vẫn cần theo dõi drift khi có năm mới.
