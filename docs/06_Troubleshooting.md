# HƯỚNG DẪN XỬ LÝ SỰ CỐ VÀ SỬA LỖI THƯỜNG GẶP (TROUBLESHOOTING GUIDE)

---

## 1. DOCKER DAEMON KHÔNG PHẢN HỒI HOẶC CHƯA CHẠY

- **Hiện tượng**:
  ```text
  failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine
  open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.
  ```
- **Nguyên nhân**: Docker Desktop chưa được khởi động trên Windows hoặc dịch vụ WSL2 backend đang bị tạm dừng.
- **Cách khắc phục**:
  1. Khởi động Docker Desktop từ Start Menu hoặc chạy lệnh:
     ```powershell
     Start-Process "C:\Users\GIGABYTE\AppData\Local\Programs\DockerDesktop\Docker Desktop.exe"
     ```
  2. Đợi 15-30 giây cho Docker Engine khởi tạo xong Named Pipe.
  3. Kiểm tra lại bằng lệnh:
     ```powershell
     docker ps
     ```

---

## 2. XUNG ĐỘT CỔNG (PORT CONFLICT) TRÊN MÁY HOST

- **Hiện tượng**:
  ```text
  Bind for 0.0.0.0:80 failed: port is already allocated
  Bind for 0.0.0.0:3306 failed: port is already allocated
  ```
- **Nguyên nhân**: Cổng 80 đang bị chiếm dụng bởi IIS, Skype, hoặc một Web Server khác. Cổng 3306 đang bị chiếm bởi MySQL cục bộ cài trên Windows.
- **Cách khắc phục**:
  1. Tìm tiến trình đang chiếm cổng trên Windows:
     ```powershell
     Get-NetTCPConnection -LocalPort 80 -ErrorAction SilentlyContinue | Select-Object OwningProcess
     Get-Process -Id <PID>
     ```
  2. Dừng dịch vụ gây xung đột (ví dụ: `iisreset /stop` hoặc tạm dừng MySQL service trong `services.msc`).
  3. Hoặc nếu cần, đổi cổng host trong `.env` hoặc `docker-compose.yml` (ví dụ `8000:80`).

---

## 3. MARIADB KHÔNG SẴN SÀNG KHI BACKEND KHỞI ĐỘNG (RACE CONDITION)

- **Hiện tượng**:
  Flask Backend log báo lỗi:
  ```text
  pymysql.err.OperationalError: (2003, "Can't connect to MySQL server on 'relational-database-server' (111)")
  ```
- **Nguyên nhân**: `depends_on` thông thường chỉ đảm bảo container database đã được tạo, không đảm bảo tiến trình MariaDB bên trong đã hoàn tất nạp dữ liệu từ thư mục init.
- **Cách khắc phục đã áp dụng trong MyMiniCloud**:
  1. Trong `docker-compose.yml`, dịch vụ `relational-database-server` được trang bị cấu hình `healthcheck`:
     ```yaml
     healthcheck:
       test: ["CMD", "healthcheck.sh", "--connect", "--innodb_initialized"]
       interval: 10s
       timeout: 5s
       retries: 5
       start_period: 15s
     ```
  2. Flask Backend sử dụng `condition: service_healthy` để chờ đợi tuyệt đối cho đến khi MariaDB sẵn sàng nhận kết nối SQL mới khởi động.

---

## 4. TOKEN KEYCLOAK BÁO LỖI 401 UNAUTHORIZED HOẶC ISSUER MISMATCH

- **Hiện tượng**:
  Gọi `/secure` trả về: `{"error": "Token issuer verification failed"}`
- **Nguyên nhân**:
  - Keycloak chạy trong mạng Docker nhưng Client lại gửi request lấy token qua `http://localhost:8081`. Trong token sinh ra, claim `iss` có thể là `http://localhost:8081/realms/MyMiniCloud` hoặc `http://authentication-identity-server:8080/realms/MyMiniCloud`.
- **Cách khắc phục đã áp dụng trong MyMiniCloud**:
  - Trong `backend/app.py`, thuật toán kiểm tra issuer hỗ trợ linh hoạt cả internal Docker DNS và localhost URL khi kiểm thử, đồng thời kiểm tra chính xác Realm Name `MyMiniCloud` và chữ ký mật mã RS256 đối chiếu qua JWKS Endpoint.

---

## 5. MINIO PULL ACCESS DENIED HOẶC KHÔNG TẠO ĐƯỢC BUCKET

- **Hiện tượng**:
  `pull access denied for minio/minio`
- **Nguyên nhân**: MinIO đã gỡ bỏ repository miễn phí trên Docker Hub vào năm 2024.
- **Cách khắc phục đã áp dụng trong MyMiniCloud**:
  - Chuyển sang sử dụng `elestio/minio:latest`, image đã tích hợp sẵn cả MinIO Server và công cụ dòng lệnh MinIO Client (`mc`).
  - Sử dụng container `object-storage-provisioner` tự động chạy script `minio/scripts/init-minio.sh` khởi tạo 2 bucket `profile-pics` và `documents`, gán quyền public và upload file mẫu.

---

## 6. ROUND ROBIN LOAD BALANCING KHÔNG THẤY THAY ĐỔI TRÊN TRÌNH DUYỆT

- **Hiện tượng**: Refresh trình duyệt liên tục vẫn thấy một web node.
- **Nguyên nhân**: Trình duyệt thường giữ kết nối HTTP Keep-Alive mở (TCP persistent connection) để tối ưu hóa hiệu năng, do đó các request tiếp theo tái sử dụng cùng một kết nối tới backend node ban đầu.
- **Cách kiểm chứng chuẩn xác**:
  - Sử dụng lệnh kiểm thử đóng kết nối sau mỗi request:
    ```powershell
    1..10 | ForEach-Object { (Invoke-WebRequest -Uri "http://localhost/" -UseBasicParsing).Headers['X-Upstream-Backend'] }
    ```
  - Hoặc kiểm tra bộ kiểm thử tự động `tests/integration_test.py` (TEST-10).
