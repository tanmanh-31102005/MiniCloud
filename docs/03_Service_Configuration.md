# CẤU HÌNH CHI TIẾT 9 VAI TRÒ DỊCH VỤ (SERVICE CONFIGURATION SPECIFICATION)

---

## 1. NGINX WEB FRONTEND SERVER (WEB NODE 1 & WEB NODE 2)

- **Vai trò**: Phục vụ nội dung web tĩnh (Static Web Hosting), trang chủ và 3 bài viết blog kỹ thuật.
- **Image**: `cloudstudent/myminicloud-web:v1.0` (Build từ base `nginx:1.25-alpine`).
- **Mã nguồn**: `frontend/`
- **Cấu hình Nginx**:
  ```nginx
  server {
      listen 80;
      root /usr/share/nginx/html;
      index index.html;
      add_header X-Served-By $hostname always;

      location / { try_files $uri $uri/ /index.html =404; }
      location ^~ /blog/ {
          alias /usr/share/nginx/html/blog/;
          index index.html;
      }
      location /health { return 200 "healthy\n"; }
      location /server-info {
          return 200 '{"server":"$hostname","status":"online"}';
      }
  }
  ```
- **Khả năng mở rộng**: Triển khai thành 2 instance `web-frontend-server1` (cổng 8080) và `web-frontend-server2` (cổng 8082) nằm sau API Gateway để minh chứng cân bằng tải Round Robin.

---

## 2. FLASK APPLICATION BACKEND SERVER

- **Vai trò**: Application Server / Microservice cung cấp REST API, trích xuất dữ liệu JSON, kết nối cơ sở dữ liệu quan hệ và xác thực OIDC JWT.
- **Image**: `cloudstudent/myminicloud-app:v1.0` (Build từ base `python:3.11-slim`).
- **Mã nguồn**: `backend/`
- **Các API Endpoints**:
  1. `GET /hello`: Baseline microservice health check, trả về JSON `{"message": "Hello from App Server!"}`.
  2. `GET /student`: Đọc file `backend/data/students.json` trả về đúng 5 sinh viên mẫu (ID, Tên, Chuyên ngành, Điểm GPA).
  3. `GET /api/students-db`: Kết nối MariaDB `studentdb`, thực thi truy vấn bảng `students`.
  4. `POST /api/students-db`: Thêm sinh viên mới vào MariaDB (hỗ trợ kiểm thử CRUD).
  5. `GET /secure`: Bảo vệ bằng JWT token. Kiểm tra chữ ký mật mã RS256 thông qua Keycloak JWKS, xác minh Issuer, Audience và thời hạn hiệu lực.
  6. `GET /metrics`: Xuất Prometheus Metrics (`Counter`, `Histogram`).
  7. `GET /health`: Healthcheck endpoint cho Docker Engine.

---

## 3. RELATIONAL DATABASE SERVER (MARIADB)

- **Vai trò**: Cơ sở dữ liệu quan hệ (tương đương AWS RDS MariaDB).
- **Image**: `mariadb:11.3`
- **Khởi tạo tự động**: Thư mục `database/init/01_init.sql` được mount vào `/docker-entrypoint-initdb.d:ro`.
- **Cơ sở dữ liệu**:
  - `minicloud`: Bảng `notes` (chứa bản ghi mẫu `Hello from MariaDB!`).
  - `studentdb`: Bảng `students` (chứa 5 sinh viên mẫu với các trường `student_id`, `fullname`, `dob`, `major`, `gpa`).
- **Lưu trữ bền vững**: Docker Volume `mariadb_data:/var/lib/mysql`. Dữ liệu hoàn toàn không bị mất khi container khởi động lại hoặc dừng.

---

## 4. AUTHENTICATION & IDENTITY SERVER (KEYCLOAK)

- **Vai trò**: Identity and Access Management (IAM), Identity Provider (IdP) theo chuẩn OIDC / OAuth 2.0.
- **Image**: `quay.io/keycloak/keycloak:24.0.5`
- **Chế độ chạy**: `start-dev --import-realm`
- **Tự động nạp cấu hình**: Thư mục `keycloak/import/myminicloud-realm.json` được mount vào `/opt/keycloak/data/import:ro`.
  - **Realm**: `MyMiniCloud`
  - **Client**: `flask-app` (Public Client, hỗ trợ Direct Access Grants flow).
  - **Tài khoản thử nghiệm**:
    - `sv01` / `password123`
    - `sv02` / `password123`
    - Admin: `admin` / `admin`
