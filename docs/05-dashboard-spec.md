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
- 100% stacked bar: cơ cấu rủi ro theo loại trường.
- Scatter geographic map: đi sâu tới từng cơ sở.

Kết luận cần rút ra: kết quả phân bố không đồng đều theo bang và loại hình, nhưng khác
biệt địa lý không tự động là tác động của bang.

## Trang 2 — Tác nhân liên quan và khoảng cách nhóm

- Scatter + trend: duy trì năm đầu với hoàn thành.
- Box plot: phân bố theo loại hình.
- Correlation heatmap: hướng và độ mạnh liên hệ đơn biến.
- Grouped bar: Pell/first-generation và hoàn thành/rút khỏi.
- Bar + line: bất lợi cộng dồn.
- Treemap: cơ cấu văn bằng theo ngành/bậc đào tạo.

Kết luận cần rút ra: duy trì năm đầu là chỉ báo mô tả mạnh; nhu cầu hỗ trợ tài chính đi
cùng khoảng cách; bất lợi nên được xem đồng thời. Treemap ngành là bối cảnh quy mô đầu ra,
không được diễn giải là tỷ lệ tốt nghiệp ngành.

## Trang 3 — Dự báo và ưu tiên kiểm tra

- Gauge xác suất rủi ro trung bình.
- Donut cơ cấu mức rủi ro.
- Confusion matrix heatmap.
- Feature-importance bar.
- Action table có progress bar xác suất.

## Tương tác

- Filter toàn cục nhiều cấp: bang, loại cơ sở, bậc đào tạo, địa bàn và đào tạo từ xa.
- Filter mức rủi ro ở trang mô hình.
- Filter áp dụng đồng thời KPI và biểu đồ, tạo cross-filter theo ngữ cảnh đã chọn.
- Drill-down theo tuyến toàn quốc → bang → cơ sở và bậc văn bằng → ngành.
- Tooltip hiển thị tên, tỷ lệ, quy mô và các biến liên quan.

## Danh mục loại biểu đồ

1. choropleth map;
2. scatter geographic map;
3. horizontal bar;
4. 100% stacked bar;
5. scatter plot + trendline;
6. box plot;
7. heatmap;
8. grouped bar;
9. line chart kết hợp bar;
10. treemap;
11. gauge;
12. donut;
13. confusion matrix;
14. table với data bar.

Màu đỏ chỉ rủi ro, xanh lá kết quả tốt, xanh lam/tràm dùng cho thông tin trung tính. Mọi
trục tỷ lệ hiển thị dạng phần trăm và biểu đồ có tiêu đề/legend/tooltip.

