#Requires -Version 5.1
<#
.SYNOPSIS
    AtCoder コンテスト支援ツール

.DESCRIPTION
    コンテスト中の様々な支援機能を提供します。
    - 問題URLの一括オープン
    - 残り時間の表示
    - 提出状況の管理
    - クイック実行・テスト

.PARAMETER Action
    実行するアクション
    - OpenProblems: 全問題URLを開く
    - Timer: タイマー表示
    - QuickTest: クイックテスト実行
    - Status: 現在の状況表示
    - Submit: 提出前チェック

.PARAMETER ContestNumber
    コンテスト番号（OpenProblems時に必要）

.PARAMETER Problem
    問題指定（QuickTest, Submit時）

.PARAMETER Language
    言語指定（QuickTest, Submit時）
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("OpenProblems", "Timer", "QuickTest", "Status", "Submit", "Help")]
    [string]$Action,

    [Parameter()]
    [int]$ContestNumber,

    [Parameter()]
    [ValidateSet("a", "b", "c", "d")]
    [string]$Problem,

    [Parameter()]
    [ValidateSet("cpp", "python")]
    [string]$Language
)

# 設定ファイルパス
$statusFile = "contest_status.json"

# コンテスト状況管理
function Get-ContestStatus {
    if (Test-Path $statusFile) {
        return Get-Content $statusFile | ConvertFrom-Json
    } else {
        return @{
            ContestNumber = 0
            StartTime = ""
            Problems = @{
                A = @{ Status = "NotStarted"; SubmitTime = ""; Score = 0; Language = "" }
                B = @{ Status = "NotStarted"; SubmitTime = ""; Score = 0; Language = "" }
                C = @{ Status = "NotStarted"; SubmitTime = ""; Score = 0; Language = "" }
                D = @{ Status = "NotStarted"; SubmitTime = ""; Score = 0; Language = "" }
            }
        }
    }
}

function Save-ContestStatus {
    param([object]$Status)
    $Status | ConvertTo-Json -Depth 10 | Out-File -FilePath $statusFile -Encoding UTF8
}

