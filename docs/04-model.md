# Logistic Regression — tài liệu chuẩn duy nhất

## Mô hình có đúng trọng tâm đề tài không?

Có, với cách hiểu chính xác sau:

> Mô hình kết hợp các yếu tố tài chính, nguồn lực, bối cảnh đào tạo và khả năng tiếp tục
> học sau năm nhất để nhận diện **nhóm cơ sở–năm có tỷ lệ hoàn thành chương trình dưới
> 40%**.

Mô hình không dự báo thu nhập, không dự báo tên trường nào “tốt/xấu” và không dự báo
từng sinh viên. Dữ liệu gốc chỉ công bố ở cấp cơ sở/nhóm nên dòng cơ sở–năm là đơn vị
tính toán; dashboard chỉ trình bày kết quả tổng hợp theo yếu tố và nhóm.

## Vì sao cần hai kịch bản?

### Kịch bản 1 — Mô hình điều kiện nền tảng

Dùng những thông tin về:

- hoàn cảnh tài chính: Pell Grant, khoản vay, chi phí thực trả và học phí;
- nguồn lực: số sinh viên trên giảng viên, chi cho giảng dạy, lương giảng viên và tỷ lệ
  giảng viên toàn thời gian;
- bối cảnh: quy mô, mức tuyển chọn, bậc đào tạo, loại hình, địa bàn, học trực tuyến và tỷ
  lệ người học trên 25 tuổi.

Mô hình này trả lời: **chỉ từ điều kiện nền tảng, có thể nhận diện nhóm kết quả thấp đến
mức nào?**

### Kịch bản 2 — Mô hình sau năm nhất

Dùng toàn bộ yếu tố trên và bổ sung tỷ lệ sinh viên tiếp tục học sau năm nhất. Mô hình
này trả lời: **sau khi đã biết sinh viên có quay lại học năm tiếp theo hay không, khả năng
nhận diện nhóm kết quả thấp cải thiện bao nhiêu?**

Vì vậy cụm từ “cảnh báo sớm” chỉ được dùng cho thời điểm sau năm nhất, không phải ngay
khi sinh viên nhập học.

## Target và chống lạc đề

`low_completion = 1` khi tỷ lệ hoàn thành chương trình trong 150% thời gian chuẩn thấp
hơn 40%; ngược lại bằng 0. Đây là kết quả học tập, không phải thu nhập sau tốt nghiệp.

Các biến `completion_rate`, `low_completion`, `C150_4` và `C150_L4` bị cấm khỏi đầu vào
để tránh mô hình nhìn trước đáp án. Test tự động kiểm tra quy tắc này.

## Thuật toán

Cả hai kịch bản dùng Logistic Regression có cân bằng lớp. Biến liên tục được biến đổi
bằng spline trước khi đi vào Logistic Regression để mô tả quan hệ không hoàn toàn tuyến
tính; thuật toán phân loại cuối vẫn là Logistic Regression đúng rubric.

## Kiểm tra theo thời gian

- Train: 27.887 dòng cơ sở–năm từ 2017–2021.
- Test: 5.359 dòng của năm 2022, hoàn toàn không dùng khi fit mô hình.
- Imputer, encoder, scaler và spline chỉ được fit trên train.
- Không đổi ngưỡng phân loại sau khi xem test để làm đẹp chỉ số.

## Kết quả test 2022

| Chỉ số | Điều kiện nền tảng | Bổ sung thông tin sau năm nhất |
|---|---:|---:|
| Accuracy | **80,09%** | **81,34%** |
| Balanced Accuracy | 78,54% | 79,86% |
| Recall nhóm kết quả thấp | 74,93% | 76,44% |
| Precision | 62,51% | 64,51% |
| F1 | 68,16% | 69,97% |
| ROC-AUC | 0,847 | **0,877** |
| Brier score | 0,145 | **0,133** |

