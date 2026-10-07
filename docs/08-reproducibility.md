# Tái lập, kiểm thử và nghiệm thu

## Môi trường

- Python 3.11 trở lên.
- Phiên bản thư viện khóa trong `requirements.txt`.
- Mọi đường dẫn được suy ra từ project root; không phụ thuộc thư mục cũ.

## Chạy từng bước

```powershell
python -m pip install -r requirements.txt
python scripts/download_data.py --include-history --skip-ipeds
python scripts/build_dataset.py
python scripts/run_eda.py
python scripts/train_model.py --prefer-temporal
python -m pytest -q
python scripts/build_report.py
streamlit run dashboard/app.py
```

Hoặc chạy `powershell -ExecutionPolicy Bypass -File scripts/run_pipeline.ps1`.

## Kiểm thử bắt buộc

- checksum rubric không đổi;
- >=5.000 dòng, `UNITID` duy nhất ở snapshot hiện tại;
- tỷ lệ nằm trong [0,1];
- lịch sử 2017–2022 đủ temporal split;
- không dùng biến target/leakage;
- Accuracy temporal test >=80%;
- xác suất dự báo nằm trong [0,1] và một dòng mỗi cơ sở hiện tại;
- đủ bảng/figure/output cần thiết.

## Cơ chế đối chiếu độ chính xác

1. Mở `models/metrics.json` để xem chiến lược split và model được chọn.
2. Dùng `models/test_predictions.csv` để tính lại dự báo từng dòng test 2022.
3. Đối chiếu tổng số với `models/confusion_matrix.csv`.
4. Chạy test model contract; test thất bại nếu Accuracy xuống dưới 0,80 hoặc xuất hiện
   feature rò rỉ.
5. Xem ROC/PR, calibration và confusion matrix thay vì chỉ nhìn Accuracy.

## Trạng thái nghiệm thu

Tạo file không đồng nghĩa hoàn thành. Một phần chỉ được nghiệm thu khi có code, đầu ra,
kiểm thử và giải thích khớp nhau. Video demo và biên tập báo cáo 40+ trang vẫn cần người
thực hiện hoàn tất trước nộp.

