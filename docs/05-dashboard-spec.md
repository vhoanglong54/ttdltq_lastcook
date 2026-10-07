# Dashboard, biểu đồ và tương tác

## Công cụ

Streamlit + Plotly. Khởi chạy bằng:

```powershell
streamlit run dashboard/app.py
```

## Trang 1 — Bức tranh toàn quốc

- KPI: số cơ sở, quy mô sinh viên, tỷ lệ hoàn thành, tỷ trọng cơ sở hoàn thành thấp.
- Choropleth theo bang: Geographic Map bắt buộc.
- Bar xếp hạng bang thấp/cao.
- Bảng đối chiếu trực tiếp bang thấp nhất và cao nhất về retention, giảng viên toàn thời
  gian, nhu cầu tài chính, cơ cấu bậc đào tạo và mức đô thị–nông thôn.
- Bar so sánh kết quả theo khu vực sống.
- 100% stacked bar: cơ cấu rủi ro theo bậc đào tạo.

Kết luận cần rút ra: chênh lệch giữa các bang đi cùng khác biệt cụ thể về khả năng tiếp
tục học, đội ngũ giảng dạy và cơ cấu chương trình. Dashboard phải nêu các chênh lệch này
ngay cạnh bản đồ thay vì chỉ nói địa lý là “bối cảnh”.

Bang được chọn vì đây là dữ liệu Hoa Kỳ và là cấp tổng hợp địa lý phù hợp với bản đồ bắt
buộc của rubric. Mức độ hẻo lánh được đo trực tiếp bằng tỷ trọng cơ sở ở nông thôn/thị
trấn, thay vì suy đoán từ vị trí của bang.

## Trang 2 — Các yếu tố liên quan đến kết quả

- Line chart bốn mức: kết quả thay đổi ra sao khi một yếu tố từ thấp lên cao.
- Scatter hệ số: hướng và độ mạnh liên hệ của từng yếu tố.
- Heatmap hai chiều: khu vực kết hợp loại hình quản lý.
- Grouped bar: Pell/first-generation và hoàn thành/rút khỏi.
- Bar + line: bất lợi cộng dồn.

Kết luận cần rút ra: tiếp tục học sau năm nhất là tín hiệu rõ nhất; số sinh viên trên
mỗi giảng viên và nhu cầu hỗ trợ tài chính đi cùng khoảng cách; bất lợi cần được xem
đồng thời thay vì tách rời.

## Trang 3 — Dự báo và ưu tiên kiểm tra

- Ba KPI dự báo hiện tại: số nhóm được dự báo dưới 40%, số nhóm rủi ro từ 70% và xác
  suất rủi ro trung bình.
- Grouped bar so sánh Accuracy, Recall và ROC-AUC giữa mô hình điều kiện nền tảng với
  mô hình bổ sung thông tin sau năm nhất.
- Gauge xác suất rủi ro trung bình.
- Donut cơ cấu mức rủi ro.
- Confusion matrix heatmap.
- Feature-importance bar.
- Heatmap mức tiếp tục học × áp lực nguồn lực giảng dạy.
- Bảng 5 hồ sơ ưu tiên: nhóm nào rủi ro cao, yếu tố nổi bật và cải thiện ưu tiên.
- Expander giải thích đầy đủ từng hồ sơ bằng kiểm tra phản thực tế của mô hình.
- Bar tổng hợp rủi ro theo loại hình, khu vực, bậc đào tạo hoặc hình thức học.
- Ba gợi ý ưu tiên được rút trực tiếp từ kết quả dự báo.

Không hiển thị danh sách hoặc bảng xếp hạng từng trường.

Trang này phải trả lời theo thứ tự: **mô hình dự báo điều gì → đáng tin đến đâu → nhóm
nào cần ưu tiên kiểm tra → vì sao mô hình gắn rủi ro cao → nên kiểm tra cải thiện gì**.
Xác suất chỉ hỗ trợ sắp xếp ưu tiên,
không phải tỷ lệ sinh viên chắc chắn thất bại và không chứng minh quan hệ nhân quả.

## Tương tác

- Filter toàn cục nhiều cấp: bang, loại cơ sở, bậc đào tạo, địa bàn và đào tạo từ xa.
- Filter mức rủi ro ở trang mô hình.
- Filter áp dụng đồng thời KPI và biểu đồ, tạo cross-filter theo ngữ cảnh đã chọn.
- Drill-down bằng bộ lọc theo tuyến toàn quốc → bang → loại hình/bậc đào tạo.
- Tooltip hiển thị tên, tỷ lệ, quy mô và các biến liên quan.

## Danh mục loại biểu đồ

1. choropleth map;
2. horizontal bar;
3. 100% stacked bar;
4. scatter plot;
5. box plot;
6. heatmap;
7. grouped bar;
8. line chart kết hợp bar;
9. grouped bar so sánh mô hình;
10. gauge;
11. donut;
12. confusion matrix;
13. heatmap hồ sơ rủi ro;
14. risk bar theo nhóm.

Màu đỏ chỉ rủi ro, xanh lá kết quả tốt, xanh lam/tràm dùng cho thông tin trung tính. Mọi
trục tỷ lệ hiển thị dạng phần trăm và biểu đồ có tiêu đề/legend/tooltip.

