# Insight và story từ dữ liệu thực tế

## Story ngắn để trình bày

**Mở đầu — Ở đâu có khoảng cách?** Kết quả hoàn thành không đồng đều theo địa lý. Trong
các bang có ít nhất 5 cơ sở, tỷ lệ hoàn thành có trọng số dao động từ 36,9% ở Alaska đến
66,1% ở Vermont. Đây là điểm xuất phát để đi sâu, không phải bằng chứng bang là nguyên
nhân.

**Nhóm nào khác biệt?** Nhóm trường tư thục vì lợi nhuận có tỷ lệ hoàn thành có trọng số
48,5%, thấp hơn nhóm tư thục phi lợi nhuận 64,0%. Khác biệt đầu vào và sứ mệnh đào tạo
có thể giải thích một phần nên không kết luận loại hình “gây ra” kết quả.

**Yếu tố nào rõ nhất?** Trong các biến đã xét, tỷ lệ duy trì sau năm đầu có liên hệ cùng
chiều mạnh nhất với tỷ lệ hoàn thành (Spearman rho = 0,57; N = 4.858). Điều này biến
retention thành chỉ báo thực hành hợp lý để theo dõi sớm, nhưng không phải quan hệ nhân
quả đã được chứng minh.

**Khoảng cách tài chính?** Trong dữ liệu có thể công bố, nhóm không nhận Pell Grant có
tỷ lệ hoàn thành sau ba năm 44,1%, cao hơn nhóm nhận Pell Grant 31,4% — chênh khoảng
12,7 điểm phần trăm. Pell là chỉ báo nhu cầu tài chính, không phải “nguyên nhân thất bại”.

**Khi bất lợi cộng dồn?** Trung vị hoàn thành giảm từ 58,1% ở nhóm không có điều kiện
bất lợi theo quy tắc phân vị xuống 51,1% ở nhóm có bốn điều kiện. Quan hệ giữa các mức
không hoàn toàn đơn điệu, vì vậy insight chỉ nói xu hướng đầu–cuối và phải xem thêm cấu
trúc nhóm.

**Có thể cảnh báo sớm không?** Logistic Regression đạt Accuracy 81,55% trên test năm
2022 chưa dùng để train và phát hiện 76,77% trường hợp hoàn thành thấp. Mô hình đủ qua
cổng Accuracy >80%, nhưng vẫn bỏ sót 354/1.524 trường hợp rủi ro; danh sách dự báo chỉ
dùng để ưu tiên kiểm tra.

## Thông điệp kết luận

Kết quả học tập ở cấp cơ sở liên quan đồng thời đến khả năng giữ sinh viên sau năm đầu,
bối cảnh tài chính, nguồn lực và loại hình/địa bàn. Không có một biến đơn lẻ đủ để kết luận
nguyên nhân. Hành động hợp lý là theo dõi retention sớm, kiểm tra khoảng cách ở nhóm cần
hỗ trợ tài chính và dùng xác suất mô hình để ưu tiên phân tích sâu hơn.

