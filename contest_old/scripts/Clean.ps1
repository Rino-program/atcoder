# =============================================================================
# Clean.ps1 - 一時ファイル削除機能
# =============================================================================

# ライブラリ読み込み
$libPath = Join-Path (Split-Path -Parent $PSScriptRoot) "lib"
. "$libPath\Common.ps1"

Write-Banner "🧹 一時ファイルクリーンアップ"

$cleanTargets = @(
    "main.exe",
    "a.out",
    "*.obj",
    "*.pdb",
    "*.ilk",
    "*.pyc",
    "__pycache__",
    "*.tmp",
    "*.log"
)

$totalCleaned = 0

# 現在のディレクトリから清掃
Write-Info "現在のディレクトリをクリーンアップ中..."
foreach ($pattern in $cleanTargets) {
    $files = Get-ChildItem $pattern -Recurse -Force -ErrorAction SilentlyContinue
    if ($files.Count -gt 0) {
        foreach ($file in $files) {
            # 仮想環境や依存フォルダは絶対に削除しない
            $full = $file.FullName
            if ($full -match "\\\.venv(\\|$)" -or $full -match "\\venv(\\|$)" -or $full -match "\\.venv-[^\\]+\\") {
                continue
            }
            try {
                Remove-Item $file.FullName -Force -Recurse -ErrorAction SilentlyContinue
                Write-Host "  削除: $($file.Name)" -ForegroundColor Gray
                $totalCleaned++
            }
            catch {
                Write-Warning2 "削除失敗: $($file.Name)"
            }
        }
    }
}

# VS Code一時ファイル削除
$vscodeDirs = Get-ChildItem ".vscode" -Directory -Recurse -ErrorAction SilentlyContinue
foreach ($dir in $vscodeDirs) {
    $tempFiles = Get-ChildItem "$($dir.FullName)\*.tmp" -ErrorAction SilentlyContinue
    foreach ($file in $tempFiles) {
        try {
            Remove-Item $file.FullName -Force
            Write-Host "  削除: $($file.Name)" -ForegroundColor Gray
            $totalCleaned++
        }
        catch {
            Write-Warning2 "削除失敗: $($file.Name)"
        }
    }
}

if ($totalCleaned -gt 0) {
    Write-Success "クリーンアップ完了: $totalCleaned ファイル削除"
} else {
    Write-Info "削除する一時ファイルは見つかりませんでした"
}

Write-Host ""
Write-Info "💡 クリーンアップ対象:"
foreach ($target in $cleanTargets) {
    Write-Host "  • $target" -ForegroundColor Gray
}