# KỊCH BẢN HƯỚNG DẪN DEMO TOÀN DIỆN HỆ THỐNG MYMINICLOUD
## TỪNG BƯỚC CHI TIẾT DEMO ĐẦY ĐỦ 9 VAI TRÒ DỊCH VỤ VÀ 10 CHỨC NĂNG MỞ RỘNG

---

## 1. MỤC TIÊU VÀ NGUYÊN TẮC THUYẾT TRÌNH DEMO

Tài liệu này được biên soạn độc lập như một **Kịch bản Demo chuẩn chỉnh (Master Demo Script)** dành cho sinh viên/kỹ sư khi báo cáo, thuyết trình và bảo vệ đồ án môn học **Cloud Computing**.

### Nguyên tắc Demo thành công:
1. **Trực quan trước, dòng lệnh sau**: Mở các trang web, đồ thị và bảng quản trị trên trình duyệt trước để tạo ấn tượng thị giác, sau đó dùng dòng lệnh (CLI/cURL) để chứng minh bản chất kỹ thuật bên dưới.
2. **Kể câu chuyện kiến trúc (Architecture Storytelling)**: Không chỉ bấm nút, hãy giải thích *vì sao dịch vụ này tồn tại*, *nó tương đương dịch vụ nào trên AWS*, và *dữ liệu truyền giữa các container như thế nào*.
3. **Bằng chứng không thể chối cãi**: Kết thúc bằng việc chạy bộ kiểm thử tự động `python tests/integration_test.py` đạt **10/10 PASS**.

---

## 2. BẢNG TỔNG HỢP CÁC ĐỊA CHỈ TRUY CẬP DEMO (DEMO CHEAT SHEET)

| STT | Dịch vụ / Chức năng | Địa chỉ URL Truy cập | Tài khoản đăng nhập (nếu có) | Mục đích demo |
|:---:|:---|:---|:---:|:---|
| 1 | **Trang chủ MyMiniCloud** | `http://localhost/` | *Không cần* | Web Server & API Gateway |
| 2 | **Trang danh mục Blog** | `http://localhost/blog/` | *Không cần* | Chức năng mở rộng 1 |
| 3 | **Flask API Sinh viên (JSON)** | `http://localhost/student` | *Không cần* | Chức năng mở rộng 2 |
| 4 | **MariaDB API (CRUD)** | `http://localhost/api/students-db` | *Không cần* | Chức năng mở rộng 3 |
| 5 | **Keycloak IAM Console** | `http://localhost:8081` | `admin` / `admin` | Chức năng mở rộng 4 (IAM) |
| 6 | **MinIO S3 Console** | `http://localhost:9001` | `minioadmin` / `minioadmin` | Chức năng mở rộng 5 (Storage) |
| 7 | **Prometheus Targets & Graph** | `http://localhost:9090` | *Không cần* | Chức năng mở rộng 7 (Metrics) |
| 8 | **Grafana Dashboard** | `http://localhost:3000` | `admin` / `admin` | Chức năng mở rộng 8 (Dashboard) |
| 9 | **Docker Hub Công khai** | `https://hub.docker.com/u/nguyenmanh3110` | *Public* | Đóng gói Image Phase 6.7 |

---

## 3. QUY TRÌNH DEMO TỪNG BƯỚC CHI TIẾT (12 PHẦN)

---

### PHẦN 1: TỔNG QUAN HẠ TẦNG VÀ TRẠNG THÁI CONTAINER (Thời lượng: ~2 phút)

#### Mục tiêu:
Chứng minh hệ thống gồm 10 container dịch vụ đang chạy thực tế trên máy tính, sử dụng kiến trúc mạng cô lập `cloud-net` và chỉ mở duy nhất cổng 80 ra ngoài.

#### Thao tác thực hiện:
Mở cửa sổ **Terminal / PowerShell** và gõ lệnh:
```powershell
docker compose ps
```

#### Những gì chỉ cho Thầy/Cô xem:
1. Cả 10 container dịch vụ đều có trạng thái **`Up`** và có nhãn **`(healthy)`** màu xanh.
2. `api-gateway-proxy-server` là container duy nhất mở cổng **`80:80`** đóng vai trò Reverse Proxy và điểm vào duy nhất.
3. Giải thích: *"Hệ thống mô phỏng kiến trúc Enterprise Cloud: Người dùng bên ngoài chỉ tương tác qua Gateway cổng 80, toàn bộ backend, database và hệ thống giám sát đều được bảo vệ trong mạng nội bộ `cloud-net`."*

