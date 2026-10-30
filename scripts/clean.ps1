# ==============================================================================
# MyMiniCloud - Clean & Reset Infrastructure Script (PowerShell)
# SAFETY GUARD: Requires explicit confirmation before deleting persistent data
# ==============================================================================
Write-Host "======================================================" -ForegroundColor Red
Write-Host "  [CANH BAO] DỌN DẸP & RESET TOÀN BỘ CONTAINER & VOLUME " -ForegroundColor Red
Write-Host "======================================================" -ForegroundColor Red
Write-Host "Thao tac nay se:" -ForegroundColor Yellow
Write-Host " 1. Dung va xoa toan bo 10+ containers." -ForegroundColor Yellow
Write-Host " 2. XOA TOAN BO DU LIEU TRONG VOLUMES (MariaDB, MinIO, Grafana)." -ForegroundColor Yellow
Write-Host " 3. Xoa mang bridge 'cloud-net'." -ForegroundColor Yellow
Write-Host "`nNeu ban chi muon DUNG he thong ma KHONG mat du lieu, hay dung: .\scripts\stop.ps1" -ForegroundColor Cyan

$confirmation = Read-Host "`nBan co chac chan muon xoa sach toan bo du lieu khong? (Nhap 'YES' de xac nhan)"
if ($confirmation -ceq "YES") {
    Write-Host "`nDang thuc hien reset toan bo he thong..." -ForegroundColor Red
    docker compose down -v --remove-orphans
    Write-Host "`n[HOAN TAT] He thong da duoc don dep va reset ve trang thai ban dau." -ForegroundColor Green
} else {
    Write-Host "`n[HUY BO] Thao tac reset da duoc huy an toan. Du lieu cua ban van duoc giu nguyen!" -ForegroundColor Green
}
