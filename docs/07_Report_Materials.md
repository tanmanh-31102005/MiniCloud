# DANH MỤC MINH CHỨNG VÀ KẾ HOẠCH BÁO CÁO (REPORT MATERIALS & EVIDENCE CHECKLIST)

Tài liệu này tổng hợp danh mục ảnh chụp màn hình, nhật ký kiểm thử (test logs) và bảng dữ liệu cần thu thập trong quá trình chạy hệ thống để đưa vào Báo cáo cuối kỳ.

---

## 1. DANH MỤC ẢNH MINH CHỨNG CẦN CHỤP (SCREENSHOT GUIDELINES)

| Mã ảnh | Nội dung minh chứng | Nơi thực hiện / URL | Mục đích trong báo cáo | Trạng thái |
|:---:|:---|:---|:---|:---:|
| `SS-01` | Trạng thái toàn bộ container đang chạy (`docker compose ps`) | Terminal / PowerShell | Chứng minh 9 vai trò dịch vụ + 2 web server + node exporter hoạt động | [ ] Chưa chụp |
| `SS-02` | Giao diện trang chủ Web Frontend qua Gateway (`http://localhost/`) | Trình duyệt Web | Minh chứng dịch vụ Web và định tuyến Gateway | [ ] Chưa chụp |
| `SS-03` | Giao diện trang Blog và 3 bài viết cá nhân (`http://localhost/blog/`) | Trình duyệt Web | Minh chứng Chức năng mở rộng 1 (Blog 3 bài) | [ ] Chưa chụp |
| `SS-04` | Kết quả gọi API JSON `/api/student` hoặc `/student/` | Trình duyệt / curl | Minh chứng Chức năng mở rộng 2 (5 sinh viên JSON) | [ ] Chưa chụp |
| `SS-05` | Truy vấn cơ sở dữ liệu MariaDB (`studentdb` và bảng `students`) | CLI / Flask API `/api/students-db` | Minh chứng Chức năng mở rộng 3 (MariaDB CRUD & Data) | [ ] Chưa chụp |
| `SS-06` | Giao diện Keycloak Admin Console (Realm `MyMiniCloud`, Client `flask-app`, Users) | `http://localhost:8081` hoặc `http://localhost/auth/` | Minh chứng Chức năng 4 (Keycloak Configuration) | [ ] Chưa chụp |
| `SS-07` | Kiểm thử endpoint bảo mật `/api/secure` (Từ chối khi thiếu token vs Thành công khi có JWT) | curl / Terminal | Minh chứng Chức năng 4 (JWT Verification RS256) | [ ] Chưa chụp |
| `SS-08` | Giao diện MinIO Console (`http://localhost:9001`) hiển thị bucket `profile-pics` và `documents` | Trình duyệt Web | Minh chứng Chức năng mở rộng 5 (Object Storage S3) | [ ] Chưa chụp |
| `SS-09` | Kết quả truy vấn DNS BIND9 (`dig` hoặc `nslookup` phân giải `cloud.local`) | Terminal / PowerShell | Minh chứng Chức năng mở rộng 6 (Internal DNS BIND9) | [ ] Chưa chụp |
| `SS-10` | Giao diện Prometheus Targets (`http://localhost:9090/targets`) trạng thái UP | Trình duyệt Web | Minh chứng Chức năng mở rộng 7 (Prometheus Monitoring) | [ ] Chưa chụp |
| `SS-11` | Giao diện Grafana Dashboard (`http://localhost:3000`) hiển thị 3 biểu đồ (CPU, RAM, Network) | Trình duyệt Web | Minh chứng Chức năng mở rộng 8 (Grafana Visualization) | [ ] Chưa chụp |
| `SS-12` | Minh chứng Round Robin Load Balancing (gửi nhiều request liên tiếp nhận header/nội dung từ Web 1 và Web 2) | Terminal loop curl | Minh chứng Chức năng mở rộng 10 (Round Robin Balancing) | [ ] Chưa chụp |
| `SS-13` | Ping kiểm tra thông mạng giữa các container trong mạng `cloud-net` | Container sh ping | Minh chứng kiểm tra kết nối mạng nội bộ Docker | [ ] Chưa chụp |