---

### PHẦN 2: DEMO WEBSITE VÀ 3 BÀI VIẾT BLOG CÔNG NGHỆ (Chức năng mở rộng 1)

#### Mục tiêu:
Chứng minh máy chủ web phục vụ trang chủ giới thiệu và 3 bài viết blog kỹ thuật đồng nhất giao diện, có điều hướng qua lại và responsive.

#### Thao tác thực hiện:
1. Mở trình duyệt web truy cập: **`http://localhost/`**
   - Giới thiệu giao diện trang chủ MyMiniCloud với danh sách 9 dịch vụ cloud được thiết kế hiện đại.
2. Bấm vào nút **"Đọc Blog Kỹ Thuật"** (hoặc truy cập `http://localhost/blog/`):
   - Bấm vào **Bài 1**: *Docker & Containerization* (`/blog/blog1.html`).
   - Bấm vào **Bài 2**: *Microservices & API Gateway* (`/blog/blog2.html`).
   - Bấm vào **Bài 3**: *Prometheus & Grafana Observability* (`/blog/blog3.html`).
3. Bấm vào nút quay lại **"Về trang chủ"** để chứng minh luồng điều hướng hoạt động hoàn hảo.

---

### PHẦN 3: DEMO CÂN BẰNG TẢI ROUND ROBIN 50/50 (Chức năng mở rộng 10)

#### Mục tiêu:
Chứng minh API Gateway sử dụng thuật toán **Round Robin** để phân phối tải luân phiên đều đặn 50% - 50% giữa hai máy chủ web độc lập: `web-frontend-server1` và `web-frontend-server2`.

#### Thao tác thực hiện:
Mở **PowerShell** và chạy lệnh gửi 10 request liên tiếp đến Gateway cổng 80:
```powershell
1..10 | ForEach-Object { 
    $resp = Invoke-WebRequest -Uri "http://localhost/" -UseBasicParsing
    "Request {0}: Server={1} (IP={2})" -f $_, $resp.Headers['X-Served-By'], $resp.Headers['X-Upstream-Backend']
}
```

#### Kết quả hiển thị ấn tượng:
```text
Request 1: Server=web-node-2 (IP=172.19.0.7:80)
Request 2: Server=web-node-1 (IP=172.19.0.5:80)
Request 3: Server=web-node-2 (IP=172.19.0.7:80)
Request 4: Server=web-node-1 (IP=172.19.0.5:80)
...
```
*(Chỉ cho Thầy/Cô thấy: Header phản hồi luân phiên xen kẽ hoàn hảo giữa Node 1 và Node 2).*

---

### PHẦN 4: DEMO FLASK BACKEND & ĐỌC JSON SINH VIÊN (Chức năng mở rộng 2)

#### Mục tiêu:
Chứng minh Flask Backend cung cấp REST API đọc tệp JSON chứa danh sách đúng 5 sinh viên mẫu và trả về định dạng JSON chuẩn.

#### Thao tác thực hiện:
1. Trên trình duyệt web, mở tab mới và truy cập:
   👉 **`http://localhost/student`**
2. Hoặc dùng lệnh cURL trong Terminal:
   ```bash
   curl -i http://localhost/student
   ```

#### Kết quả quan sát:
- Trả về mã **HTTP 200 OK**.
- Dữ liệu JSON hiển thị đủ 5 sinh viên mẫu: *Nguyen Van An (SV001)*, *Tran Thi Bich (SV002)*, *Le Hoang Cuong (SV003)*, *Pham Minh Duc (SV004)*, và *Doan Phuong Thao (SV005)*.

---

### PHẦN 5: DEMO CƠ SỞ DỮ LIỆU MARIADB & FULL CRUD 4 THAO TÁC (Chức năng mở rộng 3)

#### Mục tiêu:
Chứng minh tính năng nâng cao: Kết nối MariaDB 11.3 qua mạng Docker, sử dụng Volume bền vững, và hỗ trợ đầy đủ 4 thao tác RESTful CRUD (Create, Read, Update, Delete) với câu lệnh tham số hóa (Parameterized Queries) chống SQL Injection.

#### Thao tác thực hiện:

#### Bước 5.1: Đọc toàn bộ danh sách (READ ALL)
Mở trình duyệt truy cập:
👉 **`http://localhost/api/students-db`**
*(Dữ liệu từ CSDL MariaDB `studentdb.students` trả về với 5 bản ghi ban đầu).*

