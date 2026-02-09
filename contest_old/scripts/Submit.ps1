param(
    [Parameter(Mandatory=$true)][string]$ContestName,
    [Parameter(Mandatory=$true)][string]$Problem,
    [string]$FilePath,
    [string]$Language = "auto"
)

# Remember original location so we can restore later
$origLocation = Get-Location

# Resolve repository root (parent of scripts folder) and target contest folder
$repoRoot = Split-Path -Parent $PSScriptRoot
$contestDir = Join-Path $repoRoot $ContestName
if (-not (Test-Path $contestDir)) {
    Write-Host "[ERROR] コンテストフォルダ '$contestDir' が見つかりません" -ForegroundColor Red
    exit 1
}

# If a per-problem folder exists and contains a main file, submit from there
$probFolder = Join-Path $contestDir ($Problem.ToUpper())
if ((Test-Path $probFolder -PathType Container) -and ((Test-Path (Join-Path $probFolder 'main.py')) -or (Test-Path (Join-Path $probFolder 'main.cpp')))) {
    Set-Location $probFolder
} else {
    Set-Location $contestDir
}

# Determine problem url
$contestId = if ($ContestName -match '^[0-9]+$') { "abc$ContestName" } else { $ContestName }
$prob = $Problem.ToLower()
$problemUrl = "https://atcoder.jp/contests/$contestId/tasks/${contestId}_$prob"

# Determine file to submit
if (-not $FilePath) {
    if (($Language -eq 'auto') -or (-not $Language)) {
        if (Test-Path 'main.cpp') { $FilePath = 'main.cpp' }
        elseif (Test-Path 'main.py') { $FilePath = 'main.py' }
    } elseif ($Language -match 'py') {
        $FilePath = 'main.py'
    } else {
        $FilePath = 'main.cpp'
    }
}

if (-not (Test-Path $FilePath)) {
    Write-Host "[ERROR] 提出ファイル '$FilePath' が見つかりません" -ForegroundColor Red
    Set-Location $origLocation
    exit 1
}

Write-Host "[INFO] 提出ファイル: $FilePath" -ForegroundColor Cyan
Write-Host "[INFO] 提出先: $problemUrl" -ForegroundColor Cyan

# Prefer 'oj' if available
$oj = Get-Command oj -ErrorAction SilentlyContinue
if ($oj) {
    Write-Host "[INFO] 'oj' を使って提出します..." -ForegroundColor Cyan
    try {
        # -y to skip confirmation
        # Ensure the submitted path is relative to current directory so `oj` can detect it
        $submitPath = if ([System.IO.Path]::IsPathRooted($FilePath)) { $FilePath } else { ".\$FilePath" }
        & oj submit -y $problemUrl $submitPath
        $rc = $LASTEXITCODE
        if ($rc -eq 0) { Write-Host "[OK] 提出が完了しました (oj)" -ForegroundColor Green }
        else { Write-Host "[WARN] oj が非ゼロ終了コードを返しました: $rc" -ForegroundColor Yellow }
    } catch {
        Write-Host "[ERROR] oj による提出中にエラー: $_" -ForegroundColor Red
    }
    Set-Location $origLocation
    return
}

# Fallback to 'acc' if present
$acc = Get-Command acc -ErrorAction SilentlyContinue
if ($acc) {
    Write-Host "[INFO] 'acc' を使って提出を試みます..." -ForegroundColor Cyan
    try {
        # Try common acc invocation patterns; user may need to adjust
        & acc submit $FilePath $problemUrl
        $rc = $LASTEXITCODE
        if ($rc -eq 0) { Write-Host "[OK] 提出が完了しました (acc)" -ForegroundColor Green }
        else { Write-Host "[WARN] acc が非ゼロ終了コードを返しました: $rc" -ForegroundColor Yellow }
    } catch {
        Write-Host "[ERROR] acc による提出中にエラー: $_" -ForegroundColor Red
    }
    Set-Location $origLocation
    return
}

Write-Host "[ERROR] 'oj' も 'acc' も見つかりません。オンラインジャッジツールをインストールしてください。" -ForegroundColor Red
    Set-Location $origLocation