---

## 2. NHẬT KÝ KIỂM THỬ TÍCH HỢP (AUTOMATED TEST LOG TEMPLATE)

```text
================================================================================
                    MYMINICLOUD INTEGRATION TEST SUITE REPORT
================================================================================
Test Execution Time: [TIMESTAMP]
Environment: Local Docker Desktop (WSL2 / Windows)

[TEST-01] Docker Compose Services Health Status:        [PASS/FAIL]
[TEST-02] Docker Network 'cloud-net' Ping Connectivity: [PASS/FAIL]
[TEST-03] Web Frontend Server (Home & Blog):            [PASS/FAIL]
[TEST-04] Flask API Endpoint /student (JSON 5 students):[PASS/FAIL]
[TEST-05] MariaDB Connection & Table Query:             [PASS/FAIL]
[TEST-06] Keycloak Realm / Token Generation:            [PASS/FAIL]
[TEST-07] Keycloak JWT Secure Endpoint Verification:   [PASS/FAIL]
[TEST-08] MinIO Bucket Existence & File Storage:        [PASS/FAIL]
[TEST-09] BIND9 Internal DNS Resolution:                [PASS/FAIL]
[TEST-10] Prometheus Targets State (All UP):            [PASS/FAIL]
[TEST-11] Grafana Dashboard Provisioning:               [PASS/FAIL]
[TEST-12] API Gateway Route Forwarding:                 [PASS/FAIL]
[TEST-13] Round Robin Load Balancing Distribution:      [PASS/FAIL]
================================================================================
Overall Result: ALL TESTS VERIFIED
```

---

## 3. KẾ HOẠCH BÁO CÁO CUỐI KỲ (ĐỀ CƯƠNG 5 CHƯƠNG)

- **Chương 1: Tổng quan và Mục tiêu Đề tài**
  - Đặt vấn đề và lý do xây dựng Cloud thu nhỏ.
  - Mục tiêu đào tạo và các yêu cầu kỹ thuật đồ án.
  - Phân tích 9 vai trò dịch vụ và sự tương đương với các dịch vụ AWS.
- **Chương 2: Thiết kế Kiến trúc và Mạng Hệ thống**
  - Mô hình kiến trúc phân tầng (Multi-tier Architecture).
  - Thiết kế Docker Network (`cloud-net`), địa chỉ hóa và phân giải tên dịch vụ.
  - Thiết kế lưu trữ bền vững (Docker Volumes).
  - Cơ chế định tuyến và cân bằng tải tại API Gateway.
- **Chương 3: Cấu hình Chi tiết và Hiện thực Dịch vụ**
  - Chi tiết Dockerfile và cấu hình từng dịch vụ.
  - Cấu hình OIDC / JWT Security trên Keycloak và Flask Backend.
  - Cấu hình BIND9 DNS Zone và Records.
  - Cấu hình Prometheus Scrape Targets và Grafana Provisioning.
- **Chương 4: Kết quả Thực nghiệm và Kiểm thử Toàn diện**
  - Kiểm thử chức năng cơ bản của 9 máy chủ.
  - Kiểm thử 10 chức năng mở rộng nâng cao.
  - Bằng chứng thực nghiệm (Logs, hình ảnh thực tế).
- **Chương 5: Đánh giá, Thảo luận và Hướng phát triển**
  - So sánh mô hình Local với hạ tầng Cloud thực tế (AWS).
  - Những khó khăn kỹ thuật đã giải quyết.
  - Kế hoạch triển khai lên AWS EC2 (tích hợp theo Phase 7).
- **Phụ lục**:
  - Hướng dẫn cài đặt và vận hành nhanh (`scripts/start.ps1`, `scripts/stop.ps1`, `scripts/test.ps1`).
  - Đường dẫn Docker Hub Image Repository.

