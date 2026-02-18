$type = $args[0]
$currentDir = Get-Location
$icon = "$currentDir\icons\$type.ico"
if(!(Test-Path -Path $icon)){
    Write-Host "$icon is not existed"
    exit 1
}
if(!(Test-Path -Path $currentDir\.venv)){
    uv sync
}
uv run pyinstaller --onefile --noconsole --icon $icon --add-data="$icon;." dummy-app.py
Move-Item ./dist/dummy-app.exe ../$type-notifier.exe -Force