# Phương án đã duyệt

## Tên đề tài cố định

**Nghiên cứu và phân tích các yếu tố ảnh hưởng đến kết quả học tập của sinh viên đại học**

## Phạm vi đo lường

Dự án dùng College Scorecard kết hợp các biến có nguồn gốc IPEDS để phân tích giáo dục
đại học Hoa Kỳ. Đơn vị quan sát chính là **cơ sở–năm**; bảng ngành dùng đơn vị
**cơ sở–ngành–bậc văn bằng**. Đây không phải dữ liệu định danh từng sinh viên.

Kết quả học tập chính:

- tỷ lệ hoàn thành chương trình trong 150% thời gian chuẩn;
- tỷ lệ duy trì sau năm đầu;
- tỷ lệ rút khỏi cơ sở sau ba năm;
- khoảng cách kết quả giữa nhóm nhận/không nhận Pell Grant và nhóm thế hệ đầu.

Thu nhập và nợ sau tốt nghiệp chỉ là kết quả bổ sung. Số văn bằng theo ngành mô tả quy
mô đầu ra, không được gọi là “tỷ lệ hoàn thành theo ngành” khi thiếu mẫu số tuyển sinh
theo ngành.

## Câu hỏi nghiên cứu

Trong các câu hỏi dưới đây, “kết quả” được đo bằng tỷ lệ hoàn thành chương trình trong
150% thời gian chuẩn, tỷ lệ duy trì sau năm nhất hoặc tỷ lệ rút khỏi chương trình sau ba
năm tùy câu hỏi. Đơn vị phân tích chính là cơ sở–năm; các mối liên hệ không được diễn
giải thành nguyên nhân.

1. Tỷ lệ hoàn thành chương trình, duy trì sau năm nhất và rút khỏi chương trình khác
   nhau như thế nào giữa các bang, loại hình quản lý, bậc đào tạo chính, địa bàn và hình
   thức đào tạo từ xa?
2. Chi phí ròng sau hỗ trợ, tỷ lệ sinh viên nhận Pell Grant và tỷ lệ sinh viên sử dụng
   khoản vay liên bang liên hệ theo hướng nào và mạnh đến đâu với tỷ lệ hoàn thành và
   rút khỏi chương trình?
3. Tỷ lệ duy trì sau năm nhất, quy mô người học, số sinh viên trên một giảng viên, tỷ lệ
   giảng viên toàn thời gian, chi cho giảng dạy trên mỗi sinh viên và mức độ tuyển chọn
   liên hệ theo hướng nào với tỷ lệ hoàn thành?
4. Tỷ lệ hoàn thành và rút khỏi chương trình sau ba năm chênh lệch bao nhiêu giữa nhóm
   nhận và không nhận Pell Grant, cũng như giữa nhóm thế hệ đầu và không phải thế hệ đầu
   học đại học trong các ô dữ liệu được công bố?
5. Tỷ lệ hoàn thành và tỷ trọng cơ sở có tỷ lệ hoàn thành dưới 40% thay đổi ra sao khi
   đồng thời xuất hiện từ 0 đến 4 điều kiện: tỷ lệ nhận Pell cao, chi phí ròng cao, số
   sinh viên trên một giảng viên cao và tỷ lệ duy trì sau năm nhất thấp? Mối liên hệ này
   có tăng đều theo số điều kiện hay có nhóm ngoại lệ cần phân tích sâu?
6. Logistic Regression có nhận diện được các nhóm cơ sở–năm có tỷ lệ hoàn thành dưới
   40% trên năm kiểm tra ngoài thời gian hay không, và việc bổ sung tỷ lệ duy trì sau năm
   nhất cải thiện Accuracy, Recall, Balanced Accuracy và ROC-AUC đến mức nào?

## Story phân tích

Luồng trình bày được khóa theo thứ tự:

1. **Ở đâu?** Bản đồ toàn quốc cho biết sự phân bố kết quả.
2. **Nhóm nào?** Đi sâu theo loại trường, địa bàn, bậc đào tạo và hình thức đào tạo.
3. **Yếu tố nào đi cùng kết quả?** So sánh tài chính, nguồn lực và duy trì năm đầu.
4. **Bất lợi cộng dồn ra sao?** Xem đồng thời nhiều yếu tố thay vì từng biến rời rạc.
5. **Ưu tiên kiểm tra ở đâu?** Logistic Regression tạo xác suất rủi ro và danh sách
   cơ sở cần xem xét.

Mọi kết luận dùng từ “liên quan”, “đi cùng”, “khác biệt mô tả”; không đổi tương quan
thành quan hệ nhân quả.

## Sản phẩm

- script tải dữ liệu có checksum và nguồn;
- pipeline làm sạch, nối bảng, calculated fields và audit;
- 5 biểu đồ EDA tĩnh;
- Logistic Regression, tách train/test theo thời gian;
- dashboard Streamlit + Plotly gồm bản đồ và ít nhất 8 loại biểu đồ;
- insight/story dựa trên số liệu thực tế;
- tài liệu kỹ thuật, kiểm thử và báo cáo DOCX chuẩn bị theo cấu trúc IEEE.

## Quy tắc quản trị

- Không sửa file rubric.
- Không dùng lại thư mục dự án cũ.
- Không commit/push trước khi người dùng duyệt.
- Không công bố chỉ số thử nghiệm ban đầu như kết quả cuối nếu chưa qua temporal holdout.

