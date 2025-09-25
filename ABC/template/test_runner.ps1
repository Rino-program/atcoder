#Requires -Version 5.1
<#
.SYNOPSIS
    AtCoder問題用テストランナー

.DESCRIPTION
    複数のテストケースを自動実行し、期待される出力と比較します。
    TLE/MLE の検出も行います。

.PARAMETER Problem
    テストする問題 (a, b, c, d)

.PARAMETER Language
    使用言語 (cpp, python)

.PARAMETER TimeLimit
    時間制限（ミリ秒、デフォルト: 2000ms）

.PARAMETER MemoryLimit
    メモリ制限（MB、デフォルト: 512MB）

.EXAMPLE
    .\test_runner.ps1 -Problem a -Language python
    A問題をPythonで実行してテスト

.EXAMPLE
    .\test_runner.ps1 -Problem c -Language cpp -TimeLimit 1000
    C問題をC++で実行、制限時間1秒でテスト
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("a", "b", "c", "d")]
    [string]$Problem,

    [Parameter(Mandatory=$true)]
    [ValidateSet("cpp", "python")]
    [string]$Language,

    [Parameter()]
    [int]$TimeLimit = 2000,

    [Parameter()]
    [int]$MemoryLimit = 512
)

# 設定
$inputFile = "input_$Problem.txt"
$executable = if ($Language -eq "cpp") { "main.exe" } else { "python" }
$sourceFile = if ($Language -eq "cpp") { "main.cpp" } else { "main.py" }

Write-Host "🧪 AtCoder テストランナー" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Gray
Write-Host "問題: $Problem | 言語: $Language | 制限: ${TimeLimit}ms, ${MemoryLimit}MB" -ForegroundColor Yellow
Write-Host ""

# 入力ファイルの存在確認
if (!(Test-Path $inputFile)) {
    Write-Host "❌ 入力ファイル '$inputFile' が見つかりません。" -ForegroundColor Red
    exit 1
}

# ソースファイルの存在確認
if (!(Test-Path $sourceFile)) {
    Write-Host "❌ ソースファイル '$sourceFile' が見つかりません。" -ForegroundColor Red
    exit 1
}

# C++の場合はコンパイル
if ($Language -eq "cpp") {
    Write-Host "🔨 C++プログラムをコンパイル中..." -ForegroundColor Yellow
    $compileResult = & g++ -std=c++20 -O2 -Wall -Wextra -DLOCAL $sourceFile -o main.exe 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ コンパイルエラー:" -ForegroundColor Red
        Write-Host $compileResult -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ コンパイル完了" -ForegroundColor Green
    Write-Host ""
}

# テストケースの解析
function Parse-TestCases {
    param([string]$FilePath)
    
    $content = Get-Content $FilePath -Raw
    $testCases = @()
    
    # ## で区切られたセクションを分析
    $sections = $content -split '##\s*'
    $currentInput = ""
    $expectedOutput = ""
    
    foreach ($section in $sections) {
        $section = $section.Trim()
        if ([string]::IsNullOrEmpty($section) -or $section.StartsWith('#')) { continue }
        
        if ($section.StartsWith('Expected:')) {
            $expectedOutput = ($section -replace '^Expected:\s*', '').Trim()
            if (![string]::IsNullOrEmpty($currentInput) -and ![string]::IsNullOrEmpty($expectedOutput)) {
                $testCases += @{
                    Input = $currentInput
                    Expected = $expectedOutput
                }
                $currentInput = ""
                $expectedOutput = ""
            }
        } elseif ($section.StartsWith('Test Case')) {
            $lines = $section -split "`n"
            $inputLines = $lines | Where-Object { $_ -notmatch '^Test Case' -and ![string]::IsNullOrWhiteSpace($_) }
            $currentInput = ($inputLines -join "`n").Trim()
        }
    }
    
    return $testCases
}

