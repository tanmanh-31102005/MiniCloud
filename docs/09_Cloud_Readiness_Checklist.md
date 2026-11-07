# DANH SÁCH KIỂM TRA ĐIỀU KIỆN SẴN SÀNG TRIỂN KHAI CLOUD
## CLOUD READINESS CHECKLIST — AWS EC2 & DOCKER HUB DEPLOYMENT

---

## 1. MỤC TIÊU VÀ PHẠM VI TÀI LIỆU

Tài liệu này định nghĩa toàn bộ tiêu chuẩn kỹ thuật, danh mục kiểm tra điều kiện (Readiness Checklist), các bước chuẩn bị hạ tầng, an ninh mạng, biến môi trường và phương án quản trị rủi ro trước khi chuyển đổi hệ thống **MyMiniCloud** từ môi trường phát triển nội bộ (**Local Development Environment**) lên môi trường đám mây công cộng (**AWS EC2 Production Environment**).

---

## 2. BẢNG KIỂM TRA ĐIỀU KIỆN TIÊN QUYẾT (PREREQUISITE CHECKLIST)

| STT | Hạng mục kiểm tra | Tiêu chuẩn đánh giá | Trạng thái Local | Đạt điều kiện Cloud |
|:---:|:---|:---|:---:|:---:|
| 1 | **Kiểm thử tích hợp (Integration Tests)** | 10/10 kịch bản test tự động đạt kết quả PASS | **10/10 PASS** | ✅ SẴN SÀNG |
| 2 | **Cú pháp Docker Compose** | `docker compose config` không phát sinh cảnh báo lỗi | **HỢP LỆ** | ✅ SẴN SÀNG |
| 3 | **Đường dẫn thư mục trong Compose** | Toàn bộ volume mounts dùng đường dẫn tương đối POSIX (`./gateway`, `./backend`) | **TƯƠNG THÍCH LINUX** | ✅ SẴN SÀNG |
| 4 | **Tính bất biến của Docker Image** | Các image tự build (`myminicloud-web`, `myminicloud-app`) độc lập với host | **ĐÃ KIỂM CHỨNG** | ✅ SẴN SÀNG |
| 5 | **Cơ sở dữ liệu MariaDB CRUD** | Đầy đủ 4 thao tác GET, POST, PUT, DELETE có parameterized queries | **HOÀN THIỆN** | ✅ SẴN SÀNG |
| 6 | **Xác thực Keycloak OIDC JWT** | Kiểm tra chữ ký mật mã RS256 qua JWKS endpoint | **HOÀN THIỆN** | ✅ SẴN SÀNG |
| 7 | **MinIO Object Storage & Checksum** | Bucket tồn tại, SHA-256 upload/download khớp 100% | **HOÀN THIỆN** | ✅ SẴN SÀNG |
| 8 | **Hệ thống Giám sát Metrics** | 4 targets Prometheus UP, Grafana Dashboard nạp sẵn | **HOÀN THIỆN** | ✅ SẴN SÀNG |
| 9 | **Load Balancing & Gateway** | Gateway phân phối Round Robin 50/50 giữa 2 Web server | **HOÀN THIỆN** | ✅ SẴN SÀNG |
| 10 | **Tách biệt Secrets & Config** | Không hardcode mật khẩu, có `.env.example`, `.env` được gitignore | **AN TOÀN** | ✅ SẴN SÀNG |

---

## 3. CẤU HÌNH PHẦN CỨNG VÀ TÀI NGUYÊN TỐI THIỂU CHO AWS EC2

Hệ thống MyMiniCloud vận hành 10 container đồng thời, trong đó **Keycloak** (chạy máy ảo Java JVM Quarkus) và **MariaDB + Prometheus** đòi hỏi dung lượng bộ nhớ RAM tối thiểu để tránh tình trạng Out-Of-Memory (OOM Killer).

### 3.1. Khuyến nghị cấu hình Instance Type

