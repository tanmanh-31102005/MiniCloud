# ==============================================================================
# MyMiniCloud - Clean & Reset Infrastructure Script (PowerShell)
# ==============================================================================
Write-Host "======================================================" -ForegroundColor Red
Write-Host "     DỌN DẸP & RESET TOÀN BỘ CONTAINER VÀ VOLUME      " -ForegroundColor Red
Write-Host "======================================================" -ForegroundColor Red

docker compose down -v --remove-orphans

Write-Host "`nHe thong da duoc don dep va reset ve trang thai ban dau." -ForegroundColor Green
