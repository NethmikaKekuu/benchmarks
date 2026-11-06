# run_comparison.ps1
# Runs two 12-minute load tests sequentially (without_cache, then with_cache).
# Each test steps through 10 -> 25 -> 50 -> 100 users (3 min each step).
# After each test ends, the Locust web UI stays up for 2 minutes (--autoquit 120).
# Take your screenshot of http://localhost:8089/charts within those 2 minutes.
# The script then waits for Enter before starting the next test.

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

if (-not $HOST_WITH_CACHE -or -not $HOST_WITHOUT_CACHE) {
    Write-Host "ERROR: HOST_WITH_CACHE and HOST_WITHOUT_CACHE must be set in $envFile" -ForegroundColor Red
    exit 1
}

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
    locust -f "$locustFile,$shapeFile" --host=$($v.host) --autostart --autoquit 120 --csv=$csvPath

    if ($LASTEXITCODE -ne 0) {
        Write-Host "Locust exited with code $LASTEXITCODE (failures during load test are expected). Continuing." -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "DONE: $($v.label)" -ForegroundColor Yellow
    Write-Host "You have 2 minutes to screenshot http://localhost:8089/charts before the UI shuts down." -ForegroundColor Yellow
    Read-Host "Press Enter to start the next version"
}

Write-Host ""
Write-Host "Both versions complete. 2 CSV files saved." -ForegroundColor Green
