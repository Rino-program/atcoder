function New-RunBatGenerator([string]$FolderPath) {
    try {
        $batPath = Join-Path $FolderPath "run.bat"
        $content = @()
        $content += "@echo off"
        $content += "if exist main.exe ( main.exe ) else ( python main.py )"
        $content -join "`r`n" | Out-File -FilePath $batPath -Encoding ASCII
        return @{ Success = $true }
    } catch {
        return @{ Success = $false; Error = $_ }
    }
}
