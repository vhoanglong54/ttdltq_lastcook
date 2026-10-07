# Nguồn dữ liệu và bằng chứng

## Nguồn chính

1. **College Scorecard – Institution**, U.S. Department of Education: 6.429 cơ sở,
   3.306 cột trong file gốc.
2. **College Scorecard – Field of Study**: 229.188 dòng, 174 cột trong file gốc.
3. **College Scorecard historical institution files**: 6 snapshot từ năm học bắt đầu
   2017 đến 2022; sau chọn biến và làm sạch còn 40.321 dòng cơ sở–năm.
4. **NCES IPEDS**: nguồn gốc của nhiều trường về loại hình, địa lý, tuyển sinh, tài
   chính, duy trì và văn bằng đã được College Scorecard tích hợp. Cấu hình tải raw riêng
   gồm HD, SFA, DRVGR, DRVEF và C.

Link chính thức:

- <https://catalog.data.gov/dataset/college-scorecard>
- <https://nces.ed.gov/ipeds/use-the-data>
- <https://collegescorecard.ed.gov/assets/InstitutionDataDocumentation.pdf>
- <https://collegescorecard.ed.gov/assets/FieldOfStudyDataDocumentation.pdf>

Phiên bản URL, thời điểm tải, kích thước và SHA-256 của từng file nằm trong
`data/source_manifest.json`.

## Trạng thái raw IPEDS riêng

Trong môi trường triển khai hiện tại, máy chủ Data Center của NCES không phản hồi ổn
định nên các ZIP IPEDS riêng chưa được đưa vào raw. Không thay thế bằng mirror không
chính thức. Phân tích đang dùng các trường IPEDS đã được tích hợp trong College
Scorecard; lệnh tải IPEDS riêng được giữ để đối chiếu khi kết nối hoạt động.

## Khóa nối

- `UNITID`: cơ sở giáo dục; khóa nối chính giữa institution, field và IPEDS.
- `CIPCODE`: mã ngành.
- `CREDLEV`: bậc văn bằng.
- `academic_year`: năm bắt đầu của snapshot lịch sử.

## Giới hạn đại diện

- Một số chỉ số Scorecard chỉ bao phủ người nhận hỗ trợ Title IV.
- Ô có cỡ mẫu nhỏ có thể bị ẩn để bảo vệ riêng tư.
- Kết quả công bố ở cấp cơ sở/nhóm, không cho phép suy luận về từng sinh viên.
- Số văn bằng `IPEDSCOUNT2` không phải số người duy nhất và không phải tỷ lệ hoàn thành.