Cả hai kịch bản đều vượt yêu cầu Accuracy 80%. Bổ sung thông tin tiếp tục học sau năm
nhất giúp Accuracy tăng khoảng 1,25 điểm phần trăm và ROC-AUC tăng khoảng 0,030. Điều
này củng cố kết luận rằng khả năng duy trì việc học là tín hiệu dự báo quan trọng.

Ma trận nhầm lẫn của mô hình sau năm nhất:

| | Dự báo không thấp | Dự báo thấp |
|---|---:|---:|
| Thực tế không thấp | 3.194 | 641 |
| Thực tế thấp | 359 | 1.165 |

Mô hình phát hiện 1.165/1.524 trường hợp kết quả thấp và bỏ sót 359 trường hợp. Vì vậy
nó là công cụ tổng hợp bằng chứng, không phải quyết định tự động.

## Ý nghĩa chỉ số bằng ngôn ngữ đơn giản

- **Accuracy:** trong 100 trường hợp, mô hình dự báo đúng bao nhiêu.
- **Balanced Accuracy:** khả năng nhận ra hai nhóm được tính cân bằng.
- **Recall:** trong các trường hợp thực sự có kết quả thấp, mô hình tìm ra bao nhiêu.
- **Precision:** trong các cảnh báo mô hình phát ra, bao nhiêu cảnh báo đúng.
- **F1:** điểm cân bằng giữa phát hiện đủ và cảnh báo đúng.
- **ROC-AUC:** khả năng xếp nhóm rủi ro lên trước; 0,5 gần ngẫu nhiên, 1 là hoàn hảo.
- **Brier score:** mức sai của xác suất; càng thấp càng tốt.

Không được nói “mô hình dự đoán đúng 81,34% sinh viên”. Đơn vị test là cơ sở–năm.

## Mô hình giúp hiểu yếu tố đến mức nào?

Permutation importance cho biết yếu tố nào giúp mô hình dự báo tốt hơn. Đây là giá trị
dự báo, không phải mức tác động nhân quả. Insight về từng yếu tố phải kết hợp:

1. biểu đồ mô tả theo bốn mức;
2. hệ số liên hệ;
3. khoảng cách giữa nhóm;
4. kết quả khi nhiều yếu tố cùng xuất hiện;
5. đóng góp dự báo của mô hình.

Không dùng riêng feature importance để nói một yếu tố “gây ra” kết quả học tập.

## Đầu ra dashboard

Dashboard biến xác suất của mô hình thành thông tin có thể sử dụng:

- số và tỷ trọng nhóm được dự báo có tỷ lệ hoàn thành dưới 40% ở cut-off 0,5;
- số và tỷ trọng nhóm rủi ro cao, tức xác suất từ 70% trở lên;
- so sánh trực tiếp mô hình điều kiện nền tảng với mô hình sau năm nhất;
- ma trận kết hợp mức tiếp tục học với áp lực nguồn lực giảng dạy;
- hồ sơ nhóm ưu tiên theo tổ hợp bậc đào tạo, loại hình quản lý và khu vực sống;
- với mỗi hồ sơ: yếu tố làm xác suất dự báo cao hơn và hướng cải thiện cần kiểm tra;
- mức rủi ro tổng hợp theo loại hình, khu vực, bậc đào tạo hoặc hình thức học;
- ma trận đúng/sai và các yếu tố giúp mô hình phân biệt kết quả.

Dashboard không còn danh sách hay bảng xếp hạng tên từng trường.

## Điều rút ra từ dự báo

1. **Có thể nhận diện rủi ro trước khi biết kết quả cuối:** chỉ với tài chính, nguồn lực
   và bối cảnh, Accuracy đã đạt 80,09%.
2. **Thông tin sau năm nhất làm dự báo hữu ích hơn:** bổ sung tỷ lệ tiếp tục học làm
   Accuracy tăng 1,25 điểm phần trăm, ROC-AUC tăng 0,030 và Recall tăng 1,51 điểm phần
   trăm. Vì vậy việc sinh viên có quay lại năm tiếp theo hay không là mốc theo dõi thực
   tế quan trọng.