- **Xác thực JWT**: Phát hành Access Token ký bằng khóa riêng RSA (RS256) và công khai khóa qua endpoint `/protocol/openid-connect/certs`.

---

## 5. OBJECT STORAGE SERVER (MINIO)

- **Vai trò**: Lưu trữ đối tượng phi cấu trúc (tương đương AWS S3).
- **Image**: `minio/minio:RELEASE.2024-05-10T01-41-38Z`
- **Cổng giao tiếp**:
  - `9000`: S3 API Endpoint.
  - `9001`: MinIO Web Console (Quản trị trực quan).
- **Tự động tạo Buckets qua MinIO Provisioner (`minio/mc`)**:
  - Bucket `profile-pics`: Lưu trữ hình ảnh đại diện (avatar.jpg), áp dụng chính sách public download.
  - Bucket `documents`: Lưu trữ tệp tài liệu báo cáo (report.pdf).
- **Lưu trữ bền vững**: Docker Volume `minio_data:/data`.

---

## 6. INTERNAL DNS SERVER (BIND9)

- **Vai trò**: Máy chủ phân giải tên miền nội bộ (Internal DNS / Service Discovery, tương đương AWS Route 53 Private Hosted Zone).
- **Image**: `internetsystemsconsortium/bind9:9.18`
- **Cấu hình**:
  - `dns/named.conf.options`: Bật đệ quy (recursion), cho phép truy vấn nội bộ.
  - `dns/named.conf.local`: Định nghĩa Zone `cloud.local`.
  - `dns/zones/db.cloud.local`: Các bản ghi A ánh xạ IP cố định cho `web-frontend-server`, `app-backend`, `minio`, `keycloak`, `db`, `gateway`.
- **Cổng giao tiếp**: Port `1053/udp` và `1053/tcp`.

---

## 7. MONITORING SYSTEM (PROMETHEUS & NODE EXPORTER)

- **Vai trò**: Thu thập và quản lý dữ liệu đo lường hệ thống (Metrics Collection, tương đương AWS CloudWatch Metrics).
- **Node Exporter**: Image `prom/node-exporter:v1.8.0`, xuất thông số phần cứng (CPU, RAM, Disk, Network) tại cổng `9100`.
- **Prometheus**: Image `prom/prometheus:v2.51.2`, cổng `9090`.
- **Scrape Targets**:
  - `node`: `monitoring-node-exporter-server:9100` (Chu kỳ 15s).
  - `flask-backend`: `application-backend-server:8081/metrics` (Chu kỳ 15s).
  - `web`: `web-frontend-server1:80` & `web-frontend-server2:80`.

---

## 8. VISUALIZATION DASHBOARD (GRAFANA)

- **Vai trò**: Trực quan hóa dữ liệu giám sát và xây dựng bảng điều khiển thời gian thực.
- **Image**: `grafana/grafana:10.4.2`, cổng `3000`.
- **Auto-Provisioning**:
  - Tự động nạp Data Source Prometheus (`monitoring/grafana/provisioning/datasources/prometheus.yml`).
  - Tự động nạp Dashboard `System Health - MyMiniCloud` (`monitoring/grafana/provisioning/dashboards/dashboards.yml` & `system-health.json`).
  - Hiển thị đầy đủ 3 biểu đồ: **CPU Usage (%)**, **Memory Usage**, **Network Traffic**.

---

## 9. API GATEWAY & LOAD BALANCER (NGINX REVERSE PROXY)

- **Vai trò**: Điểm tiếp nhận duy nhất cho toàn bộ hệ thống (Single Entry Point), Reverse Proxy và cân bằng tải Round Robin.
- **Image**: `nginx:1.25-alpine`, cổng `80`.
- **Định tuyến (Routing)**:
  - `http://localhost/` -> Chuyển tiếp Round Robin tới `web_cluster` (Web 1 & Web 2).
  - `http://localhost/blog/` -> Chuyển tiếp tới Web Cluster.
  - `http://localhost/api/*` -> Chuyển tiếp tới Flask Backend (strip `/api/`).
  - `http://localhost/student` -> Chuyển tiếp tới Flask Backend `/student`.
  - `http://localhost/auth/*` -> Chuyển tiếp tới Keycloak IAM.
- **Headers**: Bổ sung `X-Gateway` và `X-Upstream-Backend` để kiểm chứng luân phiên Round Robin.

