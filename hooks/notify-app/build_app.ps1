$type = $args[0]
$icon = "./icons/$type.ico"
if(Test-Path -Path $icon){
    Write-Host "$icon is not existed"
    exit 1
}
uv run pyinstaller --onefile --noconsole --icon $icon --add-data="$icon;." dummy-app.py
Copy-Item ./dist/dummy-app.exe ../$type-notifier.exe