; NSIS installer script for Kezan Protocol
!include "MUI2.nsh"

Name "Kezan Protocol"
OutFile "KezanProtocolSetup.exe"
InstallDir "$PROGRAMFILES\Kezan Protocol"

Page Directory
Page InstFiles

Section "Install"
    SetOutPath "$INSTDIR"
    File "..\dist\KezanProtocol.exe"
    CreateDirectory "$APPDATA\KezanProtocol"
    CreateShortCut "$DESKTOP\Kezan Protocol.lnk" "$INSTDIR\KezanProtocol.exe"
    CreateShortCut "$SMPROGRAMS\Kezan Protocol\Kezan Protocol.lnk" "$INSTDIR\KezanProtocol.exe"
    WriteUninstaller "$INSTDIR\uninstall.exe"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Kezan Protocol" "DisplayName" "Kezan Protocol"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Kezan Protocol" "UninstallString" "$INSTDIR\uninstall.exe"
SectionEnd

Section "Uninstall"
    Delete "$DESKTOP\Kezan Protocol.lnk"
    RMDir /r "$SMPROGRAMS\Kezan Protocol"
    RMDir /r "$INSTDIR"
    DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Kezan Protocol"
SectionEnd
