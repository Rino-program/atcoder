@echo off
echo ?? ?????????
echo ????: test.bat [??] [??]
echo ?: test.bat a python

if "%~1"=="" goto help
if "%~2"=="" goto help

powershell.exe -ExecutionPolicy Bypass -File "test_runner.ps1" -Problem %1 -Language %2
goto end

:help
echo ??: a, b, c, d
echo ??: cpp, python
pause

:end
