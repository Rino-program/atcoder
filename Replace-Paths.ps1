# 置換対象の文字列と置換後の文字列を定義
# パターン1: ダブルバックスラッシュ (\\)
$oldPath1 = 'C:\\VSCode_program\\atcoder\\'
$newPath1 = 'C:\\Rino-program\\AtCoder\\'

# パターン2: シングルバックスラッシュ (\)
$oldPath2 = 'C:\VSCode_program\atcoder'
$newPath2 = 'C:\Rino-program\AtCoder\'

# 現在実行中のスクリプト自身のファイルパスを取得
$scriptPath = $MyInvocation.MyCommand.Path

Write-Host "ファイルの一覧を取得中..." -ForegroundColor Cyan
# 現在のディレクトリ以下のすべてのファイルを取得
$files = Get-ChildItem -File -Recurse

$totalFiles = $files.Count
$currentIndex = 0
$updatedCount = 0

Write-Host "ファイルの検索と置換を開始します（全 $totalFiles 個のファイル）..." -ForegroundColor Cyan
Write-Host "--------------------------------------------------"

foreach ($file in $files) {
    $currentIndex++
    $filePath = $file.FullName
    
    # 進行状況を上部のプログレスバーに表示
    $percent = [Math]::Round(($currentIndex / $totalFiles) * 100)
    Write-Progress -Activity "ファイルをスキャン中..." `
                   -Status "処理中: $currentIndex / $totalFiles ($percent%)" `
                   -PercentComplete $percent

    # 処理中のファイルが、このスクリプト自身である場合はスキップ
    if ($filePath -eq $scriptPath) {
        continue
    }
    
    # ファイル内容を単一の文字列として読み込む
    $content = Get-Content -Path $filePath -Raw -Encoding UTF8

    # 空のファイルなどはスキップし、対象の文字列が含まれているかチェック
    if ($null -ne $content -and ($content.Contains($oldPath1) -or $content.Contains($oldPath2))) {
        
        # 文字列の置換を実行
        $updatedContent = $content.Replace($oldPath1, $newPath1)
        $updatedContent = $updatedContent.Replace($oldPath2, $newPath2)

        # ファイルを上書き保存
        Set-Content -Path $filePath -Value $updatedContent -Encoding UTF8
        
        Write-Host "[更新完了] $filePath" -ForegroundColor Green
        $updatedCount++
    }
}

# プログレスバーを閉じる
Write-Progress -Activity "ファイルをスキャン中..." -Completed

Write-Host "--------------------------------------------------"
Write-Host "すべての処理が完了しました。" -ForegroundColor Cyan
Write-Host "スキャンしたファイル数: $totalFiles" -ForegroundColor Whit
Write-Host "置換したファイル数: $updatedCount" -ForegroundColor Green