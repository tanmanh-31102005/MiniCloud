# HỒ SƠ ĐÓNG GÓI VÀ PHÁT HÀNH DOCKER HUB
## DOCKER HUB RELEASE MANIFEST — MYMINICLOUD VERSION 1.0.0

---

## 1. THÔNG TIN PHÁT HÀNH TỔNG QUAN

- **Phiên bản phát hành (Semantic Version)**: `1.0.0`
- **Ngày build & kiểm định**: Tháng 11/2026
- **Môi trường Build**: Docker Desktop on WSL2 (Engine 29.7.2, Linux x86_64)
- **Kiến trúc đích (Target Architecture)**: `linux/amd64` (x86_64) — Tương thích 100% với AWS EC2 Ubuntu 24.04 LTS
- **Trạng thái kiểm toán an ninh (Security Audit)**: **PASSED** (0 secrets, 0 credentials, có `.dockerignore`, non-root execution trên Backend).

---

## 2. DANH MỤC CUSTOM IMAGES ĐƯỢC ĐÓNG GÓI

| STT | Tên Image & Tag | Base Image | Kích thước Nén (Content Size) | Kích thước Giải nén | User thực thi | Mục đích chức năng |
|:---:|:---|:---|:---:|:---:|:---:|:---|
| 1 | `<DOCKERHUB_USER>/myminicloud-backend:1.0.0` | `python:3.11-slim` | **60.2 MB** | 248 MB | `appuser` (UID: 1000) | Flask REST API, Full CRUD MariaDB, OIDC JWT (RS256), Prometheus Metrics. |
| 2 | `<DOCKERHUB_USER>/myminicloud-frontend:1.0.0` | `nginx:1.25-alpine` | **20.5 MB** | 74.2 MB | `nginx` (workers) | Máy chủ Web tĩnh phục vụ trang chủ MyMiniCloud và 3 bài viết Blog công nghệ. |
| 3 | `<DOCKERHUB_USER>/myminicloud-gateway:1.0.0` | `nginx:1.25-alpine` | **20.5 MB** | 74.1 MB | `nginx` (workers) | API Gateway, Reverse Proxy và Bộ cân bằng tải Round Robin (50/50). |

> [!NOTE]
> Các dịch vụ phụ trợ như MariaDB (`mariadb:11.3`), Keycloak (`quay.io/keycloak/keycloak:24.0.5`), MinIO (`elestio/minio:latest`), BIND9 (`internetsystemsconsortium/bind9:9.18`), Prometheus (`prom/prometheus:v2.51.2`), Grafana (`grafana/grafana:10.4.2`), và Node Exporter (`prom/node-exporter:v1.8.0`) sử dụng trực tiếp official image từ các registry công khai uy tín để đảm bảo tính chuẩn hóa và cập nhật bảo mật upstream.

---

## 3. QUY TRÌNH LỆNH TIÊU CHUẨN (CLI COMMAND REFERENCE)

### 3.1. Đối với Backend Image (`myminicloud-backend`)

- **Build Command**:
  ```bash
  docker build -t myminicloud-backend:1.0.0 ./backend
  ```
- **Tag Command**:
  ```bash
  docker tag myminicloud-backend:1.0.0 <DOCKERHUB_USER>/myminicloud-backend:1.0.0
  ```
- **Push Command**:
  ```bash
  docker push <DOCKERHUB_USER>/myminicloud-backend:1.0.0
  ```
- **Pull Command**:
  ```bash
  docker pull <DOCKERHUB_USER>/myminicloud-backend:1.0.0
  ```
- **Standalone Run Command (Kiểm thử độc lập)**:
  ```bash
  docker run -d --name test-backend -p 8085:8081 <DOCKERHUB_USER>/myminicloud-backend:1.0.0
  ```

### 3.2. Đối với Frontend Image (`myminicloud-frontend`)

- **Build Command**:
  ```bash
  docker build -t myminicloud-frontend:1.0.0 ./frontend
  ```
- **Tag Command**:
  ```bash
  docker tag myminicloud-frontend:1.0.0 <DOCKERHUB_USER>/myminicloud-frontend:1.0.0
  ```
