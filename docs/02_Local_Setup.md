# HƯỚNG DẪN CÀI ĐẶT VÀ VẬN HÀNH MÔI TRƯỜNG LOCAL (LOCAL SETUP GUIDE)

---

## 1. YÊU CẦU MÔI TRƯỜNG TIÊN QUYẾT (PREREQUISITES)

Để triển khai và vận hành hệ thống **MyMiniCloud** trên máy tính cá nhân (Local Machine), cần chuẩn bị:
- **Hệ điều hành**: Windows 10/11 (hỗ trợ WSL2), Ubuntu Linux 22.04/24.04, hoặc macOS.
- **Docker Desktop**: Phiên bản 4.25 trở lên (khuyến nghị Docker Engine 24+ hoặc 26+).
- **Docker Compose**: Plugin v2 (hoặc `docker-compose` CLI v2.20+).
- **RAM**: Tối thiểu 8 GB RAM (khuyến nghị 16 GB để chạy đồng thời 10+ container mượt mà).
- **Dung lượng đĩa trống**: Tối thiểu 15 GB dung lượng ổ cứng.
- **Công cụ dòng lệnh**: PowerShell 7 / Windows Terminal hoặc Bash shell, Python 3.10+ (để chạy bộ kiểm thử tự động).

---

## 2. QUY TRÌNH THIẾT LẬP TỪNG BƯỚC (STEP-BY-STEP SETUP)

### Bước 1: Clone hoặc mở thư mục dự án
Đảm bảo bạn đang đứng tại thư mục gốc của dự án:
```powershell
cd D:\Cloud\MiniCloud
```

### Bước 2: Chuẩn bị tệp cấu hình biến môi trường `.env`
Hệ thống sử dụng cơ chế bảo mật tách biệt thông tin cấu hình khỏi mã nguồn:
```powershell
# Nếu chưa có .env, sao chép từ .env.example
Copy-Item .env.example .env
```
Nội dung file `.env` chứa các thông số:
```dotenv
COMPOSE_PROJECT_NAME=myminicloud
DOCKERHUB_USERNAME=cloudstudent
MARIADB_ROOT_PASSWORD=root
MARIADB_DATABASE=studentdb
MARIADB_USER=clouduser
MARIADB_PASSWORD=cloudpassword
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
```

### Bước 3: Khởi động toàn bộ hạ tầng bằng script tự động
Tại PowerShell, chạy:
```powershell
.\scripts\start.ps1
```
Script sẽ tự động:
1. Build các Docker Image tùy chỉnh (`myminicloud-web:v1.0` và `myminicloud-app:v1.0`).
2. Khởi tạo mạng cầu nối `cloud-net`.
3. Khởi tạo các Persistent Volumes (`mariadb_data`, `minio_data`, `grafana_data`).
4. Khởi động 10 container theo đúng thứ tự phụ thuộc (dependency tree).
5. Kích hoạt container provisioner tự động tạo bucket MinIO và nạp tài liệu mẫu.

---

## 3. KIỂM TRA TRẠNG THÁI CÁC CONTAINER

Sau khi khởi động, kiểm tra trạng thái hoạt động:
```powershell
docker compose ps
```
Bảng trạng thái mong đợi:
```text
NAME                                  IMAGE                                    STATUS
api-gateway-proxy-server              nginx:1.25-alpine                        Up (healthy/active)
application-backend-server            cloudstudent/myminicloud-app:v1.0        Up (healthy)
authentication-identity-server        quay.io/keycloak/keycloak:24.0.5          Up (healthy)
internal-dns-server                   internetsystemsconsortium/bind9:9.18      Up
monitoring-grafana-dashboard-server   grafana/grafana:10.4.2                   Up
monitoring-node-exporter-server       prom/node-exporter:v1.8.0                Up
monitoring-prometheus-server          prom/prometheus:v2.51.2                  Up
object-storage-server                 minio/minio:RELEASE.2024-05-10T01-41-38Z Up (healthy)
relational-database-server            mariadb:11.3                             Up (healthy)
web-frontend-server1                  cloudstudent/myminicloud-web:v1.0        Up (healthy)
web-frontend-server2                  cloudstudent/myminicloud-web:v1.0        Up (healthy)
```

---

## 4. QUẢN LÝ VÀ DỌN DẸP HỆ THỐNG

- **Xem logs thời gian thực**:
  ```powershell
  # Xem logs toàn bộ hệ thống
  docker compose logs -f

  # Xem logs của riêng một dịch vụ cụ thể
  docker compose logs -f application-backend-server
  docker compose logs -f authentication-identity-server
  ```

- **Tạm dừng hệ thống**:
  ```powershell
  .\scripts\stop.ps1
  # hoặc: docker compose stop
  ```

- **Khởi động lại một dịch vụ**:
  ```powershell
  docker compose restart api-gateway-proxy-server
  ```

- **Dọn dẹp và reset toàn bộ dữ liệu**:
  ```powershell
  .\scripts\clean.ps1
  # hoặc: docker compose down -v --remove-orphans
  ```

