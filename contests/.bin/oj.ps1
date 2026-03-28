#Requires -Version 5.1
<#
.SYNOPSIS
    oj command wrapper for AtCoder contests (contest name auto-detected)
.DESCRIPTION
    Execute oj test / submit / test+submit from contest directories
.PARAMETER Mode
    Execution mode: t (test), m (submit), tm/both (test+submit)
.PARAMETER Problem
    Problem ID (e.g., a, b, c)
.PARAMETER Prefix
    File prefix (default: main)
.EXAMPLE
    ojp t a
    ojp tm a main
.NOTES
    Contest name is auto-detected from current directory name
#>

param(
    [string]$Mode = "",
    [string]$Problem = "",
    [string]$Prefix = "main"
)

# Color output functions
function Write-Info {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Yellow
}

function Write-ErrorMsg {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Red
}

# PyPy path
$PythonPath = "C:\VSCode_program\atcoder\contests\.venv-pypy311\Scripts\python.exe"

# Validate Python path
if (-not (Test-Path $PythonPath)) {
    Write-ErrorMsg "Python executable not found: $PythonPath"
    exit 1
}

# Auto-detect contest name from current directory
$CurrentDir = (Get-Location).Path
$Contest = Split-Path -Leaf $CurrentDir

# Interactive input for missing required arguments
if ([string]::IsNullOrWhiteSpace($Mode)) {
    Write-Info "Enter mode (t/m/tm/both):"
    $Mode = Read-Host "  > "
}

if ([string]::IsNullOrWhiteSpace($Problem)) {
    Write-Info "Enter problem ID:"
    $Problem = Read-Host "  > "
}

# Validate mode
$validModes = @("t", "m", "tm", "both")
if ($Mode -notin $validModes) {
    Write-ErrorMsg "Invalid mode: '$Mode' (valid: t, m, tm, both)"
    exit 1
}

# Resolve source file
$SourceFile = "${Prefix}${Problem}.py"
if (-not (Test-Path $SourceFile)) {
    Write-ErrorMsg "Source file not found: $SourceFile"
    exit 1
}

Write-Success "[RESOLVED] Source file: $SourceFile"

# Resolve input directory
$InputDir = "input/$Problem"

if (-not (Test-Path $InputDir)) {
    Write-Warning "[WARNING] Input directory not found: $InputDir (continuing without input)"
    $InputDirArg = $null
} else {
    Write-Success "[RESOLVED] Input directory: $InputDir"
    $InputDirArg = $InputDir
}

# Test execution function
function Invoke-TestMode {
    Write-Info ""
    if ($InputDirArg) {
        Write-Info "[TEST] Executing:"
        Write-Info "  oj test -c `"$PythonPath $SourceFile`" -d `"$InputDirArg`""
    } else {
        Write-Info "[TEST] Executing:"
        Write-Info "  oj test -c `"$PythonPath $SourceFile`""
    }
    
    if ($InputDirArg) {
        & oj test -c "$PythonPath $SourceFile" -d "$InputDirArg"
    } else {
        & oj test -c "$PythonPath $SourceFile"
    }

    # Keep a trailing newline so the shell prompt does not stick to command output.
    Write-Host ""
    
    return $LASTEXITCODE
}

# Submit execution function
function Invoke-SubmitMode {
    $Url = "https://atcoder.jp/contests/$Contest/tasks/${Contest}_${Problem}"
    Write-Info ""
    Write-Info "[SUBMIT] Executing:"
    Write-Info "  oj submit -l 6083 `"$Url`" `"$SourceFile`""
    
    & oj submit -l 6083 "$Url" "$SourceFile"

    Write-Host ""
    
    return $LASTEXITCODE
}

# Execute based on mode
Write-Info "`n========================================="
Write-Info "Mode: $Mode | Contest: $Contest | Problem: $Problem"
Write-Info "=========================================`n"

switch ($Mode) {
    "t" {
        Write-Info "=== TEST MODE ==="
        Invoke-TestMode
        $exitCode = $LASTEXITCODE
        if ($exitCode -eq 0) {
            Write-Success "[SUCCESS] Test completed"
        } else {
            Write-ErrorMsg "[FAILED] Test failed with exit code $exitCode"
        }
        exit $exitCode
    }
    
    "m" {
        Write-Info "=== SUBMIT MODE ==="
        Invoke-SubmitMode
        $exitCode = $LASTEXITCODE
        exit $exitCode
    }
    
    { $_ -in @("tm", "both") } {
        Write-Info "=== TEST + SUBMIT MODE ==="
        
        Invoke-TestMode
        $testExitCode = $LASTEXITCODE
        
        if ($testExitCode -eq 0) {
            Write-Success "[TEST PASSED] Proceeding to submit..."
            Invoke-SubmitMode
            exit $LASTEXITCODE
        } else {
            Write-ErrorMsg "[TEST FAILED] Skipping submit"
            exit $testExitCode
        }
    }
}
