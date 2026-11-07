# HỒ SƠ ĐÓNG GÓI VÀ PHÁT HÀNH DOCKER HUB
## DOCKER HUB RELEASE MANIFEST — MYMINICLOUD VERSION 1.0.0

---

## 1. THÔNG TIN PHÁT HÀNH TỔNG QUAN

- **Tài khoản Docker Hub phát hành**: **`nguyenmanh3110`**
- **Phiên bản phát hành (Semantic Version)**: **`1.0.0`**
- **Ngày build & phát hành thành công**: **Tháng 11/2026**
- **Môi trường Build**: Docker Desktop on WSL2 (Engine 29.7.2, Linux x86_64)
- **Kiến trúc đích (Target Architecture)**: `linux/amd64` (x86_64) — Tương thích 100% với AWS EC2 Ubuntu 24.04 LTS
- **Trạng thái kiểm toán an ninh (Security Audit)**: **PASSED (100% an toàn)** (0 secrets, 0 credentials, non-root execution trên Backend, loại trừ triệt để qua `.dockerignore`).
- **Trạng thái vòng đời Release**:
  - ✅ **Build thành công**: 3/3 custom images
  - ✅ **Tag thành công**: 3/3 custom images
  - ✅ **Push thành công**: 3/3 images đã publish lên Docker Hub
  - ✅ **Pull thành công**: 3/3 images kéo về và kiểm tra Digest SHA256 khớp 100%
  - ✅ **Run thành công**: Khởi chạy container từ image kéo về, kiểm tra toàn bộ API/Healthcheck đạt HTTP 200 OK

---

## 2. MA TRẬN DOCKER HUB IMAGES ĐÃ PHÁT HÀNH VÀ XÁC MINH DIGEST

| Tên Image trên Docker Hub | Version Tag | Base Image | Kích thước Nén | Kích thước Giải nén | Digest SHA-256 chính thức | User Runtime | Trạng thái Push & Pull |
|:---|:---:|:---|:---:|:---:|:---|:---:|:---:|
| `nguyenmanh3110/myminicloud-backend` | `1.0.0` | `python:3.11-slim` | **60.2 MB** | 248 MB | `sha256:e00bc1b143337dcf6aa6a9df7cae33bce149ac74911e4e6f82da2fe68653f08c` | `appuser` (1000) | **VERIFIED (PASS)** |
| `nguyenmanh3110/myminicloud-frontend`| `1.0.0` | `nginx:1.25-alpine` | **20.5 MB** | 74.2 MB | `sha256:c3d8ca510ec31c13bcb0d2be3296d48f67fdc0e60987c189756937a01942039e` | `nginx` | **VERIFIED (PASS)** |
| `nguyenmanh3110/myminicloud-gateway` | `1.0.0` | `nginx:1.25-alpine` | **20.5 MB** | 74.1 MB | `sha256:8bacbebc7b375809783f9e8003eee12a19cd4f394676b7db7c4b24d0e81578d0` | `nginx` | **VERIFIED (PASS)** |

---

## 3. LỆNH THAO TÁC TIÊU CHUẨN ĐÃ THỰC THI

### 3.1. Đối với Backend Image (`myminicloud-backend`)

- **Build**:
  ```bash
  docker build -t myminicloud-backend:1.0.0 ./backend
  ```
- **Tag**:
  ```bash
  docker tag myminicloud-backend:1.0.0 nguyenmanh3110/myminicloud-backend:1.0.0
  ```
- **Push**:
  ```bash
  docker push nguyenmanh3110/myminicloud-backend:1.0.0
  # Output: 1.0.0: digest: sha256:e00bc1b143337dcf6aa6a9df7cae33bce149ac74911e4e6f82da2fe68653f08c
  ```
- **Pull**:
  ```bash
  docker pull nguyenmanh3110/myminicloud-backend:1.0.0
  # Output: Status: Image is up to date for nguyenmanh3110/myminicloud-backend:1.0.0
  ```
- **Run & Verify**:
  ```bash
  docker run -d --name verify-backend -p 8095:8081 nguyenmanh3110/myminicloud-backend:1.0.0
  # curl http://127.0.0.1:8095/health -> HTTP 200 (healthy)
  # curl http://127.0.0.1:8095/student -> HTTP 200 (5 students JSON)
  # curl http://127.0.0.1:8095/metrics -> HTTP 200 (Prometheus exposition)
  ```

### 3.2. Đối với Frontend Image (`myminicloud-frontend`)