# メイン処理
switch ($Action) {
    "OpenProblems" {
        if (!$ContestNumber) {
            Write-Host "❌ コンテスト番号が必要です: -ContestNumber を指定してください" -ForegroundColor Red
            exit 1
        }
        
        Write-Host "🌐 ABC$ContestNumber の全問題を開いています..." -ForegroundColor Cyan
        
        $urls = @(
            "https://atcoder.jp/contests/abc$ContestNumber/tasks",
            "https://atcoder.jp/contests/abc$ContestNumber/tasks/abc$($ContestNumber)_a",
            "https://atcoder.jp/contests/abc$ContestNumber/tasks/abc$($ContestNumber)_b",
            "https://atcoder.jp/contests/abc$ContestNumber/tasks/abc$($ContestNumber)_c",
            "https://atcoder.jp/contests/abc$ContestNumber/tasks/abc$($ContestNumber)_d"
        )
        
        foreach ($url in $urls) {
            Start-Process $url
            Start-Sleep -Milliseconds 500  # ブラウザへの負荷軽減
        }
        
        Write-Host "✅ 全問題ページを開きました" -ForegroundColor Green
        
        # ステータス更新
        $status = Get-ContestStatus
        $status.ContestNumber = $ContestNumber
        $status.StartTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Save-ContestStatus $status
    }
    
    "Timer" {
        Write-Host "⏰ コンテストタイマー（Ctrl+Cで終了）" -ForegroundColor Cyan
        Write-Host "=" * 40 -ForegroundColor Gray
        
        $status = Get-ContestStatus
        if ($status.StartTime) {
            $startTime = [DateTime]::Parse($status.StartTime)
        } else {
            Write-Host "コンテスト開始時刻を入力してください（例: 21:00）:"
            $timeInput = Read-Host
            $today = Get-Date -Format "yyyy-MM-dd"
            $startTime = [DateTime]::Parse("$today $timeInput")
            $status.StartTime = $startTime.ToString("yyyy-MM-dd HH:mm:ss")
            Save-ContestStatus $status
        }
        
        $endTime = $startTime.AddMinutes(100)  # ABC は100分
        
        try {
            while ($true) {
                Clear-Host
                $now = Get-Date
                $elapsed = $now - $startTime
                $remaining = $endTime - $now
                
                Write-Host "⏰ AtCoder ABC$($status.ContestNumber) タイマー" -ForegroundColor Cyan
                Write-Host "=" * 40 -ForegroundColor Gray
                Write-Host "開始時刻: $($startTime.ToString('HH:mm:ss'))" -ForegroundColor Yellow
                Write-Host "終了時刻: $($endTime.ToString('HH:mm:ss'))" -ForegroundColor Yellow
                Write-Host ""
                Write-Host "経過時間: $($elapsed.ToString('hh\:mm\:ss'))" -ForegroundColor Green
                
                if ($remaining.TotalSeconds -gt 0) {
                    Write-Host "残り時間: $($remaining.ToString('hh\:mm\:ss'))" -ForegroundColor Magenta
                    
                    # 残り時間による警告
                    if ($remaining.TotalMinutes -lt 10) {
                        Write-Host "⚠️  残り10分を切りました！" -ForegroundColor Red
                    } elseif ($remaining.TotalMinutes -lt 30) {
                        Write-Host "⚠️  残り30分を切りました！" -ForegroundColor Yellow
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
    
    "QuickTest" {
        if (!$Problem -or !$Language) {
            Write-Host "❌ 問題と言語の指定が必要です" -ForegroundColor Red
            Write-Host "例: .\contest_helper.ps1 -Action QuickTest -Problem a -Language python" -ForegroundColor Yellow
            exit 1
        }
        
        Write-Host "🚀 $Problem 問題のクイックテスト実行" -ForegroundColor Cyan
        & ".\test_runner.ps1" -Problem $Problem -Language $Language
    }
    
    "Status" {
        $status = Get-ContestStatus
        
        Write-Host "📊 コンテスト状況" -ForegroundColor Cyan
        Write-Host "=" * 40 -ForegroundColor Gray
        Write-Host "コンテスト: ABC$($status.ContestNumber)" -ForegroundColor Yellow
        if ($status.StartTime) {
            Write-Host "開始時刻: $($status.StartTime)" -ForegroundColor Yellow
        }
        Write-Host ""
        
        foreach ($problemKey in @("A", "B", "C", "D")) {
            $problem = $status.Problems.$problemKey
            $statusColor = switch ($problem.Status) {
                "AC" { "Green" }
                "WA" { "Red" }
                "Working" { "Yellow" }
                default { "Gray" }
            }
            
            Write-Host "$problemKey 問題: " -NoNewline
            Write-Host "$($problem.Status)" -ForegroundColor $statusColor -NoNewline
            if ($problem.Language) {
                Write-Host " ($($problem.Language))" -NoNewline
            }
            if ($problem.SubmitTime) {
                Write-Host " - $($problem.SubmitTime)" -ForegroundColor Cyan
            } else {
                Write-Host ""
            }
        }
    }
    
    "Submit" {
        if (!$Problem -or !$Language) {
            Write-Host "❌ 問題と言語の指定が必要です" -ForegroundColor Red
            exit 1
        }
        
        Write-Host "🔍 提出前チェック（$Problem 問題 - $Language）" -ForegroundColor Cyan
        Write-Host "=" * 40 -ForegroundColor Gray
        
        # テスト実行
        $testResult = & ".\test_runner.ps1" -Problem $Problem -Language $Language
        
        # ステータス更新
        $status = Get-ContestStatus
        $problemKey = $Problem.ToUpper()
        $status.Problems.$problemKey.Status = "Working"
        $status.Problems.$problemKey.Language = $Language
        Save-ContestStatus $status
        
        Write-Host ""
        Write-Host "📋 提出チェックリスト:" -ForegroundColor Yellow
        Write-Host "□ すべてのテストケースが成功している" -ForegroundColor White
        Write-Host "□ TLE/MLE が発生していない" -ForegroundColor White
        Write-Host "□ デバッグ用のprint文を削除している" -ForegroundColor White
        Write-Host "□ 問題文の制約を満たしている" -ForegroundColor White
        Write-Host ""
        Write-Host "提出準備はできましたか？ (Y/N): " -NoNewline -ForegroundColor Green
        $response = Read-Host
        
        if ($response -eq "Y" -or $response -eq "y") {
            Write-Host "🎉 頑張って！結果をお祈りします 🙏" -ForegroundColor Green
        } else {
            Write-Host "👍 もう少し調整しましょう" -ForegroundColor Yellow
        }
    }
    
    "Help" {
        Write-Host "🎯 AtCoder コンテスト支援ツール" -ForegroundColor Cyan
        Write-Host "=" * 40 -ForegroundColor Gray
        Write-Host ""
        Write-Host "コマンド一覧:" -ForegroundColor Yellow
        Write-Host "  OpenProblems   - 全問題URLを開く" -ForegroundColor White
        Write-Host "  Timer          - コンテストタイマー" -ForegroundColor White
        Write-Host "  QuickTest      - クイックテスト実行" -ForegroundColor White
        Write-Host "  Status         - 現在の状況表示" -ForegroundColor White
        Write-Host "  Submit         - 提出前チェック" -ForegroundColor White
        Write-Host ""
        Write-Host "使用例:" -ForegroundColor Yellow
        Write-Host "  .\contest_helper.ps1 -Action OpenProblems -ContestNumber 372" -ForegroundColor Green
        Write-Host "  .\contest_helper.ps1 -Action Timer" -ForegroundColor Green
        Write-Host "  .\contest_helper.ps1 -Action QuickTest -Problem a -Language python" -ForegroundColor Green
        Write-Host "  .\contest_helper.ps1 -Action Status" -ForegroundColor Green
        Write-Host "  .\contest_helper.ps1 -Action Submit -Problem a -Language cpp" -ForegroundColor Green
    }
}