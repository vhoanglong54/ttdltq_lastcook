# Model card — cảnh báo tỷ lệ hoàn thành thấp

## Mục tiêu

Dự báo cơ sở/nhóm cơ sở có tỷ lệ hoàn thành trong 150% thời gian chuẩn dưới 40%. 
Mô hình không dự báo danh tính hay kết quả của từng sinh viên.

## Thuật toán

Logistic Regression với trọng số cân bằng lớp. Các biến số liên tục được biến đổi 
bằng spline trước khi đi vào Logistic Regression để biểu diễn quan hệ phi tuyến; 
bộ phân loại cuối cùng vẫn là Logistic Regression đúng yêu cầu rubric.

## Chia dữ liệu

- Chiến lược: `temporal_last_year_holdout`
- Train: 27,887 dòng
- Test: 5,359 dòng

## Kết quả trên test

- Accuracy: **0.815**
- Balanced Accuracy: **0.801**
- Recall nhóm rủi ro: **0.768**
- Precision: **0.648**
- F1: **0.703**
- ROC-AUC: **0.874**
- Brier score: **0.136**

Ngưỡng nghiệm thu bắt buộc của dự án là Accuracy >= 0,80 và không dùng biến 
rò rỉ mục tiêu. Balanced Accuracy và Recall >= 0,80 là mục tiêu chẩn đoán bổ sung, 
được công bố trung thực ngay cả khi chưa đạt.

Accuracy đo tỷ lệ dự báo đúng tổng thể; Balanced Accuracy cân bằng giữa hai lớp; 
Recall đo tỷ lệ nhóm hoàn thành thấp được phát hiện; Precision cho biết mức đúng 
của các cảnh báo; F1 cân bằng Precision–Recall; ROC-AUC đo khả năng xếp hạng rủi ro; 
Brier score đo chất lượng xác suất (càng thấp càng tốt).

## Yếu tố có giá trị dự báo lớn

- `tuition_in_state`: permutation importance 0.1346
- `retention_rate`: permutation importance 0.0745
- `predominant_degree`: permutation importance 0.0629
- `control`: permutation importance 0.0115
- `federal_loan_share`: permutation importance 0.0085
- `pell_share`: permutation importance 0.0070
- `net_price`: permutation importance 0.0017
- `log_undergrad_enrollment`: permutation importance 0.0008

## Giới hạn

- Dữ liệu quan sát chỉ chứng minh mối liên hệ, không chứng minh nguyên nhân.
- Một số chỉ số chỉ đại diện người nhận hỗ trợ Title IV.
- Ô có cỡ mẫu nhỏ có thể bị privacy suppression.
- Retention là chỉ báo sớm ở cấp cơ sở, không phải đặc điểm cá nhân.
- Kết quả hiện đã được đánh giá theo thời gian (test 2022); vẫn cần theo dõi drift khi có năm mới.
