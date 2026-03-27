param(
  [Parameter(Mandatory = $true)]
  [string]$Url
)

$scriptDir = (Resolve-Path (Join-Path $PSScriptRoot ".")).Path
$cwd = (Get-Location).Path

if ((Split-Path -Leaf $cwd) -ieq "ASP") {
  $aspRoot = $cwd
  $root = (Resolve-Path (Join-Path $aspRoot "..")).Path
} elseif (Test-Path (Join-Path $scriptDir "ASP")) {
  $root = $scriptDir
  $aspRoot = Join-Path $root "ASP"
} elseif ((Split-Path -Leaf $scriptDir) -ieq "ASP") {
  $aspRoot = $scriptDir
  $root = (Resolve-Path (Join-Path $aspRoot "..")).Path
} else {
  Write-Error "Cannot determine root/ASP directory. Run this script from ASP or place asp.ps1 under contests/."
  exit 1
}

if ($Url -notmatch "^https?://atcoder\.jp/contests/([^/]+)/tasks/([^/?#]+)") {
  Write-Error "Invalid AtCoder task URL: $Url"
  exit 1
}

$contestId = $Matches[1]
$taskId = $Matches[2]
$dest = Join-Path $aspRoot $taskId
$inputDir = Join-Path $dest "input"

New-Item -ItemType Directory -Force -Path $inputDir | Out-Null

$templateVscode = Join-Path $root ".templateASP\.vscode"
$destVscode = Join-Path $dest ".vscode"
if (Test-Path $templateVscode) {
  Copy-Item -Recurse -Force $templateVscode $destVscode
}

# Note: tasks.json is already copied from .templateASP/.vscode, so we don't need to recreate it

$templateMainSource = Join-Path $root ".template\main.py"
$templatePySource = Join-Path $root ".template\template.py"
$mainPath = Join-Path $dest "main.py"
$templatePath = Join-Path $dest "template.py"

if (Test-Path $templateMainSource) {
  Copy-Item -Force $templateMainSource $mainPath
} elseif (Test-Path $templatePySource) {
  Copy-Item -Force $templatePySource $mainPath
} elseif (-not (Test-Path $mainPath)) {
  Set-Content -Path $mainPath -Value "" -NoNewline
}

if (Test-Path $templatePySource) {
  Copy-Item -Force $templatePySource $templatePath
}

$oj = Get-Command oj -ErrorAction SilentlyContinue
if (-not $oj) {
  Write-Error "oj command not found. Install online-judge-tools first."
  exit 1
}

& $oj.Path download $Url -d $inputDir
