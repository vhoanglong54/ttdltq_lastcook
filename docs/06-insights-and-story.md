# Insight và story từ dữ liệu thực tế

## Story ngắn để trình bày

**Mở đầu — Ở đâu có khoảng cách?** Trong các bang có ít nhất 5 cơ sở, tỷ lệ hoàn thành
có trọng số dao động từ 36,9% ở Alaska đến 66,1% ở Vermont. Vermont có retention 78,1%
so với 72,1% ở Alaska, giảng viên toàn thời gian 85,1% so với 49,7%, và tỷ trọng cơ sở
đào tạo cử nhân 56,2% so với 40,0%. Vermont đồng thời có tỷ trọng cơ sở nông thôn/thị
trấn cao hơn, 68,8% so với 40,0%. Vì vậy chênh lệch quan sát phù hợp hơn với khả năng duy
trì học tập, đội ngũ giảng dạy và cơ cấu chương trình hơn là cách giải thích đơn giản
“vùng hẻo lánh thì kết quả thấp”.

**Yếu tố nổi bật nhất?** Nhóm có tỷ lệ tiếp tục học sau năm nhất cao nhất có trung vị
hoàn thành cao hơn nhóm thấp nhất 40,5 điểm phần trăm. Đây là tín hiệu dự báo mạnh,
không phải mức tác động nhân quả.

**Nguồn lực giảng dạy?** Từ nhóm có ít sinh viên trên một giảng viên nhất đến nhóm cao
nhất, trung vị hoàn thành giảm 10,6 điểm phần trăm; Spearman rho = -0,17. Chỉ số này
không đồng nhất với sĩ số từng lớp nên phải diễn giải thận trọng.

**Khoảng cách tài chính?** Trong dữ liệu có thể công bố, nhóm không nhận Pell Grant có
tỷ lệ hoàn thành sau ba năm 44,1%, cao hơn nhóm nhận Pell Grant 31,4% — chênh khoảng
12,7 điểm phần trăm. Pell là chỉ báo nhu cầu tài chính, không phải “nguyên nhân thất bại”.

**Khi bất lợi cộng dồn?** Trung vị hoàn thành giảm từ 58,1% ở nhóm không có điều kiện
bất lợi theo quy tắc phân vị xuống 51,1% ở nhóm có bốn điều kiện. Quan hệ giữa các mức
không hoàn toàn đơn điệu, vì vậy insight chỉ nói xu hướng đầu–cuối và phải xem thêm cấu
trúc nhóm.

**Có thể dự báo không?** Mô hình chỉ dùng điều kiện nền tảng đạt Accuracy 80,09%. Khi bổ
sung thông tin tiếp tục học sau năm nhất, Accuracy đạt 81,34% và ROC-AUC tăng từ 0,847
lên 0,877. Mô hình sau năm nhất phát hiện 76,44% nhóm kết quả thấp nhưng vẫn bỏ sót
359/1.524 trường hợp.

**Dự báo giúp làm gì?** Đầu ra hữu ích không phải tên một trường “tốt” hay “xấu”, mà là
xác suất một nhóm có tỷ lệ hoàn thành dưới 40%. Ma trận trên dashboard cho biết rủi ro
tăng rõ ở nhóm có khả năng tiếp tục học sau năm nhất thấp; trong cùng mức tiếp tục học,
các dấu hiệu áp lực nguồn lực giúp khoanh vùng nơi cần kiểm tra sâu hơn. Vì vậy thứ tự
ưu tiên là theo dõi khả năng quay lại học, sau đó xem đồng thời khả năng tiếp cận giảng
viên, chi cho giảng dạy và hoàn cảnh tài chính.

**Nhóm nào cần ưu tiên?** Hồ sơ cao nhất hiện tại là nhóm cao đẳng 2 năm (Associate),
công lập, ngoại ô:
rủi ro dự báo trung bình 88,6% và tỷ lệ hoàn thành điển hình 29,7%. Khả năng tiếp tục học
sau năm nhất của nhóm là 64%, thấp hơn mức chung 74%; kiểm tra phản thực tế cho thấy
riêng chênh lệch này gắn với khoảng 8,4 điểm phần trăm rủi ro dự báo. Nhận xét cải thiện
là ưu tiên kiểm tra cố vấn năm nhất, hỗ trợ học tập và theo dõi việc quay lại học. Tỷ lệ
giảng viên toàn thời gian của nhóm là 39% so với mức chung 59%, gắn với thêm khoảng 6,2
điểm phần trăm dự báo; do đó cũng cần rà soát khả năng tiếp cận và tính liên tục của đội
ngũ giảng dạy. Đây không phải khẳng định bậc Associate hay khu vực ngoại ô tự gây ra kết
quả thấp.

## Thông điệp kết luận

Kết quả học tập ở cấp nhóm liên quan đồng thời đến khả năng tiếp tục học sau năm đầu,
hoàn cảnh tài chính, nguồn lực giảng dạy và bối cảnh đào tạo. Không có một biến đơn lẻ
đủ để kết luận nguyên nhân. Mô hình dùng các yếu tố để kiểm tra khả năng dự báo tổng hợp,
không xếp hạng từng trường hay dự báo từng sinh viên. Dự báo chỉ tạo thứ tự ưu tiên ở
cấp nhóm để con người phân tích tiếp, không tự động quyết định hỗ trợ hay xử phạt.

