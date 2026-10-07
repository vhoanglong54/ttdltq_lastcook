# Logistic Regression — tài liệu chuẩn duy nhất

## Mô hình dự báo cái gì?

Mô hình trả lời:

> Với thông tin có thể biết ở cấp cơ sở, cơ sở nào có nguy cơ có tỷ lệ hoàn thành chương
> trình trong 150% thời gian chuẩn dưới 40%?

Nhãn `low_completion = 1` nếu `completion_rate < 0,40`; ngược lại bằng 0. Mô hình dự
báo **cơ sở**, không dự báo danh tính hay kết quả của từng sinh viên.

## Vì sao dùng Logistic Regression?

Đầu ra là hai lớp nên Logistic Regression đúng loại bài toán và đúng thuật toán rubric.
Mô hình tạo xác suất 0–1, dễ chuyển thành mức rủi ro và giải thích. Bản chính dùng
`SplineTransformer` cho biến số liên tục trước Logistic Regression để biểu diễn quan hệ
không hoàn toàn tuyến tính; bộ phân loại cuối vẫn là Logistic Regression.

Hai cấu hình được so sánh:

- baseline Logistic Regression;
- balanced spline Logistic Regression — mô hình được chọn vì cân bằng phát hiện hai lớp
  tốt hơn.

## Biến đầu vào

Danh mục: bậc đào tạo chính, loại hình cơ sở, địa bàn, chỉ đào tạo từ xa.

Số: log quy mô đại học, tỷ lệ Pell, tỷ lệ vay liên bang, tỷ lệ sinh viên/giảng viên,
chi phí ròng, học phí trong bang và tỷ lệ duy trì sau năm đầu.

`completion_rate`, `low_completion`, `C150_4`, `C150_L4` bị cấm khỏi đầu vào để tránh
rò rỉ mục tiêu. Test tự động kiểm tra quy tắc này.

## Chia dữ liệu và chống đánh giá quá lạc quan

- Train: 27.887 dòng cơ sở–năm từ 2017–2021.
- Test ngoài thời gian: 5.359 dòng của năm 2022.
- Imputer, encoder, scaler và spline chỉ fit trong pipeline trên train.
- Test 2022 không dùng để chọn biến hoặc sửa ngưỡng sau khi xem kết quả.
- Sau đánh giá, cùng cấu hình được refit trên lịch sử để chấm xác suất cho snapshot hiện
  tại; việc refit không làm thay đổi chỉ số test đã lưu.

## Kết quả temporal test 2022

| Chỉ số | Baseline | Balanced spline Logistic |
|---|---:|---:|
| Accuracy | 81,75% | **81,55%** |
| Balanced Accuracy | 74,97% | **80,11%** |
| Recall nhóm rủi ro | 59,25% | **76,77%** |
| Specificity | 90,69% | **83,44%** |
| Precision | 71,67% | **64,82%** |
| F1 | 64,87% | **70,29%** |
| ROC-AUC | 0,849 | **0,874** |
| Brier score | **0,133** | 0,136 |

Ma trận nhầm lẫn mô hình chọn:

| | Dự báo không thấp | Dự báo thấp |
|---|---:|---:|
| Thực tế không thấp | 3.200 | 635 |
| Thực tế thấp | 354 | 1.170 |

Accuracy vượt yêu cầu 80%. Recall chưa đạt mục tiêu tham khảo 80%; đây là giới hạn phải
nêu khi dùng danh sách cảnh báo. Không hạ ngưỡng sau khi nhìn test chỉ để làm đẹp chỉ số.

## Ý nghĩa từng chỉ số

- **Accuracy**: phần trăm dự báo đúng trên toàn test; phù hợp cổng nghiệm thu >80%.
- **Balanced Accuracy**: trung bình khả năng nhận đúng hai lớp; chống việc lớp đông lấn
  át lớp rủi ro.
- **Recall**: trong các cơ sở thực sự có kết quả thấp, mô hình phát hiện được bao nhiêu.
- **Precision**: trong các cảnh báo phát ra, bao nhiêu cảnh báo đúng.
- **F1**: cân bằng Precision và Recall.
- **ROC-AUC**: khả năng xếp một trường rủi ro cao hơn một trường không rủi ro trên mọi
  ngưỡng; 0,5 là ngẫu nhiên, 1 là hoàn hảo.
- **Brier score**: sai số bình phương của xác suất; càng thấp càng tốt.

Không diễn giải Accuracy 81,55% thành “dự đoán đúng 81,55% sinh viên”; đơn vị test là
cơ sở–năm.

## Đối chiếu và tái kiểm tra

```powershell
python scripts/build_dataset.py
python scripts/train_model.py --prefer-temporal
python -m pytest -q
```

Đối chiếu các file:

- `models/metrics.json`: chỉ số, split, feature và quality gate;
- `models/confusion_matrix.csv`: bốn ô TP/FP/TN/FN;
- `models/test_predictions.csv`: từng dòng test 2022 cùng nhãn và xác suất;
- `models/feature_importance.csv`: permutation importance trên test;
- `outputs/figures/model_roc_pr.png`, `model_calibration.png` và
  `model_confusion_matrix.png`.

## Đưa lên dashboard

`data/processed/model_predictions.csv` có một dòng cho mỗi cơ sở hiện tại, gồm
`risk_probability`, `predicted_low_completion` và `risk_level`. Dashboard hiển thị gauge,
donut, confusion matrix, feature importance và bảng ưu tiên kiểm tra. Xác suất là công cụ
xếp hạng, không phải kết luận kỷ luật hay đánh giá chất lượng tuyệt đối.

