# Định hướng Cải tiến Kiến trúc (Pha 2)

Đánh giá và so sánh trước/sau khi cải tiến trên cấu hình CPU Kaggle qua 3 chỉ số: **Throughput (RPS)**, **Latency (p95)** và **Tỷ lệ lỗi (%)**.

---

### 1. In-Memory Cache (Redis) cho `GET /computers`
* **Vấn đề Pha 1:** Truy vấn danh sách máy đọc trực tiếp từ PostgreSQL. Khi nhiều client gọi liên tục, database bị nghẽn CPU và cạn connection pool.
* **Cải tiến Pha 2:** Dùng Redis Cache-Aside (TTL 5s–10s), xóa cache khi có sự kiện mở máy hoặc tắt máy.

### 2. Khóa chống tranh chấp máy khi mở phiên (`POST /sessions`)
* **Vấn đề Pha 1:** Nhiều người cùng gửi request mở 1 máy tại cùng một thời điểm dễ gây Deadlock database hoặc mở đè phiên.
* **Cải tiến Pha 2:** Dùng Distributed Lock (Redis) hoặc Optimistic Locking (cột `version`) tại tầng Domain. Chỉ 1 request mở máy thành công, các request sau nhận ngay mã lỗi `409 Conflict`.

### 3. Ghi dữ liệu bất đồng bộ qua Queue (RabbitMQ / Redis)
* **Vấn đề Pha 1:** Máy trạm gửi tín hiệu cập nhật phút chơi và trừ tiền liên tục xuống PostgreSQL, gây nghẽn đĩa cứng (Disk I/O).
* **Cải tiến Pha 2:** Tạm tính thời gian và số dư trên Redis in-memory. Dùng worker gom mẻ (batching) đồng bộ về database mỗi 1–3 phút.

### 4. Rate Limiting bảo vệ hệ thống
* **Vấn đề Pha 1:** Chưa có cơ chế chặn spam hoặc client lỗi gửi lặp vô hạn, dễ làm sập server.
* **Cải tiến Pha 2:** Thêm middleware Rate Limiting theo IP/User (Token Bucket trên Redis).