- **Push Command**:
  ```bash
  docker push <DOCKERHUB_USER>/myminicloud-frontend:1.0.0
  ```
- **Pull Command**:
  ```bash
  docker pull <DOCKERHUB_USER>/myminicloud-frontend:1.0.0
  ```
- **Standalone Run Command (Kiểm thử độc lập)**:
  ```bash
  docker run -d --name test-frontend -p 8080:80 <DOCKERHUB_USER>/myminicloud-frontend:1.0.0
  ```

### 3.3. Đối với Gateway Image (`myminicloud-gateway`)

- **Build Command**:
  ```bash
  docker build -t myminicloud-gateway:1.0.0 ./gateway
  ```
- **Tag Command**:
  ```bash
  docker tag myminicloud-gateway:1.0.0 <DOCKERHUB_USER>/myminicloud-gateway:1.0.0
  ```
- **Push Command**:
  ```bash
  docker push <DOCKERHUB_USER>/myminicloud-gateway:1.0.0
  ```
- **Pull Command**:
  ```bash
  docker pull <DOCKERHUB_USER>/myminicloud-gateway:1.0.0
  ```
- **Standalone Run Command (Khởi chạy trên mạng Docker)**:
  ```bash
  docker run -d --name test-gateway --network cloud-net -p 80:80 <DOCKERHUB_USER>/myminicloud-gateway:1.0.0
  ```

---

## 4. BẢNG THAY ĐỔI CỦA PHIÊN BẢN (CHANGELOG V1.0.0)

| Thành phần | Thay đổi kỹ thuật trong Version 1.0.0 |
|:---|:---|
| **Backend** | - Nâng cấp hỗ trợ Full 4 thao tác CRUD (GET, POST, PUT, DELETE) với MariaDB.<br>- Tham số hóa toàn bộ câu lệnh SQL (Parameterized Queries) chống SQLi.<br>- Tích hợp OIDC JWKS token verification kiểm tra chữ ký mật mã RS256.<br>- Bổ sung tệp `.dockerignore` loại trừ `__pycache__` và file tạm.<br>- Tạo và chuyển đổi sang user phi đặc quyền `appuser` (UID 1000) tăng cường bảo mật.<br>- Cấu hình Healthcheck tự động định kỳ 15s. |
| **Frontend** | - Hoàn thiện 3 bài viết Blog công nghệ với thanh điều hướng nhất quán.<br>- Bổ sung endpoint `/health` trả về HTTP 200 cho Healthcheck.<br>- Bổ sung endpoint `/metrics` trả về chỉ số hoạt động cho Prometheus.<br>- Tối ưu quyền đọc tệp tĩnh `chmod -R 755 /usr/share/nginx/html`.<br>- Bổ sung tệp `.dockerignore`. |
| **Gateway** | - Đóng gói tệp cấu hình Reverse Proxy và Load Balancer thành image độc lập.<br>- Định tuyến thông minh `/`, `/api/`, `/student`, `/auth/`.<br>- Cấu hình Upstream `web_cluster` cân bằng tải Round Robin luân phiên giữa 2 Node.<br>- Thêm các header nhận diện `X-Gateway` và `X-Upstream-Backend`. |

---

## 5. BÁO CÁO KIỂM TRA BẢO MẬT TRƯỚC KHI PUSH (PRE-PUSH SECURITY AUDIT)

Đã thực hiện quét kiểm tra độc lập trên cả 3 image:
1. **Kiểm tra tệp nhạy cảm**: Không tìm thấy bất kỳ tệp `.env`, `.env.example`, `id_rsa`, `.pem` hoặc credentials trong image layers.
2. **Kiểm tra biến môi trường nhạy cảm**: Không có mật khẩu cứng trong Dockerfile hoặc image metadata. Toàn bộ cấu hình được nạp động từ Environment Variables lúc container khởi chạy.
3. **Kiểm tra Build Context**: Toàn bộ build context được lọc sạch sẽ qua `.dockerignore`.
4. **Kiểm tra User Permissions**: Backend container vận hành dưới tài khoản unprivileged `appuser`.
