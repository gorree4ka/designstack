<#
.SYNOPSIS  Start the local WordPress dev server (PHP built-in server + SQLite).
.USAGE     .\scripts\start.ps1 [-Port 8080] [-Background]
#>
param([int]$Port = 8080, [switch]$Background)
$Root = Split-Path -Parent $PSScriptRoot
$Php  = Join-Path $Root 'tools\php\php.exe'
$Args = @('-S', "localhost:$Port", '-t', (Join-Path $Root 'wordpress'), (Join-Path $Root 'tools\router.php'))
if ($Background) {
  $p = Start-Process -FilePath $Php -ArgumentList $Args -WorkingDirectory $Root -WindowStyle Hidden -PassThru
  Set-Content -Path (Join-Path $Root '.tmp\server.pid') -Value $p.Id -Encoding ascii
  Write-Host "WordPress running at http://localhost:$Port (pid $($p.Id)). Stop: .\scripts\stop.ps1"
} else {
  Write-Host "WordPress at http://localhost:$Port  (Ctrl+C to stop)"
  & $Php @Args
}
