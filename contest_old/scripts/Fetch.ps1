# =============================================================================
# Fetch.ps1 - サンプルテストケース一括取得 (oj 優先, acc フォールバック)
# =============================================================================

param(
    [Parameter(Mandatory=$true)][string]$ContestName,
    [Parameter(Mandatory=$false)][string]$Problem = "A:D"
)

function Write-Error2([string]$msg) { Write-Host "[ERROR] $msg" -ForegroundColor Red }
function Write-Info([string]$msg) { Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Success([string]$msg) { Write-Host "[OK] $msg" -ForegroundColor Green }

# コンテストIDをそのまま使用
$contestId = $ContestName

# Problem 引数のパース: 例 A:D, A,C,E, B など
function Expand-Problems([string]$spec) {
    $spec = $spec.Trim()
    if (-not $spec) { return @() }
    $spec = $spec.ToUpper()
    $parts = $spec -split ','
    $out = @()
    foreach ($p in $parts) {
        # 範囲指定を - または : で受け付ける (例: A-D または A:D)
        if ($p -match '^(\\w)[:-](\\w)$') {
            $start = [char]$Matches[1]
            $end = [char]$Matches[2]
            for ($c = [int][char]$start; $c -le [int][char]$end; $c++) {
                $out += ([char]$c)
            }
        } else {
            $out += $p
        }
    }
    return $out | Select-Object -Unique
}

$problemSpec = $Problem -replace ':','-'
# シンプルに範囲かカンマ区切りで処理
if ($problemSpec -match '^(\w)[:-](\w)$') {
    $start = [char]$Matches[1]
    $end = [char]$Matches[2]
    $problems = @()
    for ($c = [int][char]$start; $c -le [int][char]$end; $c++) { $problems += ([char]$c) }
} else {
    $problems = ($problemSpec -split ',') | ForEach-Object { $_.Trim().ToUpper() } | Where-Object { $_ -ne '' } | Select-Object -Unique
}
if ($problems.Count -eq 0) { Write-Info "対象問題が指定されていません。終了します。"; exit 0 }

# 作業ディレクトリ: コンテストフォルダ
$contestDir = Join-Path (Get-Location) $ContestName
if (-not (Test-Path $contestDir)) {
    Write-Info "コンテストフォルダが存在しないため作成します: $contestDir"
    New-Item -ItemType Directory -Path $contestDir | Out-Null
}

$testcasesRoot = Join-Path $contestDir "testcases"
if (-not (Test-Path $testcasesRoot)) { New-Item -ItemType Directory -Path $testcasesRoot | Out-Null }

# コマンド存在チェック
$ojCmd = Get-Command oj -ErrorAction SilentlyContinue
$accCmd = Get-Command acc -ErrorAction SilentlyContinue
if ($ojCmd) { Write-Info "'oj' を検出しました。oj を優先して使用します。" }
elseif ($accCmd) { Write-Info "'oj' が見つかりません。'acc' を使用します。" }
else { Write-Error2 "'oj' と 'acc' の両方が見つかりません。online-judge-tools または atcoder-cli を有効にしてください。"; exit 1 }

# 各問題ごとにサンプルをダウンロード
foreach ($p in $problems) {
    $prob = $p.ToString().ToUpper()
    if ($prob -eq '') { continue }
    Write-Info "--- 問題 $prob の処理 ---"

    $problemUrl = "https://atcoder.jp/contests/$contestId/tasks/${contestId}_$($prob.ToLower())"
    Write-Info "問題URL: $problemUrl"

    $destDir = Join-Path $testcasesRoot $prob
    if (-not (Test-Path $destDir)) { New-Item -ItemType Directory -Path $destDir | Out-Null }

    # 一時ディレクトリで oj/acc を実行
    $tmp = Join-Path $env:TEMP ([System.Guid]::NewGuid().ToString())
    New-Item -ItemType Directory -Path $tmp | Out-Null
    Push-Location $tmp
    try {
        if ($ojCmd) {
            Write-Info "oj でダウンロードを実行..."
            & oj d $problemUrl 2>&1 | Write-Host
            $exit = $LASTEXITCODE
        } else {
            Write-Info "acc でダウンロードを実行..."
            # acc のサンプル取得サブコマンドは環境により異なるため基本的な呼び出しを試みる
            & acc download $problemUrl 2>&1 | Write-Host
            $exit = $LASTEXITCODE
        }

        if ($exit -ne 0) {
            Write-Error2 "ダウンロードコマンドが非0を返しました (問題 $prob)。一時ディレクトリ: $tmp"
            Pop-Location
            if (Test-Path $tmp) { Remove-Item -Recurse -Force $tmp }
            continue
        }

        # ダウンロードされたファイルを探索して移動
        $files = Get-ChildItem -File -Recurse | Where-Object { $_.Length -gt 0 }
        if (-not $files -or $files.Count -eq 0) {
            Write-Error2 "サンプルが検出されませんでした (oj/acc の出力を確認してください)。"
            Pop-Location
            Remove-Item -Recurse -Force $tmp
            continue
        }

        # 推定: 入力ファイル (.in, sample-*.in, input*.txt) と出力ファイル をマッチ
        $inFiles = $files | Where-Object { $_.Name -match '\.in$|^input|sample.*\.in|^in_' }
        $outFiles = $files | Where-Object { $_.Name -match '\.out$|^output|sample.*\.out|^out_' }

        # 代替マッチ (拡張子なしで in/out のペアがある場合など)
        if (($inFiles.Count -eq 0) -and ($outFiles.Count -eq 0)) {
            # 例えば oj が sample-1.txt sample-1-ans.txt のように出すケースを考慮
            $inFiles = $files | Where-Object { $_.Name -match 'sample.*1.*in|sample.*input' }
            $outFiles = $files | Where-Object { $_.Name -match 'sample.*1.*out|sample.*ans|sample.*output' }
        }

        # 並べ替えしてペアにする
        $inFiles = $inFiles | Sort-Object Name
        $outFiles = $outFiles | Sort-Object Name

        $count = [Math]::Max($inFiles.Count, $outFiles.Count)
        if ($count -eq 0) {
            # ファイル群を行単位で分割する形式 (oj が single file にまとめる場合) を試みる
            foreach ($f in $files) {
                # もしファイルに "Sample Input" の文字列が含まれていれば分割処理に挑戦 (簡易)
                $text = Get-Content $f.FullName -Raw -ErrorAction SilentlyContinue
                if ($text -and $text -match 'Sample Input') {
                    # 単純にファイル全体を in_1.txt として保存
                    Copy-Item $f.FullName (Join-Path $destDir "in_1.txt") -Force
                    Write-Info "単一ファイルを in_1.txt として保存: $($f.Name)"
                    $count = 1
                    break
                }
            }
        }

        for ($i = 0; $i -lt $count; $i++) {
            $idx = $i + 1
            if ($i -lt $inFiles.Count) {
                $src = $inFiles[$i].FullName
                $dst = Join-Path $destDir ("in_$idx.txt")
                Copy-Item $src $dst -Force
            }
            if ($i -lt $outFiles.Count) {
                $src = $outFiles[$i].FullName
                $dst = Join-Path $destDir ("out_$idx.txt")
                Copy-Item $src $dst -Force
            }
        }

        Write-Success "問題 $prob のサンプルを $destDir に保存しました (合計 $count セット)"
    }
    catch {
        Write-Error2 "例外: $_"
    }
    finally {
        Pop-Location
        if (Test-Path $tmp) { Remove-Item -Recurse -Force $tmp }
    }
}

Write-Success "すべて完了しました。testcases フォルダを確認してください: $testcasesRoot"
