# EduShield AI — Giao diện mới

Bản cập nhật ngày 22/09/2026. Thiết kế sáng với xanh teal, dành cho sinh viên và giảng viên. Đây là mã nguồn React đã tích hợp vào dự án, không phải bản mockup độc lập.

## Áp dụng vào dự án đang chạy trên Windows

1. Giải nén tệp ZIP vào một thư mục riêng.
2. Sao lưu thư mục `frontend` của dự án hiện tại.
3. Chép toàn bộ `frontend/src` và `frontend/index.html` từ bản mới vào dự án hiện tại, đồng ý thay thế tệp trùng tên. Nhớ chép cả hai component mới `StudentGateway.jsx` và `ModalShell.jsx`.
4. Mở PowerShell ở thư mục `frontend` rồi chạy:

```powershell
npm ci
npm run dev
```

Giữ backend đang hoạt động theo cách bạn dùng trước đây. Cấu hình proxy `/api` vẫn trỏ đến `http://localhost:8000`. Mở địa chỉ Vite in trong terminal (mặc định `http://localhost:5173`). Nếu trang cũ còn hiển thị, nhấn Ctrl+F5.

Không cần thay cơ sở dữ liệu, token hoặc cài lại backend để áp dụng giao diện. Tệp ZIP vẫn chứa các tệp gốc còn lại; khi cập nhật một dự án đang có dữ liệu mới, chỉ chép phần frontend nêu trên.

## Những gì đã thay đổi

- Đăng nhập: bố cục hai cột, chọn vai trò rõ ràng, nhãn nhập liệu và thông báo lỗi bằng tiếng Việt. Sinh viên dùng mã bắt đầu SV và họ tên; giảng viên dùng mã bắt đầu GV cùng token cũ.
- Giảng viên: thanh điều hướng bên trái, tổng quan giám sát, thẻ thống kê, danh sách sinh viên và nhật ký vi phạm theo thiết kế sáng.
- Đề thi: tìm kiếm theo tên/mã, lọc trạng thái, bảng cuộn ngang trên màn hình nhỏ. Các thao tác tải DOCX/XLSX, công bố, xem điểm, xuất Excel, sao chép mã và xóa vẫn dùng API cũ.
- Hộp thoại quản lý đề: dùng dialog của trình duyệt, giữ focus trong hộp thoại, hỗ trợ Escape và trả focus về nút đã mở. Escape không đóng trong khi đang gửi/xuất dữ liệu.
- Sinh viên: màn hình nhập mã, xem thông tin đề, kết quả theo cùng một bố cục ba bước.
- Phòng thi: câu hỏi và đáp án ở cột chính; danh sách câu hỏi, camera và nhật ký ở cột bên cạnh. Chọn đáp án hỗ trợ cả chuột và bàn phím qua radio.
- Thông báo lỗi khởi tạo camera/AI được phân biệt với cảnh báo camera bị che. Lỗi khởi tạo không còn hiển thị như thể đang giám sát bình thường.
- Tải màn hình theo vai trò bằng React lazy/Suspense; giảm tải lúc mở trang. Dùng font hệ thống, không tải Google Fonts. Có cấu hình giảm chuyển động theo thiết lập thiết bị.

## Phạm vi giữ nguyên

Đã đối chiếu từng byte: toàn bộ backend và cơ sở dữ liệu bằng bản ZIP được gửi lên. Không thay schema, endpoint, thuật toán nhận diện, ngưỡng vi phạm, thời gian bài thi hoặc payload nộp bài. `useBrowserLockdown.js`, `package.json`, `package-lock.json` và proxy Vite được giữ nguyên.

## Kiểm tra đã thực hiện

- `npm run build`: thành công.
- `npm run lint`: không có lỗi; vẫn có cảnh báo tại một số effect và biến chưa dùng từ mã hiện hữu.
- Chromium/Playwright với dữ liệu API mẫu: đăng nhập hai vai trò; hiển thị thống kê/sinh viên; tìm kiếm không có kết quả; mở và đóng hộp thoại công bố/tải đề bằng Escape; nhập mã thi; xem thông tin đề; chọn đáp án; chuyển câu; nộp và xem kết quả.
- Kiểm tra tràn ngang ở độ rộng 390 px cho trang quản lý đề và màn hình sinh viên: không tràn ngang toàn trang; bảng dữ liệu có vùng cuộn riêng.
- Đã xem ảnh chụp thực tế của trang đăng nhập, dashboard, phòng thi, hộp thoại và trang quản lý trên màn hình nhỏ.

Ảnh trong `UI_PREVIEWS` được chụp từ giao diện chạy thật với **API giả lập**. Tên, số liệu và đề thi trong ảnh là dữ liệu kiểm thử, không phải thống kê từ cơ sở dữ liệu của bạn.

Chưa kiểm chứng với camera vật lý, mô hình AI tải từ mạng và backend thực đang chạy trên máy bạn. Trước buổi demo, nên thử một đề nhỏ: công bố → sinh viên vào thi → bật camera → trả lời/nộp → giảng viên xem điểm/ảnh và xuất Excel. Không thể kết luận hiệu năng hoặc độ ổn định của toàn hệ thống chỉ từ các phép thử giao diện này.

## Tệp giao diện

- `frontend/src/App.jsx`: đăng nhập và tải màn hình theo vai trò.
- `frontend/src/index.css`: màu sắc, bố cục và responsive.
- `frontend/src/main.jsx`: tôn trọng tùy chọn giảm chuyển động.
- `frontend/src/components/StudentGateway.jsx`: khung vào thi và kết quả.
- `frontend/src/components/ModalShell.jsx`: hộp thoại quản lý dùng chung.
- `frontend/src/components/StudentExam.jsx`: màn hình sinh viên.
- `frontend/src/components/ProctorDashboard.jsx`: giám sát giảng viên.
- `frontend/src/components/ExamManagement.jsx`: quản lý đề và điểm.
- `frontend/index.html`: màu chủ đề và bỏ tải font ngoài.