| Thông số | Cấu hình tối thiểu (Minimum) | Cấu hình đề xuất (Recommended) | Ghi chú kỹ thuật |
|:---|:---|:---|:---|
| **EC2 Instance Type** | **t3.medium** (hoặc t3a.medium) | **t3.large** | `t3.micro` (1 GB) hoặc `t3.small` (2 GB) sẽ bị crash Keycloak JVM do thiếu RAM. |
| **vCPU** | 2 vCPU | 2 vCPU | Đảm bảo xử lý song song Node Exporter, Flask và BIND9. |
| **RAM** | **4.0 GiB** | **8.0 GiB** | Cần kích hoạt thêm 2-4 GB Swapfile trên ổ đĩa SSD. |
| **Dung lượng ổ cứng (EBS)** | 20 GiB General Purpose SSD (gp3) | 30 GiB gp3 | Dung lượng chứa các Docker Images (~3-4 GB) và Persistent Volumes. |
| **Hệ điều hành (AMI)** | **Ubuntu Server 24.04 LTS (x86_64)** | Ubuntu Server 24.04 LTS (x86_64) | Tương thích hoàn toàn với kiến trúc Docker Engine Linux. |
| **Kiến trúc CPU** | `x86_64` (amd64) | `x86_64` (amd64) | Đồng nhất với kiến trúc image build trên máy tính hiện tại. |

### 3.2. Cấu hình Swap Memory trên EC2 Ubuntu (Bắt buộc cho t3.medium)

```bash
# Tạo và kích hoạt Swapfile 2GB để phòng chống OOM
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

## 4. QUY HOẠCH AN NINH MẠNG VÀ CẤU HÌNH AWS SECURITY GROUP

Nguyên tắc bảo mật cốt lõi: **Chỉ mở cổng công khai duy nhất đối với các dịch vụ cần giao tiếp với người dùng cuối**. Toàn bộ các dịch vụ cơ sở dữ liệu, quản trị lưu trữ và giám sát nội bộ phải được cô lập bên trong Docker Network hoặc chỉ truy cập qua kênh mã hóa SSH Tunnel.

### 4.1. Cấu hình Inbound Rules (Security Group: `myminicloud-sg`)

| Type | Protocol | Port Range | Source | Mục đích sử dụng | Mức độ rủi ro & Biện pháp |
|:---|:---:|:---:|:---|:---|:---|
| **SSH** | TCP | `22` | `My IP` (hoặc IP cố định) | Quản trị từ xa máy chủ EC2 | **CRITICAL**: Không mở `0.0.0.0/0` để chống tấn công brute-force SSH. |
| **HTTP** | TCP | `80` | `0.0.0.0/0` | Điểm truy cập duy nhất vào API Gateway | **PUBLIC**: Cổng public duy nhất, định tuyến đến Web, API và Keycloak qua Gateway. |
| **HTTPS** | TCP | `443` | `0.0.0.0/0` | SSL/TLS (Tùy chọn mở rộng khi gắn domain) | Chuẩn bị sẵn khi cấu hình Let's Encrypt / Certbot. |

### 4.2. Các cổng BẮT BUỘC KHÔNG MỞ CÔNG KHAI ra Internet

| Port | Dịch vụ | Nguy cơ khi mở công khai | Phương án truy cập an toàn trên EC2 |
|:---:|:---|:---|:---|
| `3306` | MariaDB | Lộ dữ liệu sinh viên, nguy cơ tấn công brute-force CSDL | Chỉ truy cập nội bộ trong Docker Network `cloud-net`. Nếu cần debug, dùng SSH Tunnel: `ssh -i key.pem -L 3306:localhost:3306 ubuntu@<EC2_IP>` |
| `9000` / `9001` | MinIO API & Console | Rò rỉ tài liệu và đối tượng lưu trữ S3 | Truy cập qua SSH Tunnel: `ssh -i key.pem -L 9001:localhost:9001 ubuntu@<EC2_IP>` |
| `9090` | Prometheus API | Lộ cấu trúc hạ tầng và các thông số nội bộ | Chỉ truy cập qua SSH Tunnel: `ssh -i key.pem -L 9090:localhost:9090 ubuntu@<EC2_IP>` |
| `3000` | Grafana Dashboard | Truy cập trái phép vào đồ thị quan trắc hệ thống | Có thể reverse proxy qua Gateway hoặc dùng SSH Tunnel: `ssh -i key.pem -L 3000:localhost:3000 ubuntu@<EC2_IP>` |
| `8080` / `8082` | Web Servers 1 & 2 | Bỏ qua cơ chế cân bằng tải và bảo vệ của Gateway | Đóng cổng host, chỉ giao tiếp nội bộ với Gateway. |
| `8085` / `8081` | Flask & Keycloak | Bỏ qua xác thực và proxy của Gateway | Định tuyến toàn bộ qua Gateway cổng 80. |

---

## 5. MA TRẬN CHUYỂN ĐỔI BIẾN MÔI TRƯỜNG (LOCAL VS. PRODUCTION AWS)

File `.env` trên môi trường AWS EC2 cần được điều chỉnh chính xác theo địa chỉ IP công khai hoặc DNS của EC2:

| Biến môi trường | Giá trị tại Local | Giá trị trên AWS EC2 Production | Lý do thay đổi |
|:---|:---|:---|:---|
| `SERVER_HOST` / `PUBLIC_IP` | `localhost` hoặc `127.0.0.1` | `<EC2_PUBLIC_IP>` (hoặc Elastic IP) | Trình duyệt client cần gọi token endpoint và frontend qua IP public thật. |
| `KEYCLOAK_URL` | `http://localhost/auth` | `http://<EC2_PUBLIC_IP>/auth` | Phục vụ OIDC Discovery và cấp phát token cho người dùng ngoài Internet. |
| `KEYCLOAK_ADMIN_PASSWORD` | `admin` | `<CHUỖI_NGẪU_NHIÊN_MẠNH>` | Ngăn chặn xâm nhập trái phép tài khoản Quản trị viên IAM. |
| `MARIADB_ROOT_PASSWORD` | `root` | `<CHUỖI_NGẪU_NHIÊN_MẠNH>` | Bảo mật CSDL MariaDB gốc. |
| `MARIADB_PASSWORD` | `studentdb` | `<CHUỖI_NGẪU_NHIÊN_MẠNH>` | Bảo vệ tài khoản ứng dụng Backend kết nối CSDL. |
| `MINIO_ROOT_PASSWORD` | `minioadmin` | `<CHUỖI_NGẪU_NHIÊN_MẠNH>` | Bảo mật cụm lưu trữ đối tượng MinIO. |
| `GRAFANA_ADMIN_PASSWORD` | `admin` | `<CHUỖI_NGẪU_NHIÊN_MẠNH>` | Bảo vệ tài khoản đăng nhập xem Dashboard Grafana. |
| `APP_IMAGE` | `cloudstudent/myminicloud-app:v1.0` | `<DOCKERHUB_USERNAME>/myminicloud-app:v1.0` | Kéo image đã được publish từ Docker Hub registry về máy chủ EC2. |
| `WEB_IMAGE` | `cloudstudent/myminicloud-web:v1.0` | `<DOCKERHUB_USERNAME>/myminicloud-web:v1.0` | Kéo image đã được publish từ Docker Hub registry về máy chủ EC2. |

