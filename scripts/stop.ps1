<# Stop the background dev server started with start.ps1 -Background #>
$Root = Split-Path -Parent $PSScriptRoot
$pidFile = Join-Path $Root '.tmp\server.pid'
if (Test-Path $pidFile) {
  $id = Get-Content $pidFile
  try { Stop-Process -Id $id -Force -ErrorAction Stop; Write-Host "Stopped pid $id" } catch { Write-Host "Process $id not running" }
  Remove-Item $pidFile -Force
} else {
  Get-Process php -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*DesignSite*" } | Stop-Process -Force
  Write-Host "No pid file; killed any DesignSite php.exe processes."
}
