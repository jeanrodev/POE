# MOE QA System Setup Script for Windows (PowerShell)

Write-Host "🚀 MOE QA System Setup" -ForegroundColor Cyan
Write-Host "=====================" -ForegroundColor Cyan

# Check Python version
Write-Host ""
Write-Host "Checking Python installation..." -ForegroundColor Yellow
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

$pythonVersion = python --version 2>&1
Write-Host "✓ $pythonVersion found" -ForegroundColor Green

# Create virtual environment
Write-Host ""
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv
Write-Host "✓ Virtual environment created" -ForegroundColor Green

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "✓ Virtual environment activated" -ForegroundColor Green

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip
pip install -r requirements.txt
Write-Host "✓ Dependencies installed" -ForegroundColor Green

# Create necessary directories
Write-Host ""
Write-Host "Creating directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path "qa_reports" -Force | Out-Null
New-Item -ItemType Directory -Path "logs" -Force | Out-Null
Write-Host "✓ Directories created" -ForegroundColor Green

# Check Docker
Write-Host ""
Write-Host "Checking Docker/Docker Compose..." -ForegroundColor Yellow
if (Get-Command docker-compose -ErrorAction SilentlyContinue) {
    Write-Host "✓ Docker Compose found" -ForegroundColor Green
    Write-Host ""
    Write-Host "To start Ollama infrastructure, run:" -ForegroundColor Cyan
    Write-Host "  docker-compose up -d" -ForegroundColor White
} else {
    Write-Host "⚠ Docker Compose not found. Install from https://docs.docker.com/compose/install/" -ForegroundColor Yellow
}

# Final instructions
Write-Host ""
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Start Ollama: docker-compose up -d" -ForegroundColor White
Write-Host "2. Pull models: python -m ollama pull codellama:34b" -ForegroundColor White
Write-Host "3. Run analysis: python moe_qa\main.py src\ --format html" -ForegroundColor White
Write-Host ""
