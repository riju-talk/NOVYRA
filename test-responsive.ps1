# Responsive Testing Guide
# Run this in PowerShell to test responsive components

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "   RESPONSIVE TESTING CHECKLIST     " -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Step 1: Start Development Server" -ForegroundColor Yellow
Write-Host "Run: pnpm dev" -ForegroundColor Gray
Write-Host ""

Write-Host "Step 2: Test at Standard Breakpoints" -ForegroundColor Yellow
Write-Host ""
Write-Host "Device Dimensions to Test:" -ForegroundColor Green
Write-Host "  Mobile Small:  375×667   (iPhone SE)" -ForegroundColor Gray
Write-Host "  Mobile Medium: 390×844   (iPhone 12 Pro)" -ForegroundColor Gray
Write-Host "  Mobile Large:  414×896   (iPhone 14 Pro Max)" -ForegroundColor Gray
Write-Host "  Tablet:        768×1024  (iPad Portrait)" -ForegroundColor Gray
Write-Host "  Laptop:        1280×800  (MacBook)" -ForegroundColor Gray
Write-Host "  Desktop:       1920×1080 (Full HD)" -ForegroundColor Gray
Write-Host ""

Write-Host "Step 3: Test These Components" -ForegroundColor Yellow
Write-Host ""
$components = @(
    "✅ doubt-card.tsx - Check flex layout and button sizing",
    "✅ ask-doubt-form.tsx - Test form inputs and buttons",
    "✅ sidebar.tsx - Verify hidden on mobile, visible on desktop",
    "✅ answer-form.tsx - Check textarea and AI assist section",
    "✅ footer.tsx - Test grid collapse on mobile",
    "✅ edit-profile-modal.tsx - Check modal scroll and sizing",
    "⚠️  doubts-feed.tsx - Verify responsive grid",
    "⚠️  answers-list.tsx - Check answer layout",
    "⚠️  auth-modal.tsx - Test modal on small screens"
)

foreach ($comp in $components) {
    if ($comp.StartsWith("✅")) {
        Write-Host $comp -ForegroundColor Green
    } else {
        Write-Host $comp -ForegroundColor Yellow
    }
}
Write-Host ""

Write-Host "Step 4: Interaction Testing" -ForegroundColor Yellow
Write-Host "[ ] All buttons are tappable (44x44px minimum)" -ForegroundColor Gray
Write-Host "[ ] No horizontal scroll" -ForegroundColor Gray
Write-Host "[ ] Text is readable (min 12px)" -ForegroundColor Gray
Write-Host "[ ] Forms are accessible with touch keyboard" -ForegroundColor Gray
Write-Host "[ ] Modals scroll properly" -ForegroundColor Gray
Write-Host "[ ] Navigation works on all sizes" -ForegroundColor Gray
Write-Host ""

Write-Host "Step 5: Chrome DevTools Testing" -ForegroundColor Yellow
Write-Host "1. Open Chrome DevTools (F12)" -ForegroundColor Gray
Write-Host "2. Click Toggle Device Toolbar (Ctrl+Shift+M)" -ForegroundColor Gray
Write-Host "3. Select device preset or enter custom dimensions" -ForegroundColor Gray
Write-Host "4. Test each page and component" -ForegroundColor Gray
Write-Host "5. Check 'Responsive' mode and drag to resize" -ForegroundColor Gray
Write-Host ""

Write-Host "Step 6: Lighthouse Mobile Audit" -ForegroundColor Yellow
Write-Host "Run: Write-Host 'Run Lighthouse audit in DevTools'" -ForegroundColor Gray
Write-Host "Target: 90+ on mobile performance" -ForegroundColor Gray
Write-Host ""

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "     Quick Test Commands             " -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "# Start dev server and open browser:" -ForegroundColor Green
Write-Host "pnpm dev; Start-Process 'http://localhost:3000'" -ForegroundColor Gray
Write-Host ""
Write-Host "# Check TypeScript (from root):" -ForegroundColor Green
Write-Host "cd apps/app; npx tsc --noEmit" -ForegroundColor Gray
Write-Host ""
Write-Host "# Run ESLint:" -ForegroundColor Green
Write-Host "pnpm lint" -ForegroundColor Gray
Write-Host ""

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Testing URL Checklist              " -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
$urls = @(
    "http://localhost:3000/                - Homepage with doubt feed",
    "http://localhost:3000/ask             - Ask doubt form",
    "http://localhost:3000/doubt/[id]      - Doubt detail page",
    "http://localhost:3000/profile         - User profile",
    "http://localhost:3000/communities     - Communities list",
    "http://localhost:3000/leaderboard     - Leaderboard",
    "http://localhost:3000/ai-agent        - AI Agent chat"
)

foreach ($url in $urls) {
    Write-Host "  • $url" -ForegroundColor Cyan
}
Write-Host ""

Write-Host "Happy Testing! 🚀" -ForegroundColor Green
