@echo off
chcp 65001 >nul
:: AtCoder ABC folder creation batch file v2.0

title AtCoder ABC Folder Creation Tool

if "%~1"=="" (
    echo.
    echo AtCoder ABC Folder Creation Tool v2.0
    echo =====================================
    echo.
    echo Usage: abc.bat [contest_number] [options]
    echo.
    echo Examples:
    echo   abc.bat 372                              # Basic creation
    echo   abc.bat 372 -Force                      # Force overwrite
    echo   abc.bat 372 -Open                       # Open folder
    echo   abc.bat 372 -VSCode                     # Open with VS Code
    echo   abc.bat 372 -CreateTestFiles            # Create test files
    echo   abc.bat 372 -Language cpp               # C++ only
    echo   abc.bat 372 -Date "2025-01-15"          # Set contest date
    echo   abc.bat 372 -Force -VSCode -CreateTestFiles # All options
    echo.
    echo Options:
    echo   -Force         Overwrite existing folder
    echo   -Open          Open in Explorer
    echo   -VSCode        Open in VS Code
    echo   -CreateTestFiles Create test input files
    echo   -Language      Specify language (cpp/python/both)
    echo   -Date          Set contest date (YYYY-MM-DD)
    echo.
    pause
    exit /b 1
)

echo Creating ABC%1 folder...
echo.

:: Execute PowerShell script
powershell.exe -ExecutionPolicy Bypass -File "%~dp0create_abc_v2.ps1" %*

echo.
echo Process completed!
pause