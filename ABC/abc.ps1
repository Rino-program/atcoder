#Requires -Version 5.1
<#
.SYNOPSIS
    AtCoder ABC 統合ツール

.PARAMETER Action
    実行するアクション:
    new [回数] - 新しいフォルダ作成
    test [問題] [言語] - テスト実行  
    timer - タイマー開始
    open [回数] - 全問題URL開く
    help - ヘルプ表示

.EXAMPLE
    .\abc.ps1 new 372
    .\abc.ps1 test a py
    .\abc.ps1 timer
#>

param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$Action,
    
    [Parameter(Position=1)]
    [string]$Param1,
    
    [Parameter(Position=2)]
    [string]$Param2
)

$ErrorActionPreference = 'Stop'

# 共通設定
$templateDir = "template"
$timeLimit = 2000
$memoryLimit = 512

function Write-Banner {
    param([string]$Text)
    Write-Host "🚀 $Text" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Text)
    Write-Host "✅ $Text" -ForegroundColor Green
}

function Write-Error {
    param([string]$Text)
    Write-Host "❌ $Text" -ForegroundColor Red
}

function Write-Warning {
    param([string]$Text)
    Write-Host "⚠️  $Text" -ForegroundColor Yellow
}

function Write-Info {
    param([string]$Text)
    Write-Host "ℹ️  $Text" -ForegroundColor Cyan
}

