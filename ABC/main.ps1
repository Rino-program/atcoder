# ============================================================    Write-Host "🎯 " -NoNewline -ForegroundColor Magenta
    Write-Host "基本コマンド:" -ForegroundColor White
    Write-Host "  new [名前]                       - コンテストフォルダ作成"
    Write-Host "  test [名前] [問題] [言語]        - テスト実行（複数ケース・TLE判定）"
    Write-Host "  open [番号]                      - ブラウザでコンテストを開く"
    Write-Host "  generate [名前] [問題]           - テストケース自動生成"
    Write-Host "  validate [対象]                  - ライブラリ検証"
    Write-Host "  clean                            - 一時ファイル削除"
    Write-Host ""==========
# main.    { $_ -in @("clean", "cl") } {
        & "$scriptsPath\Clean.ps1"
    }
    
    { $_ -in @("generate", "gen", "g") } {
        if (-not $ContestName -or -not $Problem) {
            Write-Host "❌ generate コマンドにはコンテスト名と問題が必要です" -ForegroundColor Red
            Write-Host "使用例: .\main.ps1 generate 373 A" -ForegroundColor Yellow
            exit 1
        }
        & "$libPath\TestCaseGenerator.ps1" -ContestNumber $ContestName -Problem $Problem.ToUpper()
    }
    
    { $_ -in @("validate", "val", "v") } {
        if (-not $Problem) {
            $Problem = "All"
        }
        & "$libPath\LibraryValidator.ps1" -TestTarget $Problem -Language $Language
    }
    
    { $_ -in @("help", "h", "?") -or $_ -eq "" } {
        Show-HelpAtCoder ABC 多機能統合システム v4.0 メインエントリポイント
# =============================================================================

param(
    [Parameter(Position = 0, Mandatory = $false)]
    [string]$Command,
    
    [Parameter(Position = 1, Mandatory = $false)]
    [string]$ContestName,
    
    [Parameter(Position = 2, Mandatory = $false)]
    [string]$Problem,
    
    [Parameter(Position = 3, Mandatory = $false)]
    [string]$Language = "cpp",
    
    [switch]$VSCode,
    [switch]$Browser,
    [switch]$Explorer,
    [switch]$Move,
    [switch]$Generate  # テストケース生成用
)

# ライブラリ読み込み
$libPath = Join-Path $PSScriptRoot "lib"
. "$libPath\Common.ps1"
. "$libPath\VSCodeConfig.ps1"
. "$libPath\ReadmeGenerator.ps1" 
. "$libPath\RunBatGenerator.ps1"

# スクリプトパス
$scriptsPath = Join-Path $PSScriptRoot "scripts"

# バージョン情報
$VERSION = "4.0"

# ヘルプ表示
function Show-Help {
    Write-Header "AtCoder ABC 多機能統合システム v$VERSION"
    
    Write-Host "� " -NoNewline -ForegroundColor Magenta
    Write-Host "基本コマンド:" -ForegroundColor White
    Write-Host "  new [名前]                       - コンテストフォルダ作成"
    Write-Host "  test [名前] [問題] [言語]        - テスト実行（複数ケース・TLE判定）"
    Write-Host "  open [番号]                      - ブラウザでコンテストを開く"
    Write-Host "  clean                            - 一時ファイル削除"
    Write-Host ""
    
    Write-Host "💡 " -NoNewline -ForegroundColor Yellow
    Write-Host "使用例:" -ForegroundColor White
    Write-Host "  .\main.ps1 new 373               # ABC373フォルダ作成"
    Write-Host "  .\main.ps1 new JOI -VSCode       # 練習用フォルダ作成+VS Code起動"
    Write-Host "  .\main.ps1 test 373 a cpp        # ABC373のA問題をC++でテスト"
    Write-Host "  .\main.ps1 test 373 b py         # ABC373のB問題をPythonでテスト"
    Write-Host "  .\main.ps1 open 373              # ABC373を全問題ブラウザで開く"
    Write-Host ""
    
    Write-Host "🎯 " -NoNewline -ForegroundColor Green
    Write-Host "オプション:" -ForegroundColor White
    Write-Host "  -VSCode                          # VS Code自動起動"
    Write-Host "  -Browser                         # ブラウザ自動起動" 
    Write-Host "  -Explorer                        # エクスプローラー起動"
    Write-Host ""
    
    Write-Host "🔥 " -NoNewline -ForegroundColor Red
    Write-Host "特殊機能:" -ForegroundColor White
    Write-Host "  • 複数テストケース対応"
    Write-Host "  • 実行時間測定・TLE判定"
    Write-Host "  • 自動README生成（コンテスト情報・メモ用）"
    Write-Host "  • 高品質C++/Pythonテンプレート"
    Write-Host ""
}

# メイン処理
switch ($Command.ToLower()) {
    { $_ -in @("new", "n", "create", "c") } {
        & "$scriptsPath\New.ps1" -ContestName $ContestName -VSCode:$VSCode -Browser:$Browser -Explorer:$Explorer
    }
    
    { $_ -in @("test", "t", "run", "r") } {
        & "$scriptsPath\Test.ps1" -ContestName $ContestName -Problem $Problem -Language $Language
    }
    
    { $_ -in @("open", "o", "browse", "b") } {
        & "$scriptsPath\Open.ps1" -ContestNumber $ContestName
    }
    
    { $_ -in @("clean", "cl") } {
        & "$scriptsPath\Clean.ps1"
    }
    
    { $_ -in @("generate", "gen", "g") } {
        if (-not $ContestName -or -not $Problem) {
            Write-Host "❌ generate コマンドにはコンテスト名と問題が必要です" -ForegroundColor Red
            Write-Host "使用例: .\main.ps1 generate 373 A" -ForegroundColor Yellow
            exit 1
        }
        & "$libPath\TestCaseGenerator.ps1" -ContestNumber $ContestName -Problem $Problem.ToUpper()
    }
    
    { $_ -in @("validate", "val", "v") } {
        if (-not $Problem) {
            $Problem = "All"
        }
        & "$libPath\LibraryValidator.ps1" -TestTarget $Problem -Language $Language
    }
    
    { $_ -in @("help", "h", "?") -or $_ -eq "" } {
        Show-Help
    }
    
    default {
        Write-Error2 "未知のコマンド: $Command"
        Write-Host "ヘルプを表示: .\main.ps1 help"
    }
}