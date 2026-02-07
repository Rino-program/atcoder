# =============================================================================
# RunBatGenerator.ps1 - run.bat生成ライブラリ
# =============================================================================

function New-RunBat {
    param(
        [string]$FolderPath,
        [string]$ContestName,
        [bool]$IsNumeric = $false
    )
    
    $runBatContent = @'
@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo.
echo 🚀 AtCoder Contest Runner - 高速実行ツール
echo.

if "%1"=="" goto help
if /i "%1"=="a" goto test_a
if /i "%1"=="b" goto test_b
if /i "%1"=="c" goto test_c
if /i "%1"=="d" goto test_d
if /i "%1"=="build" goto build_cpp
if /i "%1"=="py" goto run_python
if /i "%1"=="python" goto run_python
if /i "%1"=="cpp" goto build_cpp
'@

    if ($IsNumeric) {
        $runBatContent += @'
if /i "%1"=="open" goto open_browser
if /i "%1"=="browser" goto open_browser
'@
    }

    $runBatContent += @'
goto help

:test_a
echo ⚡ A問題テスト実行中...
echo.
if exist "main.exe" (
    echo 📄 入力ファイル: in_a.txt
    type in_a.txt | main.exe
) else (
    echo ⚠️  main.exeが見つかりません。先にビルドしてください。
    echo    run.bat build でビルドできます
)
echo.
pause
goto end

:test_b
echo ⚡ B問題テスト実行中...
echo.
if exist "main.exe" (
    echo 📄 入力ファイル: in_b.txt
    type in_b.txt | main.exe
) else (
    echo ⚠️  main.exeが見つかりません。先にビルドしてください。
    echo    run.bat build でビルドできます
)
echo.
pause
goto end

:test_c
echo ⚡ C問題テスト実行中...
echo.
if exist "main.exe" (
    echo 📄 入力ファイル: in_c.txt
    type in_c.txt | main.exe
) else (
    echo ⚠️  main.exeが見つかりません。先にビルドしてください。
    echo    run.bat build でビルドできます
)
echo.
pause
goto end

:test_d
echo ⚡ D問題テスト実行中...
echo.
if exist "main.exe" (
    echo 📄 入力ファイル: in_d.txt
    type in_d.txt | main.exe
) else (
    echo ⚠️  main.exeが見つかりません。先にビルドしてください。
    echo    run.bat build でビルドできます
)
echo.
pause
goto end

:build_cpp
echo 🔨 C++ビルド中...
echo.
g++ -std=c++20 -O2 -Wall -Wextra main.cpp -o main.exe
if %errorlevel%==0 (
    echo ✅ ビルド成功！
) else (
    echo ❌ ビルドエラーが発生しました
)
echo.
pause
goto end

:run_python
echo 🐍 Python実行中...
echo.
if exist "main.py" (
    echo 📄 入力ファイル: in_a.txt
    type in_a.txt | python main.py
) else (
    echo ❌ main.pyが見つかりません
)
echo.
pause
goto end
'@

    if ($IsNumeric) {
        $contestNum = $ContestName
        $runBatContent += @"

:open_browser
echo 🌐 ブラウザで全問題を開いています...
echo.
start https://atcoder.jp/contests/abc$contestNum/tasks
timeout /t 1 >nul 2>&1
start https://atcoder.jp/contests/abc$contestNum/tasks/abc$($contestNum)_a
timeout /t 1 >nul 2>&1
start https://atcoder.jp/contests/abc$contestNum/tasks/abc$($contestNum)_b
timeout /t 1 >nul 2>&1
start https://atcoder.jp/contests/abc$contestNum/tasks/abc$($contestNum)_c
timeout /t 1 >nul 2>&1
start https://atcoder.jp/contests/abc$contestNum/tasks/abc$($contestNum)_d
echo ✅ 全問題URLを開きました
echo.
pause
goto end
"@
    }

    $runBatContent += @'

:help
echo 📝 使用可能コマンド:
echo.
echo   🧪 テスト実行:
echo     run.bat a        - A問題テスト実行
echo     run.bat b        - B問題テスト実行
echo     run.bat c        - C問題テスト実行
echo     run.bat d        - D問題テスト実行
echo.
echo   🔨 開発作業:
echo     run.bat build    - C++ビルド
echo     run.bat py       - Python実行
echo.
'@

    if ($IsNumeric) {
        $runBatContent += @'
echo   🌐 ブラウザ:
echo     run.bat open     - 全問題URLを開く
echo.
'@
    }

    $runBatContent += @'
echo 💡 使用例:
echo   run.bat a           # A問題をテスト
echo   run.bat build       # C++をビルド
echo   run.bat py          # Pythonを実行
echo.
pause

:end
'@

    try {
        $runBatPath = Join-Path $FolderPath "run.bat"
        $runBatContent | Out-File -FilePath $runBatPath -Encoding ASCII
        return @{
            "Success" = $true
            "Path" = $runBatPath
        }
    }
    catch {
        return @{
            "Success" = $false
            "Error" = $_.Exception.Message
        }
    }
}