# フォルダ作成機能
function New-ABCFolder {
    param([int]$ContestNumber)
    
    if ($ContestNumber -lt 1 -or $ContestNumber -gt 999) {
        Write-Error "コンテスト番号は1-999の範囲で指定してください"
        return
    }
    
    $folderName = "ABC$ContestNumber"
    $folderPath = Join-Path (Get-Location) $folderName
    
    if (Test-Path $folderPath) {
        Write-Warning "フォルダ '$folderName' は既に存在します。上書きしますか？ (Y/N)"
        $response = Read-Host
        if ($response -ne "Y" -and $response -ne "y") {
            Write-Info "操作をキャンセルしました"
            return
        }
        Remove-Item -Path $folderPath -Recurse -Force
    }
    
    Write-Banner "ABC$ContestNumber フォルダを作成中..."
    
    # フォルダ作成
    New-Item -Path $folderPath -ItemType Directory -Force | Out-Null
    
    # テンプレートファイルをコピー
    $templateFiles = @("main.cpp", "main.py")
    foreach ($file in $templateFiles) {
        $source = Join-Path $templateDir $file
        if (Test-Path $source) {
            Copy-Item -Path $source -Destination (Join-Path $folderPath $file)
        }
    }
    
    # テスト入力ファイル作成
    $problems = @("a", "b", "c", "d")
    foreach ($problem in $problems) {
        $content = @"
# $($problem.ToUpper())問題テスト入力

## Test 1
5
## Expected:
5
"@
        $inputFile = Join-Path $folderPath "in_$problem.txt"
        $content | Out-File -FilePath $inputFile -Encoding UTF8
    }
    
    # 統合実行スクリプト作成
    $runScript = @"
@echo off
chcp 65001 >nul
if "%1"=="" goto help

if "%1"=="test" goto test
if "%1"=="timer" goto timer
if "%1"=="open" goto open
goto help

:test
if "%2"=="" echo 使用法: run.bat test [a/b/c/d] [cpp/py] && pause && exit
powershell -ExecutionPolicy Bypass -Command "$test_func"
goto end

:timer
powershell -ExecutionPolicy Bypass -Command "$timer_func"
goto end

:open
start https://atcoder.jp/contests/abc$ContestNumber/tasks
start https://atcoder.jp/contests/abc$ContestNumber/tasks/abc$($ContestNumber)_a
start https://atcoder.jp/contests/abc$ContestNumber/tasks/abc$($ContestNumber)_b
start https://atcoder.jp/contests/abc$ContestNumber/tasks/abc$($ContestNumber)_c
start https://atcoder.jp/contests/abc$ContestNumber/tasks/abc$($ContestNumber)_d
goto end

:help
echo 🚀 ABC$ContestNumber 支援ツール
echo test [a-d] [cpp/py] - テスト実行
echo timer              - タイマー
echo open               - 全問題URL開く
pause

:end
"@
    
    # PowerShell関数を埋め込み
    $test_func = @'
param($prob, $lang)
$prob = $args[0]; $lang = $args[1]
if (!$prob -or !$lang) { Write-Host "引数が不足しています"; return }
$lang = if ($lang -eq "cpp") { "cpp" } else { "py" }
$inputFile = "in_$prob.txt"
$sourceFile = if ($lang -eq "cpp") { "main.cpp" } else { "main.py" }

if (!(Test-Path $inputFile)) { Write-Host "❌ $inputFile が見つかりません"; return }
if (!(Test-Path $sourceFile)) { Write-Host "❌ $sourceFile が見つかりません"; return }

Write-Host "🧪 $prob 問題をテスト中 ($lang)..."

if ($lang -eq "cpp") {
    $result = & g++ -std=c++20 -O2 -DLOCAL $sourceFile -o main.exe 2>&1
    if ($LASTEXITCODE -ne 0) { Write-Host "❌ コンパイルエラー: $result" -ForegroundColor Red; return }
}

$content = Get-Content $inputFile -Raw
$sections = $content -split '##\s*'
$testNum = 0

foreach ($section in $sections) {
    if (!$section.Trim() -or $section.StartsWith('#')) { continue }
    if ($section.StartsWith('Test ')) {
        $testNum++
        $lines = $section -split "`n"
        $inputLines = $lines | Where-Object { $_ -notmatch '^Test ' -and ![string]::IsNullOrWhiteSpace($_) }
        $input = ($inputLines -join "`n").Trim()
        
        Write-Host "Test $testNum 実行中..."
        $input | Out-File -FilePath "temp.txt" -Encoding UTF8 -NoNewline
        
        $start = Get-Date
        if ($lang -eq "cpp") {
            $output = cmd /c "main.exe < temp.txt"
        } else {
            $output = cmd /c "python main.py < temp.txt"
        }
        $end = Get-Date
        $time = ($end - $start).TotalMilliseconds
        
        Write-Host "   出力: $output"
        Write-Host "   時間: $([math]::Round($time, 2))ms" -ForegroundColor Cyan
        if ($time -gt 2000) { Write-Host "   ⚠️ TLE" -ForegroundColor Red }
        
        Remove-Item "temp.txt" -Force -ErrorAction SilentlyContinue
    }
}
if (Test-Path "main.exe") { Remove-Item "main.exe" -Force }
'@
    
    $timer_func = @'
Write-Host "⏰ タイマー開始 (Ctrl+Cで終了)"
$start = Get-Date
try {
    while ($true) {
        Clear-Host
        $elapsed = (Get-Date) - $start
        $remaining = [TimeSpan]::FromMinutes(100) - $elapsed
        Write-Host "⏰ ABC タイマー" -ForegroundColor Cyan
        Write-Host "経過: $($elapsed.ToString('hh\:mm\:ss'))" -ForegroundColor Green
        if ($remaining.TotalSeconds -gt 0) {
            Write-Host "残り: $($remaining.ToString('hh\:mm\:ss'))" -ForegroundColor Magenta
            if ($remaining.TotalMinutes -lt 10) { Write-Host "⚠️ 残り10分！" -ForegroundColor Red }
        } else { Write-Host "終了！" -ForegroundColor Red; break }
        Start-Sleep 1
    }
} catch { Write-Host "タイマー終了" }
'@
    
    # run.batの内容を生成（関数を埋め込み）
    $runBat = $runScript.Replace('$test_func', $test_func).Replace('$timer_func', $timer_func)
    $runBat | Out-File -FilePath (Join-Path $folderPath "run.bat") -Encoding ASCII
    
    # README作成
    $readme = @"
# AtCoder Beginner Contest $ContestNumber

## 🎯 使用方法
\`\`\`
run.bat test a py    # A問題をPythonでテスト
run.bat test b cpp   # B問題をC++でテスト  
run.bat timer        # タイマー開始
run.bat open         # 全問題URL開く
\`\`\`

## 📋 問題一覧
- A問題: [https://atcoder.jp/contests/abc$ContestNumber/tasks/abc$($ContestNumber)_a](https://atcoder.jp/contests/abc$ContestNumber/tasks/abc$($ContestNumber)_a)
- B問題: [https://atcoder.jp/contests/abc$ContestNumber/tasks/abc$($ContestNumber)_b](https://atcoder.jp/contests/abc$ContestNumber/tasks/abc$($ContestNumber)_b)
- C問題: [https://atcoder.jp/contests/abc$ContestNumber/tasks/abc$($ContestNumber)_c](https://atcoder.jp/contests/abc$ContestNumber/tasks/abc$($ContestNumber)_c)
- D問題: [https://atcoder.jp/contests/abc$ContestNumber/tasks/abc$($ContestNumber)_d](https://atcoder.jp/contests/abc$ContestNumber/tasks/abc$($ContestNumber)_d)

## 📝 メモ

### A問題


### B問題


### C問題


### D問題


## 📊 結果
- 順位: 
- レーティング変化: 
"@
    
    $readme | Out-File -FilePath (Join-Path $folderPath "README.md") -Encoding UTF8
    
    Write-Success "ABC$ContestNumber フォルダを作成しました"
    Write-Info "場所: $folderPath"
    Write-Info "使用方法: cd $folderName && run.bat help"
}

# テスト実行機能（現在のフォルダ内で）
function Start-Test {
    param([string]$Problem, [string]$Language)
    
    if (!$Problem -or !$Language) {
        Write-Error "使用法: abc.ps1 test [a/b/c/d] [cpp/py]"
        return
    }
    
    $lang = if ($Language -eq "cpp" -or $Language -eq "c") { "cpp" } else { "py" }
    $inputFile = "in_$Problem.txt"
    $sourceFile = if ($lang -eq "cpp") { "main.cpp" } else { "main.py" }
    
    if (!(Test-Path $inputFile)) { Write-Error "$inputFile が見つかりません"; return }
    if (!(Test-Path $sourceFile)) { Write-Error "$sourceFile が見つかりません"; return }
    
    Write-Banner "$($Problem.ToUpper()) 問題をテスト中 ($lang)..."
    
    # C++の場合はコンパイル
    if ($lang -eq "cpp") {
        $compileResult = & g++ -std=c++20 -O2 -DLOCAL $sourceFile -o main.exe 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Error "コンパイルエラー: $compileResult"
            return
        }
    }
    
    # テストケース実行
    $content = Get-Content $inputFile -Raw
    $sections = $content -split '##\s*'
    $testCount = 0
    $passCount = 0
    
    foreach ($section in $sections) {
        $section = $section.Trim()
        if (!$section -or $section.StartsWith('#')) { continue }
        
        if ($section.StartsWith('Test ')) {
            $testCount++
            $lines = $section -split "`n"
            
            # Expected行を探す
            $expectedIndex = -1
            for ($i = 0; $i -lt $lines.Length; $i++) {
                if ($lines[$i] -match '^Expected:\s*$' -or $lines[$i] -match '^## Expected') {
                    $expectedIndex = $i + 1
                    break
                }
            }
            
            # 入力部分を抽出
            $inputLines = @()
            for ($i = 1; $i -lt $lines.Length; $i++) {
                if ($lines[$i] -match '^Expected:' -or $lines[$i] -match '^## Expected') { break }
                if (![string]::IsNullOrWhiteSpace($lines[$i])) {
                    $inputLines += $lines[$i]
                }
            }
            
            # 期待値を抽出
            $expectedOutput = ""
            if ($expectedIndex -ge 0 -and $expectedIndex -lt $lines.Length) {
                $expectedOutput = $lines[$expectedIndex].Trim()
            }
            
            if ($inputLines.Count -eq 0) { continue }
            
            $input = ($inputLines -join "`n").Trim()
            
            Write-Host "  Test $($testCount): " -NoNewline
            $input | Out-File -FilePath "temp.txt" -Encoding UTF8 -NoNewline
            
            $start = Get-Date
            try {
                if ($lang -eq "cpp") {
                    $output = (cmd /c "main.exe < temp.txt 2>nul").Trim()
                } else {
                    $output = (cmd /c "python main.py < temp.txt 2>nul").Trim()
                }
            } catch {
                $output = "ERROR"
            }
            $end = Get-Date
            $time = ($end - $start).TotalMilliseconds
            
            # 結果判定
            $passed = $expectedOutput -eq "" -or $output -eq $expectedOutput
            if ($passed) {
                Write-Host "✅ PASS" -ForegroundColor Green -NoNewline
                $passCount++
            } else {
                Write-Host "❌ FAIL" -ForegroundColor Red -NoNewline
                Write-Host " (期待値: '$expectedOutput', 実際: '$output')" -ForegroundColor Yellow -NoNewline
            }
            
            Write-Host " ($([math]::Round($time, 1))ms)" -ForegroundColor Cyan
            
            if ($time -gt $timeLimit) {
                Write-Host "    ⚠️ TLE (制限: ${timeLimit}ms)" -ForegroundColor Red
            }
            
            Remove-Item "temp.txt" -Force -ErrorAction SilentlyContinue
        }
    }
    
    # 結果サマリー
    if ($testCount -gt 0) {
        Write-Host ""
        if ($passCount -eq $testCount) {
            Write-Success "全テストケース成功！ ($passCount/$testCount)"
        } else {
            Write-Warning "一部テスト失敗 ($passCount/$testCount)"
        }
    }
    
    # cleanup
    if (Test-Path "main.exe") { Remove-Item "main.exe" -Force }
}