# テストケースの実行
function Run-TestCase {
    param([hashtable]$TestCase, [int]$Index)
    
    Write-Host "📝 Test Case $Index 実行中..." -ForegroundColor Cyan
    
    # 入力を一時ファイルに保存
    $tempInput = "temp_input_$Index.txt"
    $TestCase.Input | Out-File -FilePath $tempInput -Encoding UTF8 -NoNewline
    
    try {
        $startTime = Get-Date
        
        # プログラム実行
        if ($Language -eq "cpp") {
            $result = cmd /c "main.exe < $tempInput 2>temp_stderr_$Index.txt"
        } else {
            $result = cmd /c "python main.py < $tempInput 2>temp_stderr_$Index.txt"
        }
        
        $endTime = Get-Date
        $executionTime = ($endTime - $startTime).TotalMilliseconds
        
        # 標準エラー出力を取得（パフォーマンス情報）
        $stderrContent = ""
        if (Test-Path "temp_stderr_$Index.txt") {
            $stderrContent = Get-Content "temp_stderr_$Index.txt" -Raw
            Remove-Item "temp_stderr_$Index.txt" -Force
        }
        
        # 結果の比較
        $actualOutput = ($result -join "`n").Trim()
        $expectedOutput = $TestCase.Expected.Trim()
        
        $passed = $actualOutput -eq $expectedOutput
        
        # 結果表示
        if ($passed) {
            Write-Host "   ✅ PASSED" -ForegroundColor Green
        } else {
            Write-Host "   ❌ FAILED" -ForegroundColor Red
            Write-Host "   期待値: '$expectedOutput'" -ForegroundColor Yellow
            Write-Host "   実際値: '$actualOutput'" -ForegroundColor Yellow
        }
        
        # パフォーマンス情報
        Write-Host "   ⏱️  実行時間: $([math]::Round($executionTime, 2))ms" -ForegroundColor Cyan
        
        # TLE/MLE チェック
        if ($executionTime -gt $TimeLimit) {
            Write-Host "   ⚠️  TLE: 制限時間 ${TimeLimit}ms を超過" -ForegroundColor Red
        }
        
        # 標準エラー出力からメモリ情報を抽出
        if ($stderrContent -match 'Memory: ([\d.]+)MB') {
            $memoryUsage = [double]$matches[1]
            Write-Host "   💾 メモリ使用量: $([math]::Round($memoryUsage, 2))MB" -ForegroundColor Cyan
            if ($memoryUsage -gt $MemoryLimit) {
                Write-Host "   ⚠️  MLE: 制限メモリ ${MemoryLimit}MB を超過" -ForegroundColor Red
            }
        }
        
        Write-Host ""
        return @{
            Passed = $passed
            Time = $executionTime
            Memory = if ($matches) { [double]$matches[1] } else { 0 }
            TLE = $executionTime -gt $TimeLimit
            MLE = ($matches -and [double]$matches[1] -gt $MemoryLimit)
        }
    }
    finally {
        # 一時ファイルの削除
        if (Test-Path $tempInput) {
            Remove-Item $tempInput -Force
        }
    }
}

# メイン処理
try {
    $testCases = Parse-TestCases -FilePath $inputFile
    
    if ($testCases.Count -eq 0) {
        Write-Host "⚠️  テストケースが見つかりません。" -ForegroundColor Yellow
        Write-Host "入力ファイルの形式を確認してください。" -ForegroundColor Yellow
        exit 1
    }
    
    Write-Host "📊 $($testCases.Count) 個のテストケースを実行します。" -ForegroundColor Green
    Write-Host ""
    
    $results = @()
    for ($i = 0; $i -lt $testCases.Count; $i++) {
        $result = Run-TestCase -TestCase $testCases[$i] -Index ($i + 1)
        $results += $result
    }
    
    # 総合結果
    $passedCount = ($results | Where-Object { $_.Passed }).Count
    $tleCount = ($results | Where-Object { $_.TLE }).Count
    $mleCount = ($results | Where-Object { $_.MLE }).Count
    $maxTime = ($results | Measure-Object -Property Time -Maximum).Maximum
    $maxMemory = ($results | Measure-Object -Property Memory -Maximum).Maximum
    
    Write-Host "=" * 50 -ForegroundColor Gray
    Write-Host "📊 テスト結果サマリー" -ForegroundColor Cyan
    Write-Host "✅ 成功: $passedCount / $($testCases.Count)" -ForegroundColor Green
    if ($tleCount -gt 0) {
        Write-Host "⏰ TLE: $tleCount 件" -ForegroundColor Red
    }
    if ($mleCount -gt 0) {
        Write-Host "💾 MLE: $mleCount 件" -ForegroundColor Red
    }
    Write-Host "⚡ 最大実行時間: $([math]::Round($maxTime, 2))ms" -ForegroundColor Cyan
    Write-Host "💾 最大メモリ: $([math]::Round($maxMemory, 2))MB" -ForegroundColor Cyan
    
    if ($passedCount -eq $testCases.Count -and $tleCount -eq 0 -and $mleCount -eq 0) {
        Write-Host "`n🎉 全テストケース成功！提出準備完了です。" -ForegroundColor Green
    } else {
        Write-Host "`n❌ 一部テストが失敗しました。コードを見直してください。" -ForegroundColor Red
    }
    
} catch {
    Write-Host "❌ エラーが発生しました: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}