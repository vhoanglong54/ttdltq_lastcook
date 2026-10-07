# Truy vết yêu cầu rubric

File rubric gốc là tài liệu chỉ đọc. SHA-256 được khóa trong
`data/source_manifest.json` và được kiểm tra tự động.

| Tiêu chí rubric | Bằng chứng trong dự án | Trạng thái |
|---|---|---|
| Nguồn có link/minh chứng | `config/data_sources.yaml`, `data/source_manifest.json`, `docs/02-data-sources.md` | Đạt |
| Ít nhất 5.000 dòng | Institution 6.429; field 229.188; panel lịch sử 40.321 | Đạt |
| Ít nhất 3 bảng | Institution, field-of-study, 6 bảng institution-year; các bảng processed riêng | Đạt |
| Data dictionary | `data/processed/data_dictionary.csv` | Đạt |
| Xử lý missing/outlier/định dạng | `src/ttdltq/data/prepare.py`, audit JSON | Đạt bằng code |
| Join/Merge | `UNITID` nối institution–field; khóa năm cho panel; bảng equity dạng long | Đạt |
| Calculated fields | `completion_rate`, `low_completion`, log enrollment, risk probability, disadvantage count | Đạt |
| 3–5 biểu đồ EDA tĩnh | 5 PNG trong `outputs/figures/eda_*.png` | Đạt |
| Công cụ hợp lệ | Streamlit + Plotly | Đạt |
| UI/UX, tiêu đề, legend | `dashboard/app.py`, bảng màu và giải thích trực tiếp | Đã triển khai; cần duyệt hình thức |
| Ít nhất 8 loại biểu đồ | Choropleth, scatter map, bar, 100% stacked bar, scatter, box, heatmap, grouped bar, line, treemap, gauge, donut, matrix, table | Đạt |
| Geographic Map | Choropleth theo bang và point map theo cơ sở | Đạt |
| Filter nhiều cấp | Bang, loại cơ sở, bậc đào tạo, địa bàn, đào tạo từ xa, risk level | Đạt |
| Drill-down | Toàn quốc → bang → cơ sở; nhóm ngành → ngành/bậc văn bằng | Đạt qua bộ lọc |
| Tooltip | Plotly hover cho bản đồ và biểu đồ | Đạt |
| Cross-filtering | Bộ lọc toàn cục tác động đồng thời các KPI và biểu đồ trên trang | Đạt |
| Insight/story | `outputs/eda/insights.json`, `docs/06-insights-and-story.md`, insight card trên dashboard | Đạt bản đầu |
| Logistic Regression | baseline và balanced spline Logistic; classifier cuối là Logistic Regression | Đạt |
| Trực quan dự báo | Gauge, donut, confusion matrix, feature importance và rủi ro tổng hợp theo nhóm | Đạt |
| Accuracy >80% | Test 2022: nền tảng 80,09%; sau năm nhất 81,34% | Đạt |
| Pipeline/sơ đồ/pseudocode | `docs/03-data-processing.md`, báo cáo DOCX | Đạt bản đầu |
| Báo cáo khoa học >=40 trang | `report/TTDLTQ_report_draft.docx`: Word kiểm tra 73 trang, 5.183 từ | Đạt số trang ở bản thảo; cần điền thông tin nhóm và biên tập cuối |
| Video demo backup | Kịch bản có trong báo cáo | Chưa quay video |
| Bảo vệ hiểu code | `docs/08-reproducibility.md` và nội dung giải thích chỉ số | Cần người thực hiện luyện trình bày |

Không đánh dấu “đạt” cho video và báo cáo 40 trang chỉ dựa trên việc có placeholder.

