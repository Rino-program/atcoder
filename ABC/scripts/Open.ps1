# =============================================================================
# Open.ps1 - ブラウザ起動機能
# =============================================================================

param(
    [Parameter(Mandatory = $true)]
    [string]$ContestNumber
)

# ライブラリ読み込み
$libPath = Join-Path (Split-Path -Parent $PSScriptRoot) "lib"
. "$libPath\Common.ps1"

# 引数検証
if (-not (Test-IsNumeric $ContestNumber)) {
    Write-Error2 "数値のコンテスト番号を指定してください"
    Write-Host "使用例: .\main.ps1 open 373"
    exit 1
}

Write-Banner "🌐 ABC$ContestNumber をブラウザで開く"

# URL取得
$urls = Get-AtCoderURLs $ContestNumber

if ($urls.Count -eq 0) {
    Write-Error2 "URLの生成に失敗しました"
    exit 1
}

Write-Info "📋 開くURL:"
foreach ($url in $urls) {
    Write-Host "  • $url" -ForegroundColor Gray
}
Write-Host ""

# ブラウザでURL起動
Write-Info "🚀 ブラウザ起動中..."
try {
    Start-Browser -URLs $urls
    Write-Success "ブラウザでコンテスト+全問題を表示完了"
}
catch {
    Write-Error2 "ブラウザ起動中にエラーが発生しました: $($_.Exception.Message)"
    exit 1
}

Write-Host ""
Write-Info "💡 フォルダ内のrun.batからも起動できます:"
Write-Host "  cd ABC$ContestNumber"
Write-Host "  run.bat open"