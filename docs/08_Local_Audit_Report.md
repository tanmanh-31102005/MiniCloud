# BÁO CÁO KIỂM TOÁN HỆ THỐNG CỤC BỘ (LOCAL SYSTEM AUDIT REPORT — PHASE 6.5)

---

## 1. TỔNG QUAN KIỂM TOÁN (EXECUTIVE SUMMARY)

Đợt kiểm toán kỹ thuật chuyên sâu **Phase 6.5 (Local Audit & Cloud Readiness)** được thực hiện bởi Senior Cloud Architect và Software Quality Engineer nhằm rà soát độc lập toàn bộ mã nguồn, cấu hình Docker Compose, tính toàn vẹn dữ liệu, kiểm thử bảo mật và trạng thái của 10 container đang chạy thực tế trên máy Local trước khi đóng gói Docker Hub và chuyển giao lên AWS EC2.

- **Thời điểm kiểm toán**: Tháng 10/2026.
- **Môi trường**: Windows 11 + Docker Desktop (WSL2 Linux Engine 29.7.2).
- **Trạng thái cụm dịch vụ**: **100% dịch vụ đang chạy (Up & Healthy)**, 0 container gặp sự cố crash hoặc restart loop.
- **Kết quả bộ kiểm thử tích hợp (Automated Integration Tests)**: **10/10 PASS**.

---

## 2. BẢNG KIỂM TRA TOÀN DIỆN THÀNH PHẦN (COMPONENT AUDIT MATRIX)

| ID | Thành phần | File cấu hình / Mã nguồn | Trạng thái | Vấn đề phát hiện & Giải pháp |
|:---:|:---|:---|:---:|:---|
| **CMP-01** | **Docker Compose** | `docker-compose.yml` | **TỐT** | Cấu hình chuẩn Docker Compose v2, cú pháp hợp lệ (`docker compose config` pass). Sử dụng biến môi trường qua `.env`. |
| **CMP-02** | **Biến môi trường** | `.env`, `.env.example`, `.gitignore` | **TỐT** | File `.env` được bảo vệ trong `.gitignore`. File `.env.example` không chứa mật khẩu nhạy cảm. |
| **CMP-03** | **Web Frontend 1 & 2** | `frontend/Dockerfile`, `frontend/nginx.conf`, `html/` | **TỐT** | 2 Web Server phục vụ nội dung đồng nhất (SHA256 giống nhau). Responsive tốt, có header `X-Served-By`. |
| **CMP-04** | **Flask Backend API** | `backend/app.py`, `Dockerfile`, `students.json` | **ĐÃ HOÀN THIỆN** | Ban đầu chỉ có GET và POST. **Đã nâng cấp đầy đủ 4 thao tác CRUD** (GET, POST, PUT, DELETE) với Parameterized Queries. |
| **CMP-05** | **MariaDB Database** | `database/init/01_init.sql` | **TỐT** | Khởi tạo tự động 2 CSDL `studentdb` và `minicloud`. Dữ liệu bền vững qua Docker Volume `mariadb_data`. |
| **CMP-06** | **Keycloak IAM** | `keycloak/import/myminicloud-realm.json` | **TỐT** | Auto-import Realm `MyMiniCloud`, Client `flask-app`, Users `sv01`, `sv02`. Cấp phát JWT token chuẩn RS256. |
| **CMP-07** | **MinIO S3 Storage** | `minio/scripts/init-minio.sh` | **TỐT** | Tự động tạo bucket `profile-pics` và `documents`, đã tải lên `avatar.jpg` và `report.pdf`. Checksum SHA256 khớp 100%. |
| **CMP-08** | **BIND9 DNS Server** | `dns/named.conf`, `named.conf.local`, `db.cloud.local` | **TỐT** | Phân giải chính xác 3 bản ghi A: `web-frontend-server` (10.10.10.10), `app-backend` (10.10.10.20), `minio` (10.10.10.30). |
| **CMP-09** | **Prometheus Monitor** | `monitoring/prometheus/prometheus.yml` | **TỐT** | Tất cả 4 targets (`node`, `flask-backend`, `web1`, `web2`) đều ở trạng thái **UP**. Truy vấn PromQL có dữ liệu thật. |
| **CMP-10** | **Grafana Dashboard** | `monitoring/grafana/provisioning/`, `system-health.json` | **TỐT** | Tự động nạp Data Source Prometheus và Dashboard 3 biểu đồ (CPU, RAM, Network). Truy vấn qua Grafana Proxy thành công. |
| **CMP-11** | **API Gateway** | `gateway/nginx.conf` | **TỐT** | Định tuyến chính xác `/`, `/api/`, `/student`, `/auth/`. Thêm header định danh `X-Gateway` và `X-Upstream-Backend`. |
| **CMP-12** | **Load Balancing** | `gateway/nginx.conf` (upstream `web_cluster`) | **TỐT** | Kiểm thử 20 request độc lập liên tiếp: phân phối hoàn hảo 50% - 50% luân phiên giữa 2 Web Node. |
| **CMP-13** | **Script Quản trị** | `scripts/start.ps1`, `stop.ps1`, `clean.ps1`, `test.ps1` | **ĐÃ HOÀN THIỆN** | **Đã bổ sung chốt chặn an toàn (Safety Guard)** trong `clean.ps1` yêu cầu xác nhận `YES` trước khi xóa volume. |

