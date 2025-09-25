@echo off
echo ?? AtCoder ???????
echo.
echo 1. ??????  : contest.bat open 375
echo 2. ????      : contest.bat timer  
echo 3. ????      : contest.bat status
echo 4. ??????  : contest.bat submit [??] [??]
echo 5. ???        : contest.bat help
echo.

if "%~1"=="open" powershell.exe -ExecutionPolicy Bypass -File "contest_helper.ps1" -Action OpenProblems -ContestNumber %2
if "%~1"=="timer" powershell.exe -ExecutionPolicy Bypass -File "contest_helper.ps1" -Action Timer
if "%~1"=="status" powershell.exe -ExecutionPolicy Bypass -File "contest_helper.ps1" -Action Status
if "%~1"=="submit" powershell.exe -ExecutionPolicy Bypass -File "contest_helper.ps1" -Action Submit -Problem %2 -Language %3
if "%~1"=="help" powershell.exe -ExecutionPolicy Bypass -File "contest_helper.ps1" -Action Help

if "%~1"=="" (
    echo ?????: ????
    powershell.exe -ExecutionPolicy Bypass -File "contest_helper.ps1" -Action Status
)
pause