#### Bước 5.2: Thêm một sinh viên mới (CREATE - POST)
Chạy lệnh cURL trong Terminal:
```bash
curl -X POST http://localhost/api/students-db -H "Content-Type: application/json" -d "{\"student_id\":\"SV006\",\"fullname\":\"Vu Dinh Trong\",\"dob\":\"2004-12-01\",\"major\":\"Cloud DevOps\",\"gpa\":3.92}"
```
- **Kết quả**: Trả về **HTTP 201 Created** kèm trường `"id": <ID_MỚI>` (ví dụ `"id": 14` do cơ chế AUTO_INCREMENT trong MariaDB tự tăng sau các lần chạy test).

#### Bước 5.3: Lấy chi tiết sinh viên vừa tạo (READ SINGLE - GET)
*(Thay số ID bằng ID nhận được ở Bước 5.2, ví dụ 14)*:
```bash
curl http://localhost/api/students-db/14
```
- **Kết quả**: Trả về đúng thông tin sinh viên *Vu Dinh Trong*.

#### Bước 5.4: Cập nhật thông tin sinh viên (UPDATE - PUT)
```bash
curl -X PUT http://localhost/api/students-db/14 -H "Content-Type: application/json" -d "{\"gpa\":4.00}"
```
- **Kết quả**: Điểm GPA được cập nhật thành `4.0`, trả về **HTTP 200 OK**.

#### Bước 5.5: Xóa sinh viên vừa tạo (DELETE)
```bash
curl -X DELETE http://localhost/api/students-db/14
```
- **Kết quả**: Trả về **HTTP 200 OK** xác nhận đã xóa. Gọi lại `curl http://localhost/api/students-db/14` sẽ trả về **404 Not Found**.

#### Bước 5.6: Kiểm tra trực tiếp bên trong CSDL MariaDB
Chạy lệnh sau để truy vấn trực tiếp bảng dữ liệu MariaDB (Mật khẩu của tài khoản `clouduser` là `cloudpassword`):
```powershell
docker exec -it relational-database-server mariadb -u clouduser -pcloudpassword studentdb -e "SELECT * FROM students;"
```
*(Hoặc dùng tài khoản root: `docker exec -it relational-database-server mariadb -uroot -proot studentdb -e "SELECT * FROM students;"`)*

---

### PHẦN 6: DEMO ĐỊNH DANH KEYCLOAK OIDC & XÁC THỰC MẬT MÃ JWT (Chức năng mở rộng 4)

#### Mục tiêu:
Chứng minh hệ thống IAM (Identity and Access Management) chuyên nghiệp với Keycloak 24, cấu hình Realm `MyMiniCloud`, Client `flask-app`, và cơ chế kiểm tra chữ ký mật mã RS256 của Access Token.

#### Thao tác thực hiện:

#### Bước 6.1: Khám phá giao diện quản trị Keycloak Admin Console
1. Truy cập: **`http://localhost:8081`**
2. Đăng nhập: Username: **`admin`** | Password: **`admin`**
3. Chọn Realm: **`MyMiniCloud`** (ở góc trên bên trái).
4. Mở mục **Clients** -> xem Client **`flask-app`**.
5. Mở mục **Users** -> xem danh sách tài khoản đã provision: **`sv01`**, **`sv02`**.

#### Bước 6.2: Demo gọi API khi CHƯA có Token -> Bị từ chối
```bash
curl -i http://localhost:8085/secure
```
- **Kết quả**: Trả về **`HTTP 401 Unauthorized`** kèm thông báo `{"error": "Missing Authorization header"}`.

#### Bước 6.3: Cấp phát Access Token chuẩn OIDC qua cURL
```powershell
$tokenResponse = Invoke-RestMethod -Uri "http://localhost:8081/realms/MyMiniCloud/protocol/openid-connect/token" -Method Post -Body @{
    client_id  = "flask-app"
    username   = "sv01"
    password   = "password"
    grant_type = "password"
}
$token = $tokenResponse.access_token
Write-Host "JWT Token nhận được: $($token.Substring(0, 40))..."
```

#### Bước 6.4: Gọi API với Token hợp lệ -> Thành công
```powershell
Invoke-RestMethod -Uri "http://localhost:8085/secure" -Headers @{ Authorization = "Bearer $token" }
```
- **Kết quả**: Trả về **`HTTP 200 OK`**, hiển thị:
  ```json
  {
    "message": "Welcome to protected cloud resource!",
    "user": "sv01",
    "email": "sv01@cloud.local"
  }
  ```

