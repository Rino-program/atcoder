# =============================================================================
# VSCodeConfig.ps1 - VS Code設定生成ライブラリ
# =============================================================================

# VS Code設定フォルダを作成
function New-VSCodeConfigFolder {
    param([string]$FolderPath)
    
    $vscodeDir = Join-Path $FolderPath ".vscode"
    if (-not (Test-Path $vscodeDir)) {
        New-Item -ItemType Directory -Path $vscodeDir | Out-Null
    }
    return $vscodeDir
}

# tasks.json生成
function New-TasksJson {
    param([string]$VSCodeDir)
    
    $tasksJson = @{
        "version" = "2.0.0"
        "tasks" = @(
            @{
                "label" = "Build C++ (Release)"
                "type" = "shell"
                "command" = "g++"
                "args" = @(
                    "-std=c++20",
                    "-O2",
                    "-Wall",
                    "-Wextra",
                    "main.cpp",
                    "-o",
                    "main.exe"
                )
                "group" = @{
                    "kind" = "build"
                    "isDefault" = $true
                }
                "problemMatcher" = @("$gcc")
                "presentation" = @{
                    "echo" = $true
                    "reveal" = "always"
                    "focus" = $false
                    "panel" = "shared"
                }
            },
            @{
                "label" = "Build C++ (Debug)"
                "type" = "shell"
                "command" = "g++"
                "args" = @(
                    "-std=c++20",
                    "-g",
                    "-DDEBUG",
                    "-Wall",
                    "-Wextra",
                    "main.cpp",
                    "-o",
                    "main_debug.exe"
                )
                "group" = "build"
                "problemMatcher" = @("$gcc")
                "presentation" = @{
                    "echo" = $true
                    "reveal" = "always"
                    "focus" = $false
                    "panel" = "shared"
                }
            },
            @{
                "label" = "Run C++ (with input)"
                "type" = "shell"
                "command" = "Get-Content in_a.txt | ./main.exe"
                "dependsOn" = "Build C++ (Release)"
                "group" = @{
                    "kind" = "test"
                    "isDefault" = $true
                }
                "presentation" = @{
                    "echo" = $true
                    "reveal" = "always"
                    "focus" = $true
                    "panel" = "shared"
                }
            },
            @{
                "label" = "Run Python (with input)"
                "type" = "shell"
                "command" = "Get-Content in_a.txt | python main.py"
                "group" = "test"
                "presentation" = @{
                    "echo" = $true
                    "reveal" = "always"
                    "focus" = $true
                    "panel" = "shared"
                }
            }
        )
    }
    
    $tasksPath = Join-Path $VSCodeDir "tasks.json"
    $tasksJson | ConvertTo-Json -Depth 10 | Out-File -FilePath $tasksPath -Encoding UTF8
    return $tasksPath
}

# launch.json生成
function New-LaunchJson {
    param([string]$VSCodeDir)
    
    $launchJson = @{
        "version" = "0.2.0"
        "configurations" = @(
            @{
                "name" = "C++ Debug"
                "type" = "cppdbg"
                "request" = "launch"
                "program" = "${workspaceFolder}/main_debug.exe"
                "args" = @()
                "stopAtEntry" = $false
                "cwd" = "${workspaceFolder}"
                "environment" = @()
                "externalConsole" = $true
                "MIMode" = "gdb"
                "setupCommands" = @(
                    @{
                        "description" = "Enable pretty-printing for gdb"
                        "text" = "-enable-pretty-printing"
                        "ignoreFailures" = $true
                    }
                )
                "preLaunchTask" = "Build C++ (Debug)"
            }
        )
    }
    
    $launchPath = Join-Path $VSCodeDir "launch.json"
    $launchJson | ConvertTo-Json -Depth 10 | Out-File -FilePath $launchPath -Encoding UTF8
    return $launchPath
}

# VS Code設定一括生成
function New-VSCodeConfig {
    param(
        [string]$FolderPath,
        [string]$ContestName = "",
        [bool]$IsNumeric = $false
    )
    
    try {
        $vscodeDir = New-VSCodeConfigFolder -FolderPath $FolderPath
        $tasksPath = New-TasksJson -VSCodeDir $vscodeDir
        $launchPath = New-LaunchJson -VSCodeDir $vscodeDir
        
        return @{
            "Success" = $true
            "VSCodeDir" = $vscodeDir
            "TasksPath" = $tasksPath
            "LaunchPath" = $launchPath
        }
    }
    catch {
        return @{
            "Success" = $false
            "Error" = $_.Exception.Message
        }
    }
}