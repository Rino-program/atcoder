function New-ContestReadme([string]$ContestName, [string]$FolderPath, [bool]$IsNumeric) {
    try {
        if (-not (Test-Path $FolderPath)) { New-Item -Path $FolderPath -ItemType Directory | Out-Null }

        $readmePath = Join-Path $FolderPath "README.md"

        # 非数値コンテストの場合は URL 自動生成を行わず、簡易 README を作成
        if (-not $IsNumeric) {
            $title = "Contest: $ContestName"
            $content = @()
            $content += "# $title"
            $content += ""
            $content += "※ このコンテスト名は数値ではないため、問題ページの自動生成をスキップしています。手動で編集してください。"
            $content += ""
            $content += "## 使い方"
            $content += ('- サンプル取得: ..\\..\\scripts\\Fetch.ps1 -ContestName {0} -Problem A:D' -f $ContestName)
            $content += ('- テスト実行: ..\\..\\main.ps1 test {0} a py' -f $ContestName)
            $content -join "`n" | Out-File -FilePath $readmePath -Encoding UTF8
            return @{ Success = $true; Skipped = $true }
        }

        # 数値コンテスト (例: 431 -> abc431)
        $contestId = if ($ContestName -match '^[0-9]+$') { "abc$ContestName" } else { $ContestName }

        # 取得日時
        $now = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

        # Try to fetch the tasks page and parse problem ids (A, B, ...)
        $taskUrl = "https://atcoder.jp/contests/$contestId/tasks"
        $problems = @()
        try {
            $resp = Invoke-WebRequest -Uri $taskUrl -UseBasicParsing -ErrorAction Stop -TimeoutSec 15
            $html = $resp.Content
            # Find links like /contests/abc431/tasks/abc431_a
            $matches = [regex]::Matches($html, '/contests/[^"''>]+/tasks/(?<task>[^"''/>]+)')
            foreach ($m in $matches) {
                $task = $m.Groups['task'].Value
                # extract trailing part after last _ (abc431_a -> a)
                if ($task -match '_([a-zA-Z0-9]+)$') { $p = $Matches[1].ToUpper(); $problems += $p }
            }
            $problems = $problems | Select-Object -Unique
            # sort by single-letter if possible
            $problems = $problems | Sort-Object { $_ }
        } catch {
            # on failure fallback to A-D
            $problems = @('A','B','C','D')
        }

        if (-not $problems -or $problems.Count -eq 0) { $problems = @('A','B','C','D') }

        # Build README content based on the old template but dynamic
        $title = "${ContestName} コンテスト情報・記録"
        $content = New-Object System.Collections.ArrayList
        $content.Add("# $ContestName コンテスト情報・記録") | Out-Null
        $content.Add("") | Out-Null
        $content.Add("**作成日時**: $now") | Out-Null
        $content.Add("**システム**: AtCoder ABC 多機能統合システム v4.1") | Out-Null
        $content.Add("## 🔗 コンテストリンク") | Out-Null
        $content.Add("") | Out-Null
        $content.Add("**メインページ**: https://atcoder.jp/contests/$contestId/tasks") | Out-Null
        $content.Add("") | Out-Null
        $content.Add("### 個別問題") | Out-Null
        foreach ($p in $problems) {
            $link = "https://atcoder.jp/contests/$contestId/tasks/${contestId}_$($p.ToLower())"
            # Count local samples if present
            $tcDir = Join-Path $FolderPath (Join-Path 'testcases' $p)
            $sampleCount = 0
            if (Test-Path $tcDir) {
                $ins = Get-ChildItem -Path $tcDir -Filter 'in_*.txt' -File -ErrorAction SilentlyContinue
                if ($ins) { $sampleCount = $ins.Count }
            }
            $suffix = if ($sampleCount -gt 0) { " (サンプル: $sampleCount セット)" } else { "" }
            $content.Add(("- **$($p)問題**: $link$suffix")) | Out-Null
        }
        $content.Add("") | Out-Null
        $content.Add("## 📊 問題進捗") | Out-Null
        $content.Add("") | Out-Null
        # Table header
        $content.Add("| 問題 | 状態 | 難易度 | 解法 | 実行時間 | 備考 |") | Out-Null
        $content.Add("|------|------|--------|------|----------|------|") | Out-Null
        foreach ($p in $problems) {
            # If testcases exist, show count in 備考
            $tcDir = Join-Path $FolderPath (Join-Path 'testcases' $p)
            $sampleCount = 0
            if (Test-Path $tcDir) {
                $ins = Get-ChildItem -Path $tcDir -Filter 'in_*.txt' -File -ErrorAction SilentlyContinue
                if ($ins) { $sampleCount = $ins.Count }
            }
            $note = if ($sampleCount -gt 0) { "サンプル:$sampleCount" } else { "" }
            $content.Add(("| $p | ⭕❌ | | | ms | $note |")) | Out-Null
        }
        $content.Add("") | Out-Null
        $content.Add("## ⏱️ 時間記録") | Out-Null
        $content.Add("") | Out-Null
        $content.Add("- **開始時刻**: ____:____") | Out-Null
        foreach ($p in $problems) { $content.Add(("- **$($p)問題**: ____:____ (____分)")) | Out-Null }
        $content.Add("- **終了時刻**: ____:____") | Out-Null
        $content.Add("- **合計時間**: ____分") | Out-Null
        $content.Add("") | Out-Null
        $content.Add("## 💡 解法メモ・反省点") | Out-Null
        $content.Add("") | Out-Null
        foreach ($p in $problems) {
            $content.Add("### $($p)問題") | Out-Null
            $content.Add("\\\\") | Out-Null
            $content.Add("解法:") | Out-Null
            $content.Add("") | Out-Null
            $content.Add("反省:") | Out-Null
            $content.Add("\\\\") | Out-Null
            $content.Add("") | Out-Null
        }
        $content.Add("## 🔍 学んだこと・Tips") | Out-Null
        $content.Add("") | Out-Null
        $content.Add("## 🗂️ ファイル構成") | Out-Null
        $content.Add("") | Out-Null
        $content.Add("- **main.cpp** / **main.py** - 解答ファイル") | Out-Null
        $content.Add("- **testcases/** - 自動ダウンロードされたテストケース (scripts/Fetch.ps1)") | Out-Null
        $content.Add("- **.vscode/** - VS Code設定") | Out-Null
        $content.Add("") | Out-Null
        $content.Add("---") | Out-Null
        $content.Add("*AtCoder ABC 多機能統合システム v4.1*") | Out-Null

        # Write README
        ($content -join "`n") | Out-File -FilePath $readmePath -Encoding UTF8

        return @{ Success = $true }
    } catch {
        return @{ Success = $false; Error = $_ }
    }
}
