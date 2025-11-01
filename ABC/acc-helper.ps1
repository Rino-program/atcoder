# =============================================================================
# AtCoder oj+acc 統合スクリプト
# =============================================================================
# このスクリプトは、atcoder-cli (acc) と online-judge-tools (oj) を
# 既存の main.ps1 システムと統合するためのヘルパー関数を提供します
# =============================================================================

param(
    [Parameter(Position = 0)] [string]$Command,
    [Parameter(Position = 1)] [string]$ContestID,
    [Parameter(Position = 2)] [string]$Problem,
    [switch]$VSCode = $false
)

function Show-Help {
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "  AtCoder oj+acc 統合コマンド" -ForegroundColor Yellow
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🎯 基本コマンド" -ForegroundColor Magenta
    Write-Host "  download <contestID>        : 問題をダウンロード (acc new)" -ForegroundColor White
    Write-Host "  test <contestID> <problem>  : テストを実行 (oj t)" -ForegroundColor White
    Write-Host "  submit <contestID> <problem>: 提出 (acc s)" -ForegroundColor White
    Write-Host "  login                       : ログイン設定" -ForegroundColor White
    Write-Host ""
    Write-Host "💡 使用例" -ForegroundColor Yellow
    Write-Host "  .\acc-helper.ps1 download 373" -ForegroundColor White
    Write-Host "  .\acc-helper.ps1 test 373 a" -ForegroundColor White
    Write-Host "  .\acc-helper.ps1 submit 373 a" -ForegroundColor White
    Write-Host "  .\acc-helper.ps1 login" -ForegroundColor White
    Write-Host ""
}

function Download-Contest {
    param([string]$ContestID)
    
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "  📥 コンテストをダウンロード: ABC$ContestID" -ForegroundColor Yellow
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    
    acc new "abc$ContestID"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ ダウンロード完了！" -ForegroundColor Green
        Write-Host ""
        Write-Host "次のステップ:" -ForegroundColor Yellow
        Write-Host "  cd abc$ContestID\a" -ForegroundColor White
        Write-Host "  code main.cpp (または main.py)" -ForegroundColor White
        
        if ($VSCode) {
            Start-Process code "abc$ContestID"
        }
    } else {
        Write-Host "❌ ダウンロード失敗" -ForegroundColor Red
    }
}

function Test-Problem {
    param(
        [string]$ContestID,
        [string]$Problem
    )
    
    $contestDir = "abc$ContestID"
    $problemDir = Join-Path $contestDir $Problem.ToLower()
    
    if (-not (Test-Path $problemDir)) {
        Write-Host "❌ フォルダが見つかりません: $problemDir" -ForegroundColor Red
        return
    }
    
    Push-Location $problemDir
    
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "  🧪 テスト実行: ABC$ContestID - $($Problem.ToUpper())" -ForegroundColor Yellow
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    
    # C++ファイルがあるか確認
    if (Test-Path "main.cpp") {
        Write-Host "📝 C++でテスト実行" -ForegroundColor Cyan
        Write-Host "コンパイル中..." -ForegroundColor Gray
        g++ main.cpp
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ コンパイル成功" -ForegroundColor Green
            Write-Host "テスト実行中..." -ForegroundColor Gray
            oj t
        } else {
            Write-Host "❌ コンパイルエラー" -ForegroundColor Red
        }
    } elseif (Test-Path "main.py") {
        Write-Host "📝 Python(PyPy)でテスト実行" -ForegroundColor Cyan
        $pypyPath = "..\..\\.venv-pypy310\Scripts\python.exe"
        
        if (Test-Path $pypyPath) {
            oj t -c "$pypyPath main.py"
        } else {
            Write-Host "⚠️ PyPy環境が見つからないため、デフォルトのPythonを使用します" -ForegroundColor Yellow
            oj t -c "python main.py"
        }
    } else {
        Write-Host "❌ main.cpp または main.py が見つかりません" -ForegroundColor Red
    }
    
    Pop-Location
}

function Submit-Problem {
    param(
        [string]$ContestID,
        [string]$Problem
    )
    
    $contestDir = "abc$ContestID"
    $problemDir = Join-Path $contestDir $Problem.ToLower()
    
    if (-not (Test-Path $problemDir)) {
        Write-Host "❌ フォルダが見つかりません: $problemDir" -ForegroundColor Red
        return
    }
    
    Push-Location $problemDir
    
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "  📤 提出: ABC$ContestID - $($Problem.ToUpper())" -ForegroundColor Yellow
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    
    if (Test-Path "main.cpp") {
        Write-Host "📝 C++ファイルを提出" -ForegroundColor Cyan
        acc s main.cpp
    } elseif (Test-Path "main.py") {
        Write-Host "📝 Pythonファイルを提出" -ForegroundColor Cyan
        acc s main.py
    } else {
        Write-Host "❌ main.cpp または main.py が見つかりません" -ForegroundColor Red
    }
    
    Pop-Location
}

function Setup-Login {
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "  🔐 ログイン設定" -ForegroundColor Yellow
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "ステップ1: atcoder-cli (acc) にログイン" -ForegroundColor Cyan
    acc login
    
    Write-Host ""
    Write-Host "ステップ2: online-judge-tools (oj) にログイン" -ForegroundColor Cyan
    Write-Host "(ブラウザが開くので、AtCoderにログインしてください)" -ForegroundColor Gray
    oj login https://atcoder.jp/
    
    Write-Host ""
    Write-Host "✅ ログイン設定完了！" -ForegroundColor Green
}

# ===== メイン処理 =====
if (-not $Command) {
    Show-Help
    exit
}

$cmd = $Command.ToLower()

switch ($cmd) {
    "download" {
        if (-not $ContestID) {
            Write-Host "❌ コンテストIDが必要です" -ForegroundColor Red
            Write-Host "使用例: .\acc-helper.ps1 download 373" -ForegroundColor Yellow
            exit 1
        }
        Download-Contest -ContestID $ContestID
    }
    "test" {
        if (-not ($ContestID -and $Problem)) {
            Write-Host "❌ コンテストIDと問題が必要です" -ForegroundColor Red
            Write-Host "使用例: .\acc-helper.ps1 test 373 a" -ForegroundColor Yellow
            exit 1
        }
        Test-Problem -ContestID $ContestID -Problem $Problem
    }
    "submit" {
        if (-not ($ContestID -and $Problem)) {
            Write-Host "❌ コンテストIDと問題が必要です" -ForegroundColor Red
            Write-Host "使用例: .\acc-helper.ps1 submit 373 a" -ForegroundColor Yellow
            exit 1
        }
        Submit-Problem -ContestID $ContestID -Problem $Problem
    }
    "login" {
        Setup-Login
    }
    default {
        Show-Help
    }
}
