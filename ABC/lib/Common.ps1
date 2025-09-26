# =============================================================================
# Common.ps1 - AtCoder ABC 共通機能ライブラリ
# =============================================================================

# カラー出力関数
function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Error2 {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Warning2 {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Cyan
}

function Write-Banner {
    param([string]$Message)
    Write-Host ""
    Write-Host "🚀 $Message" -ForegroundColor Magenta
    Write-Host ""
}

function Write-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host "=" * 60 -ForegroundColor Blue
    Write-Host " $Message" -ForegroundColor White
    Write-Host "=" * 60 -ForegroundColor Blue
    Write-Host ""
}

# パス関連関数
function Get-ScriptRoot {
    return Split-Path -Parent $PSScriptRoot
}

function Get-TemplateDir {
    return Join-Path (Get-ScriptRoot) "templates"
}

function Get-LibDir {
    return Join-Path (Get-ScriptRoot) "lib"
}

# コンテスト名検証
function Test-ContestName {
    param([string]$Name)
    if ([string]::IsNullOrWhiteSpace($Name)) {
        return $false
    }
    return $true
}

function Test-IsNumeric {
    param([string]$Value)
    return $Value -match '^\d+$'
}

# ファイル操作
function Copy-TemplateFiles {
    param(
        [string]$SourceDir,
        [string]$DestDir
    )
    
    if (-not (Test-Path $SourceDir)) {
        Write-Warning2 "テンプレートフォルダが見つかりません: $SourceDir"
        return $false
    }
    
    try {
        Get-ChildItem $SourceDir | ForEach-Object {
            if ($_.Name -notin @("vscode_tasks.ps1", ".gitkeep")) {
                Copy-Item $_.FullName -Destination $DestDir -Force -Recurse
            }
        }
        return $true
    }
    catch {
        Write-Error2 "テンプレートファイルのコピーに失敗しました: $($_.Exception.Message)"
        return $false
    }
}

# URL関連
function Get-AtCoderURLs {
    param([string]$ContestNumber)
    
    if (-not (Test-IsNumeric $ContestNumber)) {
        return @()
    }
    
    return @(
        "https://atcoder.jp/contests/abc$ContestNumber/tasks",
        "https://atcoder.jp/contests/abc$ContestNumber/tasks/abc$($ContestNumber)_a",
        "https://atcoder.jp/contests/abc$ContestNumber/tasks/abc$($ContestNumber)_b",
        "https://atcoder.jp/contests/abc$ContestNumber/tasks/abc$($ContestNumber)_c",
        "https://atcoder.jp/contests/abc$ContestNumber/tasks/abc$($ContestNumber)_d"
    )
}

# ブラウザ起動
function Start-Browser {
    param([string[]]$URLs)
    
    foreach ($url in $URLs) {
        try {
            Start-Process $url
            Start-Sleep -Milliseconds 400
        }
        catch {
            Write-Warning2 "URL起動に失敗: $url"
        }
    }
}

# 日付文字列生成
function Get-DateString {
    return Get-Date -Format "yyyy年M月d日 HH:mm"
}

# エラーハンドリング
function Invoke-SafeAction {
    param(
        [scriptblock]$Action,
        [string]$ErrorMessage = "操作中にエラーが発生しました"
    )
    
    try {
        & $Action
        return $true
    }
    catch {
        Write-Error2 "$ErrorMessage : $($_.Exception.Message)"
        return $false
    }
}