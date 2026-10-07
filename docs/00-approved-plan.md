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

1. Kết quả học tập khác nhau thế nào giữa bang, loại trường, bậc đào tạo, địa bàn và
   hình thức đào tạo?
2. Chi phí ròng, Pell Grant, khoản vay liên bang và hỗ trợ tài chính liên quan thế nào
   với tỷ lệ hoàn thành/rút khỏi chương trình?
3. Quy mô, tỷ lệ sinh viên/giảng viên, mức tuyển chọn và địa bàn liên quan thế nào với
   kết quả?
4. Khoảng cách kết quả của sinh viên nhận Pell Grant và thế hệ đầu học đại học là bao
   nhiêu trong các ô dữ liệu được công bố?
5. Khi nhiều bất lợi cùng xuất hiện, nhóm cơ sở nào có kết quả thấp nhất?
6. Logistic Regression có nhận diện cơ sở có tỷ lệ hoàn thành dưới 40% với Accuracy
   trên 80% trên năm chưa dùng để train hay không?

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

