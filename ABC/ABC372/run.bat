@echo off
chcp 65001 >nul
if "%1"=="" goto help

if "%1"=="test" goto test
if "%1"=="timer" goto timer
if "%1"=="open" goto open
goto help

:test
if "%2"=="" echo ???: run.bat test [a/b/c/d] [cpp/py] && pause && exit
powershell -ExecutionPolicy Bypass -Command ""
goto end

:timer
powershell -ExecutionPolicy Bypass -Command ""
goto end

:open
start https://atcoder.jp/contests/abc372/tasks
start https://atcoder.jp/contests/abc372/tasks/abc372_a
start https://atcoder.jp/contests/abc372/tasks/abc372_b
start https://atcoder.jp/contests/abc372/tasks/abc372_c
start https://atcoder.jp/contests/abc372/tasks/abc372_d
goto end

:help
echo ?? ABC372 ?????
echo test [a-d] [cpp/py] - ?????
echo timer              - ????
echo open               - ???URL??
pause

:end