---

## 6. QUY TRÌNH BACKUP DỮ LIỆU PERSISTENT VOLUMES

Trước khi triển khai lên Cloud hoặc trước khi cập nhật mã nguồn, việc sao lưu toàn bộ dữ liệu trạng thái (Stateful Data) là bắt buộc.

### 6.1. Script sao lưu toàn bộ Docker Volumes trên Local

```powershell
# Tạo thư mục chứa bản sao lưu
New-Item -ItemType Directory -Force -Path .\backups

# 1. Sao lưu MariaDB Volume
docker run --rm -v minicloud_mariadb_data:/source -v ${PWD}/backups:/backup alpine tar -czf /backup/mariadb_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').tar.gz -C /source .

# 2. Sao lưu MinIO Data Volume
docker run --rm -v minicloud_minio_data:/source -v ${PWD}/backups:/backup alpine tar -czf /backup/minio_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').tar.gz -C /source .

# 3. Sao lưu Grafana Storage
docker run --rm -v minicloud_grafana_data:/source -v ${PWD}/backups:/backup alpine tar -czf /backup/grafana_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').tar.gz -C /source .
```

### 6.2. Quy trình phục hồi dữ liệu từ bản sao lưu (Restore Procedure)

```powershell
# Phục hồi MariaDB Volume từ bản backup tar.gz
docker volume create minicloud_mariadb_data
docker run --rm -v minicloud_mariadb_data:/target -v ${PWD}/backups:/backup alpine sh -c "cd /target && tar -xzf /backup/<TÊN_FILE_BACKUP>.tar.gz"
```

---

## 7. QUY TRÌNH ROLLBACK (KẾ HOẠCH HỒI PHỤC KHI GẶP SỰ CỐ TRÊN CLOUD)

Nếu trong quá trình triển khai trên AWS EC2 phát sinh lỗi nghiêm trọng (ví dụ: container crashloop, cấu hình mạng lỗi, dữ liệu hỏng), thực hiện quy trình Rollback gồm 4 bước:

1. **Bước 1: Hạ cụm dịch vụ đang lỗi**
   ```bash
   docker compose down
   ```
