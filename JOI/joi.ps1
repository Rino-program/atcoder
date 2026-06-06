param(
  [Parameter(Mandatory = $true)]
  [string]$DirName,
  
  [string[]]$Urls,
  [string]$UrlFile
)

$scriptDir = (Resolve-Path (Join-Path $PSScriptRoot ".")).Path
$cwd = (Get-Location).Path

if ((Split-Path -Leaf $scriptDir) -ieq "JOI") {
  $joiRoot = $scriptDir
  $root = (Resolve-Path (Join-Path $joiRoot "..")).Path
} elseif ((Split-Path -Leaf $cwd) -ieq "JOI") {
  $joiRoot = $cwd
  $root = (Resolve-Path (Join-Path $joiRoot "..")).Path
} elseif (Test-Path (Join-Path $scriptDir "JOI")) {
  $root = $scriptDir
  $joiRoot = Join-Path $root "JOI"
} else {
  Write-Error "Cannot determine root/JOI directory. Put joi.ps1 under contests/JOI or run from JOI."
  exit 1
}

$allUrls = @()
if ($Urls) {
  $allUrls += $Urls
}
if (-not [string]::IsNullOrWhiteSpace($UrlFile)) {
  if (-not (Test-Path $UrlFile)) {
    Write-Error "UrlFile not found: $UrlFile"
    exit 1
  }
  $fileUrls = Get-Content -Path $UrlFile | ForEach-Object { $_.Trim() } | Where-Object { $_ -and -not $_.StartsWith("#") }
  $allUrls += $fileUrls
}

$allUrls = $allUrls | ForEach-Object { $_.Trim() } | Where-Object { $_ } | Select-Object -Unique
if (-not $allUrls -or $allUrls.Count -eq 0) {
  Write-Error "No URLs provided. Specify -Urls and/or -UrlFile."
  exit 1
}

$parsed = @()
foreach ($url in $allUrls) {
  if ($url -notmatch "^https?://atcoder\.jp/contests/([^/]+)/tasks/([^/?#]+)") {
    Write-Error "Invalid AtCoder task URL: $url"
    exit 1
  }

  $parsed += [PSCustomObject]@{
    Url = $url
    ContestId = $Matches[1]
    TaskId = $Matches[2]
  }
}

$contestIds = @($parsed | Select-Object -ExpandProperty ContestId | Sort-Object -Unique)
if ($contestIds.Count -eq 1) {
  $contestId = $contestIds[0]
  $contestUrl = "https://atcoder.jp/contests/$contestId"
} else {
  $contestId = $DirName
  $contestUrl = ""
}
$defaultProblemId = $parsed[0].TaskId

$dest = Join-Path $joiRoot $DirName
$inputRoot = Join-Path $dest "input"
$destVscode = Join-Path $dest ".vscode"

New-Item -ItemType Directory -Force -Path $inputRoot | Out-Null

$templateVscode = Join-Path $root ".template\.vscode"
if (Test-Path $templateVscode) {
  Copy-Item -Recurse -Force $templateVscode $destVscode
} else {
  New-Item -ItemType Directory -Force -Path $destVscode | Out-Null
}

$templateMainSource = Join-Path $root ".template\main.py"
$templatePySource = Join-Path $root ".template\template.py"
$templateSource = $null
if (Test-Path $templateMainSource) {
  $templateSource = $templateMainSource
} elseif (Test-Path $templatePySource) {
  $templateSource = $templatePySource
}

if (Test-Path $templatePySource) {
  Copy-Item -Force $templatePySource (Join-Path $dest "template.py")
} elseif (-not (Test-Path (Join-Path $dest "template.py"))) {
  Set-Content -Path (Join-Path $dest "template.py") -Value "" -NoNewline
}

$tasks = @"
{
  "version": "2.0.0",
  "inputs": [
    {
      "id": "problemId",
      "type": "promptString",
      "description": "Problem ID (e.g. joi2026_yo1a_d)",
      "default": "$defaultProblemId"
    }
  ],
  "tasks": [
    {
      "label": "OJ Test",
      "type": "shell",
      "command": "oj",
      "args": [
        "test",
        "-c",
        "`${config:python.defaultInterpreterPath} `${input:problemId}.py",
        "-d",
        "input/`${input:problemId}"
      ],
      "options": {
        "cwd": "`${workspaceFolder}"
      },
      "problemMatcher": []
    }
  ]
}
"@
Set-Content -Path (Join-Path $destVscode "tasks.json") -Value $tasks -Encoding ascii
Remove-Item -Force -ErrorAction SilentlyContinue (Join-Path $destVscode "oj_submit.ps1")
Remove-Item -Force -ErrorAction SilentlyContinue (Join-Path $destVscode "oj_test_submit.ps1")
Remove-Item -Force -ErrorAction SilentlyContinue (Join-Path $destVscode "problem_urls.json")

$settingsPath = Join-Path $destVscode "settings.json"
if (-not (Test-Path $settingsPath)) {
  $settings = @"
{
  "workbench.secondarySideBar.defaultVisibility": "hidden"
}
"@
  Set-Content -Path $settingsPath -Value $settings -Encoding ascii
}
$tasksAcc = @()

for ($i = 0; $i -lt $parsed.Count; $i++) {
  $taskId = $parsed[$i].TaskId

  $mainPath = Join-Path $dest "$taskId.py"
  if ($templateSource) {
    Copy-Item -Force $templateSource $mainPath
  } elseif (-not (Test-Path $mainPath)) {
    Set-Content -Path $mainPath -Value "" -NoNewline
  }

  $inputDir = Join-Path $inputRoot $taskId
  New-Item -ItemType Directory -Force -Path $inputDir | Out-Null

  $tasksAcc += @{
    id = $taskId
    label = $taskId
    title = $taskId
    url = $parsed[$i].Url
    directory = @{
      path = "."
      testdir = "input/$taskId"
      submit = "$taskId.py"
    }
  }
}

$contestAcc = @{
  contest = @{
    id = $contestId
    title = $contestId
    url = $contestUrl
  }
  tasks = $tasksAcc
}
$contestAccJson = $contestAcc | ConvertTo-Json -Depth 6
Set-Content -Path (Join-Path $dest "contest.acc.json") -Value $contestAccJson -Encoding ascii

$oj = Get-Command oj -ErrorAction SilentlyContinue
if (-not $oj) {
  Write-Error "oj command not found. Install online-judge-tools first."
  exit 1
}

for ($i = 0; $i -lt $parsed.Count; $i++) {
  $taskId = $parsed[$i].TaskId
  $inputDir = Join-Path $inputRoot $taskId
  & $oj.Path download $parsed[$i].Url -d $inputDir
  if ($LASTEXITCODE -ne 0) {
    Write-Warning "oj download failed for URL: $($parsed[$i].Url). Continue without samples."
  }
}
