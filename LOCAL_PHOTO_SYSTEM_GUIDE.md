===============================================================
🎯 HƯỚNG DẪN SỬ DỤNG HỆ THỐNG FACE ATTENDANCE MỚI
===============================================================
📅 Ngày cập nhật: 19/08/2025

🎉 **TÍNH NĂNG MỚI: LƯU TRỮ ẢNH LOCAL VỚI MÃ NHÂN VIÊN**

Hệ thống đã được cập nhật để lưu trữ ảnh nhân viên local và sử dụng để 
so khớp trong quá trình chấm công.

===============================================================
📋 CÁCH THỨC HOẠT ĐỘNG MỚI:
===============================================================

**1. THÊM NHÂN VIÊN VỚI ẢNH:**
   ✅ Vào web admin: http://localhost:8000/admin
   ✅ Click "Thêm nhân viên mới"
   ✅ Điền thông tin + Upload ảnh thẻ
   ✅ Hệ thống tự động:
      - Lưu ảnh local theo mã nhân viên
      - Xử lý AI (phát hiện khuôn mặt, chống giả mạo)
      - Trích xuất face embedding
      - Lưu vào database để so khớp

**2. CẤU TRÚC LƯU TRỮ LOCAL:**
   📁 backend/data/employee_photos/
   └── 📁 [MÃ_NHÂN_VIÊN]/
       ├── 🖼️ [ID]_original.jpg    (ảnh gốc)
       ├── 🖼️ [ID]_processed.jpg   (ảnh đã xử lý)
       └── 🖼️ [ID]_thumb.jpg       (thumbnail)

**3. QUÁ TRÌNH CHẤM CÔNG:**
   📷 Camera chụp ảnh nhân viên
   🔍 AI phát hiện và trích xuất face embedding
   📊 So sánh với ảnh local đã lưu
   ✅ Xác định nhân viên và ghi nhận chấm công

===============================================================
🆕 CÁC API ENDPOINT MỚI:
===============================================================

**1. Tạo nhân viên với ảnh:**
   POST /api/v1/employees/with-photo
   - Form data: name, department, email, phone, position, photo
   - Trả về: thông tin nhân viên + kết quả xử lý ảnh

**2. Quản lý ảnh nhân viên:**
   GET    /api/v1/employees/{id}/photos           # Xem ảnh
   POST   /api/v1/employees/{id}/photos/upload    # Thêm ảnh
   GET    /api/v1/employees/{id}/photos/{photo_id}/thumbnail  # Thumbnail
   DELETE /api/v1/employees/{id}/photos/{photo_id}  # Xóa ảnh

**3. Thống kê storage:**
   GET /api/v1/employees/storage/stats

===============================================================
💻 CÁCH SỬ DỤNG WEB ADMIN:
===============================================================

**1. Khởi động hệ thống:**
   ```bash
   # Terminal 1: Backend
   cd backend
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   
   # Terminal 2: Admin Dashboard  
   cd admin-dashboard
   npm start
   ```

**2. Truy cập web admin:**
   🌐 http://localhost:8000/admin

**3. Thêm nhân viên mới:**
   📝 Click "Thêm nhân viên mới"
   ✏️ Điền thông tin: Tên, phòng ban, email, v.v.
   📷 **QUAN TRỌNG:** Upload ảnh thẻ rõ nét
   💾 Click "Lưu"

**4. Kết quả xử lý:**
   ✅ Hệ thống hiển thị:
   - Nhân viên đã tạo thành công
   - Ảnh đã lưu local
   - Kết quả phát hiện khuôn mặt
   - Chất lượng ảnh (%)
   - Face embedding đã lưu

===============================================================
🔧 CẤU HÌNH VÀ TỐI ƯU:
===============================================================

**1. Yêu cầu ảnh tốt:**
   📐 Kích thước: Tối thiểu 300x300px
   📝 Định dạng: JPG, PNG
   👤 Khuôn mặt: Rõ nét, đầy đủ, nhìn thẳng
   💡 Ánh sáng: Đều, không bị tối hoặc chói
   📱 Nguồn: Ảnh thật từ camera/điện thoại

**2. Tham số nhận diện:**
   🎯 Ngưỡng so khớp: 60% (có thể điều chỉnh)
   ⚡ Thời gian xử lý: 130-400ms/ảnh
   🎲 Chất lượng tối thiểu: 30%

**3. Giám sát hệ thống:**
   📊 Thống kê storage: /api/v1/employees/storage/stats
   📈 Thống kê nhân viên: /api/v1/employees/stats
   🔍 Log hệ thống: Terminal backend

===============================================================
🚀 LUỒNG CÔNG VIỆC THỰC TẾ:
===============================================================

**BƯỚC 1: Setup ban đầu**
1. Khởi động backend + admin dashboard
2. Truy cập http://localhost:8000/admin
3. Kiểm tra hệ thống hoạt động

**BƯỚC 2: Thêm nhân viên**
1. Click "Thêm nhân viên mới"
2. Điền đầy đủ thông tin
3. **Upload ảnh thẻ chất lượng cao**
4. Lưu và kiểm tra kết quả

**BƯỚC 3: Kiểm tra lưu trữ**
1. Xem thư mục: backend/data/employee_photos/[MÃ_NV]/
2. Xác nhận có đầy đủ ảnh: original, processed, thumb
3. Kiểm tra database có face embedding

**BƯỚC 4: Test chấm công**
1. Khởi động kiosk app hoặc dùng API
2. Chụp ảnh nhân viên với camera
3. Gửi lên hệ thống để nhận diện
4. Kiểm tra kết quả so khớp

===============================================================
⚠️ LƯU Ý QUAN TRỌNG:
===============================================================

**1. Chất lượng ảnh quyết định độ chính xác:**
   - Ảnh mờ → Nhận diện sai
   - Góc nghiêng → Không phát hiện được
   - Ánh sáng kém → Chất lượng thấp

**2. Backup dữ liệu:**
   - Ảnh local: backend/data/employee_photos/
   - Database: Xuất định kỳ
   - Cấu hình hệ thống

**3. Bảo mật:**
   - Ảnh nhân viên là dữ liệu nhạy cảm
   - Hạn chế quyền truy cập thư mục storage
   - Mã hóa đường truyền (HTTPS trong production)

===============================================================
🛠️ TROUBLESHOOTING:
===============================================================

**Lỗi: "No face detected"**
→ Kiểm tra chất lượng ảnh, góc chụp, ánh sáng

**Lỗi: "Spoof detected"**
→ Đảm bảo dùng ảnh thật, không phải màn hình/in

**Lỗi: Upload thất bại**
→ Kiểm tra định dạng file, kích thước, quyền ghi thư mục

**Lỗi: Nhận diện sai**
→ Kiểm tra ngưỡng so khớp, chất lượng ảnh tham chiếu

===============================================================
📞 SUPPORT:
===============================================================

Hệ thống đã sẵn sàng cho production với khả năng:
✅ Lưu trữ ảnh local hiệu quả
✅ Xử lý AI nhanh chóng (130-400ms)
✅ Giao diện quản lý thân thiện
✅ API đầy đủ cho tích hợp
✅ Logging và monitoring chi tiết

🎯 **Hệ thống Face Attendance với lưu trữ local đã sẵn sàng!**

===============================================================