# タイマー機能
function Start-Timer {
    Write-Banner "コンテストタイマー開始 (Ctrl+Cで終了)"
    $start = Get-Date
    
    try {
        while ($true) {
            Clear-Host
            $elapsed = (Get-Date) - $start
            $remaining = [TimeSpan]::FromMinutes(100) - $elapsed
            
            Write-Host "⏰ AtCoder ABC タイマー" -ForegroundColor Cyan
            Write-Host "経過時間: $($elapsed.ToString('hh\:mm\:ss'))" -ForegroundColor Green
            
            if ($remaining.TotalSeconds -gt 0) {
                Write-Host "残り時間: $($remaining.ToString('hh\:mm\:ss'))" -ForegroundColor Magenta
                
                if ($remaining.TotalMinutes -lt 10) {
                    Write-Host "⚠️  残り10分を切りました！" -ForegroundColor Red
                } elseif ($remaining.TotalMinutes -lt 30) {
                    Write-Host "⚠️  残り30分です" -ForegroundColor Yellow
                }
            } else {
                Write-Host "⏰ コンテスト終了！" -ForegroundColor Red
                break
            }
            
            Start-Sleep -Seconds 1
        }
    }
    catch {
        Write-Host "`n👋 タイマーを終了しました" -ForegroundColor Green
    }
}

