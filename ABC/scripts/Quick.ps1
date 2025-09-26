# =============================================================================
# Quick.ps1 - クイックスタート機能
# =============================================================================

param(
    [Parameter(Mandatory = $true)]
    [string]$ContestName,
    
    [switch]$VSCode,
    [switch]$Browser,
    [switch]$Explorer,
    [switch]$Move
)

# ライブラリ読み込み
$libPath = Join-Path (Split-Path -Parent $PSScriptRoot) "lib"
. "$libPath\Common.ps1"
. "$libPath\VSCodeConfig.ps1"
. "$libPath\ReadmeGenerator.ps1"
. "$libPath\RunBatGenerator.ps1"

# 引数検証
if (-not (Test-ContestName $ContestName)) {
    Write-Error2 "コンテスト名を指定してください"
    Write-Host "使用例: .\main.ps1 quick 373"
    exit 1
}

Write-Banner "⚡ 瞬速コンテストスタート: $ContestName"

# パス設定
$folderPath = Join-Path (Get-Location) $ContestName
$templateDir = Get-TemplateDir
$isNumeric = Test-IsNumeric $ContestName

# フォルダ存在チェック
if (Test-Path $folderPath) {
    Write-Warning2 "フォルダ '$ContestName' は既に存在します"
} else {
    # フォルダ作成
    $success = Invoke-SafeAction {
        New-Item -ItemType Directory -Path $folderPath | Out-Null
    } "フォルダ作成中にエラー"
    
    if (-not $success) { 
        exit 1 
    }
    Write-Success "フォルダを作成: $ContestName"
    
    # テンプレートファイルコピー
    if (Copy-TemplateFiles -SourceDir $templateDir -DestDir $folderPath) {
        Write-Success "テンプレートファイルをコピー完了"
    } else {
        Write-Error2 "テンプレートファイルのコピーに失敗"
        exit 1
    }
    
    # VS Code設定生成
    $vscodeResult = New-VSCodeConfig -FolderPath $folderPath -ContestName $ContestName -IsNumeric $isNumeric
    if ($vscodeResult.Success) {
        Write-Success "VS Code設定を生成 (.vscode/tasks.json, launch.json)"
    } else {
        Write-Warning2 "VS Code設定の生成に失敗: $($vscodeResult.Error)"
    }
    
    # run.bat生成
    $runBatResult = New-RunBat -FolderPath $folderPath -ContestName $ContestName -IsNumeric $isNumeric
    if ($runBatResult.Success) {
        Write-Success "高機能run.batを生成"
    } else {
        Write-Warning2 "run.bat生成に失敗: $($runBatResult.Error)"
    }
    
    # README.md生成
    $readmeResult = New-ContestReadme -ContestName $ContestName -FolderPath $folderPath -IsNumeric $isNumeric
    if ($readmeResult.Success) {
        Write-Success "詳細README.mdを生成"
    } else {
        Write-Warning2 "README.md生成に失敗: $($readmeResult.Error)"
    }
}

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

# フォルダ移動
if ($Move) {
    Write-Info "📂 作業フォルダに移動中..."
    try {
        Set-Location $folderPath
        Write-Success "フォルダに移動: $folderPath"
    }
    catch {
        Write-Warning2 "フォルダ移動に失敗: $($_.Exception.Message)"
    }
}

Write-Banner "🎯 セットアップ完了！競技プログラミングを開始しましょう！"