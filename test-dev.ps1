# Entropy Development Testing Script
# This script runs comprehensive tests for the Entropy platform

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ENTROPY DEVELOPMENT TEST SUITE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Color function for output
function Write-Step {
    param($text)
    Write-Host "`n[STEP] $text" -ForegroundColor Yellow
}

function Write-Success {
    param($text)
    Write-Host "[SUCCESS] $text" -ForegroundColor Green
}

function Write-Error-Custom {
    param($text)
    Write-Host "[ERROR] $text" -ForegroundColor Red
}

# Test 1: Check Node version
Write-Step "Checking Node.js version..."
$nodeVersion = node --version
if ($LASTEXITCODE -eq 0) {
    Write-Success "Node.js version: $nodeVersion"
} else {
    Write-Error-Custom "Node.js not found. Please install Node.js 18+"
    exit 1
}

# Test 2: Check Python version (for AI agent)
Write-Step "Checking Python version..."
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python 3") {
        Write-Success "Python version: $pythonVersion"
    } else {
        Write-Error-Custom "Python 3 required for AI agent"
    }
} catch {
    Write-Error-Custom "Python not found. Install Python 3.8+ for AI agent"
}

# Test 3: Install dependencies
Write-Step "Installing dependencies..."
npm install
if ($LASTEXITCODE -eq 0) {
    Write-Success "Dependencies installed successfully"
} else {
    Write-Error-Custom "Failed to install dependencies"
    exit 1
}

# Test 4: Check environment variables
Write-Step "Checking environment variables..."
if (Test-Path "apps\app\.env") {
    Write-Success "Found apps/app/.env file"
} else {
    Write-Error-Custom "Missing apps/app/.env file. Copy from .env.example"
}

if (Test-Path "apps\ai-agent\.env") {
    Write-Success "Found apps/ai-agent/.env file"
} else {
    Write-Error-Custom "Missing apps/ai-agent/.env file"
}

# Test 5: Lint check
Write-Step "Running ESLint..."
npm run lint --workspaces --if-present
if ($LASTEXITCODE -eq 0) {
    Write-Success "Lint check passed"
} else {
    Write-Error-Custom "Lint check failed. Run 'npm run lint' to see details"
}

# Test 6: TypeScript compilation check
Write-Step "Checking TypeScript compilation..."
cd apps\app
npx tsc --noEmit
if ($LASTEXITCODE -eq 0) {
    Write-Success "TypeScript compilation successful"
} else {
    Write-Error-Custom "TypeScript compilation errors found"
}
cd ..\..

# Test 7: Database connection test
Write-Step "Testing database connection..."
cd apps\app
npx prisma db push --skip-generate --accept-data-loss 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Success "Database connection successful"
} else {
    Write-Error-Custom "Database connection failed. Check DATABASE_URL in .env"
}
cd ..\..

# Test 8: Build test
Write-Step "Testing production build..."
$buildOutput = npm run build 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Success "Production build successful"
} else {
    Write-Error-Custom "Production build failed"
    Write-Host $buildOutput
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  DEVELOPMENT TESTING COMPLETE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start development server:" -ForegroundColor Yellow
Write-Host "  npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "To start specific services:" -ForegroundColor Yellow
Write-Host "  npm run dev:app   (Frontend only)" -ForegroundColor White
Write-Host "  npm run dev:agent (AI Agent only)" -ForegroundColor White
Write-Host ""
