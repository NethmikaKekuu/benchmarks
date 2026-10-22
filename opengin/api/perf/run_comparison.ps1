# run_comparison.ps1
# One 12-minute run per version: 10 -> 25 -> 50 -> 100 users (3 min each step).
# Take a screenshot of http://localhost:8089 after each version finishes.

$locustFile  = Join-Path $PSScriptRoot "locust_gi.py"
$shapeFile   = Join-Path $PSScriptRoot "comparison_shape.py"
$envFile     = Join-Path $PSScriptRoot ".env"

# Load host URLs from .env
Get-Content $envFile | ForEach-Object {
    if ($_ -match "^\s*([^#][^=]+)=(.+)$") {
        [System.Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim())
    }
}
$HOST_WITH_CACHE    = $env:HOST_WITH_CACHE
$HOST_WITHOUT_CACHE = $env:HOST_WITHOUT_CACHE

$versions = @(
    @{ label = "without_cache"; host = $HOST_WITHOUT_CACHE },
    @{ label = "with_cache";    host = $HOST_WITH_CACHE }
)

foreach ($v in $versions) {
    $csv = "results_$($v.label)"
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "STARTING: $($v.label)" -ForegroundColor Cyan
    Write-Host "10 -> 25 -> 50 -> 100 users, 3 min each = 12 min total" -ForegroundColor Cyan
    Write-Host "Watch: http://localhost:8089" -ForegroundColor Cyan
    Write-Host "CSV: ${csv}_stats.csv" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan

    $csvPath = Join-Path $PSScriptRoot $csv
    locust -f "$locustFile,$shapeFile" --host=$($v.host) --autostart --autoquit 5 --csv=$csvPath

    Write-Host ""
    Write-Host "DONE: $($v.label)" -ForegroundColor Yellow
    Write-Host "Screenshot the Charts tab at http://localhost:8089 NOW." -ForegroundColor Yellow
    Read-Host "Press Enter to start the next version"
}

Write-Host ""
Write-Host "Both versions complete. 2 CSV files saved." -ForegroundColor Green