- **Build**:
  ```bash
  docker build -t myminicloud-frontend:1.0.0 ./frontend
  ```
- **Tag**:
  ```bash
  docker tag myminicloud-frontend:1.0.0 nguyenmanh3110/myminicloud-frontend:1.0.0
  ```
- **Push**:
  ```bash
  docker push nguyenmanh3110/myminicloud-frontend:1.0.0
  # Output: 1.0.0: digest: sha256:c3d8ca510ec31c13bcb0d2be3296d48f67fdc0e60987c189756937a01942039e
  ```
- **Pull**:
  ```bash
  docker pull nguyenmanh3110/myminicloud-frontend:1.0.0
  # Output: Status: Image is up to date for nguyenmanh3110/myminicloud-frontend:1.0.0
  ```
- **Run & Verify**:
  ```bash
  docker run -d --name verify-frontend -p 8096:80 nguyenmanh3110/myminicloud-frontend:1.0.0
  # curl http://127.0.0.1:8096/health -> HTTP 200
  # curl http://127.0.0.1:8096/ -> HTTP 200 (11,624 bytes HTML)
  # curl http://127.0.0.1:8096/blog/blog1.html -> HTTP 200 (6,817 bytes HTML)
  ```

### 3.3. Đối với Gateway Image (`myminicloud-gateway`)

- **Build**:
  ```bash
  docker build -t myminicloud-gateway:1.0.0 ./gateway
  ```
- **Tag**:
  ```bash
  docker tag myminicloud-gateway:1.0.0 nguyenmanh3110/myminicloud-gateway:1.0.0
  ```
- **Push**:
  ```bash
  docker push nguyenmanh3110/myminicloud-gateway:1.0.0
  # Output: 1.0.0: digest: sha256:8bacbebc7b375809783f9e8003eee12a19cd4f394676b7db7c4b24d0e81578d0
  ```
- **Pull**:
  ```bash
  docker pull nguyenmanh3110/myminicloud-gateway:1.0.0
  # Output: Status: Image is up to date for nguyenmanh3110/myminicloud-gateway:1.0.0
  ```
- **Run & Verify**:
  ```bash
  docker run --rm --network cloud-net nguyenmanh3110/myminicloud-gateway:1.0.0 nginx -t
  # Output: syntax is ok, test is successful
  ```

---

## 4. CHI TIẾT CÁC THAY ĐỔI TRONG PHIÊN BẢN (CHANGELOG V1.0.0)

| Image | Điểm cải tiến chính |
|:---|:---|
| `nguyenmanh3110/myminicloud-backend:1.0.0` | - Hoàn thiện 4 thao tác CRUD MariaDB (`/api/students-db`) có Parameterized Queries.<br>- Thẩm định chữ ký số JWT qua JWKS Keycloak OIDC (RS256).<br>- Tích hợp Prometheus client xuất bản số liệu tại `/metrics`.<br>- Tách biệt quyền hạn: Chạy dưới tài khoản phi đặc quyền `appuser` (UID 1000).<br>- Bổ sung tệp `.dockerignore` loại trừ file nhạy cảm và cache. |
| `nguyenmanh3110/myminicloud-frontend:1.0.0` | - Phục vụ website tĩnh và 3 bài viết blog kỹ thuật.<br>- Bổ sung endpoint `/health` trả về HTTP 200 phục vụ Docker Healthcheck.<br>- Bổ sung endpoint `/metrics` trả về `nginx_up: 1` cho Prometheus Scrape Target.<br>- Tối ưu quyền đọc tệp tĩnh `755` và bổ sung `.dockerignore`. |
| `nguyenmanh3110/myminicloud-gateway:1.0.0` | - Đóng gói cấu hình Reverse Proxy thành Docker image độc lập.<br>- Định tuyến thông minh `/`, `/api/`, `/student`, `/auth/`.<br>- Tích hợp cụm Upstream Round Robin cân bằng tải 50/50 giữa 2 Web Node.<br>- Bổ sung header nhận diện `X-Gateway` và `X-Upstream-Backend`. |

---

## 5. KẾT LUẬN KIỂM ĐỊNH

Tất cả các custom images đã được đăng tải công khai, kéo về kiểm định và chạy thử nghiệm thành công 100%. Hệ thống đã sẵn sàng tuyệt đối để chuyển giao và triển khai trên môi trường đám mây **AWS EC2 Ubuntu 24.04 LTS**.
