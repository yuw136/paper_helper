# Paper Helper 停止脚本
# 使用方法: .\stop.ps1

Write-Host "Paper Helper 停止脚本" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "停止 Docker 服务..." -ForegroundColor Yellow
docker-compose down

if ($LASTEXITCODE -eq 0) {
    Write-Host "所有 Docker 服务已停止" -ForegroundColor Green
} else {
    Write-Host "错误: 停止服务时出现问题" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "提示:" -ForegroundColor Yellow
Write-Host "- Python 后端和 React 前端需要手动在终端中停止 (Ctrl+C)" -ForegroundColor White
Write-Host "- 如需删除数据库数据，使用: docker-compose down -v" -ForegroundColor White
Write-Host "================================" -ForegroundColor Cyan
