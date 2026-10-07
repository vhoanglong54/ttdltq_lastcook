# Nghiên cứu và phân tích các yếu tố ảnh hưởng đến kết quả học tập của sinh viên đại học

Dự án phân tích dữ liệu giáo dục đại học Hoa Kỳ từ **College Scorecard** và
**NCES IPEDS**. Trọng tâm là các mối liên hệ giữa tài chính, nguồn lực, loại hình
cơ sở, địa lý và kết quả hoàn thành chương trình; không diễn giải tương quan
thành quan hệ nhân quả.

## Phạm vi đã chốt

- Kết quả chính: tỷ lệ hoàn thành trong 150% thời gian chuẩn, duy trì sau năm
  đầu và rút khỏi chương trình.
- Đơn vị phân tích: cơ sở, nhóm cơ sở, ngành/bậc đào tạo và năm; không phải hồ
  sơ định danh từng sinh viên.
- Mô hình: Logistic Regression cảnh báo nhóm cơ sở có tỷ lệ hoàn thành dưới
  40%; dashboard chỉ ra nhóm ưu tiên, yếu tố làm xác suất dự báo cao hơn và
  hướng cải thiện cần kiểm tra.
- Trực quan: Streamlit + Plotly, có bản đồ địa lý, bộ lọc, drill-down,
  tooltip và cross-filter.
- Thu nhập sau tốt nghiệp chỉ là kết quả bổ sung.

## Cấu trúc

```text
config/                 Cấu hình nguồn dữ liệu, biến và mô hình
data/
  raw/                  Dữ liệu gốc (không đưa lên Git)
  interim/              Dữ liệu trung gian (không đưa lên Git)
  processed/            Bảng đã làm sạch phục vụ phân tích/dashboard
docs/                   Kế hoạch, dữ liệu, mô hình, insight và rubric mapping
models/                 Mô hình và metadata đánh giá
outputs/                Biểu đồ EDA, bảng kiểm tra và kết quả mô hình
report/                 Báo cáo DOCX sinh tự động
scripts/                Điểm chạy từng bước
src/ttdltq/             Mã nguồn chính
dashboard/              Ứng dụng Streamlit
tests/                   Kiểm tra schema, chất lượng và leakage
```

## Chạy dự án

Yêu cầu Python 3.11+.

```powershell
python -m pip install -r requirements.txt
python scripts/download_data.py --include-history --skip-ipeds
python scripts/build_dataset.py
python scripts/run_eda.py
python scripts/train_model.py --prefer-temporal
python scripts/build_report.py
streamlit run dashboard/app.py
```

Tải riêng các bảng IPEDS chính thức khi máy có thể kết nối máy chủ NCES:

```powershell
python scripts/download_data.py --skip-scorecard
```

College Scorecard đã tích hợp nhiều biến gốc IPEDS. Bản raw IPEDS riêng được dùng
để đối chiếu nguồn; pipeline không tự thay bằng nguồn không chính thức khi máy chủ
NCES không phản hồi.

Chạy kiểm thử:

```powershell
python -m pytest -q
```

## Nguồn chính thức

- College Scorecard: <https://catalog.data.gov/dataset/college-scorecard>
- NCES IPEDS: <https://nces.ed.gov/ipeds/use-the-data>

Chi tiết nguồn, phiên bản, giới hạn và checksum được ghi trong
`data/source_manifest.json` sau khi tải.

## Nguyên tắc nghiệm thu

Một kết quả chỉ được coi là hoàn thành khi có đủ mã tái lập, đầu ra, kiểm tra
chất lượng và giải thích trong tài liệu. Không xem việc tạo file hoặc chạy mô
hình một lần là bằng chứng nghiệm thu.

