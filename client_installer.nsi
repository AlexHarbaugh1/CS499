
; Hospital Management System Client Installer Script
; Created with NSIS

!include "MUI2.nsh"
!include "LogicLib.nsh"
!include "nsDialogs.nsh"
!include "FileFunc.nsh"

; General configuration
Name "Hospital Management System Client"
OutFile "HospitalManagementSystem_Client_Setup.exe"
InstallDir "$PROGRAMFILES\Hospital Management System Client"
InstallDirRegKey HKLM "Software\Hospital Management System Client" "Install_Dir"

; Request application privileges
RequestExecutionLevel admin

; Variables
Var ServerConfigPage
Var ServerHost
Var ServerHostText
Var ServerPort
Var ServerPortText
Var ServerUser
Var ServerUserText
Var ServerPassword
Var ServerPasswordText
Var HCPPage
Var HCPClientID
Var HCPClientIDText
Var HCPClientSecret
Var HCPClientSecretText

; Interface Settings
!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "${NSISDIR}\Contrib\Graphics\Header\win.bmp"
!define MUI_WELCOMEFINISHPAGE_BITMAP "${NSISDIR}\Contrib\Graphics\Wizard\win.bmp"

; Welcome page
!insertmacro MUI_PAGE_WELCOME

; Components page
!insertmacro MUI_PAGE_COMPONENTS

; Directory page
!insertmacro MUI_PAGE_DIRECTORY

; Custom Server configuration page
Page custom serverConfigPage serverConfigPageLeave

; Custom HCP configuration page
Page custom hcpConfigPage hcpConfigPageLeave

; Install files page
!insertmacro MUI_PAGE_INSTFILES

; Finish page
!define MUI_FINISHPAGE_RUN "$INSTDIR\HospitalManagementSystem_Client.exe"
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Language
!insertmacro MUI_LANGUAGE "English"

; Server Configuration Page
Function serverConfigPage
    !insertmacro MUI_HEADER_TEXT "Server Configuration" "Configure connection to the Hospital Management System Server"
    
    nsDialogs::Create 1018
    Pop $ServerConfigPage
    
    ${If} $ServerConfigPage == error
        Abort
    ${EndIf}
    
    ; Server Host
    ${NSD_CreateLabel} 10 20 120u 12u "Server Host:"
    Pop $0
    
    ${NSD_CreateText} 140 18 150u 12u "localhost"
    Pop $ServerHostText
    
    ; Server Port
    ${NSD_CreateLabel} 10 50 120u 12u "PostgreSQL Port:"
    Pop $0
    
    ${NSD_CreateText} 140 48 150u 12u "5432"
    Pop $ServerPortText
    
    ; Server Username
    ${NSD_CreateLabel} 10 80 120u 12u "Database Username:"
    Pop $0
    
    ${NSD_CreateText} 140 78 150u 12u "postgres"
    Pop $ServerUserText
    
    ; Server Password
    ${NSD_CreateLabel} 10 110 120u 12u "Database Password:"
    Pop $0
    
    ${NSD_CreatePassword} 140 108 150u 12u ""
    Pop $ServerPasswordText
    
    nsDialogs::Show
FunctionEnd

Function serverConfigPageLeave
    ${NSD_GetText} $ServerHostText $ServerHost
    ${NSD_GetText} $ServerPortText $ServerPort
    ${NSD_GetText} $ServerUserText $ServerUser
    ${NSD_GetText} $ServerPasswordText $ServerPassword
FunctionEnd

; HCP Configuration Page
Function hcpConfigPage
    !insertmacro MUI_HEADER_TEXT "HashiCorp Cloud Platform Configuration" "Configure HCP credentials for encryption keys"
    
    nsDialogs::Create 1018
    Pop $HCPPage
    
    ${If} $HCPPage == error
        Abort
    ${EndIf}
    
    ; HCP Client ID
    ${NSD_CreateLabel} 10 20 120u 12u "HCP Client ID:"
    Pop $0
    
    ${NSD_CreateText} 140 18 250u 12u ""
    Pop $HCPClientIDText
    
    ; HCP Client Secret
    ${NSD_CreateLabel} 10 50 120u 12u "HCP Client Secret:"
    Pop $0
    
    ${NSD_CreatePassword} 140 48 250u 12u ""
    Pop $HCPClientSecretText
    
    ; Instructions
    ${NSD_CreateLabel} 10 90 380u 40u "These credentials are used to securely retrieve encryption keys from HashiCorp Cloud Platform. If you don't have HCP credentials, contact your system administrator."
    Pop $0
    
    nsDialogs::Show
