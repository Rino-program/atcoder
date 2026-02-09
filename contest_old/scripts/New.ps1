# =============================================================================
# New.ps1 - コンテストフォルダ作成機能
# =============================================================================

param(
    [Parameter(Mandatory = $true)]
    [string]$ContestName,
    
    [switch]$VSCode,
    [switch]$Browser,
    [switch]$Explorer,
    [switch]$Fetch
)

# ライブラリ読み込み
$libPath = Join-Path (Split-Path -Parent $PSScriptRoot) "lib"
. "$libPath\Common.ps1"
. "$libPath\VSCodeConfig.ps1"
. "$libPath\ReadmeGenerator.ps1"
. "$libPath\RunBatGenerator.ps1"

# スクリプトディレクトリ
$scriptsPath = Join-Path (Split-Path -Parent $PSScriptRoot) "scripts"

# 引数検証
if (-not (Test-ContestName $ContestName)) {
    Write-Error2 "コンテスト名を指定してください"
    Write-Host "使用例: .\main.ps1 new 373"
    exit 1
}

Write-Banner "📁 コンテストフォルダ作成: $ContestName"

# パス設定
$folderPath = Join-Path (Get-Location) $ContestName
$templateDir = Get-TemplateDir
$isNumeric = Test-IsNumeric $ContestName

# フォルダ存在チェック
if (Test-Path $folderPath) {
    Write-Error2 "フォルダ '$ContestName' は既に存在します"
    exit 1
}

# フォルダ作成
$success = Invoke-SafeAction {
    New-Item -ItemType Directory -Path $folderPath | Out-Null
} "フォルダ作成中にエラー"

if (-not $success) { 
    exit 1 
}
Write-Success "フォルダを作成: $ContestName"

# 各問題ごとにフォルダを作成し、テンプレートを配置
try {
    $tcRoot = Join-Path $folderPath 'testcases'
    if (-not (Test-Path $tcRoot)) { New-Item -Path $tcRoot -ItemType Directory | Out-Null }

    $probs = Get-ContestProblems -ContestName $ContestName
    foreach ($p in $probs) {
        $prob = $p.ToString().ToUpper()
        # 問題用フォルダ (例: <Contest>\A)
        $probDir = Join-Path $folderPath $prob
        if (-not (Test-Path $probDir)) { New-Item -Path $probDir -ItemType Directory | Out-Null }

        # コピー先として問題フォルダにテンプレートファイルを配置
        if (Copy-TemplateFiles -SourceDir $templateDir -DestDir $probDir) {
            Write-Success "テンプレートを $probDir に配置"
        } else {
            Write-Warning2 "テンプレートのコピーに失敗: $probDir"
        }

        # 問題フォルダ内に testcases ディレクトリ (ユーザがここで `oj d` を叩けるように)
        $localTc = Join-Path $probDir 'testcases'
        if (-not (Test-Path $localTc)) { New-Item -Path $localTc -ItemType Directory | Out-Null }

        # ルートの testcases/<Prob> も作成しておく（既存スクリプト互換用）
        $rootProbTc = Join-Path $tcRoot $prob
        if (-not (Test-Path $rootProbTc)) { New-Item -Path $rootProbTc -ItemType Directory | Out-Null }
    }
    Write-Success "問題ごとのフォルダと testcases を作成しました"
} catch {
    Write-Warning2 "問題フォルダの作成に失敗: $_"
}

# VS Code設定生成 (ルートと各問題フォルダに対して最低限生成する)
$vscodeResult = New-VSCodeConfig -FolderPath $folderPath -ContestName $ContestName -IsNumeric $isNumeric
if ($vscodeResult.Success) { Write-Success "ルートの VS Code 設定を生成" } else { Write-Warning2 "VS Code設定の生成に失敗: $($vscodeResult.Error)" }

$probs | ForEach-Object {
    $prob = $_.ToString().ToUpper()
    $probDir = Join-Path $folderPath $prob
    $v = New-VSCodeConfig -FolderPath $probDir -ContestName $ContestName -IsNumeric $isNumeric
    if ($v.Success) { Write-Success "VS Code 設定を $probDir に生成" } else { Write-Warning2 "VS Code 設定生成失敗: $probDir : $($v.Error)" }
}

# README.md生成（コンテスト情報・メモ用）
$readmeResult = New-ContestReadme -ContestName $ContestName -FolderPath $folderPath -IsNumeric $isNumeric
if ($readmeResult.Success) { Write-Success "コンテスト情報README.mdを生成" } else { Write-Warning2 "README.md生成に失敗: $($readmeResult.Error)" }

# ブラウザ起動
if ($Browser -and $isNumeric) {
    Write-Info "🌐 ブラウザでABC$ContestName の全問題を開いています..."
    $urls = Get-AtCoderURLs $ContestName
    if ($urls.Count -gt 0) {
        Start-Browser -URLs $urls
        Write-Success "ブラウザでコンテスト+全問題を表示"
    }
} elseif ($Browser) {
    Write-Warning2 "非数値コンテスト名のためブラウザ機能は無効"
}

# VS Code起動
if ($VSCode) {
    Write-Info "💻 VS Codeでフォルダを開いています..."
    $success = Invoke-SafeAction {
        Start-Process code -ArgumentList $folderPath
    } "VS Code起動エラー"
    
    if ($success) {
        Write-Success "VS Codeを起動"
    }
}

# エクスプローラー起動  
if ($Explorer) {
    Write-Info "📁 エクスプローラーでフォルダを開いています..."
    $success = Invoke-SafeAction {
        Start-Process explorer.exe -ArgumentList $folderPath
    } "エクスプローラー起動エラー"
    
    if ($success) {
        Write-Success "エクスプローラーを起動"
    }
}

Write-Success "コンテストフォルダ '$ContestName' の作成が完了しました"
Write-Host ""
Write-Info "💡 次のステップ:"
Write-Host "  cd $ContestName                          # フォルダに移動"
Write-Host "  ..\main.ps1 test $ContestName a cpp      # A問題をテスト実行"

if ($Fetch) {
    Write-Info "📥 サンプルテストケースをダウンロードしています..."
    & "$scriptsPath\Fetch.ps1" -ContestName $ContestName
}