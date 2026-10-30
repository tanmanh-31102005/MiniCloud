# ==============================================================================
# MyMiniCloud - Automated Integration Test Runner (PowerShell)
# ==============================================================================
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "     CHẠY KIỂM THỬ TÍCH HỢP HỆ THỐNG MYMINICLOUD      " -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan

python tests/integration_test.py

