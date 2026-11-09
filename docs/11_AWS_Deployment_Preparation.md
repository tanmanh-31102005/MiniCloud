# HƯỚNG DẪN CHUẨN BỊ TRIỂN KHAI AWS EC2
## AWS EC2 DEPLOYMENT PREPARATION GUIDE — MYMINICLOUD

---

## 1. MỤC TIÊU VÀ PHẠM VI

Tài liệu này đóng vai trò cẩm nang kỹ thuật hướng dẫn chuẩn bị môi trường, cấu hình an ninh và quy trình chuyển giao toàn diện hệ thống **MyMiniCloud** từ máy phát triển Local lên đám mây công cộng **Amazon Web Services (AWS EC2)** sử dụng Docker Compose và các Docker Images đã xuất bản lên Docker Hub.

---

## 2. KIẾN TRÚC TRIỂN KHAI TRÊN CLOUD

```
                   INTERNET / USERS
                          │
                          │ Port 80 (HTTP)
                          ▼
            ┌─────────────────────────────┐
            │   AWS Security Group        │
            │   Port 80: 0.0.0.0/0        │
            │   Port 22: Your IP only     │
            └─────────────┬───────────────┘
                          │
                          ▼
      ┌───────────────────────────────────────────┐
      │  AWS EC2 Instance (Ubuntu 24.04 LTS)       │
      │                                           │
      │   ┌───────────────────────────────────┐   │
      │   │ API Gateway (Reverse Proxy / LB)  │   │
      │   │ Port 80:80                        │   │
      │   └───────────────┬───────────────────┘   │
      │                   │                       │
      │  ┌────────────────┴────────────────┐      │
      │  │ Docker Isolated Network:        │      │
      │  │        cloud-net                │      │
      │  │                                 │      │
      │  │  ├── Web Server Node 1          │      │
      │  │  ├── Web Server Node 2          │      │
      │  │  ├── Flask Backend API          │      │
      │  │  ├── MariaDB 11.3 (Volume)      │      │
      │  │  ├── Keycloak OIDC (Volume)     │      │
      │  │  ├── MinIO S3 (Volume)          │      │
      │  │  ├── BIND9 DNS Server           │      │
      │  │  ├── Prometheus (Volume)        │      │
      │  │  ├── Grafana Dashboard (Volume) │      │
      │  │  └── Node Exporter              │      │
      │  └─────────────────────────────────┘      │
      └───────────────────────────────────────────┘
```

---

## 3. THÔNG SỐ VÀ CẤU HÌNH PHẦN CỨNG ĐỀ XUẤT

| Thành phần | Cấu hình tối thiểu (Lab) | Cấu hình tối ưu (Recommended) | Giải thích kỹ thuật |
|:---|:---|:---|:---|
| **Instance Type** | **t3.medium** | **t3.large** | Keycloak chạy Java Quarkus JVM kết hợp MariaDB và Prometheus cần tối thiểu 3.5 GiB RAM. Không dùng `t3.micro` (1 GB) hoặc `t3.small` (2 GB). |
| **vCPU** | 2 vCPU | 2 vCPU | Đảm bảo đa luồng xử lý đồng thời giữa API, Database và Giám sát. |
| **RAM** | 4.0 GiB (+ 2 GiB Swap) | 8.0 GiB | Đủ bộ nhớ an toàn, tránh tình trạng kích hoạt Linux OOM Killer. |
| **Lưu trữ (EBS)**| 20 GiB gp3 | 30 GiB gp3 | Lưu trữ hệ điều hành, các Docker Images và persistent volumes. |
| **Hệ điều hành** | Ubuntu Server 24.04 LTS (x86_64) | Ubuntu Server 24.04 LTS (x86_64) | Hệ điều hành tiêu chuẩn cho môi trường Cloud hiện đại. |

---

## 4. QUY HOẠCH AN NINH MẠNG (AWS SECURITY GROUP)

Đặt tên Security Group: `myminicloud-production-sg`

### 4.1. Inbound Rules

| Protocol | Port | Source | Mục đích | Ghi chú bảo mật |
|:---:|:---:|:---:|:---|:---|
| **SSH (TCP)** | `22` | `My IP` | Quản trị máy chủ từ xa | **Không mở 0.0.0.0/0** để chống tấn công brute-force. |
| **HTTP (TCP)** | `80` | `0.0.0.0/0` | Cổng công khai duy nhất vào API Gateway | Định tuyến toàn bộ lưu lượng web, API và xác thực. |
| **HTTPS (TCP)** | `443`| `0.0.0.0/0` | Tùy chọn (khi gắn domain và SSL/TLS) | Để sẵn cho Let's Encrypt / Certbot. |

### 4.2. Quản trị dịch vụ nội bộ qua SSH Port Forwarding Tunneling & 127.0.0.1 Loopback Binding

Trong file `docker-compose.aws.yml`, các cổng dịch vụ nội bộ được cấu hình tường minh gắn vào địa chỉ loopback cục bộ `127.0.0.1` (thay vì mở `0.0.0.0` hay dùng `expose:`):
- `127.0.0.1:8080:80` & `127.0.0.1:8082:80` (Web 1 & 2)
- `127.0.0.1:8085:8081` (Flask Backend API)
- `127.0.0.1:3306:3306` (MariaDB)
- `127.0.0.1:8081:8080` (Keycloak)
- `127.0.0.1:9000:9000` & `127.0.0.1:9001:9001` (MinIO S3 & Console)
- `127.0.0.1:9090:9090` (Prometheus)
- `127.0.0.1:3000:3000` (Grafana)

