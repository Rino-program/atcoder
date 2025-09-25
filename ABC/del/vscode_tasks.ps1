# PowerShell関数でVS Codeワークスペース用のタスクを生成
function New-VSCodeTasks {
    param([int]$ContestNumber, [string]$FolderPath)
    
    $tasksContent = @{
        version = "2.0.0"
        tasks = @(
            @{
                label = "Build C++"
                type = "shell"
                command = "g++"
                args = @(
                    "-std=c++20",
                    "-O2",
                    "-Wall",
                    "-Wextra",
                    "-I", "C:\atcoder-library",
                    "main.cpp",
                    "-o", "main.exe"
                )
                group = "build"
                presentation = @{
                    echo = $true
                    reveal = "always"
                    focus = $false
                    panel = "shared"
                }
                problemMatcher = @('$gcc')
            },
            @{
                label = "Run C++"
                type = "shell"
                command = "./main.exe"
                args = @()
                group = "test"
                dependsOn = "Build C++"
                presentation = @{
                    echo = $true
                    reveal = "always"
                    focus = $false
                    panel = "shared"
                }
            },
            @{
                label = "Run Python"
                type = "shell"
                command = "python"
                args = @("main.py")
                group = "test"
                presentation = @{
                    echo = $true
                    reveal = "always"
                    focus = $false
                    panel = "shared"
                }
            },
            @{
                label = "Test C++ with input"
                type = "shell"
                command = "./main.exe"
                args = @()
                options = @{
                    shell = @{
                        executable = "cmd.exe"
                        args = @("/c", "./main.exe < input_a.txt")
                    }
                }
                dependsOn = "Build C++"
                group = "test"
            }
        )
    }
    
    $vscodeDir = Join-Path $FolderPath ".vscode"
    if (!(Test-Path $vscodeDir)) {
        New-Item -Path $vscodeDir -ItemType Directory -Force | Out-Null
    }
    
    $tasksFile = Join-Path $vscodeDir "tasks.json"
    $tasksContent | ConvertTo-Json -Depth 10 | Out-File -FilePath $tasksFile -Encoding UTF8
}