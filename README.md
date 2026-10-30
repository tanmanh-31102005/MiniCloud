# MyMiniCloud — Cloud Infrastructure Simulation Platform

Dự án đồ án học phần **Cloud Computing**: Xây dựng mô phỏng hạ tầng Điện toán Đám mây (Cloud Infrastructure) thu nhỏ bằng **Docker**, **Docker Compose** và kiến trúc mạng cô lập `cloud-net`.

---

## 1. TỔNG QUAN KIẾN TRÚC

Hệ thống triển khai 9 vai trò dịch vụ cốt lõi, mô phỏng các dịch vụ thực tế của các nhà cung cấp Cloud (AWS, GCP, Azure):

1. **Web Frontend Server (Nginx)**: 2 Node (`web-frontend-server1` & `web-frontend-server2`) phục vụ website tĩnh và 3 bài viết Blog kỹ thuật.
2. **Application Backend Server (Flask REST API)**: Cung cấp API `/student` (JSON 5 sinh viên), `/api/students-db` (kết nối MariaDB), `/secure` (xác thực Keycloak OIDC JWT) và xuất Prometheus metrics tại `/metrics`.
3. **Relational Database Server (MariaDB 11.3)**: Quản lý CSDL `studentdb` với bảng `students`, lưu trữ bền vững qua Docker Volume `mariadb_data`.
4. **Authentication & Identity Server (Keycloak 24.0)**: Quản lý định danh tập trung (IAM), cấp phát token OIDC qua Realm `MyMiniCloud`.
5. **Object Storage Server (MinIO S3)**: Lưu trữ tệp tin phi cấu trúc với 2 bucket tự động tạo: `profile-pics` (ảnh avatar) và `documents` (PDF).
6. **Internal DNS Server (BIND9 9.18)**: Phân giải tên miền nội bộ cho private zone `cloud.local`.
7. **Monitoring Metrics Server (Prometheus 2.51)**: Định kỳ thu thập số liệu từ Node Exporter, Flask Backend và Web Server.
8. **Host Resource Collector (Node Exporter 1.8)**: Cung cấp số liệu CPU, RAM, Network của hệ thống cho Prometheus.
9. **Visualization Dashboard Server (Grafana 10.4)**: Tự động kết nối Prometheus và nạp Dashboard *System Health* hiển thị 3 biểu đồ (CPU, RAM, Network).
10. **API Gateway / Reverse Proxy & Load Balancer (Nginx)**: Điểm tiếp nhận duy nhất tại cổng `80`, định tuyến linh hoạt và cân bằng tải Round Robin giữa 2 Web Node.

---

## 2. BẢNG DANH MỤC CỔNG DỊCH VỤ (PORT MAPPING)

| STT | Dịch vụ (Service) | Container Name | Cổng Host (Exposed) | Cổng Nội bộ Container | Chức năng chính |
|:---:|:---|:---|:---:|:---:|:---|
| 1 | **API Gateway (Nginx)** | `api-gateway-proxy-server` | **80** | 80 | Điểm vào chính, Reverse Proxy, Round Robin |
| 2 | **Web Frontend 1** | `web-frontend-server1` | **8080** | 80 | Web tĩnh, Trang chủ & Blog 1, 2, 3 |
| 3 | **Web Frontend 2** | `web-frontend-server2` | **8082** | 80 | Web Node 2 phục vụ Load Balancing |
| 4 | **Flask Backend API** | `application-backend-server` | **8085** | 8081 | REST API, MariaDB ORM, JWT Verification |
| 5 | **MariaDB Database** | `relational-database-server` | **3306** | 3306 | CSDL `studentdb` & `minicloud` |
| 6 | **Keycloak IAM** | `authentication-identity-server` | **8081** | 8080 | OIDC/OAuth2 Provider, Admin Console |
| 7 | **MinIO S3 API** | `object-storage-server` | **9000** | 9000 | S3 Object Storage API |
| 8 | **MinIO S3 Console** | `object-storage-server` | **9001** | 9001 | Giao diện quản trị Object Storage |
| 9 | **Internal BIND9 DNS** | `internal-dns-server` | **1053/udp** | 53 | Phân giải tên miền `cloud.local` |
| 10 | **Node Exporter** | `monitoring-node-exporter-server` | **9100** | 9100 | Số liệu phần cứng máy chủ |
| 11 | **Prometheus Server** | `monitoring-prometheus-server` | **9090** | 9090 | Thu thập và lưu trữ Time-series Metrics |
| 12 | **Grafana Dashboard** | `monitoring-grafana-dashboard-server` | **3000** | 3000 | Trực quan hóa biểu đồ giám sát |

---

## 3. CẤU TRÚC THƯ MỤC DỰ ÁN