FunctionEnd

Function hcpConfigPageLeave
    ${NSD_GetText} $HCPClientIDText $HCPClientID
    ${NSD_GetText} $HCPClientSecretText $HCPClientSecret
FunctionEnd

; Main sections
Section "Hospital Management System Client (required)" SecMain
    SectionIn RO
    
    ; Set output path to the installation directory
    SetOutPath "$INSTDIR"
    
    ; Add all files from the PyInstaller distribution
    File /r "dist\HospitalManagementSystem_Client\*.*"
    
    ; Create data directory
    CreateDirectory "$INSTDIR\data"
    
    ; Create database configuration file
    FileOpen $0 "$INSTDIR\config.ini" w
    FileWrite $0 "[Database]$\r$\n"
    FileWrite $0 "host=$ServerHost$\r$\n"
    FileWrite $0 "port=$ServerPort$\r$\n"
    FileWrite $0 "user=$ServerUser$\r$\n"
    FileWrite $0 "password=$ServerPassword$\r$\n"
    FileWrite $0 "database=huntsvillehospital$\r$\n"
    FileWrite $0 "$\r$\n"
    FileWrite $0 "[Application]$\r$\n"
    FileWrite $0 "log_level=INFO$\r$\n"
    FileWrite $0 "data_directory=$INSTDIR\data$\r$\n"
    FileClose $0
    
    ; Create .env file with HCP credentials
    FileOpen $0 "$INSTDIR\.env" w
    FileWrite $0 "# Environment variables for HCP authentication$\r$\n"
    FileWrite $0 "HCP_CLIENT_ID=$HCPClientID$\r$\n"
    FileWrite $0 "HCP_CLIENT_SECRET=$HCPClientSecret$\r$\n"
    FileClose $0
    
    ; Create uninstaller
    WriteUninstaller "$INSTDIR\uninstall.exe"
    
    ; Create shortcuts
    CreateDirectory "$SMPROGRAMS\Hospital Management System Client"
    CreateShortcut "$SMPROGRAMS\Hospital Management System Client\Hospital Management System Client.lnk" "$INSTDIR\HospitalManagementSystem_Client.exe"
    CreateShortcut "$SMPROGRAMS\Hospital Management System Client\Uninstall.lnk" "$INSTDIR\uninstall.exe"
    CreateShortcut "$DESKTOP\Hospital Management System Client.lnk" "$INSTDIR\HospitalManagementSystem_Client.exe"
    
    ; Write registry keys
    WriteRegStr HKLM "Software\Hospital Management System Client" "Install_Dir" "$INSTDIR"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\HospitalManagementSystemClient" "DisplayName" "Hospital Management System Client"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\HospitalManagementSystemClient" "UninstallString" '"$INSTDIR\uninstall.exe"'
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\HospitalManagementSystemClient" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\HospitalManagementSystemClient" "NoRepair" 1
SectionEnd

Section "PostgreSQL Client" SecPostgresClient
    ; Download and install PostgreSQL client if not on Windows
    ${If} ${FileExists} "$WINDIR\system32\msvcr120.dll"
        DetailPrint "MSVC runtime already installed, skipping PostgreSQL client installation"
    ${Else}
        SetOutPath "$TEMP"
        NSISdl::download "https://sbp.enterprisedb.com/getfile.jsp?fileid=1258326" "postgresql-14.5-1-windows-x64-client.exe"
        ExecWait '"$TEMP\postgresql-14.5-1-windows-x64-client.exe" --mode unattended --unattendedmodeui minimal'
    ${EndIf}
SectionEnd

; Uninstaller section
Section "Uninstall"
    ; Remove registry keys
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\HospitalManagementSystemClient"
    DeleteRegKey HKLM "Software\Hospital Management System Client"

    ; Remove files and uninstaller
    RMDir /r "$INSTDIR"
    
    ; Remove shortcuts
    Delete "$SMPROGRAMS\Hospital Management System Client\*.*"
    RMDir "$SMPROGRAMS\Hospital Management System Client"
    Delete "$DESKTOP\Hospital Management System Client.lnk"
SectionEnd

; Section descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecMain} "Core Hospital Management System Client files."
    !insertmacro MUI_DESCRIPTION_TEXT ${SecPostgresClient} "PostgreSQL client for database connectivity."
!insertmacro MUI_FUNCTION_DESCRIPTION_END
