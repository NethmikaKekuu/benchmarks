# run_comparison.ps1
# One 12-minute run per version: 10 -> 25 -> 50 -> 100 users (3 min each step).
# Take a screenshot of http://localhost:8089 after each version finishes.

$HOST_WITH_CACHE    = "https://aaf8ece1-3077-4a52-ab05-183a424f6d93-dev.e1-us-east-azure.choreoapis.dev/data-platform/giservice/v1.0"
$HOST_WITHOUT_CACHE = "https://aaf8ece1-3077-4a52-ab05-183a424f6d93-dev.e1-us-east-azure.choreoapis.dev/data-platform/giservice/v1.6"

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

    locust -f locust_gi.py,comparison_shape.py --host=$($v.host) --autostart --autoquit 5 --csv=$csv

    Write-Host ""
    Write-Host "DONE: $($v.label)" -ForegroundColor Yellow
    Write-Host "Screenshot the Charts tab at http://localhost:8089 NOW." -ForegroundColor Yellow
    Read-Host "Press Enter to start the next version"
}

Write-Host ""
Write-Host "Both versions complete. 2 CSV files saved." -ForegroundColor Green