2. **Bước 2: Khôi phục mã nguồn và cấu hình về commit ổn định gần nhất**
   ```bash
   git fetch origin
   git reset --hard <STABLE_COMMIT_HASH_OR_TAG>
   ```
3. **Bước 3: Khôi phục Persistent Volumes từ bản sao lưu gần nhất**
   - Xóa volume lỗi: `docker volume rm minicloud_mariadb_data minicloud_minio_data`
   - Bung nén tệp sao lưu tar.gz vào volume mới theo mục 6.2.
4. **Bước 4: Khởi động lại hệ thống với image phiên bản ổn định**
   ```bash
   docker compose pull
   docker compose up -d
   docker compose ps
   ```

---

## 8. CHECKLIST KIỂM THỬ XÁC NHẬN SAU KHI DEPLOY LÊN AWS EC2 (SMOKE TEST)

Sau khi chạy lệnh `docker compose up -d` trên máy chủ AWS EC2 Ubuntu, kỹ sư triển khai phải thực hiện tuần tự danh sách kiểm tra sau:

- [ ] **1. Kiểm tra trạng thái toàn bộ containers:**
  - Lệnh: `docker compose ps`
  - Tiêu chuẩn: 10/10 containers đều có trạng thái `Up` (hoặc `healthy`), provisioner ở trạng thái `Exited (0)`.
- [ ] **2. Kiểm tra truy cập Gateway cổng 80:**
  - Truy cập: `http://<EC2_PUBLIC_IP>/`
  - Tiêu chuẩn: Tải trang chủ MyMiniCloud thành công, mã HTTP 200.
- [ ] **3. Kiểm tra Round Robin Load Balancing:**
  - Gửi 10 request: `curl -i http://<EC2_PUBLIC_IP>/`
  - Tiêu chuẩn: Header `X-Served-By` luân phiên xen kẽ giữa `web-node-1` và `web-node-2`.
- [ ] **4. Kiểm tra trang Blog:**
  - Truy cập: `http://<EC2_PUBLIC_IP>/blog/index.html`
  - Tiêu chuẩn: Các liên kết bài viết 1, 2, 3 hiển thị đầy đủ hình ảnh, CSS và nội dung.
- [ ] **5. Kiểm tra JSON API:**
  - Truy cập: `http://<EC2_PUBLIC_IP>/student`
  - Tiêu chuẩn: Trả về danh sách 5 sinh viên mẫu với HTTP 200.
- [ ] **6. Kiểm tra MariaDB CRUD qua Gateway:**
  - Lệnh: `curl -X GET http://<EC2_PUBLIC_IP>/api/students-db`
  - Tiêu chuẩn: Trả về danh sách sinh viên từ CSDL MariaDB với HTTP 200.
- [ ] **7. Kiểm tra xác thực Keycloak:**
  - Lấy JWT token:
    ```bash
    curl -X POST http://<EC2_PUBLIC_IP>/auth/realms/MyMiniCloud/protocol/openid-connect/token \
      -d "client_id=flask-app" -d "username=sv01" -d "password=password" -d "grant_type=password"
    ```
  - Gọi API bảo vệ bằng token vừa lấy:
    ```bash
    curl -H "Authorization: Bearer <TOKEN>" http://<EC2_PUBLIC_IP>/api/protected
    ```
  - Tiêu chuẩn: Trả về thông điệp chào mừng `sv01` với HTTP 200.
- [ ] **8. Kiểm tra phân giải DNS nội bộ BIND9:**
  - Lệnh: `docker exec internal-dns-server dig @127.0.0.1 web-frontend-server.cloud.local +short`
  - Tiêu chuẩn: Trả về `10.10.10.10`.
- [ ] **9. Kiểm tra Prometheus Scrape Targets:**
  - Mở SSH Tunnel: `ssh -i key.pem -L 9090:localhost:9090 ubuntu@<EC2_PUBLIC_IP>`
  - Mở trình duyệt máy tính: `http://localhost:9090/targets`
  - Tiêu chuẩn: Toàn bộ 4 targets đều có trạng thái xanh **UP**.
- [ ] **10. Kiểm tra Grafana Dashboard:**
  - Mở SSH Tunnel: `ssh -i key.pem -L 3000:localhost:3000 ubuntu@<EC2_PUBLIC_IP>`
  - Mở trình duyệt: `http://localhost:3000`
  - Tiêu chuẩn: Dashboard `System Health - MyMiniCloud` hiển thị các chỉ số CPU, Memory và Network thời gian thực.

