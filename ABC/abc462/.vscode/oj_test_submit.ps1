param(
    [string]$PythonPath,
    [string]$ProblemLabel,
    [string]$ContestName
)

if ([string]::IsNullOrWhiteSpace($PythonPath) -or
    [string]::IsNullOrWhiteSpace($ProblemLabel) -or
    [string]::IsNullOrWhiteSpace($ContestName)) {
    Write-Error "PythonPath, ProblemLabel, and ContestName are required."
    exit 1
}

$testCommand = "$PythonPath main$ProblemLabel.py"

& oj test -c $testCommand -d "input/$ProblemLabel"
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

& oj submit -l 6083 "https://atcoder.jp/contests/$ContestName/tasks/${ContestName}_$ProblemLabel" "main$ProblemLabel.py"