3. **Không nên chỉ nhìn một yếu tố:** dashboard ghép mức tiếp tục học với ba dấu hiệu
   áp lực nguồn lực — nhiều sinh viên trên giảng viên, chi giảng dạy thấp và ít giảng
   viên toàn thời gian. Nhóm tiếp tục học thấp có rủi ro cao nhất; áp lực nguồn lực giúp
   xác định nhóm nào cần được kiểm tra sâu hơn trong cùng một mức tiếp tục học.
4. **Kết quả dùng để ưu tiên hỗ trợ, không để phán quyết:** nhóm rủi ro cao cần được
   kiểm tra thêm về cố vấn học tập, hỗ trợ môn học, khả năng tiếp cận giảng viên và hoàn
   cảnh tài chính. Mô hình không chứng minh biện pháp nào sẽ gây ra mức cải thiện cụ thể.

## Cách giải thích vì sao một nhóm có rủi ro cao

Dashboard không suy đoán lý do chỉ từ việc một biến cao hay thấp. Với từng nhóm đủ ít
nhất 20 quan sát, hệ thống thực hiện kiểm tra phản thực tế trên chính Logistic Regression:

1. giữ nguyên toàn bộ các yếu tố của nhóm;
2. lần lượt đưa một yếu tố có thể can thiệp về trung vị toàn dữ liệu;
3. chạy lại `predict_proba`;
4. đo mức giảm xác suất rủi ro trung bình;
5. chỉ hiển thị yếu tố vừa đúng chiều bất lợi đã định trước, vừa làm rủi ro dự báo giảm
   ít nhất 0,2 điểm phần trăm.

Ví dụ trên dữ liệu hiện tại, nhóm **Cao đẳng 2 năm (Associate) · Công lập · Ngoại ô** có rủi ro dự báo
trung bình 88,6% và tỷ lệ hoàn thành điển hình 29,7%. Tỷ lệ tiếp tục học sau năm nhất của
nhóm là 64% so với mức chung 74%; khi riêng yếu tố này được đưa về mức chung, xác suất
dự báo giảm khoảng 8,4 điểm phần trăm. Tỷ lệ giảng viên toàn thời gian là 39% so với mức
chung 59%, gắn với thêm khoảng 6,2 điểm phần trăm dự báo. Vì vậy ưu tiên hợp lý là kiểm
tra chương trình cố vấn, hỗ trợ học tập, cơ chế theo dõi việc quay lại sau năm nhất và
mức độ sẵn có của đội ngũ giảng dạy.

Đây là **giải thích hành vi của mô hình**, không phải ước lượng tác động nhân quả. Không
được phát biểu rằng tăng retention đúng 10 điểm phần trăm chắc chắn làm completion tăng
8,4 điểm phần trăm. Bậc đào tạo, loại hình và khu vực chỉ dùng để xác định nhóm, không
được gọi là nguyên nhân.

`risk_probability` là xác suất dự báo cho một quan sát cấp cơ sở, không phải tỷ lệ sinh
viên chắc chắn thất bại. `predicted_low_completion = 1` dùng cut-off 0,5 để kiểm tra mô
hình; `risk_level = Cao` dùng ngưỡng 0,7 để tạo nhóm ưu tiên trên dashboard. Hai ngưỡng
này có mục đích khác nhau và không được đánh tráo.

## Cách kiểm tra lại

```powershell
python scripts/build_dataset.py
python scripts/run_eda.py
python scripts/train_model.py --prefer-temporal
python -m pytest -q
```

Đối chiếu `models/metrics.json`, `models/confusion_matrix.csv`,
`models/test_predictions.csv`, `models/feature_importance.csv` và ba hình chẩn đoán trong
`outputs/figures/`.
