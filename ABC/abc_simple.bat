@echo off
chcp 65001 >nul

if "%1"=="" goto help

powershell.exe -ExecutionPolicy Bypass -File "%~dp0abc.ps1" %*
goto end

:help
echo 🚀 AtCoder ABC ツール
echo.
echo new [回数]         - 新しいフォルダ作成
echo test [問題] [言語] - テスト実行 (a-d, cpp/py)
echo timer             - タイマー開始  
echo open [回数]        - 全問題URL開く
echo help              - ヘルプ
echo.
echo 例: abc new 372
echo 例: abc test a py
pause

:end