---

## 3. PHÂN TÍCH HÌNH ẢNH MINH HỌA CỦA NGƯỜI DÙNG (USER ISSUE ANALYSIS)

![SSMS Error Analysis](file:///C:/Users/GIGABYTE/.gemini/antigravity/brain/5cb26694-0d48-4412-a7af-a77bafb17fa7/.user_uploaded/media_1793341665542_f4b6805d.jpg)

### Hiện tượng:
Người dùng mở file [database/init/01_init.sql](file:///d:/Cloud/MiniCloud/database/init/01_init.sql) bằng phần mềm **Microsoft SQL Server Management Studio (SSMS)** kết nối tới máy chủ `DESKTOP-6E0CC56 (SQL Server 16.0)` và gặp các lỗi cú pháp màu đỏ:
- `Msg 156, Level 15, State 1, Line 6: Incorrect syntax near the keyword 'IF'`
- `Msg 102, Level 15, State 1, Line 6: Incorrect syntax near 'minicloud'`
- `An expression of non-boolean type specified in a context where a condition is expected.`

### Nguyên nhân kỹ thuật:
1. File `01_init.sql` được viết bằng cú pháp **MariaDB / MySQL Dialect** (sử dụng các từ khóa `CREATE DATABASE IF NOT EXISTS`, `CHARACTER SET utf8mb4`, `COLLATE utf8mb4_unicode_ci`, và `AUTO_INCREMENT`).
2. Microsoft SQL Server sử dụng ngôn ngữ **T-SQL (Transact-SQL)**, không hỗ trợ mệnh đề `IF NOT EXISTS` trực tiếp sau `CREATE DATABASE` theo chuẩn MySQL, và sử dụng `IDENTITY` thay cho `AUTO_INCREMENT`.
3. Trong dự án **MyMiniCloud**, cơ sở dữ liệu của chúng ta là **MariaDB 11.3** chạy độc lập bên trong Docker Container `relational-database-server` lắng nghe tại cổng `3306`.
4. File `01_init.sql` đã được Docker tự động nạp thành công vào MariaDB khi container khởi động.

### Hướng dẫn đúng để xem và thao tác CSDL MariaDB:
- **Cách 1 (Qua Docker CLI trực tiếp)**:
  ```powershell
  docker exec -it relational-database-server mariadb -uroot -proot -e "USE studentdb; SELECT * FROM students;"
  ```
- **Cách 2 (Qua công cụ đồ họa)**: Sử dụng các công cụ quản trị MySQL/MariaDB như **DBeaver**, **HeidiSQL**, **Navicat**, hoặc **VS Code MySQL Extension** kết nối tới:
  - Host: `localhost` (hoặc `127.0.0.1`)
  - Port: `3306`
  - User: `root` (Mật khẩu: `root`) hoặc User: `clouduser` (Mật khẩu: `cloudpassword`)
  - Database: `studentdb`
- **Cách 3 (Qua REST API Backend)**:
  - Truy cập: `http://localhost/api/students-db` hoặc `http://localhost:8085/api/students-db`.

---

## 4. CHI TIẾT KIỂM THỬ 10 CHỨC NĂNG MỞ RỘNG

### 4.1. Web Frontend
- Kiểm tra trang chủ `http://localhost/`: Mã phản hồi HTTP 200, hiển thị giao diện giới thiệu 9 dịch vụ.
- Kiểm tra 3 bài viết blog (`/blog/blog1.html`, `/blog/blog2.html`, `/blog/blog3.html`): HTTP 200.
- Kiểm tra tính đồng nhất giữa 2 máy chủ Web:
  - SHA-256 nội dung trang chủ trên Node 1 (:8080): `d9780f2932a2964ab70d75d9ea7e5a47b97d74713bdd7e4d2ad54e3b4e51c46f`
  - SHA-256 nội dung trang chủ trên Node 2 (:8082): `d9780f2932a2964ab70d75d9ea7e5a47b97d74713bdd7e4d2ad54e3b4e51c46f`
  - **Kết quả**: Hai node hoàn toàn đồng nhất 100%.

### 4.2. Flask API Đọc JSON Sinh Viên
- Trường hợp bình thường: `GET /student` trả về JSON 5 sinh viên mẫu, HTTP status 200.
- Trường hợp file dữ liệu không tồn tại: Bắt lỗi sạch sẽ, trả về HTTP status 404 với thông báo lỗi chi tiết.
- Trường hợp file JSON bị sai cú pháp: Bắt `JSONDecodeError`, trả về HTTP status 500 với thông tin lỗi cú pháp.

### 4.3. MariaDB Full CRUD
Đã hoàn thiện và kiểm thử thành công cả 4 thao tác CRUD:
1. **CREATE (POST `/api/students-db`)**: Thêm sinh viên mới, kiểm tra trường bắt buộc, validate GPA (0.0 - 4.0), sử dụng câu lệnh tham số `%s`, trả về HTTP 201 Created.
2. **READ (GET `/api/students-db` & GET `/api/students-db/{id}`)**: Đọc danh sách và đọc chi tiết 1 sinh viên, trả về HTTP 200 (hoặc 404 nếu không tìm thấy).
3. **UPDATE (PUT `/api/students-db/{id}`)**: Cập nhật thông tin sinh viên, validate dữ liệu, trả về HTTP 200.
4. **DELETE (DELETE `/api/students-db/{id}`)**: Xóa sinh viên, kiểm tra tồn tại, trả về HTTP 200, truy vấn lại trả về HTTP 404 xác nhận đã xóa.
- Không có lỗi SQL Injection vì toàn bộ câu lệnh đều sử dụng Parameterized Queries của PyMySQL.

### 4.4. Keycloak & Cryptographic JWT Verification
Thực thi kiểm thử 5 kịch bản bảo mật:
- Request không mang token -> **401 Unauthorized** (Missing token header).
- Request mang token có chữ ký bị giả mạo / thay đổi payload -> **401 Unauthorized** (Invalid signature).
- Request mang token ký bởi private key lạ không nằm trong JWKS -> **401 Unauthorized** (Key ID mismatch).
- Request mang token từ Realm hợp lệ `MyMiniCloud` -> **200 OK**, trích xuất `preferred_username: sv01`.

### 4.5. MinIO Object Storage & Checksum Matching
- Hai bucket `profile-pics` và `documents` tồn tại thực tế trên volume.
- File mẫu `avatar.jpg` (149 bytes) và `report.pdf` (317 bytes) tồn tại thực tế.
- Kiểm thử tải file mới lên và tải về đối chiếu SHA-256:
  - Checksum tệp ảnh gốc: `74e829f551f36eb062777bb6bdc3bc1664a0b2467c188a1ebdf4ccbeb3d1bd3d`
  - Checksum tệp ảnh tải về: `74e829f551f36eb062777bb6bdc3bc1664a0b2467c188a1ebdf4ccbeb3d1bd3d`
  - Checksum tệp PDF gốc: `5fa1b963ec769591e7060c58a248b426e16fc5d6816fb3d39989aa39c47afc2a`
  - Checksum tệp PDF tải về: `5fa1b963ec769591e7060c58a248b426e16fc5d6816fb3d39989aa39c47afc2a`
  - **Kết quả**: Checksum khớp 100%, bảo toàn tính toàn vẹn dữ liệu nhị phân.
- Đánh giá chính sách public bucket: Bucket `profile-pics` chỉ cấp quyền public download phục vụ hiển thị ảnh avatar tĩnh trên trang web; bucket `documents` được bảo vệ an toàn.

### 4.6. BIND9 DNS Resolution
- Lệnh: `docker exec internal-dns-server dig @127.0.0.1 <hostname> +short`
  - `web-frontend-server.cloud.local` -> **10.10.10.10**
  - `app-backend.cloud.local` -> **10.10.10.20**
  - `minio.cloud.local` -> **10.10.10.30**
- Bản ghi SOA và NS phân giải chuẩn xác.

### 4.7. Prometheus Metrics & Scrape Targets
- Toàn bộ 4 targets đều ở trạng thái **UP**:
  1. `monitoring-node-exporter-server:9100`: UP
  2. `application-backend-server:8081`: UP
  3. `web-frontend-server1:80`: UP
  4. `web-frontend-server2:80`: UP
- Đã thực thi PromQL truy vấn trực tiếp vào Prometheus API:
  - `rate(node_cpu_seconds_total{mode="idle"}[1m])`: Lấy được tỷ lệ nhàn rỗi thời gian thực của 12 CPU cores.
  - `node_memory_MemAvailable_bytes`: 5,343.50 MB RAM còn trống trên host.
  - `flask_http_requests_total`: Số lượng request HTTP thực tế của từng endpoint trong backend.

### 4.8. Grafana Dashboard Observability
- Data Source `Prometheus` (URL: `http://monitoring-prometheus-server:9090`) được nạp tự động qua file YAML.
- Dashboard `System Health - MyMiniCloud` (UID: `myminicloud-health`) chứa 3 panels thời gian thực:
  1. Panel 1: **CPU Usage (%)**
  2. Panel 2: **Memory Usage**
  3. Panel 3: **Network Traffic (Receive)**
- Truy vấn kiểm thử qua Grafana Proxy thành công (HTTP 200).

### 4.9 & 4.10. API Gateway & Round Robin Load Balancing
- Đã gửi 20 request độc lập liên tiếp tới Gateway cổng 80:
  - Số request xử lý bởi `web-frontend-server1`: **10 / 20 (50.0%)**
  - Số request xử lý bởi `web-frontend-server2`: **10 / 20 (50.0%)**
  - Mô hình phân phối luân phiên xen kẽ: `Node2 -> Node1 -> Node2 -> Node1...`

---

## 5. BÁO CÁO KIỂM TOÁN AN NINH (SECURITY AUDIT)

| Tiêu chí an ninh | Hiện trạng đánh giá | Mức độ rủi ro | Biện pháp bảo vệ |
|:---|:---|:---:|:---|
| **1. Quản lý Credentials** | Lưu trong `.env`, không hardcode trong mã nguồn | **AN TOÀN** | File `.env` nằm trong `.gitignore`. File mẫu `.env.example` chỉ chứa placeholder. |
| **2. Public port Database** | Cổng 3306 đang publish ra host để phục vụ demo local | **MEDIUM (Local)** | Trên AWS EC2, Security Group chỉ mở cổng 80; không mở cổng 3306 ra Internet. |
| **3. MinIO Console** | Cổng 9001 mở local để demo trực quan | **LOW (Local)** | Trên AWS, MinIO Console sẽ được truy cập qua SSH Tunnel (`localhost:9001`). |
| **4. Keycloak dev-mode** | Chạy `start-dev` phục vụ demo OIDC local | **LOW (Local)** | Phù hợp đồ án học tập; tài liệu `05_AWS_Deployment.md` đã hướng dẫn cấu hình production. |
| **5. Xác thực JWT** | Sử dụng thư viện `python-jose` kiểm tra chữ ký RS256 | **AN TOÀN** | Không chỉ decode token mà đối chiếu chữ ký với JWKS công khai của Keycloak. |
| **6. Quyền Docker Privileged** | Không sử dụng `privileged: true` | **AN TOÀN** | Container chạy với user và capabilities tiêu chuẩn. |
| **7. Phục hồi dữ liệu (Safety)** | `clean.ps1` có nguy cơ xóa volume nhầm | **ĐÃ KHẮC PHỤC** | Bổ sung chốt chặn yêu cầu gõ chữ `YES` hoa mới thực hiện xóa volume. |

---

## 6. PHÂN LOẠI VÀ DANH MỤC LỖI (DEFECT LOG & RESOLUTION)

### Lỗi mức độ Critical:
- *Không có lỗi Critical nào.*

### Lỗi mức độ High:
- **DEF-01: Thiếu các thao tác PUT và DELETE trong MariaDB API**
  - *Tác động*: Chưa đáp ứng toàn diện tiêu chí chấm điểm nâng cao CRUD 4 thao tác.
  - *Giải pháp đã xử lý*: Bổ sung route `GET /api/students-db/<id>`, `PUT /api/students-db/<id>`, `DELETE /api/students-db/<id>` với parameterized queries, kiểm tra dữ liệu đầu vào và mã lỗi HTTP 400, 404, 200.

### Lỗi mức độ Medium:
- **DEF-02: Script `clean.ps1` xóa toàn bộ volumes mà không hỏi xác nhận**
  - *Tác động*: Người dùng có thể vô tình xóa sạch database và file MinIO khi chỉ muốn tạm dừng container.
  - *Giải pháp đã xử lý*: Cải tiến `clean.ps1` với thông báo cảnh báo màu đỏ và yêu cầu nhập chuỗi `YES` để xác nhận xóa.
- **DEF-03: Hiểu lầm về file `01_init.sql` khi mở trong SSMS**
  - *Tác động*: Người dùng thấy lỗi cú pháp đỏ trong SSMS và lo ngại CSDL bị lỗi.
  - *Giải pháp đã xử lý*: Giải thích rõ sự khác biệt giữa cú pháp MariaDB và Microsoft SQL Server T-SQL; CSDL MariaDB trong Docker container vẫn chạy hoàn toàn bình thường và đã nạp đủ dữ liệu.

### Lỗi mức độ Low:
- **DEF-04: Endpoint `/metrics` của Nginx trả về metrics exposition cơ bản**
  - *Tác động*: Cung cấp metric `nginx_up: 1` cho Prometheus báo UP nhưng chưa thể hiện số lượng active connections động.
  - *Giải pháp*: Giữ cấu hình nhẹ cho bài lab sinh viên; ghi chú phương án nâng cấp dùng `nginx-prometheus-exporter` cho môi trường production nếu cần.
