@echo off
:: AtCoder ABC フォルダ作成バッチファイル v2.0
:: 使用法: abc.bat 372 [options]

title AtCoder ABC フォルダ作成ツール

if "%~1"=="" (
    echo.
    echo 🚀 AtCoder ABC フォルダ作成ツール v2.0
    echo =====================================
    echo.
    echo 使用法: abc.bat [contest_number] [options]
    echo.
    echo 例:
    echo   abc.bat 372                              # 基本作成
    echo   abc.bat 372 -Force                      # 強制上書き
    echo   abc.bat 372 -Open                       # フォルダを開く
    echo   abc.bat 372 -VSCode                     # VS Codeで開く
    echo   abc.bat 372 -CreateTestFiles            # テストファイル作成
    echo   abc.bat 372 -Language cpp               # C++のみ
    echo   abc.bat 372 -Date "2025-01-15"          # 開催日指定
    echo   abc.bat 372 -Force -VSCode -CreateTestFiles # 全部盛り
    echo.
    echo オプション:
    echo   -Force         既存フォルダを上書き
    echo   -Open          エクスプローラーで開く
    echo   -VSCode        VS Codeで開く
    echo   -CreateTestFiles テストファイル作成
    echo   -Language      言語指定 (cpp/python/both)
    echo   -Date          開催日指定 (YYYY-MM-DD)
    echo.
    pause
    exit /b 1
)

echo 🚀 AtCoder ABC%1 フォルダを作成中...
echo.

:: PowerShellスクリプトを実行
powershell.exe -ExecutionPolicy Bypass -File "%~dp0create_abc_v2.ps1" %*

echo.
echo ✅ 処理完了！
pause