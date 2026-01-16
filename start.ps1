# Paper Helper 快速启动脚本
# 使用方法: .\start.ps1

Write-Host "Paper Helper 启动脚本" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Docker 是否运行
Write-Host "检查 Docker..." -ForegroundColor Yellow
$dockerRunning = docker ps 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: Docker 未运行，请先启动 Docker Desktop" -ForegroundColor Red
    exit 1
}
Write-Host "Docker 正在运行" -ForegroundColor Green
Write-Host ""

# 启动 Docker 服务
Write-Host "启动 PostgreSQL 和 Adminer..." -ForegroundColor Yellow
docker-compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: Docker 服务启动失败" -ForegroundColor Red
    exit 1
}
Write-Host "Docker 服务已启动" -ForegroundColor Green
Write-Host ""

# 等待数据库就绪
Write-Host "等待数据库就绪 (5秒)..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
Write-Host "数据库已就绪" -ForegroundColor Green
Write-Host ""

# 打开 Adminer
Write-Host "打开 Adminer 数据库管理界面..." -ForegroundColor Yellow
Start-Process "http://localhost:8080"
Write-Host "Adminer: http://localhost:8080" -ForegroundColor Green
Write-Host ""

# 提示后续步骤
Write-Host "================================" -ForegroundColor Cyan
Write-Host "启动成功！接下来的步骤：" -ForegroundColor Green
Write-Host ""
Write-Host "1. 启动 Python 后端:" -ForegroundColor Cyan
Write-Host "   cd server" -ForegroundColor White
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "   python main.py" -ForegroundColor White
Write-Host ""
Write-Host "2. 启动 React 前端 (在新终端):" -ForegroundColor Cyan
Write-Host "   npm start" -ForegroundColor White
Write-Host ""
Write-Host "访问地址:" -ForegroundColor Cyan
Write-Host "   React 前端:  http://localhost:3001" -ForegroundColor White
Write-Host "   Adminer:     http://localhost:8080" -ForegroundColor White
Write-Host "   PostgreSQL:  localhost:5432" -ForegroundColor White
Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
