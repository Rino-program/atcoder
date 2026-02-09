function New-VSCodeConfig([string]$FolderPath, [string]$ContestName, [bool]$IsNumeric) {
    try {
        $vscodeDir = Join-Path $FolderPath ".vscode"
        if (-not (Test-Path $vscodeDir)) { New-Item -ItemType Directory -Path $vscodeDir | Out-Null }

        # 既存テンプレートに .vscode があればコピー
        $templateVscode = Join-Path (Join-Path (Split-Path -Parent $PSScriptRoot) "templates") ".vscode"
        if (Test-Path $templateVscode) {
            Copy-Item -Path (Join-Path $templateVscode "*") -Destination $vscodeDir -Recurse -Force -ErrorAction SilentlyContinue
        } else {
            # 最低限の launch.json を置く
            $launch = @{
                version = "0.2.0"
                configurations = @()
            } | ConvertTo-Json -Depth 10
            $launchPath = Join-Path $vscodeDir "launch.json"
            $launch | Out-File -FilePath $launchPath -Encoding UTF8
        }

        return @{ Success = $true }
    } catch {
        return @{ Success = $false; Error = $_ }
    }
}