#### Bước 6.5: Demo chống giả mạo Token (Tamper Detection)
Gửi một token bị can thiệp thêm ký tự vào đuôi:
```powershell
try {
    Invoke-RestMethod -Uri "http://localhost:8085/secure" -Headers @{ Authorization = "Bearer $($token)forged" }
} catch {
    Write-Host "Server phát hiện chữ ký giả mạo: $($_.Exception.Message)"
}
```
- **Kết quả**: Backend từ chối ngay lập tức với mã **401 Unauthorized** vì sai chữ ký mật mã RS256.

---

### PHẦN 7: DEMO LƯU TRỮ ĐỐI TƯỢNG MINIO S3 (Chức năng mở rộng 5)

#### Mục tiêu:
Chứng minh dịch vụ Object Storage S3-compatible, quản lý các bucket phi cấu trúc và bảo toàn tính toàn vẹn dữ liệu qua Checksum SHA-256.

#### Thao tác thực hiện:

#### Bước 7.1: Giao diện quản trị MinIO Console
1. Mở trình duyệt truy cập: **`http://localhost:9001`**
2. Đăng nhập: Username: **`minioadmin`** | Password: **`minioadmin`**
3. Xem mục **Buckets**:
   - Bucket **`profile-pics`**: Chứa tệp `avatar.jpg`.
   - Bucket **`documents`**: Chứa tệp `report.pdf`.

#### Bước 7.2: Truy cập ảnh trực tiếp qua Web Gateway
Mở trình duyệt truy cập URL công khai của ảnh avatar:
👉 **`http://localhost:9000/profile-pics/avatar.jpg`**
*(Hình ảnh avatar hiển thị sắc nét trực tiếp trên trình duyệt).*

#### Bước 7.3: Chứng minh tính toàn vẹn Checksum SHA-256
Chạy script kiểm tra checksum giữa tệp gốc và tệp tải từ MinIO:
```powershell
docker exec object-storage-server mc cat local/profile-pics/avatar.jpg | Out-File -Encoding Byte temp_avatar.jpg
(Get-FileHash temp_avatar.jpg -Algorithm SHA256).Hash
Remove-Item temp_avatar.jpg
```
*(Checksum SHA-256 khớp tuyệt đối với tệp gốc trong mã nguồn).*

---

### PHẦN 8: DEMO PHÂN GIẢI TÊN MIỀN NỘI BỘ BIND9 DNS (Chức năng mở rộng 6)

#### Mục tiêu:
Chứng minh DNS Server nội bộ BIND9 9.18 phân giải chính xác zone riêng tư `cloud.local` cho cả 3 bản ghi A, SOA và NS.

#### Thao tác thực hiện:
Trong **Terminal**, chạy các lệnh truy vấn DNS trực tiếp vào máy chủ BIND9:

```powershell
# 1. Bản ghi máy chủ Web Frontend
docker exec internal-dns-server dig @127.0.0.1 web-frontend-server.cloud.local +short

# 2. Bản ghi máy chủ Backend
docker exec internal-dns-server dig @127.0.0.1 app-backend.cloud.local +short

# 3. Bản ghi máy chủ MinIO Storage
docker exec internal-dns-server dig @127.0.0.1 minio.cloud.local +short
```

#### Kết quả hiển thị:
- `web-frontend-server.cloud.local` -> **`10.10.10.10`**
- `app-backend.cloud.local` -> **`10.10.10.20`**
- `minio.cloud.local` -> **`10.10.10.30`**

