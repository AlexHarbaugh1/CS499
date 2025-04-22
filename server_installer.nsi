
; Hospital Management System Server Installer Script
; Created with NSIS

!include "MUI2.nsh"
!include "LogicLib.nsh"
!include "nsDialogs.nsh"
!include "FileFunc.nsh"

; General configuration
Name "Hospital Management System Server"
OutFile "HospitalManagementSystem_Server_Setup.exe"
InstallDir "$PROGRAMFILES\Hospital Management System Server"
InstallDirRegKey HKLM "Software\Hospital Management System Server" "Install_Dir"

; Request application privileges
RequestExecutionLevel admin

; Variables
Var PostgreSQLPage
Var PostgreSQLDir
Var PostgreSQLDirText
Var PostgreSQLUser
Var PostgreSQLUserText
Var PostgreSQLPassword
Var PostgreSQLPasswordText
Var PostgreSQLPort
Var PostgreSQLPortText
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

; Custom PostgreSQL configuration page
Page custom pgSQLConfigPage pgSQLConfigPageLeave

; Custom HCP configuration page
Page custom hcpConfigPage hcpConfigPageLeave

; Install files page
!insertmacro MUI_PAGE_INSTFILES

; Finish page
!define MUI_FINISHPAGE_RUN "$INSTDIR\HospitalManagementSystem_Server.exe"
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Language
!insertmacro MUI_LANGUAGE "English"

; PostgreSQL Configuration Page
Function pgSQLConfigPage
    !insertmacro MUI_HEADER_TEXT "Database Configuration" "Configure PostgreSQL settings"
    
    nsDialogs::Create 1018
    Pop $PostgreSQLPage
    
    ${If} $PostgreSQLPage == error
        Abort
    ${EndIf}
    
    ; PostgreSQL Installation Directory
    ${NSD_CreateLabel} 10 20 120u 12u "PostgreSQL Directory:"
    Pop $0
    
    ${NSD_CreateText} 140 18 150u 12u "C:\Program Files\PostgreSQL\14"
    Pop $PostgreSQLDirText
    
    ; PostgreSQL Port
    ${NSD_CreateLabel} 10 50 120u 12u "PostgreSQL Port:"
    Pop $0
    
    ${NSD_CreateText} 140 48 150u 12u "5432"
    Pop $PostgreSQLPortText
    
    ; PostgreSQL Admin Username
    ${NSD_CreateLabel} 10 80 120u 12u "Admin Username:"
    Pop $0
    
    ${NSD_CreateText} 140 78 150u 12u "postgres"
    Pop $PostgreSQLUserText
    
    ; PostgreSQL Admin Password
    ${NSD_CreateLabel} 10 110 120u 12u "Admin Password:"
    Pop $0
    
    ${NSD_CreatePassword} 140 108 150u 12u ""
    Pop $PostgreSQLPasswordText
    
    nsDialogs::Show
FunctionEnd

Function pgSQLConfigPageLeave
    ${NSD_GetText} $PostgreSQLDirText $PostgreSQLDir
    ${NSD_GetText} $PostgreSQLPortText $PostgreSQLPort
    ${NSD_GetText} $PostgreSQLUserText $PostgreSQLUser
    ${NSD_GetText} $PostgreSQLPasswordText $PostgreSQLPassword
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
Section "Hospital Management System Server (required)" SecMain
    SectionIn RO
    
    ; Set output path to the installation directory
    SetOutPath "$INSTDIR"
    
    ; Add all files from the PyInstaller distribution
    File /r "dist\HospitalManagementSystem_Server\*.*"
    
    ; Create data directory
    CreateDirectory "$INSTDIR\data"
    
    ; Create database configuration file
    FileOpen $0 "$INSTDIR\config.ini" w
    FileWrite $0 "[Database]$\r$\n"
    FileWrite $0 "host=localhost$\r$\n"
    FileWrite $0 "port=$PostgreSQLPort$\r$\n"
    FileWrite $0 "user=$PostgreSQLUser$\r$\n"
    FileWrite $0 "password=$PostgreSQLPassword$\r$\n"
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
    CreateDirectory "$SMPROGRAMS\Hospital Management System Server"
    CreateShortcut "$SMPROGRAMS\Hospital Management System Server\Hospital Management System Server.lnk" "$INSTDIR\HospitalManagementSystem_Server.exe"
    CreateShortcut "$SMPROGRAMS\Hospital Management System Server\Uninstall.lnk" "$INSTDIR\uninstall.exe"
    CreateShortcut "$DESKTOP\Hospital Management System Server.lnk" "$INSTDIR\HospitalManagementSystem_Server.exe"
    
    ; Write registry keys
    WriteRegStr HKLM "Software\Hospital Management System Server" "Install_Dir" "$INSTDIR"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\HospitalManagementSystemServer" "DisplayName" "Hospital Management System Server"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\HospitalManagementSystemServer" "UninstallString" '"$INSTDIR\uninstall.exe"'
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\HospitalManagementSystemServer" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\HospitalManagementSystemServer" "NoRepair" 1
SectionEnd

Section "PostgreSQL Server" SecPostgres
    ; Download and install PostgreSQL
    SetOutPath "$TEMP"
    NSISdl::download "https://sbp.enterprisedb.com/getfile.jsp?fileid=1258323" "postgresql-14.5-1-windows-x64.exe"
    ExecWait '"$TEMP\postgresql-14.5-1-windows-x64.exe" --mode unattended --unattendedmodeui minimal --superpassword "$PostgreSQLPassword" --serverport $PostgreSQLPort'
    
    ; Initialize the database
    ${If} ${FileExists} "$PostgreSQLDir\bin\psql.exe"
        ExecWait '"$PostgreSQLDir\bin\psql.exe" -U $PostgreSQLUser -p $PostgreSQLPort -c "CREATE DATABASE huntsvillehospital;"'
    ${EndIf}
SectionEnd

; Uninstaller section
Section "Uninstall"
    ; Remove registry keys
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\HospitalManagementSystemServer"
    DeleteRegKey HKLM "Software\Hospital Management System Server"

    ; Remove files and uninstaller
    RMDir /r "$INSTDIR"
    
    ; Remove shortcuts
    Delete "$SMPROGRAMS\Hospital Management System Server\*.*"
    RMDir "$SMPROGRAMS\Hospital Management System Server"
    Delete "$DESKTOP\Hospital Management System Server.lnk"
SectionEnd

; Section descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecMain} "Core Hospital Management System Server files."
    !insertmacro MUI_DESCRIPTION_TEXT ${SecPostgres} "PostgreSQL database server."
!insertmacro MUI_FUNCTION_DESCRIPTION_END
