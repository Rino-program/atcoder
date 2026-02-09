param(
  [Parameter(Mandatory = $true)]
  [string]$Url
)

$root = Resolve-Path (Join-Path $PSScriptRoot ".")
$aspRoot = Join-Path $root "ASP"

if ($Url -notmatch "^https?://atcoder\.jp/contests/([^/]+)/tasks/([^/?#]+)") {
  Write-Error "Invalid AtCoder task URL: $Url"
  exit 1
}

$taskId = $Matches[2]
$dest = Join-Path $aspRoot $taskId
$inputDir = Join-Path $dest "input"

New-Item -ItemType Directory -Force -Path $inputDir | Out-Null

$templateMain = Join-Path $root ".template\main.py"
$mainPath = Join-Path $dest "main.py"

if (Test-Path $templateMain) {
  Copy-Item -Force $templateMain $mainPath
} elseif (-not (Test-Path $mainPath)) {
  Set-Content -Path $mainPath -Value "" -NoNewline
}

$oj = Get-Command oj -ErrorAction SilentlyContinue
if (-not $oj) {
  Write-Error "oj command not found. Install online-judge-tools first."
  exit 1
}

& $oj.Path download $Url -d $inputDir
