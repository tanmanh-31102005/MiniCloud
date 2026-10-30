# ==============================================================================
# MyMiniCloud - Stop Infrastructure Script (PowerShell)
# ==============================================================================
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "         DỪNG HỆ THỐNG MYMINICLOUD                    " -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan

docker compose stop

Write-Host "`nToan bo container da duoc tam dung an toan." -ForegroundColor Green
docker compose ps
