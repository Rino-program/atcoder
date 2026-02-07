# =============================================================================
# Test.ps1 - 高機能テスト実行（複数ケース・TLE判定対応）
# =============================================================================

param(
    [Parameter(Mandatory = $true)]
    [string]$ContestName,
    
    [Parameter(Mandatory = $true)]
    [string]$Problem,
    
    [Parameter(Mandatory = $false)]
    [string]$Language = "cpp"
)

# ライブラリ読み込み
$libPath = Join-Path (Split-Path -Parent $PSScriptRoot) "lib"
. "$libPath\Common.ps1"

# 引数検証
$problem = $Problem.ToLower()
if ($problem -notin @("a", "b", "c", "d")) {
    Write-Error2 "問題は a, b, c, d のいずれかを指定してください"
    Write-Host "使用例: .\main.ps1 test 373 a cpp"
    exit 1
}

$lang = $Language.ToLower()
if ($lang -notin @("cpp", "c++", "py", "python")) {
    Write-Error2 "言語は cpp, c++, py, python のいずれかを指定してください"
    exit 1
}

# フォルダ確認
$contestDir = $ContestName
if (-not (Test-Path $contestDir)) {
    Write-Error2 "コンテストフォルダ '$ContestName' が見つかりません"
    Write-Host "先に .\main.ps1 new $ContestName でフォルダを作成してください"
    exit 1
}

Write-Banner "🧪 $ContestName - $($problem.ToUpper())問題テスト実行 ($lang)"

# フォルダに移動
Set-Location $contestDir

# 入力ファイル検索
$inputFiles = Get-ChildItem "in_$problem*.txt" -ErrorAction SilentlyContinue
if ($inputFiles.Count -eq 0) {
    Write-Error2 "テスト入力ファイル 'in_$problem*.txt' が見つかりません"
    Write-Info "例: in_${problem}_1.txt, in_${problem}_2.txt または in_$problem.txt"
    Set-Location ..
    exit 1
}

Write-Info "� 見つかったテスト入力: $($inputFiles.Count)個"
foreach ($file in $inputFiles) {
    Write-Host "  • $($file.Name)" -ForegroundColor Gray
}
Write-Host ""

# 実行時間測定関数
function Measure-Execution {
    param([scriptblock]$ScriptBlock)
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    try {
        & $ScriptBlock
        $stopwatch.Stop()
        return @{
            Success = $true
            ElapsedMs = $stopwatch.ElapsedMilliseconds
            Error = $null
        }
    }
    catch {
        $stopwatch.Stop()
        return @{
            Success = $false
            ElapsedMs = $stopwatch.ElapsedMilliseconds
            Error = $_.Exception.Message
        }
    }
}

$allResults = @()
$maxTime = 0

# C++の場合
if ($lang -in @("cpp", "c++")) {
    Write-Info "⚙️ C++版でテスト実行..."
    
    # ビルドが必要かチェック
    $needBuild = (-not (Test-Path "main.exe")) -or ((Get-Item "main.cpp").LastWriteTime -gt (Get-Item "main.exe" -ErrorAction SilentlyContinue).LastWriteTime)
    
    if ($needBuild) {
        Write-Info "🔨 ビルド中..."
        $buildResult = & g++ -std=c++20 -O2 -Wall -Wextra main.cpp -o main.exe 2>&1
        
        if ($LASTEXITCODE -ne 0) {
            Write-Error2 "コンパイルエラー:"
            Write-Host $buildResult -ForegroundColor Red
            Set-Location ..
            exit 1
        }
        Write-Success "ビルド完了"
    }
    
    # 各テストケース実行
    foreach ($inputFile in $inputFiles) {
        Write-Info "▶️  テスト実行: $($inputFile.Name)"
        
        $result = Measure-Execution {
            Get-Content $inputFile.FullName | .\main.exe 2>&1
        }
        
        if ($result.Success) {
            $output = Get-Content $inputFile.FullName | .\main.exe 2>&1
            Write-Host "   出力: " -NoNewline -ForegroundColor Cyan
            Write-Host $output
            Write-Host "   実行時間: " -NoNewline -ForegroundColor Yellow
            Write-Host "$($result.ElapsedMs)ms" -ForegroundColor Green
        } else {
            Write-Host "   エラー: " -NoNewline -ForegroundColor Red
            Write-Host $result.Error -ForegroundColor Red
            Write-Host "   実行時間: " -NoNewline -ForegroundColor Yellow
            Write-Host "$($result.ElapsedMs)ms" -ForegroundColor Red
        }
        
        $allResults += @{
            File = $inputFile.Name
            Success = $result.Success
            Time = $result.ElapsedMs
            Error = $result.Error
        }
        
        if ($result.ElapsedMs -gt $maxTime) {
            $maxTime = $result.ElapsedMs
        }
        
        Write-Host ""
    }
}
# Pythonの場合
elseif ($lang -in @("py", "python")) {
    Write-Info "🐍 Python版でテスト実行..."
    
    if (-not (Test-Path "main.py")) {
        Write-Error2 "main.py が見つかりません"
        Set-Location ..
        exit 1
    }
    
    # 各テストケース実行
    foreach ($inputFile in $inputFiles) {
        Write-Info "▶️  テスト実行: $($inputFile.Name)"
        
        $result = Measure-Execution {
            Get-Content $inputFile.FullName | python main.py 2>&1
        }
        
        if ($result.Success) {
            $output = Get-Content $inputFile.FullName | python main.py 2>&1
            Write-Host "   出力: " -NoNewline -ForegroundColor Cyan
            Write-Host $output
            Write-Host "   実行時間: " -NoNewline -ForegroundColor Yellow
            Write-Host "$($result.ElapsedMs)ms" -ForegroundColor Green
        } else {
            Write-Host "   エラー: " -NoNewline -ForegroundColor Red
            Write-Host $result.Error -ForegroundColor Red
            Write-Host "   実行時間: " -NoNewline -ForegroundColor Yellow
            Write-Host "$($result.ElapsedMs)ms" -ForegroundColor Red
        }
        
        $allResults += @{
            File = $inputFile.Name
            Success = $result.Success
            Time = $result.ElapsedMs
            Error = $result.Error
        }
        
        if ($result.ElapsedMs -gt $maxTime) {
            $maxTime = $result.ElapsedMs
        }
        
        Write-Host ""
    }
}

# 結果サマリー
Write-Header "� テスト結果サマリー"
Write-Host "実行ケース数: $($allResults.Count)" -ForegroundColor White
Write-Host "最大実行時間: ${maxTime}ms" -ForegroundColor Yellow

# TLE判定 (2秒 = 2000ms)
$TLE_LIMIT = 2000
if ($maxTime -gt $TLE_LIMIT) {
    Write-Host "⚠️  TLE警告: 制限時間(${TLE_LIMIT}ms)を超過" -ForegroundColor Red
} else {
    Write-Host "✅ TLE判定: OK (制限時間内)" -ForegroundColor Green
}

# 成功・失敗統計
$successCount = ($allResults | Where-Object { $_.Success }).Count
$failCount = $allResults.Count - $successCount

Write-Host "成功: $successCount ケース" -ForegroundColor Green
if ($failCount -gt 0) {
    Write-Host "失敗: $failCount ケース" -ForegroundColor Red
}

Write-Host ""
Write-Info "💡 他の問題をテストする場合:"
$otherProblems = @("a", "b", "c", "d") | Where-Object { $_ -ne $problem }
foreach ($p in $otherProblems) {
    Write-Host "  .\main.ps1 test $ContestName $p $lang    # $($p.ToUpper())問題"
}

Set-Location ..