# URL開く機能
function Open-Problems {
    param([int]$ContestNumber)
    
    if ($ContestNumber -lt 1 -or $ContestNumber -gt 999) {
        Write-Error "コンテスト番号は1-999の範囲で指定してください"
        return
    }
    
    Write-Banner "ABC$ContestNumber の全問題を開いています..."
    
    $urls = @(
        "https://atcoder.jp/contests/abc$ContestNumber/tasks",
        "https://atcoder.jp/contests/abc$ContestNumber/tasks/abc$($ContestNumber)_a",
        "https://atcoder.jp/contests/abc$ContestNumber/tasks/abc$($ContestNumber)_b", 
        "https://atcoder.jp/contests/abc$ContestNumber/tasks/abc$($ContestNumber)_c",
        "https://atcoder.jp/contests/abc$ContestNumber/tasks/abc$($ContestNumber)_d"
    )
    
    foreach ($url in $urls) {
        Start-Process $url
        Start-Sleep -Milliseconds 300
    }
    
    Write-Success "全問題ページを開きました"
}

# ヘルプ表示
function Show-Help {
    Write-Banner "AtCoder ABC 統合ツール"
    Write-Host ""
    Write-Host "📝 コマンド一覧:" -ForegroundColor Yellow
    Write-Host "  new [回数]      - 新しいコンテストフォルダ作成"
    Write-Host "  test [問題] [言語] - テスト実行 (a-d, cpp/py)"  
    Write-Host "  timer           - コンテストタイマー開始"
    Write-Host "  open [回数]     - 全問題URLをブラウザで開く"
    Write-Host "  help            - このヘルプ表示"
    Write-Host ""
    Write-Host "📚 使用例:" -ForegroundColor Yellow
    Write-Host "  .\abc.ps1 new 372        # ABC372フォルダ作成"
    Write-Host "  .\abc.ps1 test a py      # A問題をPythonでテスト"
    Write-Host "  .\abc.ps1 test b cpp     # B問題をC++でテスト"
    Write-Host "  .\abc.ps1 timer          # タイマー開始"
    Write-Host "  .\abc.ps1 open 372       # ABC372の全問題を開く"
}

# メイン処理
switch ($Action.ToLower()) {
    "new" {
        if ($Param1) {
            New-ABCFolder -ContestNumber ([int]$Param1)
        } else {
            Write-Error "使用法: abc.ps1 new [コンテスト番号]"
        }
    }
    "test" {
        Start-Test -Problem $Param1 -Language $Param2
    }
    "timer" {
        Start-Timer
    }
    "open" {
        if ($Param1) {
            Open-Problems -ContestNumber ([int]$Param1)
        } else {
            Write-Error "使用法: abc.ps1 open [コンテスト番号]"
        }
    }
    "help" {
        Show-Help
    }
    default {
        Write-Error "不明なコマンド: $Action"
        Show-Help
    }
}
