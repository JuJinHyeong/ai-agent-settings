$currentDir = Get-Location
$type = $args[0]
$lnkName = $args[1]
$appId = $args[2]
$snoreToastPath = "$currentDir\node_modules\node-notifier\vendor\snoreToast\snoretoast-x64.exe"
$executablePath = "$currentDir\$type-notifier.exe"

Write-Host "Dummy app 생성 시작..."
Push-Location $currentDir\notify-app
& $currentDir\notify-app\build-app.ps1 $type
Pop-Location
Write-Host "Dummy app 생성 종료. $type-notifier.exe 를 확인해주세요."

if (Test-Path $snoreToastPath) {
    Write-Host "snoreToast.exe 경로 확인: $snoreToastPath"
} else {
    Write-Host "snoreToast.exe를 찾을 수 없습니다. 경로를 확인하세요: $snoreToastPath"
    exit
}

if (Test-Path $executablePath) {
    Write-Host "알림 실행 파일 경로 확인: $executablePath"
} else {
    Write-Host "알림 실행 파일을 찾을 수 없습니다. 경로를 확인하세요: $executablePath"
    exit
}

# 기존 설치 확인 및 제거
Write-Host "기존 설치 확인 중..."

# 레지스트리에서 기존 알림 설정 제거
$regPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Notifications\Settings"
Get-ChildItem $regPath -ErrorAction SilentlyContinue | 
    Where-Object { $_.PSChildName -like "*$appId*" -or $_.PSChildName -like "*$lnkName*" } | 
    ForEach-Object {
        Write-Host "레지스트리 항목 제거: $($_.PSChildName)"
        Remove-Item $_.PSPath -Recurse -Force -ErrorAction SilentlyContinue
    }

# 기존 바로가기 제거
$shortcutPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\$lnkName.lnk"
if (Test-Path $shortcutPath) {
    Write-Host "기존 바로가기 제거: $shortcutPath"
    Remove-Item $shortcutPath -Force
}

Write-Host "새로 설치 시작..."

# 바로가기 설치
& $snoreToastPath -install "$lnkName" "$executablePath" $appId

Write-Host "설치 및 아이콘 변경 완료: $shortcutPath"