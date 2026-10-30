# HƯỚNG DẪN KIỂM THỬ TOÀN DIỆN VÀ MINH CHỨNG (TESTING & VERIFICATION MANUAL)

Tài liệu này hướng dẫn chi tiết quy trình kiểm thử 9 vai trò máy chủ cơ bản và 10 chức năng mở rộng thực tế trong hệ thống **MyMiniCloud**.

---

## 1. KIỂM THỬ TỰ ĐỘNG BẰNG PYTHON SCRIPT (AUTOMATED INTEGRATION TESTING)

Hệ thống được trang bị bộ kiểm thử tích hợp tự động `tests/integration_test.py` thực thi kiểm tra toàn bộ luồng hoạt động:
```powershell
python tests/integration_test.py
```
Hoặc chạy thông qua script PowerShell:
```powershell
.\scripts\test.ps1
```

### Kết quả đầu ra mong đợi:
```text
================================================================================
             MYMINICLOUD AUTOMATED INTEGRATION TEST SUITE
================================================================================

[PASS] TEST-01: Web Frontend & 3 Blog Posts
       Details: Home: 200, Blog: 200, Blog1/2/3: 200/200/200
[PASS] TEST-02: Flask API GET /student (5 Students JSON)
       Details: Status: 200, Students returned: 5
[PASS] TEST-03: MariaDB Connection & studentdb.students Query
       Details: Status: 200, DB records found: 5
[PASS] TEST-04: Keycloak OIDC JWT Verification (Missing token -> 401, Valid JWT -> 200)
       Details: Unauth status: 401, Token request: 200, Secure access: True
[PASS] TEST-05: MinIO S3 Buckets (profile-pics & documents)
       Details: Buckets verified in MinIO storage: profile-pics=True, documents=True
[PASS] TEST-06: BIND9 DNS Resolution (web-frontend-server.cloud.local)
       Details: Resolved IP: 10.10.10.10
[PASS] TEST-07: Prometheus Scrape Targets Status (UP)
       Details: Status: 200, Targets UP: 3
[PASS] TEST-08: Grafana Observability Dashboard Service
       Details: Grafana Health Status: 200
[PASS] TEST-09: API Gateway Reverse Proxy (Path-based Routing)
       Details: Gateway / -> 200, /api/hello -> 200, /student -> 200
[PASS] TEST-10: Round Robin Load Balancing between Web 1 & Web 2
       Details: Distinct Upstream Backend Nodes hit: ['172.x.x.1:80', '172.x.x.2:80']

================================================================================
SUMMARY: 10/10 Tests Passed.
>>> ALL INTEGRATION TESTS PASSED SUCCESSFULLY! <<<
```

---

## 2. HƯỚNG DẪN KIỂM THỬ THỦ CÔNG TỪNG CHỨC NĂNG (MANUAL VERIFICATION)

### Chức năng 1: Web Frontend & 3 Trang Blog
- **Lệnh kiểm thử**:
  ```powershell
  curl -I http://localhost:8080/
  curl -I http://localhost:8080/blog/
  curl -I http://localhost:8080/blog/blog1.html
  ```
- **Kỳ vọng**: HTTP/1.1 200 OK. Mở trình duyệt xem giao diện đồng nhất, thanh điều hướng hoạt động đầy đủ.

### Chức năng 2: Flask API Đọc JSON Sinh Viên
- **Lệnh kiểm thử**:
  ```powershell
  curl http://localhost:8085/student
  # Hoặc kiểm tra qua API Gateway:
  curl http://localhost/student
  ```
- **Kỳ vọng**: Trả về đúng 5 sinh viên với đầy đủ `id`, `student_id`, `name`, `major`, `gpa`.

### Chức năng 3: Cơ sở dữ liệu MariaDB
- **Lệnh kiểm thử trực tiếp CLI**:
  ```powershell
  docker exec -i relational-database-server mariadb -uroot -proot -e "USE studentdb; SELECT * FROM students;"
  ```
- **Kiểm thử qua Flask Backend**:
  ```powershell
  curl http://localhost:8085/api/students-db
  ```
- **Kỳ vọng**: Bảng `students` hiển thị 5 sinh viên mẫu. Dữ liệu được lưu trữ bền vững trong volume `mariadb_data`.

### Chức năng 4: Keycloak IAM & Xác thực JWT Token
1. **Kiểm tra từ chối truy cập khi không có token**:
   ```powershell
   curl -i http://localhost:8085/secure
   # Kỳ vọng: HTTP/1.1 401 Unauthorized
   ```
2. **Lấy Access Token từ Keycloak OIDC**:
   ```powershell
   $response = Invoke-RestMethod -Uri "http://localhost:8081/realms/MyMiniCloud/protocol/openid-connect/token" `
       -Method Post `
       -Body @{
           client_id = "flask-app"
           grant_type = "password"
           username = "sv01"
           password = "password123"
       }
   $token = $response.access_token
   Write-Host "Access Token: $token"
   ```
3. **Gọi endpoint bảo vệ với Header Bearer**:
   ```powershell
   curl -H "Authorization: Bearer $token" http://localhost:8085/secure
   # Kỳ vọng: HTTP/1.1 200 OK, preferred_username: "sv01"
   ```

### Chức năng 5: MinIO Object Storage
1. Mở trình duyệt truy cập: `http://localhost:9001`
2. Đăng nhập: `minioadmin` / `minioadmin`
3. Kiểm tra danh sách bucket:
   - `profile-pics`: chứa file `avatar.jpg` (Public download).
   - `documents`: chứa file `report.pdf`.

### Chức năng 6: BIND9 Internal DNS Server
- **Lệnh kiểm thử**:
  ```powershell
  docker exec internal-dns-server dig @127.0.0.1 web-frontend-server.cloud.local +short
  docker exec internal-dns-server dig @127.0.0.1 app-backend.cloud.local +short
  ```
- **Kỳ vọng**: Phân giải ra IP `10.10.10.10` và `10.10.10.20`.

### Chức năng 7: Prometheus Monitoring
- Truy cập trình duyệt: `http://localhost:9090/targets`
- **Kỳ vọng**: Các targets `node`, `flask-backend`, `web` đều hiển thị trạng thái màu xanh lá cây (**UP**).

### Chức năng 8: Grafana Dashboard
- Truy cập trình duyệt: `http://localhost:3000` (Đăng nhập: `admin` / `admin`).
- Mở menu: **Dashboards** -> **System Health - MyMiniCloud**.
- **Kỳ vọng**: 3 biểu đồ CPU, RAM, Network Traffic cập nhật số liệu thời gian thực.

### Chức năng 9 & 10: API Gateway & Round Robin Load Balancing
- Gửi 10 request liên tiếp đến Gateway cổng 80:
  ```powershell
  1..10 | ForEach-Object { (Invoke-WebRequest -Uri "http://localhost/" -UseBasicParsing).Headers['X-Upstream-Backend'] }
  ```
- **Kỳ vọng**: Địa chỉ backend upstream trả về luân phiên giữa 2 IP của `web-frontend-server1` và `web-frontend-server2`.

