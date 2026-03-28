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
.PARAMETER Art
    Display ASCII art banner (switch flag)
.EXAMPLE
    acp abc450
    acp abc450 s
    acp abc450 -Art
.NOTES
    After execution, changes to contest directory via cd command
#>

param(
    [string]$Contest = "",
    [string]$Mode = "",
    [switch]$Art = $false
)

# Global start time
$script:StartTime = Get-Date

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

# Get current timestamp in HH:MM:SS format
function Get-Timestamp {
    return (Get-Date).ToString("HH:mm:ss")
}

# Display ASCII art from file if -Art flag is set
function Show-AsciiArt {
    $asciiPath = Join-Path (Split-Path $PSScriptRoot) "image_ascii.txt"
    if ((Test-Path $asciiPath) -and $Art) {
        Write-Info "[$(Get-Timestamp)] ASCII Art Banner"
        Write-Host ""
        try {
            $asciiContent = Get-Content $asciiPath -Raw
            Write-Host $asciiContent
        } catch {
            Write-Warning "[$(Get-Timestamp)] ASCII art file not found or unreadable"
        }
        Write-Host ""
        Write-Host ""
    }
}

# Check network connectivity to atcoder.jp
function Check-Network {
    Write-Info "[$(Get-Timestamp)] Network connectivity check..."
    try {
        $pingResult = Test-Connection -ComputerName "atcoder.jp" -Count 1 -Quiet -ErrorAction SilentlyContinue
        if ($pingResult) {
            Write-Success "[$(Get-Timestamp)] ✓ Connected to AtCoder"
        } else {
            Write-Warning "[$(Get-Timestamp)] ⚠ Cannot reach AtCoder.jp (continuing anyway)"
        }
    } catch {
        Write-Warning "[$(Get-Timestamp)] ⚠ Network check failed: $_"
    }
}

# Get generated files information
function Get-GeneratedFiles {
    param([string]$ContestPath)
    
    Write-Info "[$(Get-Timestamp)] Checking generated files..."
    
    $mainFiles = @()
    $foreach = [char[]]"abcdefghijklmnopqrstuvwxyz"
    foreach ($letter in $foreach) {
        $file = Join-Path $ContestPath "main${letter}.py"
        if (Test-Path $file) {
            $mainFiles += $letter.ToString().ToUpper()
        }
    }
    
    # Check for template.py
    $hasTemplate = Test-Path (Join-Path $ContestPath "template.py")
    $hasInput = Test-Path (Join-Path $ContestPath "input")
    
    Write-Success "[$(Get-Timestamp)] ✓ Files generated:"
    Write-Host "    Problems: $($mainFiles -join ', ')" -ForegroundColor Green
    Write-Host "    Template: $(if ($hasTemplate) { '✓' } else { '✗' })" -ForegroundColor Green
    Write-Host "    Input dir: $(if ($hasInput) { '✓' } else { '✗' })" -ForegroundColor Green
}

# Display checklist from template
function Show-Checklist {
    $templatePath = (Split-Path $PSScriptRoot) + "\templates\.md"
    # Alternative: read from .template/.md in parent directory
    $altPath = Join-Path (Split-Path $PSScriptRoot) ".template" | Join-Path -ChildPath ".md"
    
    if (Test-Path $altPath) {
        $templatePath = $altPath
    }
    
    if (Test-Path $templatePath) {
        Write-Host ""
        Write-Info "[$(Get-Timestamp)] ======================== CHECKLIST ========================"
        try {
            $checklistContent = Get-Content $templatePath -Raw
            Write-Host $checklistContent
        } catch {
            Write-Warning "[$(Get-Timestamp)] Could not read checklist"
        }
        Write-Info "[$(Get-Timestamp)] ============================================================"
        Write-Host ""
    }
}

# Calculate elapsed time
function Get-ElapsedTime {
    $elapsed = (Get-Date) - $script:StartTime
    return [int]$elapsed.TotalSeconds
}

# Display summary
function Show-Summary {
    $elapsed = Get-ElapsedTime
    Write-Host ""
    Write-Success "[$(Get-Timestamp)] ✓ Setup complete!"
    Write-Info "[$(Get-Timestamp)] Total time: ${elapsed}s"
    Write-Host ""
}

