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

- Hai kịch bản Logistic Regression: điều kiện nền tảng và bổ sung thông tin sau năm nhất.
- Temporal holdout: train 2017–2021, test 2022.
- Mô hình nền tảng đạt Accuracy 80,09%; mô hình sau năm nhất đạt Accuracy 81,34% và
  ROC-AUC 0,877.
- Có confusion matrix, calibration, ROC/PR, feature importance, test predictions và model
  card.
- Dashboard đã chuyển đầu ra dự báo thành số nhóm dưới ngưỡng 40%, số nhóm rủi ro cao,
  so sánh hai thời điểm dự báo và ma trận tiếp tục học × áp lực nguồn lực.
- Có hồ sơ ưu tiên tự động ở cấp nhóm, kiểm tra phản thực tế từng yếu tố trên mô hình và
  ánh xạ yếu tố nổi bật sang hướng cải thiện cần xem xét.
- Kết luận hành động được giới hạn ở ưu tiên kiểm tra và hỗ trợ cấp nhóm; không xếp hạng
  từng trường, không dự báo từng sinh viên và không diễn giải thành tác động nhân quả.

## Dashboard

- Ba trang Streamlit/Plotly.
- Trên 8 loại biểu đồ, có choropleth Geographic Map bắt buộc theo bang.
- Ngay dưới bản đồ có bảng giải thích chênh lệch bang bằng retention, nguồn lực giảng
  dạy, nhu cầu tài chính, cơ cấu bậc đào tạo và mức nông thôn/thị trấn.
- Filter nhiều cấp, drill-down, tooltip, cross-filter qua ngữ cảnh lọc.
- Trang mô hình hiển thị rủi ro tổng hợp, tổ hợp rủi ro và gợi ý ưu tiên theo nhóm, không
  xếp hạng tên từng trường.

## Tài liệu và chất lượng

- Kế hoạch duyệt, truy vết rubric, nguồn, xử lý, model, dashboard, insight/story, giới hạn
  và hướng dẫn tái lập.
- Test tự động bảo vệ rubric, chất lượng dữ liệu và model contract.
- Báo cáo DOCX đã tái tập trung vào yếu tố, mở hợp lệ trong Word; kiểm tra được 73 trang
  và 5.183 từ.
- Chưa commit/push. Rubric không bị sửa.

