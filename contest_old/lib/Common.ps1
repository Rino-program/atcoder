function Write-Header([string]$msg) { Write-Host "`n=== $msg ===`n" -ForegroundColor Cyan }
function Write-Banner([string]$msg) { Write-Host "---- $msg ----" -ForegroundColor Yellow }
function Write-Info([string]$msg) { Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Success([string]$msg) { Write-Host "[OK] $msg" -ForegroundColor Green }
function Write-Error2([string]$msg) { Write-Host "[ERROR] $msg" -ForegroundColor Red }
function Write-Warning2([string]$msg) { Write-Host "[WARN] $msg" -ForegroundColor Yellow }

# テンプレート関連の簡易実装
function Get-TemplateDir() {
    return (Join-Path (Split-Path -Parent $PSScriptRoot) "templates")
}

function Copy-TemplateFiles([string]$SourceDir, [string]$DestDir) {
    try {
        Copy-Item -Path (Join-Path $SourceDir "*") -Destination $DestDir -Recurse -Force
        return $true
    }
    catch {
        Write-Error2 "テンプレートのコピー失敗: $_"
        return $false
    }
}

function Test-ContestName([string]$name) {
    return -not [string]::IsNullOrWhiteSpace($name)
}

function Test-IsNumeric([string]$name) {
    return $name -match '^[0-9]+$'
}

function Invoke-SafeAction([scriptblock]$action, [string]$errMsg) {
    try {
        & $action
        return $true
    }
    catch {
        Write-Error2 $errMsg
        return $false
    }
}

function Start-Browser {
    param(
        [Parameter(Mandatory=$true)][object]$URLs
    )
    if ($URLs -is [System.Collections.IEnumerable]) {
            foreach ($u in $URLs) {
                try {
                    # Try multiple ways to locate Chrome; fallback to default browser
                    $chrome = $null
                    $pf = $env:ProgramFiles
                    $pf86 = ${env:ProgramFiles(x86)}
                    $chromePaths = @()
                    if ($pf) { $chromePaths += (Join-Path $pf 'Google\Chrome\Application\chrome.exe') }
                    if ($pf86) { $chromePaths += (Join-Path $pf86 'Google\Chrome\Application\chrome.exe') }
                    foreach ($p in $chromePaths) { if (Test-Path $p) { $chrome = $p; break } }

                    # Check registry App Paths for chrome.exe
                    if (-not $chrome) {
                        try {
                            $reg = Get-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe' -ErrorAction SilentlyContinue
                            if ($reg) {
                                if ($reg.'(default)') { $chrome = $reg.'(default)' }
                                elseif ($reg.Path) { $chrome = Join-Path $reg.Path 'chrome.exe' }
                            }
                        } catch {}
                    }

                    # Check PATH (Get-Command)
                    if (-not $chrome) {
                        try {
                            $cmd = Get-Command chrome.exe -ErrorAction SilentlyContinue
                            if ($cmd) { $chrome = $cmd.Source }
                        } catch {}
                    }

                    if ($chrome) {
                        Start-Process -FilePath $chrome -ArgumentList $u
                    } else {
                        # As a last resort, try to invoke chrome via cmd start (works if 'chrome' is registered)
                        try {
                            Start-Process -FilePath 'cmd.exe' -ArgumentList "/c start chrome \"$u\""
                        } catch {
                            # fallback: open URL with default browser
                            Start-Process $u
                        }
                    }
                } catch {
                    Write-Warning "ブラウザーを開けませんでした: $u"
                }
            }
    } else {
        Start-Process $URLs
    }
}

    function Get-ContestProblems {
        param(
            [Parameter(Mandatory=$true)][string]$ContestName
        )
        # Try to fetch problem list from AtCoder tasks page. Returns array of problem ids (A,B,C...)
        $url = "https://atcoder.jp/contests/abc$ContestName/tasks"
        try {
            $html = (Invoke-WebRequest -Uri $url -UseBasicParsing -ErrorAction Stop).Content
            # Look for task links like /contests/abc123/tasks/abc123_a
            $matches = [regex]::Matches($html, "/tasks/abc${ContestName}_(?<prob>[a-z])")
            $probs = @{}
            foreach ($m in $matches) { $probs[$m.Groups['prob'].Value.ToUpper()] = $true }
            $list = $probs.Keys | Sort-Object
            if ($list.Count -gt 0) { return ,$list }
        } catch {
            # ignore, fallback
        }
        # Fallback to A..D
        return ,('A','B','C','D')
    }
# 指定したコンテストの AtCoder URL リストを返す (簡易実装)
function Get-AtCoderURLs([string]$ContestName) {
    if (-not $ContestName) { return @() }
    $contestId = $ContestName
    if ($ContestName -match '^[0-9]+$') { $contestId = "abc$ContestName" }

    $urls = @()
    # コンテスト概要ページ
    $urls += "https://atcoder.jp/contests/$contestId"

    # デフォルトで A〜D の問題ページを生成（必要なら範囲を拡張可能）
    $probs = @('a','b','c','d')
    foreach ($p in $probs) {
        $urls += "https://atcoder.jp/contests/$contestId/tasks/${contestId}_$p"
    }

    return $urls
}

# Export-ModuleMember is not used here; this file is dot-sourced, not a module.