*(Cho Thầy/Cô xem tệp cấu hình [dns/zones/db.cloud.local](file:///d:/Cloud/MiniCloud/dns/zones/db.cloud.local) để chứng minh cấu hình Zone bài bản).*

---

### PHẦN 9: DEMO THU THẬP METRICS PROMETHEUS (Chức năng mở rộng 7)

#### Mục tiêu:
Chứng minh Prometheus thu thập số liệu tự động (Pull-based Metrics) từ 4 scrape targets khác nhau (Node Exporter, Flask Backend, Web1, Web2) đều ở trạng thái hoạt động tốt.

#### Thao tác thực hiện:
1. Mở trình duyệt web truy cập: **`http://localhost:9090/targets`**
   - Chỉ cho Thầy/Cô thấy danh sách 4 Scrape Targets đều có trạng thái màu xanh **`UP (1/1)`**.
2. Nhấp vào tab **`Graph`** (`http://localhost:9090/graph`):
   - Nhập câu lệnh PromQL theo dõi CPU:
     ```promql
     rate(node_cpu_seconds_total{mode="idle"}[1m])
     ```
     Bấm **Execute** -> chuyển sang tab **Graph** để xem đồ thị nhịp tim CPU thời gian thực.
   - Nhập câu lệnh PromQL theo dõi HTTP Requests của Flask:
     ```promql
     flask_http_requests_total
     ```
     Bấm **Execute** -> xem số lượng request thực tế của từng endpoint `/student`, `/api/students-db`.

---

### PHẦN 10: DEMO TRỰC QUAN HÓA BẢNG ĐIỀU KHIỂN GRAFANA (Chức năng mở rộng 8)

#### Mục tiêu:
Chứng minh Grafana được nạp cấu hình tự động (Provisioning) từ file YAML/JSON, tự động kết nối Prometheus Data Source và hiển thị Dashboard giám sát 3 chỉ số phần cứng thời gian thực.

#### Thao tác thực hiện:
1. Mở trình duyệt web truy cập: **`http://localhost:3000`**
2. Đăng nhập: Username: **`admin`** | Password: **`admin`**
3. Vào menu bên trái chọn **Dashboards** -> Mở dashboard **`System Health - MyMiniCloud`**.
4. Trình bày 3 đồ thị trực quan:
   - **Panel 1: CPU Usage (%)**: Tỷ lệ phần trăm CPU sử dụng hiện tại.
   - **Panel 2: Memory Usage (RAM)**: Dung lượng bộ nhớ RAM đã sử dụng và còn trống.
   - **Panel 3: Network Traffic (Receive)**: Lưu lượng băng thông mạng truyền nhận qua các container.

> [!TIP]
> **Mẹo tạo hiệu ứng sống động khi Demo**: Mở thêm một cửa sổ terminal và gửi liên tục 50 request (dùng script hoặc F5 liên tục trang web), sau đó quay lại màn hình Grafana: Bạn sẽ thấy đồ thị Network Traffic và CPU vọt lên ngay trước mắt Thầy/Cô!

---

### PHẦN 11: DEMO ĐÓNG GÓI VÀ PHÁT HÀNH TRÊN DOCKER HUB (Phase 6.7)

#### Mục tiêu:
Chứng minh các image tự xây dựng (Custom Images) đã được tối ưu hóa bảo mật (chạy non-root, có `.dockerignore`, dung lượng nhỏ gọn) và đã được publish công khai lên Docker Hub registry chính thức.

#### Thao tác thực hiện:
Mở trình duyệt web và truy cập trang cá nhân Docker Hub của bạn:
👉 **[https://hub.docker.com/u/nguyenmanh3110](https://hub.docker.com/u/nguyenmanh3110)**

#### Những gì trình bày:
1. Cho xem 3 Repositories công khai:
   - **`nguyenmanh3110/myminicloud-backend`** (Tag: `1.0.0`, kích thước nén: ~60 MB)
   - **`nguyenmanh3110/myminicloud-frontend`** (Tag: `1.0.0`, kích thước nén: ~20 MB)
   - **`nguyenmanh3110/myminicloud-gateway`** (Tag: `1.0.0`, kích thước nén: ~20 MB)
2. Nhấp vào tab **Tags** của từng repo để xem **Digest SHA-256**, kiến trúc `linux/amd64`, và thời gian cập nhật.
3. Nhấn mạnh: *"Tất cả các image này đã sẵn sàng để máy chủ AWS EC2 kéo về triển khai một chạm thông qua file `docker-compose.aws.yml`."*

---

### PHẦN 12: CHẠY BỘ KIỂM THỬ TỰ ĐỘNG CHỐT HẠ (AUTOMATED TEST SUITE)

#### Mục tiêu:
Đây là "cú chốt" hoàn hảo cho buổi demo. Chạy một câu lệnh duy nhất kiểm thử tự động toàn diện tất cả các chức năng từ A đến Z, in ra bảng kết quả màu xanh 100% thành công.

#### Thao tác thực hiện:
Mở **Terminal / PowerShell** và gõ lệnh:
```powershell
python tests/integration_test.py
```

#### Màn hình kết quả mẫu:
```text
================================================================================
             MYMINICLOUD AUTOMATED INTEGRATION TEST SUITE (PHASE 6.5)
================================================================================

[PASS] TEST-01: Web Frontend & 3 Blog Posts (Static Hosting)
       Details: Home: 200, Blog: 200, Blog1/2/3: 200/200/200
[PASS] TEST-02: Flask API GET /student (5 Students JSON Reading)
       Details: Status: 200, Students returned: 5
[PASS] TEST-03: MariaDB Full CRUD Operations (POST, GET, PUT, DELETE)
       Details: Initial: 5, POST: 201, GET_ID: 200, PUT: 200, DELETE: 200, 404_Check: 404
[PASS] TEST-04: Keycloak OIDC JWT Cryptographic Verification (RS256)
       Details: Missing Token: 401, Token Gen: 200, Valid Access: 200, Tampered Rejected: 401
[PASS] TEST-05: MinIO S3 Storage (profile-pics, documents & Checksum)
       Details: Buckets present, avatar SHA256: d4d1929e44e41054..., bytes: 149
[PASS] TEST-06: BIND9 DNS Resolution (All 3 Records: web, app, minio)
       Details: web: 10.10.10.10, app: 10.10.10.20, minio: 10.10.10.30
[PASS] TEST-07: Prometheus Scrape Targets Status (All UP)
       Details: Targets UP: 4/4 (node, flask-backend, web1, web2)
[PASS] TEST-08: Grafana Observability & PromQL Proxy Query Execution
       Details: Grafana Health: 200, Datasource Proxy Query Status: 200
[PASS] TEST-09: API Gateway Reverse Proxy (/, /api/, /student, /auth/)
       Details: Gateway /: 200, /api/hello: 200, /student: 200, /auth/: 200
[PASS] TEST-10: Round Robin Load Balancing Distribution (20 Requests)
       Details: web1: 10 (50%), web2: 10 (50%)

================================================================================
SUMMARY: 10/10 Tests Passed.
================================================================================

>>> ALL PHASE 6.5 INTEGRATION TESTS PASSED WITH 100% SUCCESS! <<<
```

---

## 4. BỘ CÂU HỎI VẤN ĐÁP THƯỜNG GẶP KHI DEMO (Q&A CHEAT SHEET)

| Câu hỏi của Giảng viên | Câu trả lời chuẩn kỹ thuật |
|:---|:---|
| **1. Tại sao phải có Nginx Gateway mà không để người dùng gọi thẳng vào Flask hoặc Web?** | *"Dạ thưa Thầy/Cô, API Gateway đóng vai trò là Single Entrypoint (điểm vào duy nhất), giúp giấu kín cấu trúc mạng nội bộ, chịu trách nhiệm Reverse Proxy, cân bằng tải Round Robin và SSL Termination. Người dùng không cần biết port nào của backend, tăng tính bảo mật."* |
| **2. Dữ liệu MariaDB và MinIO có bị mất khi container bị tắt hoặc restart không?** | *"Dạ không ạ. Em đã cấu hình Docker Persistent Volumes (`myminicloud_mariadb_data` và `myminicloud_minio_data`). Khi container bị tắt hoặc xóa (`docker compose down`), dữ liệu trên ổ đĩa vật lý vẫn được giữ nguyên vẹn."* |
| **3. Cơ chế xác thực JWT trong Backend hoạt động như thế nào? Nó có kiểm tra chữ ký không?** | *"Dạ có ạ. Backend của em sử dụng thư viện `python-jose` lấy Public Keys từ endpoint JWKS của Keycloak (`/certs`) để giải mã và xác thực chữ ký mật mã RS256. Nếu token bị can thiệp dù chỉ 1 ký tự, server sẽ từ chối ngay với mã 401 Unauthorized."* |
| **4. Các container giao tiếp với nhau bằng cách nào nếu không mở cổng ra ngoài host?** | *"Dạ thưa Thầy/Cô, toàn bộ container cùng tham gia vào bridge network mang tên `cloud-net`. Docker Engine tích hợp sẵn DNS nội bộ, các container gọi nhau trực tiếp bằng tên dịch vụ (ví dụ `http://application-backend-server:8081` hoặc `relational-database-server:3306`) mà không cần map cổng ra host."* |
| **5. Khi chuyển từ Local lên AWS EC2, hệ thống cần thay đổi những gì?** | *"Dạ em đã chuẩn bị sẵn file `docker-compose.aws.yml`. Trên AWS EC2, ta chỉ cần mở cổng 80 và 22 trên Security Group, đổi biến `PUBLIC_IP` thành IP của EC2, và kéo trực tiếp các image đã đóng gói trên Docker Hub (`nguyenmanh3110/*:1.0.0`) về chạy mà không cần build mã nguồn trên server."* |

