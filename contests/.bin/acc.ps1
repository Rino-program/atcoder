#Requires -Version 5.1
<#
.SYNOPSIS
    acc command wrapper for AtCoder contest setup
.DESCRIPTION
    Setup AtCoder contests and open files in VSCode or Sublime
.PARAMETER Contest
    Contest ID (e.g., abc450)
.PARAMETER Mode
    Execution mode: (default) open in VSCode, s (Sublime mode)
.EXAMPLE
    acp abc450
    acp abc450 s
.NOTES
    After execution, changes to contest directory via cd command
#>

param(
    [string]$Contest = "",
    [string]$Mode = ""
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

# Interactive input for missing contest
if ([string]::IsNullOrWhiteSpace($Contest)) {
    Write-Info "Enter contest name:"
    $Contest = Read-Host "  > "
}

if ([string]::IsNullOrWhiteSpace($Contest)) {
    Write-ErrorMsg "Contest name is required"
    exit 1
}

Write-Info "`n========================================="
Write-Info "Contest: $Contest | Mode: $(if ([string]::IsNullOrWhiteSpace($Mode)) { 'default (VSCode)' } else { $Mode })"
Write-Info "=========================================`n"

# Setup contest (acc new)
Write-Info "[SETUP] Executing: acc new $Contest"
& acc new $Contest

if ($LASTEXITCODE -ne 0) {
    Write-ErrorMsg "[ERROR] acc new failed with exit code $LASTEXITCODE"
    exit 1
}

Write-Success "[SETUP] Contest setup completed"

# Navigate to contest directory
$ContestPath = ".\$Contest"
if (-not (Test-Path $ContestPath)) {
    Write-ErrorMsg "[ERROR] Contest directory not created: $ContestPath"
    exit 1
}

# Handle mode
if ([string]::IsNullOrWhiteSpace($Mode) -or $Mode -eq "default") {
    # Default mode: open in VSCode
    Write-Info "[DEFAULT MODE] Opening contest folder in VSCode..."
    & code $ContestPath
    Write-Success "[SUCCESS] VSCode opened"
} elseif ($Mode -eq "s") {
    # Sublime mode: open files in order
    Write-Info "[SUBLIME MODE] Opening files in Sublime..."
    
    # Check if contest directory has template.py
    $TemplatePath = Join-Path $ContestPath "template.py"
    if (-not (Test-Path $TemplatePath)) {
        Write-ErrorMsg "[ERROR] template.py not found in $ContestPath"
        exit 1
    }
    
    Write-Info "Opening: template.py"
    & subl (Join-Path $ContestPath "template.py")
    Start-Sleep -Milliseconds 200
    
    # Get all main*.py files and filter for single-letter suffix (a-z)
    $mainFiles = @()
    foreach ($letter in [char[]]"abcdefghijklmnopqrstuvwxyz") {
        $file = Join-Path $ContestPath "main${letter}.py"
        if (Test-Path $file) {
            $mainFiles += $file
            Write-Info "Opening: main${letter}.py"
            & subl $file
            Start-Sleep -Milliseconds 200
        }
    }
    
    if ($mainFiles.Count -eq 0) {
        Write-Warning "[WARNING] No main*.py files found (only template.py opened)"
    } else {
        Write-Success "[SUCCESS] Opened template.py and $($mainFiles.Count) problem file(s) in Sublime"
    }
} else {
    Write-ErrorMsg "Invalid mode: '$Mode' (use 's' for Sublime or leave empty for VSCode)"
    exit 1
}

# Change to contest directory
Write-Info "[CD] Changing to contest directory: $Contest"
Set-Location -Path $ContestPath
Write-Success "[SUCCESS] Changed to: $(Get-Location)"
