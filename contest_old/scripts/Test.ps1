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

# ルートパスとコンテストのフルパス
$rootPath = (Get-Location).Path
$contestFullPath = Join-Path $rootPath $ContestName

# 問題ローカルフォルダが存在する場合はそちらを優先してテストを行う
$probFolder = Join-Path $contestFullPath ($problem.ToUpper())
$useLocal = $false
if (Test-Path $probFolder) {
    # 移動してそこに main.* があればローカル実行モード
    if ((Test-Path (Join-Path $probFolder 'main.py')) -or (Test-Path (Join-Path $probFolder 'main.cpp'))) {
        Set-Location $probFolder
        $useLocal = $true
    }
}

# テストケース配置先候補 (優先順)
if ($useLocal) {
    $localTc = Join-Path (Get-Location) 'testcases'
    if (Test-Path $localTc) { $inputFiles = Get-ChildItem (Join-Path $localTc 'in_*.txt') -ErrorAction SilentlyContinue } else { $inputFiles = @() }
    # fallback to contest/testcases/<prob>
    if (-not $inputFiles -or $inputFiles.Count -eq 0) {
        $tcRoot = Join-Path $contestFullPath 'testcases'
        $problemDir = Join-Path $tcRoot ($problem.ToUpper())
        if (Test-Path $problemDir) { $inputFiles = Get-ChildItem (Join-Path $problemDir 'in_*.txt') -ErrorAction SilentlyContinue }
    }
} else {
    $tcRoot = Join-Path $contestFullPath 'testcases'
    $problemDir = Join-Path $tcRoot ($problem.ToUpper())
    if (Test-Path $problemDir) { $inputFiles = Get-ChildItem (Join-Path $problemDir 'in_*.txt') -ErrorAction SilentlyContinue } else { $inputFiles = @() }
    if (-not $inputFiles -or $inputFiles.Count -eq 0) { $inputFiles = Get-ChildItem (Join-Path $contestFullPath "in_$problem*.txt") -ErrorAction SilentlyContinue }
}

if (-not $inputFiles -or $inputFiles.Count -eq 0) {
    Write-Error2 "テスト入力ファイルが見つかりません (期待: testcases\\$($problem.ToUpper())\\in_*.txt または in_$problem*.txt)"
    Write-Info "例: testcases\\$($problem.ToUpper())\\in_1.txt, in_${problem}_2.txt または in_$problem.txt"
    Set-Location ..
    exit 1
}

