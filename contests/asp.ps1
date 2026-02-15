param(
  [Parameter(Mandatory = $true)]
  [string]$Url
)

$scriptDir = (Resolve-Path (Join-Path $PSScriptRoot ".")).Path
$cwd = (Get-Location).Path

if ((Split-Path -Leaf $cwd) -ieq "ASP") {
  $aspRoot = $cwd
  $root = (Resolve-Path (Join-Path $aspRoot "..")).Path
} elseif (Test-Path (Join-Path $scriptDir "ASP")) {
  $root = $scriptDir
  $aspRoot = Join-Path $root "ASP"
} elseif ((Split-Path -Leaf $scriptDir) -ieq "ASP") {
  $aspRoot = $scriptDir
  $root = (Resolve-Path (Join-Path $aspRoot "..")).Path
} else {
  Write-Error "Cannot determine root/ASP directory. Run this script from ASP or place asp.ps1 under contests/."
  exit 1
}

if ($Url -notmatch "^https?://atcoder\.jp/contests/([^/]+)/tasks/([^/?#]+)") {
  Write-Error "Invalid AtCoder task URL: $Url"
  exit 1
}

$contestId = $Matches[1]
$taskId = $Matches[2]
$dest = Join-Path $aspRoot $taskId
$inputDir = Join-Path $dest "input"

New-Item -ItemType Directory -Force -Path $inputDir | Out-Null

$templateVscode = Join-Path $root ".template\.vscode"
$destVscode = Join-Path $dest ".vscode"
if (Test-Path $templateVscode) {
  Copy-Item -Recurse -Force $templateVscode $destVscode
}

$tasksPath = Join-Path $destVscode "tasks.json"
$aspTasks = @"
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "OJ Test",
      "type": "shell",
      "command": "oj",
      "args": [
        "test",
        "-c",
        "`${config:python.defaultInterpreterPath} main.py",
        "-d",
        "input"
      ],
      "options": {
        "cwd": "`${workspaceFolder}"
      },
      "problemMatcher": []
    },
    {
      "label": "OJ Test+Submit",
      "type": "shell",
      "command": "powershell",
      "args": [
        "-NoProfile",
        "-Command",
        "oj test -c `${config:python.defaultInterpreterPath} main.py -d input; if (`$LASTEXITCODE -ne 0) { exit `$LASTEXITCODE }; oj submit -l 6083 $Url main.py"
      ],
      "options": {
        "cwd": "`${workspaceFolder}"
      },
      "problemMatcher": []
    },
    {
      "label": "OJ Submit",
      "type": "shell",
      "command": "oj",
      "args": [
        "submit",
        "-l",
        "6083",
        "$Url",
        "main.py"
      ],
      "options": {
        "cwd": "`${workspaceFolder}"
      },
      "problemMatcher": []
    }
  ]
}
"@
if (Test-Path $destVscode) {
  Set-Content -Path $tasksPath -Value $aspTasks -Encoding ascii
}

$templateMainSource = Join-Path $root ".template\main.py"
$templatePySource = Join-Path $root ".template\template.py"
$mainPath = Join-Path $dest "main.py"
$templatePath = Join-Path $dest "template.py"

if (Test-Path $templateMainSource) {
  Copy-Item -Force $templateMainSource $mainPath
} elseif (Test-Path $templatePySource) {
  Copy-Item -Force $templatePySource $mainPath
} elseif (-not (Test-Path $mainPath)) {
  Set-Content -Path $mainPath -Value "" -NoNewline
}

if (Test-Path $templatePySource) {
  Copy-Item -Force $templatePySource $templatePath
}

$contestAccPath = Join-Path $dest "contest.acc.json"
if (-not (Test-Path $contestAccPath)) {
  $contestUrl = "https://atcoder.jp/contests/$contestId"
  $acc = @{
    contest = @{
      id = $contestId
      title = $contestId
      url = $contestUrl
    }
    tasks = @(
      @{
        id = $taskId
        label = $taskId
        title = $taskId
        url = $Url
        directory = @{
          path = "."
          testdir = "input"
          submit = "main.py"
        }
      }
    )
  }
  $accJson = $acc | ConvertTo-Json -Depth 5
  Set-Content -Path $contestAccPath -Value $accJson -Encoding ascii
}

$oj = Get-Command oj -ErrorAction SilentlyContinue
if (-not $oj) {
  Write-Error "oj command not found. Install online-judge-tools first."
  exit 1
}

& $oj.Path download $Url -d $inputDir
