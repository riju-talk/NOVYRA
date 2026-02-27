# Quick Test Script - Fast validation during development
Write-Host "Running quick validation tests..." -ForegroundColor Cyan

# Quick lint
Write-Host "`nLinting..." -ForegroundColor Yellow
cd apps\app
npx eslint . --ext .ts,.tsx --max-warnings 0 --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Lint passed" -ForegroundColor Green
} else {
    Write-Host "✗ Lint failed" -ForegroundColor Red
}

# Quick TypeScript check
Write-Host "`nType checking..." -ForegroundColor Yellow
npx tsc --noEmit --incremental
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Type check passed" -ForegroundColor Green
} else {
    Write-Host "✗ Type check failed" -ForegroundColor Red
}

cd ..\..

Write-Host "`nQuick tests complete!" -ForegroundColor Cyan
