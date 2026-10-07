# Tổng hợp phần đã triển khai

## Dữ liệu

- Tải chính thức College Scorecard institution, field-of-study và lịch sử 2017–2022.
- Lưu URL, thời điểm, byte và SHA-256 trong manifest.
- Tạo 7 bảng processed cho institution, history, state, equity, field, field-state và
  model prediction; có data dictionary và audit.

## Phân tích

- 5 biểu đồ EDA tĩnh.
- 5 insight định lượng, mỗi insight có câu hỏi nghiên cứu và giới hạn.
- Story đi từ địa lý → nhóm → yếu tố → bất lợi cộng dồn → cảnh báo.

## Mô hình

- Hai cấu hình Logistic Regression.
- Temporal holdout: train 2017–2021, test 2022.
- Mô hình chọn đạt Accuracy 81,55%, Balanced Accuracy 80,11%, ROC-AUC 0,874.
- Có confusion matrix, calibration, ROC/PR, feature importance, test predictions và model
  card.

## Dashboard

- Ba trang Streamlit/Plotly.
- Trên 8 loại biểu đồ, có hai geographic map.
- Filter nhiều cấp, drill-down, tooltip, cross-filter qua ngữ cảnh lọc.
- Trang mô hình tích hợp xác suất, mức rủi ro và action list.

## Tài liệu và chất lượng

- Kế hoạch duyệt, truy vết rubric, nguồn, xử lý, model, dashboard, insight/story, giới hạn
  và hướng dẫn tái lập.
- Test tự động bảo vệ rubric, chất lượng dữ liệu và model contract.
- Báo cáo DOCX bản thảo mở hợp lệ trong Word; kiểm tra được 73 trang và 5.039 từ.
- Chưa commit/push. Rubric không bị sửa.