Write-Info "� 見つかったテスト入力: $($inputFiles.Count)個"
for ($fi = 0; $fi -lt $inputFiles.Count; $fi++) {
    $file = $inputFiles[$fi]
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

# 出力差分を表示する (簡易)
function Show-Diff {
    param(
        [string]$Expected,
        [string]$Actual,
        [int]$MaxDiffs = 10
    )
    $expLines = @()
    $outLines = @()
    if ($Expected) { $expLines = ($Expected -split "\r?\n") }
    if ($Actual) { $outLines = ($Actual -split "\r?\n") }
    $max = [Math]::Max($expLines.Count, $outLines.Count)
    $diffCount = 0
    Write-Host "--- Diff (expected vs actual) ---" -ForegroundColor Magenta
    for ($ln = 0; $ln -lt $max; $ln++) {
        $e = ''
        $a = ''
        if ($ln -lt $expLines.Count) { $e = $expLines[$ln] }
        if ($ln -lt $outLines.Count) { $a = $outLines[$ln] }
        if ($e -ne $a) {
            $diffCount++
            Write-Host ("[{0}] - {1}" -f ($ln+1), $e) -ForegroundColor Yellow
            Write-Host ("[{0}] + {1}" -f ($ln+1), $a) -ForegroundColor Cyan
        }
        if ($diffCount -ge $MaxDiffs) { Write-Host "... (差分が多すぎるため省略)" -ForegroundColor Gray; break }
    }
    if ($diffCount -eq 0) { Write-Host "差分なし (行単位では一致)" -ForegroundColor Green }
    Write-Host "--- End Diff ---" -ForegroundColor Magenta
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
    for ($i = 0; $i -lt $inputFiles.Count; $i++) {
        $inputFile = $inputFiles[$i]
        Write-Info "▶️  テスト実行: $($inputFile.Name)"

        $result = Measure-Execution {
            Get-Content $inputFile.FullName | .\main.exe 2>&1
        }

        if ($result.Success) {
            $procOutput = & { Get-Content $inputFile.FullName | .\main.exe 2>&1 }
            $outputText = ($procOutput -join "`n").TrimEnd()
            Write-Host "   出力: " -NoNewline -ForegroundColor Cyan
            Write-Host $outputText
            Write-Host "   実行時間: " -NoNewline -ForegroundColor Yellow
            Write-Host "$($result.ElapsedMs)ms" -ForegroundColor Green

            # 期待出力があれば比較
            $expectedPath = Join-Path $contestFullPath (Join-Path "testcases\$($problem.ToUpper())" ("out_$($i + 1).txt"))
            if (-not (Test-Path $expectedPath)) {
                # fallback: try legacy out_<problem>* files
                $expectedPath = Get-ChildItem (Join-Path $contestFullPath ("out_$($problem)*.txt")) -ErrorAction SilentlyContinue | Select-Object -First 1
            }
            $pass = $null
            if ($expectedPath -and (Test-Path $expectedPath)) {
                $exp = Get-Content $expectedPath -Raw
                # Normalize line endings and trim trailing whitespace
                $expTrim = $exp.Trim()
                $outTrim = $outputText.Trim()
                $pass = $expTrim -eq $outTrim
                # Debug output
                # Write-Host "   [DEBUG] ExpTrim: [$expTrim] OutTrim: [$outTrim] Pass: $pass" -ForegroundColor Gray
                if ($pass) { Write-Host "   判定: " -NoNewline -ForegroundColor Green; Write-Host "PASS" -ForegroundColor Green }
                else { Write-Host "   判定: " -NoNewline -ForegroundColor Red; Write-Host "FAIL" -ForegroundColor Red }
                if (-not $pass) { Show-Diff -Expected $exp -Actual $outputText }
            } else {
                Write-Host "   判定: " -NoNewline -ForegroundColor Yellow; Write-Host "期待出力ファイルなし" -ForegroundColor Yellow
            }
        } else {
            Write-Host "   エラー: " -NoNewline -ForegroundColor Red
            Write-Host $result.Error -ForegroundColor Red
            Write-Host "   実行時間: " -NoNewline -ForegroundColor Yellow
            Write-Host "$($result.ElapsedMs)ms" -ForegroundColor Red
            $pass = $false
        }

        $allResults += @{
            File = $inputFile.Name
            Success = $result.Success
            Pass = $pass
            Time = $result.ElapsedMs
            Error = $result.Error
        }

        if ($result.ElapsedMs -gt $maxTime) { $maxTime = $result.ElapsedMs }

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
    for ($i = 0; $i -lt $inputFiles.Count; $i++) {
        $inputFile = $inputFiles[$i]
        Write-Info "▶️  テスト実行: $($inputFile.Name)"

        $result = Measure-Execution {
            Get-Content $inputFile.FullName | python main.py 2>&1
        }

        if ($result.Success) {
            $procOutput = & { Get-Content $inputFile.FullName | python main.py 2>&1 }
            $outputText = ($procOutput -join "`n").TrimEnd()
            Write-Host "   出力: " -NoNewline -ForegroundColor Cyan
            Write-Host $outputText
            Write-Host "   実行時間: " -NoNewline -ForegroundColor Yellow
            Write-Host "$($result.ElapsedMs)ms" -ForegroundColor Green

            $expectedPath = Join-Path $contestFullPath (Join-Path "testcases\$($problem.ToUpper())" ("out_$($i + 1).txt"))
            if (-not (Test-Path $expectedPath)) {
                $expectedPath = Get-ChildItem (Join-Path $contestFullPath ("out_$($problem)*.txt")) -ErrorAction SilentlyContinue | Select-Object -First 1
            }
            $pass = $null
            if ($expectedPath -and (Test-Path $expectedPath)) {
                $exp = Get-Content $expectedPath -Raw
                $expTrim = $exp.Trim()
                $outTrim = $outputText.Trim()
                $pass = $expTrim -eq $outTrim
                if ($pass) { Write-Host "   判定: " -NoNewline -ForegroundColor Green; Write-Host "PASS" -ForegroundColor Green }
                else { Write-Host "   判定: " -NoNewline -ForegroundColor Red; Write-Host "FAIL" -ForegroundColor Red }
                if (-not $pass) { Show-Diff -Expected $exp -Actual $outputText }
            } else {
                Write-Host "   判定: " -NoNewline -ForegroundColor Yellow; Write-Host "期待出力ファイルなし" -ForegroundColor Yellow
            }
        } else {
            Write-Host "   エラー: " -NoNewline -ForegroundColor Red
            Write-Host $result.Error -ForegroundColor Red
            Write-Host "   実行時間: " -NoNewline -ForegroundColor Yellow
            Write-Host "$($result.ElapsedMs)ms" -ForegroundColor Red
            $pass = $false
        }

        $allResults += @{
            File = $inputFile.Name
            Success = $result.Success
            Pass = $pass
            Time = $result.ElapsedMs
            Error = $result.Error
        }

        if ($result.ElapsedMs -gt $maxTime) { $maxTime = $result.ElapsedMs }

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
$passCount = ($allResults | Where-Object { $_.Pass -eq $true }).Count
$failCount = ($allResults | Where-Object { $_.Pass -eq $false }).Count
$unknownCount = ($allResults | Where-Object { $null -eq $_.Pass }).Count

if ($passCount -gt 0) {
    Write-Host "✅ PASS: $passCount ケース" -ForegroundColor Green
}
if ($failCount -gt 0) {
    Write-Host "❌ FAIL: $failCount ケース" -ForegroundColor Red
}
if ($unknownCount -gt 0) {
    Write-Host "⚠️  期待出力なし: $unknownCount ケース" -ForegroundColor Yellow
}

Write-Host ""
Write-Info "💡 他の問題をテストする場合:"
$otherProblems = @("a", "b", "c", "d") | Where-Object { $_ -ne $problem }
foreach ($p in $otherProblems) {
    Write-Host "  .\main.ps1 test $ContestName $p $lang    # $($p.ToUpper())問題"
}

Set-Location ..