> [!IMPORTANT]
> **Tại sao bind vào `127.0.0.1` là an toàn tuyệt đối 100% trên Cloud?**
> 1. Khi bind `127.0.0.1:<PORT>`, Linux Kernel trên EC2 chỉ chấp nhận gói tin từ adapter nội bộ loopback của chính máy chủ. Toàn bộ traffic đến từ card mạng công khai `eth0` đều bị từ chối ở tầng OS.
> 2. AWS Security Group chặn toàn bộ traffic ngoài cổng 80 và 22, tạo thêm lớp bảo vệ vật lý vòng ngoài.
> 3. Cơ chế này cho phép SSH Port Forwarding (`ssh -L ...`) từ laptop và script kiểm thử `python3 tests/integration_test.py` trên EC2 chạy trơn tru 10/10 PASS mà không bị lỗi `Connection Refused` như khi dùng `expose:`.

Để truy cập các bảng điều khiển nội bộ từ máy tính cá nhân, sử dụng lệnh SSH Tunnel an toàn:

```bash
# Mở đường hầm bảo mật cho MinIO Console (9001) và Grafana (3000)
ssh -i "your-key.pem" -L 9001:localhost:9001 -L 3000:localhost:3000 -L 9090:localhost:9090 ubuntu@<EC2_PUBLIC_IP>
```
Sau đó truy cập trên máy cá nhân:
- MinIO: [http://localhost:9001](http://localhost:9001)
- Grafana: [http://localhost:3000](http://localhost:3000)
- Prometheus: [http://localhost:9090](http://localhost:9090)

---

## 5. QUY TRÌNH THIẾT LẬP MÁY CHỦ EC2 (STEP-BY-STEP PROVISIONING)

### Bước 1: Khởi tạo máy ảo EC2 và kết nối SSH
```bash
ssh -i "your-key.pem" ubuntu@<EC2_PUBLIC_IP>
```

### Bước 2: Cập nhật hệ điều hành và kích hoạt Swapfile
```bash
sudo apt update && sudo apt upgrade -y

# Thiết lập Swapfile 2GB phòng ngừa tràn RAM
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### Bước 3: Cài đặt Docker Engine và Docker Compose Plugin
```bash
# Cài đặt các gói hỗ trợ
sudo apt install -y ca-certificates curl gnupg

# Thêm khóa GPG chính thức của Docker
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Thêm repository của Docker vào APT
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Cài đặt Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Phân quyền cho user ubuntu chạy docker không cần sudo
sudo usermod -aG docker ubuntu
newgrp docker
```

### Bước 4: Sao chép dự án hoặc Clone Git về máy chủ
```bash
git clone https://github.com/<YOUR_GITHUB_USER>/MyMiniCloud.git
cd MyMiniCloud
```

### Bước 5: Cấu hình biến môi trường Production
```bash
# Tạo file .env từ file mẫu production
cp .env.production.example .env

# Chỉnh sửa file .env với thông tin thực tế của bạn
nano .env
# - Cập nhật DOCKERHUB_USERNAME
# - Cập nhật PUBLIC_IP=<EC2_PUBLIC_IP>
# - Thay đổi các mật khẩu mặc định thành chuỗi mạnh ngẫu nhiên
```

### Bước 6: Khởi chạy cụm dịch vụ bằng Docker Compose AWS
```bash
# Kéo các Docker Images từ Docker Hub
docker compose -f docker-compose.aws.yml pull

# Khởi chạy toàn bộ hệ thống
docker compose -f docker-compose.aws.yml up -d

# Kiểm tra trạng thái toàn bộ containers
docker compose -f docker-compose.aws.yml ps
```

---

## 6. KỊCH BẢN KIỂM TRA HỆ THỐNG SAU TRIỂN KHAI (POST-DEPLOYMENT SMOKE TEST)

Thực hiện kiểm tra tại máy tính cá nhân qua trình duyệt hoặc cURL:

1. **Trang chủ & Blog**: Mở `http://<EC2_PUBLIC_IP>/` và `http://<EC2_PUBLIC_IP>/blog/index.html`.
2. **Cân bằng tải Round Robin**: Gửi 10 request và kiểm tra header phản hồi:
   ```bash
   curl -i http://<EC2_PUBLIC_IP>/
   ```
3. **API Sinh viên (JSON)**:
   ```bash
   curl http://<EC2_PUBLIC_IP>/student
   ```
4. **API Cơ sở dữ liệu MariaDB (CRUD)**:
   ```bash
   curl http://<EC2_PUBLIC_IP>/api/students-db
   ```
5. **Xác thực Token Keycloak JWT**:
   ```bash
   curl -X POST http://<EC2_PUBLIC_IP>/auth/realms/MyMiniCloud/protocol/openid-connect/token \
     -d "client_id=flask-app" -d "username=sv01" -d "password=password123" -d "grant_type=password"
   ```

---

## 7. QUY TRÌNH SAO LƯU VÀ PHỤC HỒI DỮ LIỆU (BACKUP & DISASTER RECOVERY)

### 7.1. Sao lưu tự động định kỳ vào tệp nén
```bash
mkdir -p ~/backups
docker run --rm -v myminicloud_mariadb_data:/source -v ~/backups:/backup alpine tar -czf /backup/mariadb_backup_$(date +%Y%m%d_%H%M%S).tar.gz -C /source .
docker run --rm -v myminicloud_minio_data:/source -v ~/backups:/backup alpine tar -czf /backup/minio_backup_$(date +%Y%m%d_%H%M%S).tar.gz -C /source .
```

### 7.2. Phục hồi khi có sự cố
```bash
docker compose -f docker-compose.aws.yml down
docker run --rm -v myminicloud_mariadb_data:/target -v ~/backups:/backup alpine sh -c "cd /target && rm -rf * && tar -xzf /backup/<FILE_BACKUP>.tar.gz"
docker compose -f docker-compose.aws.yml up -d
```

