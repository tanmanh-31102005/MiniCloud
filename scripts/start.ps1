# ==============================================================================
# MyMiniCloud - Start Infrastructure Script (PowerShell)
# ==============================================================================
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "       KHỞI ĐỘNG HỆ THỐNG MYMINICLOUD (DOCKER)        " -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "[!] File .env chua ton tai. Dang sao chep tu .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
}

Write-Host "`n[1/3] Dang build Docker Image cho Web Frontend & Flask Backend..." -ForegroundColor Green
docker compose build

Write-Host "`n[2/3] Dang khoi dong toan bo cac containers..." -ForegroundColor Green
docker compose up -d

Write-Host "`n[3/3] Dang kiem tra trang thai cac container..." -ForegroundColor Green
Start-Sleep -Seconds 5
docker compose ps

Write-Host "`n======================================================" -ForegroundColor Cyan
Write-Host " HE THONG MYMINICLOUD DA KHOI DONG THANH CONG!        " -ForegroundColor Green
Write-Host " Cac diem truy cap chinh:                             " -ForegroundColor Yellow
Write-Host " - Web Frontend / Gateway:  http://localhost/         " -ForegroundColor White
Write-Host " - Blog Ky Thuat:           http://localhost/blog/    " -ForegroundColor White
Write-Host " - Flask API Students:      http://localhost/student  " -ForegroundColor White
Write-Host " - Keycloak IAM Admin:      http://localhost:8081     " -ForegroundColor White
Write-Host " - MinIO S3 Console:        http://localhost:9001     " -ForegroundColor White
Write-Host " - Prometheus Monitoring:   http://localhost:9090     " -ForegroundColor White
Write-Host " - Grafana Observability:   http://localhost:3000     " -ForegroundColor White
Write-Host "======================================================" -ForegroundColor Cyan
