# 自動テストケース生成システム
param(
    [Parameter(Mandatory=$true)]
    [string]$ContestNumber,
    
    [Parameter(Mandatory=$true)]
    [ValidateSet("A", "B", "C", "D", "E", "F")]
    [string]$Problem,
    
    [ValidateSet("Simple", "Edge", "Random", "Stress")]
    [string]$Type = "Simple",
    
    [int]$Count = 3
)

function Generate-SimpleCase {
    param($Problem, $Index)
    
    switch ($Problem) {
        "A" {
            # A問題は通常簡単な計算問題
            $n = Get-Random -Minimum 1 -Maximum 10
            $content = "$n`n"
            for ($i = 1; $i -le $n; $i++) {
                $val = Get-Random -Minimum 1 -Maximum 100
                $content += "$val "
            }
            return $content.Trim()
        }
        "B" {
            # B問題は配列操作やループが多い
            $n = Get-Random -Minimum 3 -Maximum 20
            $m = Get-Random -Minimum 1 -Maximum $n
            return "$n $m`n"
        }
        "C" {
            # C問題はより複雑
            $n = Get-Random -Minimum 5 -Maximum 100
            $content = "$n`n"
            for ($i = 1; $i -le $n; $i++) {
                $a = Get-Random -Minimum 1 -Maximum 1000
                $b = Get-Random -Minimum 1 -Maximum 1000
                $content += "$a $b`n"
            }
            return $content
        }
        default {
            return "1`n1`n"
        }
    }
}

function Generate-EdgeCase {
    param($Problem, $Index)
    
    switch ($Index) {
        1 {
            # 最小ケース
            return "1`n1`n"
        }
        2 {
            # 最大ケース (適度なサイズ)
            switch ($Problem) {
                "A" { return "10`n" + ((1..10 | ForEach-Object { Get-Random -Minimum 1 -Maximum 1000 }) -join " ") }
                "B" { return "100 50`n" }
                "C" { 
                    $content = "100`n"
                    for ($i = 1; $i -le 100; $i++) {
                        $content += "1000 1000`n"
                    }
                    return $content
                }
                default { return "1000`n1000`n" }
            }
        }
        3 {
            # 特殊ケース (全て同じ値など)
            switch ($Problem) {
                "A" { return "5`n1 1 1 1 1`n" }
                "B" { return "5 5`n" }
                default { return "3`n1 1`n1 1`n1 1`n" }
            }
        }
        default {
            return Generate-SimpleCase $Problem $Index
        }
    }
}

function Generate-RandomCase {
    param($Problem, $Index)
    
    # より複雑なランダムケース
    $seed = Get-Random
    Get-Random -SetSeed $seed
    
    switch ($Problem) {
        "A" {
            $n = Get-Random -Minimum 1 -Maximum 50
            $content = "$n`n"
            $values = 1..$n | ForEach-Object { Get-Random -Minimum 1 -Maximum 10000 }
            $content += ($values -join " ") + "`n"
            return $content
        }
        "B" {
            $n = Get-Random -Minimum 10 -Maximum 1000
            $m = Get-Random -Minimum 1 -Maximum $n
            return "$n $m`n"
        }
        "C" {
            $n = Get-Random -Minimum 10 -Maximum 500
            $content = "$n`n"
            for ($i = 1; $i -le $n; $i++) {
                $a = Get-Random -Minimum 1 -Maximum 100000
                $b = Get-Random -Minimum 1 -Maximum 100000
                $content += "$a $b`n"
            }
            return $content
        }
        default {
            $n = Get-Random -Minimum 1 -Maximum 1000
            return "$n`n"
        }
    }
}

function Generate-TestCase {
    param($Problem, $Type, $Index)
    
    switch ($Type) {
        "Simple" { return Generate-SimpleCase $Problem $Index }
        "Edge" { return Generate-EdgeCase $Problem $Index }
        "Random" { return Generate-RandomCase $Problem $Index }
        "Stress" { return Generate-RandomCase $Problem $Index }
    }
}

# メイン処理
$contestPath = Join-Path (Get-Location) $ContestNumber
if (-not (Test-Path $contestPath)) {
    Write-Host "❌ コンテストフォルダが見つかりません: $ContestNumber" -ForegroundColor Red
    exit 1
}

Write-Host "🎯 $ContestNumber 問題$Problem の$Type テストケース生成中..." -ForegroundColor Cyan

for ($i = 1; $i -le $Count; $i++) {
    $content = Generate-TestCase $Problem $Type $i
    $fileName = "in_$($Problem.ToLower())_$i.txt"
    $filePath = Join-Path $contestPath $fileName
    
    # 既存ファイルがある場合は確認
    if (Test-Path $filePath) {
        $response = Read-Host "ファイル $fileName は既に存在します。上書きしますか？ (y/N)"
        if ($response -ne "y" -and $response -ne "Y") {
            Write-Host "スキップ: $fileName" -ForegroundColor Yellow
            continue
        }
    }
    
    $content | Out-File -FilePath $filePath -Encoding UTF8 -NoNewline
    Write-Host "✅ 生成完了: $fileName" -ForegroundColor Green
}

Write-Host "🎉 テストケース生成完了!" -ForegroundColor Green
Write-Host "💡 使用方法: .\main.ps1 test $ContestNumber $($Problem.ToLower()) cpp" -ForegroundColor Blue