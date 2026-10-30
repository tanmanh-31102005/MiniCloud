# KẾ HOẠCH VÀ HƯỚNG DẪN TRIỂN KHAI AWS EC2 (AWS DEPLOYMENT PLAN)

---

## 1. MỤC TIÊU VÀ NGUYÊN TẮC QUAN TRỌNG

> [!IMPORTANT]
> Theo thỏa thuận lộ trình, **Phase 7 (Triển khai lên AWS EC2)** và **Phase 8 (Báo cáo tổng kết)** sẽ được kích hoạt thực hiện sau khi toàn bộ hệ thống trên môi trường máy cục bộ (Local) đã được kiểm thử ổn định 100%.

Tài liệu này chuẩn bị sẵn kiến trúc, ước tính chi phí, cấu hình Security Group và toàn bộ kịch bản dòng lệnh triển khai để khi người dùng cấp quyền và cung cấp thông tin EC2, việc triển khai sẽ diễn ra nhanh chóng, chính xác và an toàn tuyệt đối.

---

## 2. CẤU HÌNH HẠ TẦNG AWS MỤC TIÊU DỰ KIẾN

- **AWS Region**: `ap-southeast-1` (Asia Pacific - Singapore) để có độ trễ mạng thấp nhất về Việt Nam.
- **Hệ điều hành**: `Ubuntu Server 24.04 LTS (Noble Numbat)` 64-bit (x86_64).
- **Loại Instance**: `t3.large` (2 vCPU, 8 GiB RAM).
  - *Lý do*: Hệ thống chạy đồng thời 10+ containers (Keycloak OIDC Java JVM, MariaDB, Prometheus, Grafana, MinIO, Nginx...), yêu cầu tối thiểu 4GB - 8GB RAM để tránh lỗi Out-Of-Memory (OOM-killer).
- **Lưu trữ (Storage)**: 40 GiB EBS Volume loại `gp3` (3000 IOPS, 125 MB/s).
- **Mô hình kiến trúc**: Triển khai đơn Node trên một EC2 chạy Docker Engine + Docker Compose.

---

## 3. BẢNG DỰ TOÁN CHI PHÍ (COST ESTIMATION)

| Dịch vụ AWS | Thông số cấu hình | Chi phí ước tính (ap-southeast-1) | Ghi chú |
|:---|:---|:---:|:---|
| **EC2 Instance (t3.large)** | On-Demand (2 vCPU, 8 GiB RAM) | ~ $0.104 USD / giờ (~ $2.5 / ngày) | Bật khi thực nghiệm và demo, tắt khi không sử dụng |
| **EBS Storage (gp3)** | 40 GiB Volume | ~ $0.096 USD / GiB / tháng (~ $3.8 / tháng) | Dữ liệu persistent |
| **Public IPv4 Address** | 1 địa chỉ In-use public IPv4 | ~ $0.005 USD / giờ (~ $0.12 / ngày) | Chính sách giá mới của AWS |
| **Data Transfer OUT** | Dưới 100 GB / tháng | Miễn phí (AWS Free Tier) | Phục vụ demo web và API |

*Khuyến nghị*: Sau khi hoàn tất kiểm thử và chụp ảnh minh chứng trên AWS, thực hiện lệnh `docker compose stop` và Stop EC2 instance trên AWS Console để tránh phát sinh chi phí ngoài ý muốn.

---

## 4. THIẾT KẾ SECURITY GROUP (FIREWALL RULES)

Tuân thủ nghiêm ngặt **Quy tắc bảo mật** của đồ án: Không mở trực tiếp các cổng nội bộ (Database 3306, Keycloak 8081, Prometheus 9090, Grafana 3000, Node Exporter 9100) ra toàn Internet. Chỉ Reverse Proxy Gateway (Port 80) được mở công khai:

| Loại lưu lượng | Port | Protocol | Nguồn (Source) | Mục đích |
|:---|:---:|:---:|:---:|:---|
| **SSH** | 22 | TCP | `My IP / IP Quản trị` | Quản trị từ xa và thiết lập SSH Tunneling |
| **HTTP (Gateway)** | 80 | TCP | `0.0.0.0/0` (Anywhere) | Điểm vào duy nhất cho người dùng truy cập Website & API |
| **HTTPS (TLS)** | 443 | TCP | `0.0.0.0/0` (Nếu cấu hình TLS) | Bảo mật mã hóa đường truyền |

*Quản trị các dịch vụ nội bộ trên AWS*: Sử dụng kỹ thuật **SSH Port Forwarding (SSH Tunnel)** từ máy Local:
```powershell
# Mở SSH Tunnel để truy cập Grafana và MinIO trên AWS an toàn tuyệt đối qua cổng nội bộ:
ssh -i "your-key.pem" -L 3000:localhost:3000 -L 9001:localhost:9001 ubuntu@<EC2-PUBLIC-IP>
# Sau đó mở trình duyệt Local: http://localhost:3000 và http://localhost:9001
```

---

## 5. KỊCH BẢN TRIỂN KHAI TRÊN UBUNTU EC2 (DEPLOYMENT SCRIPT)

Khi tiến hành Phase 7, các bước trên máy chủ EC2 sẽ được thực hiện như sau:

```bash
# 1. Cập nhật hệ thống
sudo apt update && sudo apt upgrade -y

# 2. Cài đặt Docker Engine & Docker Compose Plugin
sudo apt install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker ubuntu

# 3. Clone mã nguồn hoặc chuyển thư mục dự án lên EC2
# (rsync hoặc git clone)
cd MyMiniCloud

# 4. Chuẩn bị file .env cấu hình môi trường Production
cp .env.example .env
nano .env

# 5. Khởi chạy toàn bộ hệ thống
docker compose up -d

# 6. Kiểm tra trạng thái
docker compose ps
curl http://localhost/
curl http://localhost/student
```

