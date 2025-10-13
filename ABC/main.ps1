# =============================================================================
# main.ps1 - AtCoder ABC 多機能統合システム v4.1 メインエントリポイント
# =============================================================================
param(
    [Parameter(Position = 0)] [string]$Command,
    [Parameter(Position = 1)] [string]$ContestName,
    [Parameter(Position = 2)] [string]$Problem,
    [Parameter(Position = 3)] [string]$Language = "cpp",
    [switch]$VSCode = $false,
    [switch]$Browser = $false,
    [switch]$Explorer = $false
)

if (-not $Command) { $Command = "help" }

# ===== パス設定 =====
$libPath = Join-Path $PSScriptRoot "lib"
$scriptsPath = Join-Path $PSScriptRoot "scripts"
$VERSION = "4.1"

# ===== ライブラリ読み込み =====
. "$libPath/Common.ps1"
. "$libPath/VSCodeConfig.ps1"
. "$libPath/ReadmeGenerator.ps1"
. "$libPath/RunBatGenerator.ps1"

function Show-Help {
    Write-Header "AtCoder ABC 多機能統合システム v$VERSION"

    Write-Host "🎯 基本コマンド" -ForegroundColor Magenta
    Write-Host "  new|n <contest>                 : コンテスト/練習フォルダ作成" -ForegroundColor White
    Write-Host "  test|t <contest> <prob> <lang>  : テスト実行 (cpp/py)" -ForegroundColor White
    Write-Host "  open|o <contest>                : ブラウザで問題一覧を開く" -ForegroundColor White
    Write-Host "  generate|gen <contest> <prob>   : テストケース自動生成" -ForegroundColor White
    Write-Host "  validate|val [target]           : ライブラリ検証 (DSU/BIT/All)" -ForegroundColor White
    Write-Host "  clean|cl                        : 一時ファイル削除" -ForegroundColor White
    Write-Host "  help|h|?                        : このヘルプ" -ForegroundColor White
    Write-Host ""

    Write-Host "💡 使用例" -ForegroundColor Yellow
    Write-Host "  .\\main.ps1 new 373 -VSCode" -ForegroundColor White
    Write-Host "  .\\main.ps1 test 373 a cpp" -ForegroundColor White
    Write-Host "  .\\main.ps1 test 373 b py" -ForegroundColor White
    Write-Host "  .\\main.ps1 generate 373 A" -ForegroundColor White
    Write-Host "  .\\main.ps1 validate DSU" -ForegroundColor White
    Write-Host ""

    Write-Host "🔥 機能" -ForegroundColor Red
    Write-Host "  • 複数テストケース & TLE判定" -ForegroundColor White
    Write-Host "  • README自動生成 / 記録補助" -ForegroundColor White
    Write-Host "  • C++ / Python 高品質テンプレ" -ForegroundColor White
    Write-Host "  • ライブラリ自動検証 & ケース生成" -ForegroundColor White
}

# ===== 入力正規化 =====
$cmd = $Command.ToLower()

switch ($cmd) {
    "new" { $cmd = "new" }
    "n" { $cmd = "new" }
    "create" { $cmd = "new" }
    "c" { $cmd = "new" }

    "test" { $cmd = "test" }
    "t" { $cmd = "test" }
    "run" { $cmd = "test" }
    "r" { $cmd = "test" }

    "open" { $cmd = "open" }
    "o" { $cmd = "open" }
    "browse" { $cmd = "open" }
    "b" { $cmd = "open" }

    "generate" { $cmd = "generate" }
    "gen" { $cmd = "generate" }
    "g" { $cmd = "generate" }

    "validate" { $cmd = "validate" }
    "val" { $cmd = "validate" }
    "v" { $cmd = "validate" }

    "clean" { $cmd = "clean" }
    "cl" { $cmd = "clean" }

    "help" { $cmd = "help" }
    "h" { $cmd = "help" }
    "?" { $cmd = "help" }
}

# ===== コマンド実行 =====
try {
    switch ($cmd) {
        "new" {
            if (-not $ContestName) { Write-Error2 "コンテスト名が必要です"; return }
            & "$scriptsPath/New.ps1" -ContestName $ContestName -VSCode:$VSCode -Browser:$Browser -Explorer:$Explorer
        }
        "test" {
            if (-not ($ContestName -and $Problem)) { Write-Error2 "test には <contest> <problem> が必要"; return }
            & "$scriptsPath/Test.ps1" -ContestName $ContestName -Problem $Problem -Language $Language
        }
        "open" {
            if (-not $ContestName) { Write-Error2 "open には <contest> が必要"; return }
            & "$scriptsPath/Open.ps1" -ContestNumber $ContestName
        }
        "generate" {
            if (-not ($ContestName -and $Problem)) { Write-Error2 "generate には <contest> <problem> が必要"; return }
            & "$libPath/TestCaseGenerator.ps1" -ContestNumber $ContestName -Problem $Problem.ToUpper()
        }
        "validate" {
            $target = if ($Problem) { $Problem } else { "All" }
            & "$libPath/LibraryValidator.ps1" -TestTarget $target -Language $Language
        }
        "clean" {
            & "$scriptsPath/Clean.ps1"
        }
        default {
            Show-Help
        }
    }
}
catch {
    Write-Host "❌ 実行中にエラーが発生: $_" -ForegroundColor Red
}