# Display banner if -Art flag is set
if ($Art) {
    Show-AsciiArt
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

# Show startup information
Write-Host ""
Write-Info "[$(Get-Timestamp)] ========================================="
Write-Info "[$(Get-Timestamp)] Contest: $Contest | Mode: $(if ([string]::IsNullOrWhiteSpace($Mode)) { 'default (VSCode)' } else { $Mode })"
Write-Info "[$(Get-Timestamp)] ========================================="
Write-Host ""

# Network check
Check-Network
Write-Host ""

# Setup contest (acc new)
Write-Info "[$(Get-Timestamp)] [SETUP] Executing: acc new $Contest"
& acc new $Contest

if ($LASTEXITCODE -ne 0) {
    Write-ErrorMsg "[$(Get-Timestamp)] [ERROR] acc new failed with exit code $LASTEXITCODE"
    exit 1
}

Write-Success "[$(Get-Timestamp)] [SETUP] Contest setup completed"

# Navigate to contest directory
$ContestPath = ".\$Contest"
if (-not (Test-Path $ContestPath)) {
    Write-ErrorMsg "[$(Get-Timestamp)] [ERROR] Contest directory not created: $ContestPath"
    exit 1
}

# Display generated files information
Get-GeneratedFiles $ContestPath
Write-Host ""

# Display checklist/motivation
Show-Checklist

# Handle mode
if ([string]::IsNullOrWhiteSpace($Mode) -or $Mode -eq "default") {
    # Default mode: open in VSCode
    Write-Info "[$(Get-Timestamp)] [DEFAULT MODE] Opening contest folder in VSCode..."
    & code $ContestPath
    Write-Success "[$(Get-Timestamp)] [SUCCESS] VSCode opened"
} elseif ($Mode -eq "s") {
    # Sublime mode: open files in order
    Write-Info "[$(Get-Timestamp)] [SUBLIME MODE] Opening Sublime first..."
    
    # Launch Sublime and wait 3 seconds
    & subl
    Write-Info "[$(Get-Timestamp)] Waiting 1.5 seconds for Sublime to launch..."
    Start-Sleep -Seconds 1.5
    
    # Check if contest directory has template.py
    $TemplatePath = Join-Path $ContestPath "template.py"
    if (-not (Test-Path $TemplatePath)) {
        Write-ErrorMsg "[$(Get-Timestamp)] [ERROR] template.py not found in $ContestPath"
        exit 1
    }
    
    Write-Info "[$(Get-Timestamp)] Opening: template.py"
    & subl (Join-Path $ContestPath "template.py")
    Start-Sleep -Milliseconds 50
    
    # Get all main*.py files and filter for single-letter suffix (a-z)
    $mainFiles = @()
    foreach ($letter in [char[]]"abcdefghijklmnopqrstuvwxyz") {
        $file = Join-Path $ContestPath "main${letter}.py"
        if (Test-Path $file) {
            $mainFiles += $file
            Write-Info "[$(Get-Timestamp)] Opening: main${letter}.py"
            & subl $file
            Start-Sleep -Milliseconds 50
        }
    }
    & subl (Join-Path $ContestPath "maina.py")
    if ($mainFiles.Count -eq 0) {
        Write-Warning "[$(Get-Timestamp)] [WARNING] No main*.py files found (only template.py opened)"
    } else {
        Write-Success "[$(Get-Timestamp)] [SUCCESS] Opened template.py and $($mainFiles.Count) problem file(s) in Sublime"
    }
} else {
    Write-ErrorMsg "[$(Get-Timestamp)] Invalid mode: '$Mode' (use 's' for Sublime or leave empty for VSCode)"
    exit 1
}

# Show summary and elapsed time
Show-Summary

# Change to contest directory
Write-Info "[$(Get-Timestamp)] [CD] Changing to contest directory: $Contest"
Set-Location -Path $ContestPath
Write-Success "[$(Get-Timestamp)] [SUCCESS] Changed to: $(Get-Location)"
