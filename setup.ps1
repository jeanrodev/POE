# MOE QA System Setup Script for Windows (PowerShell)
# Ollama and all LLM models run entirely inside Docker — no local install needed.

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
Write-Host "Checking Docker..." -ForegroundColor Yellow
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker not found. Install from https://docs.docker.com/get-docker/" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Docker found" -ForegroundColor Green

# Build the custom Ollama image
Write-Host ""
Write-Host "Building the Ollama image..." -ForegroundColor Yellow
docker compose build ollama
Write-Host "✓ Image built" -ForegroundColor Green

# Final instructions
Write-Host ""
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Start the stack:  docker compose up -d" -ForegroundColor White
Write-Host "   ↳ Models are downloaded automatically on first start (30–60 min)." -ForegroundColor DarkGray
Write-Host ""
Write-Host "2. Monitor download: docker logs -f ollama_server" -ForegroundColor White
Write-Host ""
Write-Host "3. Open chat UI:     http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "4. Run analysis:     python moe_qa\main.py src\ --format html" -ForegroundColor White
Write-Host ""