```text
MyMiniCloud/
├── docker-compose.yml          # Định nghĩa toàn bộ cụm dịch vụ và mạng cloud-net
├── .env                        # Biến môi trường cục bộ (tài khoản, mật khẩu)
├── .env.example                # File mẫu biến môi trường
├── .gitignore                  # Bỏ qua file nhạy cảm và tệp build
├── README.md                   # Hướng dẫn chi tiết
│
├── frontend/                   # Mã nguồn Web Frontend Server (Nginx)
│   ├── Dockerfile
│   ├── nginx.conf
│   └── html/
│       ├── index.html          # Trang chủ giới thiệu MyMiniCloud
│       └── blog/
│           ├── index.html      # Trang danh mục Blog
│           ├── blog1.html      # Bài 1: Docker & Containerization
│           ├── blog2.html      # Bài 2: Microservices & API Gateway
│           └── blog3.html      # Bài 3: Prometheus & Grafana
│
├── backend/                    # Mã nguồn Application Backend Server (Flask)
│   ├── Dockerfile
│   ├── app.py                  # REST API, JWT RS256 Verification, Prometheus Metrics
│   ├── requirements.txt
│   └── data/
│       └── students.json       # Danh sách 5 sinh viên mẫu
│
├── database/                   # Khởi tạo MariaDB
│   └── init/
│       └── 01_init.sql         # Script tạo CSDL studentdb và bảng students
│
├── keycloak/                   # Cấu hình Identity Provider
│   └── import/
│       └── myminicloud-realm.json # Realm MyMiniCloud, Client flask-app, User sv01/sv02
│
├── minio/                      # Object Storage S3
│   ├── scripts/
│   │   └── init-minio.sh       # Script tạo bucket profile-pics và documents
│   └── data_sample/            # File mẫu avatar.jpg và report.pdf
│
├── dns/                        # BIND9 Internal DNS Server
│   ├── named.conf.options
│   ├── named.conf.local
│   └── zones/
│       └── db.cloud.local      # Zone file phân giải domain nội bộ
│
├── monitoring/                 # Hệ thống Observability
│   ├── prometheus/
│   │   └── prometheus.yml      # Cấu hình Scrape Targets
│   └── grafana/
│       ├── provisioning/       # Auto-provisioning Data Source & Dashboards
│       └── dashboards/
│           └── system-health.json # Dashboard CPU, RAM, Network tự động nạp
│
├── gateway/                    # API Gateway & Reverse Proxy
│   └── nginx.conf              # Cấu hình định tuyến và Round Robin Load Balancing
│
├── scripts/                    # Scripts quản lý và kiểm thử (PowerShell)
│   ├── start.ps1               # Khởi động toàn bộ hệ thống
│   ├── stop.ps1                # Dừng hệ thống
│   ├── clean.ps1               # Dọn dẹp container và volume
│   └── test.ps1                # Chạy kiểm thử tự động
│
├── tests/
│   └── integration_test.py     # Bộ kiểm thử tích hợp tự động 10 chức năng
│
└── docs/                       # Tài liệu đồ án
    ├── 01_Architecture.md      # Thiết kế chi tiết và sơ đồ Mermaid
    └── 07_Report_Materials.md  # Danh mục ảnh minh chứng và kế hoạch báo cáo
```

---

## 4. HƯỚNG DẪN VẬN HÀNH TRÊN MÁY LOCAL

### Bước 1: Khởi động hệ thống
Mở PowerShell tại thư mục dự án `d:\Cloud\MiniCloud` và chạy:
```powershell
.\scripts\start.ps1
```
Hoặc dùng lệnh Docker Compose trực tiếp:
```powershell
docker compose up -d --build
```

### Bước 2: Kiểm tra trạng thái các container
```powershell
docker compose ps
```
Đảm bảo tất cả 10 container chính (`web-frontend-server1`, `web-frontend-server2`, `application-backend-server`, `relational-database-server`, `authentication-identity-server`, `object-storage-server`, `internal-dns-server`, `monitoring-node-exporter-server`, `monitoring-prometheus-server`, `monitoring-grafana-dashboard-server`, `api-gateway-proxy-server`) đều ở trạng thái `Up` (hoặc `healthy`).

### Bước 3: Chạy bộ kiểm thử tự động (Integration Tests)
```powershell
.\scripts\test.ps1
```
Hoặc:
```powershell
python tests/integration_test.py
```

### Bước 4: Kiểm thử thủ công các chức năng mở rộng
1. **Web & Blog**: Truy cập `http://localhost/` và `http://localhost/blog/`
2. **API Sinh viên JSON**: Truy cập `http://localhost/student`
3. **MariaDB API**: Truy cập `http://localhost/api/students-db`
4. **Keycloak Console**: Truy cập `http://localhost:8081` (Tài khoản: `admin` / `admin`)
5. **MinIO Console**: Truy cập `http://localhost:9001` (Tài khoản: `minioadmin` / `minioadmin`)
6. **Prometheus Targets**: Truy cập `http://localhost:9090/targets` (Tất cả target trạng thái UP)
7. **Grafana Dashboard**: Truy cập `http://localhost:3000` (Tài khoản: `admin` / `admin`), mở Dashboard *System Health - MyMiniCloud*
8. **Round Robin Load Balancing**: Gửi liên tiếp 10 request:
   ```powershell
   1..10 | ForEach-Object { (Invoke-WebRequest -Uri "http://localhost/" -UseBasicParsing).Headers['X-Upstream-Backend'] }
   ```
   Kết quả trả về sẽ luân phiên giữa 2 địa chỉ IP của 2 Web Server!

### Bước 5: Dừng hệ thống khi kết thúc
```powershell
.\scripts\stop.ps1
```
Hoặc xoá sạch toàn bộ để chạy lại từ đầu:
```powershell
.\scripts\clean.ps1
```

