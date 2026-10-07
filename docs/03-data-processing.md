# Quy trình xử lý dữ liệu

## Luồng dữ liệu

```text
Nguồn chính thức
  ├─ Scorecard Institution (hiện tại + 6 năm lịch sử)
  └─ Scorecard Field of Study
          ↓ tải nguyên tử + SHA-256
data/raw → chọn cột → chuẩn hóa NA/kiểu dữ liệu → kiểm tra miền giá trị
          ↓                         ↓
institution / history         field-of-study
          ↓ UNITID join             ↓ CIP/CREDLEV aggregate
equity, state, audit, EDA, Logistic Regression, dashboard, DOCX
```

## Làm sạch

- Quy ước `NULL`, `NA`, `PS`, `PrivacySuppressed` và chuỗi rỗng là missing.
- Ép các cột số bằng `to_numeric(errors="coerce")`; giữ tên, thành phố, bang và mô tả
  ngành ở dạng chuỗi.
- Chuẩn hóa `UNITID` thành số nguyên nullable, bỏ bản ghi không có khóa và giữ một dòng
  cho mỗi `UNITID` ở snapshot hiện tại.
- Đồng nhất biến bốn năm/dưới bốn năm bằng phép coalesce có thứ tự.
- Không tự ý xóa ngoại lai hợp lệ như trường rất lớn/chi phí cao. Outlier được hiển thị
  trong box plot; các tỷ lệ ngoài [0,1] mới bị xem là lỗi dữ liệu.
- Mô hình xử lý missing bên trong pipeline: median cho số, mode cho danh mục. Imputer chỉ
  được fit trên train nên không lấy thông tin từ test.

## Nối và biến đổi

- `field-of-study many-to-one institution` qua `UNITID`, có kiểm tra `validate`.
- Bảng Pell/first-generation chuyển từ wide sang long để so sánh nhóm.
- Bảng lịch sử ghép dọc và thêm `academic_year` từ tên file.
- `completion_rate`: coalesce `C150_4` và `C150_L4`.
- `low_completion = 1` khi `completion_rate < 0.40`.
- `log_undergrad_enrollment = log(1 + UGDS)`.
- `risk_probability`: xác suất từ Logistic Regression.
- `risk_level`: Thấp [0;0,4), Trung bình [0,4;0,7), Cao [0,7;1].
- `disadvantage_count`: tổng số điều kiện bất lợi theo các ngưỡng phân vị được lưu ở
  `outputs/eda/disadvantage_thresholds.csv`.

## Audit thực tế

- Institution raw: 6.429 dòng; 5.256 dòng có kết quả hoàn thành.
- Field raw: 229.188 dòng.
- Tọa độ hợp lệ: 5.924 cơ sở.
- Panel lịch sử: 40.321 dòng, 2017–2022.
- `UNITID` trùng trong snapshot hiện tại: 0.
- Số tỷ lệ nằm ngoài [0,1]: 0.

Chi tiết và tỷ lệ thiếu của từng biến quan trọng ở
`outputs/eda/data_quality_audit.json`.

