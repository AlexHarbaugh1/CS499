#!/usr/bin/env python
# package_server.py - Packaging Script for Hospital Management System Server

import os
import sys
import shutil
import subprocess
import platform
import tempfile
import zipfile
import datetime
from pathlib import Path

# Configuration
APP_NAME = "HospitalManagementSystem_Server"
APP_VERSION = "1.0.0"
MAIN_SCRIPT = "C:/Users/rstaf/OneDrive/Documents/GitHub/CS499/DatabaseHost/GUI499.py"  # Adjust this path to your main server script
ICON_PATH = os.path.join("assets", "icon.ico")

def setup_environment():
    """Set up the packaging environment"""
    print("Setting up packaging environment...")
    
    # Create necessary directories
    os.makedirs("build", exist_ok=True)
    os.makedirs("dist", exist_ok=True)
    os.makedirs("assets", exist_ok=True)
    
    # Create a simple icon if it doesn't exist
    if not os.path.exists(ICON_PATH):
        print(f"Creating a placeholder icon at {ICON_PATH}...")
        with open(ICON_PATH, "w") as f:
            f.write("This is a placeholder for an icon file. Replace with a real .ico file.")
    
    # Create __init__.py files in subdirectories if they don't exist
    for dir_path in ["DatabaseHost"]:
        init_file = os.path.join(dir_path, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, "w") as f:
                f.write("# Package initialization file\n")
    
    # Check and copy .env file
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"Found .env file at {env_file}")
    else:
        print("Warning: .env file not found in the current directory.")
        # Create a template .env file if it doesn't exist
        with open(env_file, "w") as f:
            f.write("""# Environment variables for HCP authentication
HCP_CLIENT_ID=your_client_id_here
HCP_CLIENT_SECRET=your_client_secret_here
""")
        print(f"Created template {env_file} file. Please fill in your actual credentials.")
    
    print("Environment setup completed")

def install_dependencies():
    """Install required Python dependencies"""
    print("Installing Python dependencies...")
    
    # Create requirements file if it doesn't exist
    if not os.path.exists("requirements.txt"):
        with open("requirements.txt", "w") as f:
            f.write("""
# Core dependencies
pyqt5>=5.15.0
psycopg2-binary>=2.8.6
pandas>=1.3.0
pyinstaller>=4.5.1
python-dotenv>=0.19.0

# Additional utilities
pytz>=2021.1
requests>=2.26.0
configparser>=5.2.0
""")
    
    # Install dependencies
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    
    print("Dependencies installed successfully")

def copy_config_files():
    """Copy configuration files to the DatabaseHost directory"""
    print("Copying configuration files...")
    
    # Make sure the config files exist
    if not os.path.exists("config_handler.py"):
        with open("config_handler.py", "w") as f:
            f.write("""# Configuration handler module placeholder
# Replace this with the actual config_handler.py content
""")
    
    if not os.path.exists("dbconfig.py"):
        with open("dbconfig.py", "w") as f:
            f.write("""# Database configuration module placeholder
# Replace this with the actual dbconfig.py content
""")
    
    # Copy files to the DatabaseHost directory
    for file in ["config_handler.py", "dbconfig.py", "db_migration.py"]:
        if os.path.exists(file):
            shutil.copy(file, os.path.join("DatabaseHost", file))
    
    # Copy .env file to DatabaseHost directory
    env_file = ".env"
    if os.path.exists(env_file):
        shutil.copy(env_file, os.path.join("DatabaseHost", env_file))
        print(f"Copied {env_file} to DatabaseHost directory")
    
    print("Configuration files copied successfully")

def build_executable():
    """Build the executable using PyInstaller"""
    print("Building executable with PyInstaller...")
    
    # Create temporary spec file
    spec_content = f"""
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{MAIN_SCRIPT}'],
    pathex=[],
    binaries=[],
    datas=[
        ('DatabaseHost/*.ui', '.'),
        ('DatabaseHost/*.py', '.'),
        ('assets/*', 'assets/'),
        ('DatabaseHost/config_handler.py', '.'),
        ('DatabaseHost/dbconfig.py', '.'),
        ('DatabaseHost/db_migration.py', '.'),
        ('.env', '.'),  # Include .env file in the root directory
        ('DatabaseHost/.env', '.'),  # Also include if it exists in DatabaseHost
    ],
    hiddenimports=[
        'PyQt5', 
        'PyQt5.QtWidgets', 
        'PyQt5.QtCore', 
        'PyQt5.QtGui', 
        'psycopg2', 
        'pandas', 
        'dotenv', 
        'python-dotenv'
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='{APP_NAME}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Set to True for server to show console output
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='{ICON_PATH}' if os.path.exists('{ICON_PATH}') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='{APP_NAME}',
)
"""
    
    with open(f"{APP_NAME}.spec", "w") as f:
        f.write(spec_content)
    
    # Run PyInstaller
    subprocess.run([sys.executable, "-m", "PyInstaller", f"{APP_NAME}.spec", "--noconfirm"], check=True)
    
    print(f"Executable built successfully: dist/{APP_NAME}/{APP_NAME}.exe")
    return True

def create_installer():
    """Create the installer using NSIS"""
    print("Creating installer with NSIS...")
    
    # Define the NSIS script path
    nsis_script = "server_installer.nsi"
    
    # Create NSIS script
    with open(nsis_script, "w") as f:
        f.write("""
; Hospital Management System Server Installer Script
; Created with NSIS

!include "MUI2.nsh"
!include "LogicLib.nsh"
!include "nsDialogs.nsh"
!include "FileFunc.nsh"

; General configuration
Name "Hospital Management System Server"
OutFile "HospitalManagementSystem_Server_Setup.exe"
InstallDir "$PROGRAMFILES\\Hospital Management System Server"
InstallDirRegKey HKLM "Software\\Hospital Management System Server" "Install_Dir"

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
!define MUI_ICON "${NSISDIR}\\Contrib\\Graphics\\Icons\\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\\Contrib\\Graphics\\Icons\\modern-uninstall.ico"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "${NSISDIR}\\Contrib\\Graphics\\Header\\win.bmp"
!define MUI_WELCOMEFINISHPAGE_BITMAP "${NSISDIR}\\Contrib\\Graphics\\Wizard\\win.bmp"

; Welcome page
!insertmacro MUI_PAGE_WELCOME

; License page
;!insertmacro MUI_PAGE_LICENSE "license.txt"  ; Include your license file

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
!define MUI_FINISHPAGE_RUN "$INSTDIR\\HospitalManagementSystem_Server.exe"
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
    
    ${NSD_CreateText} 140 18 150u 12u "C:\\Program Files\\PostgreSQL\\14"
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
    File /r "dist\\HospitalManagementSystem_Server\\*.*"
    
    ; Create database configuration file
    FileOpen $0 "$INSTDIR\\config.ini" w
    FileWrite $0 "[Database]$\\r$\\n"
    FileWrite $0 "host=localhost$\\r$\\n"
    FileWrite $0 "port=$PostgreSQLPort$\\r$\\n"
    FileWrite $0 "user=$PostgreSQLUser$\\r$\\n"
    FileWrite $0 "password=$PostgreSQLPassword$\\r$\\n"
    FileWrite $0 "database=huntsvillehospital$\\r$\\n"
    FileWrite $0 "$\\r$\\n"
    FileWrite $0 "[Application]$\\r$\\n"
    FileWrite $0 "log_level=INFO$\\r$\\n"
    FileWrite $0 "data_directory=$INSTDIR\\data$\\r$\\n"
    FileClose $0
    
    ; Create .env file with HCP credentials
    FileOpen $0 "$INSTDIR\\.env" w
    FileWrite $0 "# Environment variables for HCP authentication$\\r$\\n"
    FileWrite $0 "HCP_CLIENT_ID=$HCPClientID$\\r$\\n"
    FileWrite $0 "HCP_CLIENT_SECRET=$HCPClientSecret$\\r$\\n"
    FileClose $0
    
    ; Create uninstaller
    WriteUninstaller "$INSTDIR\\uninstall.exe"
    
    ; Create shortcuts
    CreateDirectory "$SMPROGRAMS\\Hospital Management System Server"
    CreateShortcut "$SMPROGRAMS\\Hospital Management System Server\\Hospital Management System Server.lnk" "$INSTDIR\\HospitalManagementSystem_Server.exe"
    CreateShortcut "$SMPROGRAMS\\Hospital Management System Server\\Uninstall.lnk" "$INSTDIR\\uninstall.exe"
    CreateShortcut "$DESKTOP\\Hospital Management System Server.lnk" "$INSTDIR\\HospitalManagementSystem_Server.exe"
    
    ; Write registry keys
    WriteRegStr HKLM "Software\\Hospital Management System Server" "Install_Dir" "$INSTDIR"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\HospitalManagementSystemServer" "DisplayName" "Hospital Management System Server"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\HospitalManagementSystemServer" "UninstallString" '"$INSTDIR\\uninstall.exe"'
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\HospitalManagementSystemServer" "NoModify" 1
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\HospitalManagementSystemServer" "NoRepair" 1
SectionEnd

Section "PostgreSQL Server" SecPostgres
    ; Download and install PostgreSQL
    SetOutPath "$TEMP"
    NSISdl::download "https://sbp.enterprisedb.com/getfile.jsp?fileid=1258323" "postgresql-14.5-1-windows-x64.exe"
    ExecWait '"$TEMP\\postgresql-14.5-1-windows-x64.exe" --mode unattended --unattendedmodeui minimal --superpassword "$PostgreSQLPassword" --serverport $PostgreSQLPort'
    
    ; Initialize the database
    ${If} ${FileExists} "$PostgreSQLDir\\bin\\psql.exe"
        ExecWait '"$PostgreSQLDir\\bin\\psql.exe" -U $PostgreSQLUser -p $PostgreSQLPort -c "CREATE DATABASE huntsvillehospital;"'
    ${EndIf}
SectionEnd

; Uninstaller section
Section "Uninstall"
    ; Remove registry keys
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\HospitalManagementSystemServer"
    DeleteRegKey HKLM "Software\\Hospital Management System Server"

    ; Remove files and uninstaller
    RMDir /r "$INSTDIR"
    
    ; Remove shortcuts
    Delete "$SMPROGRAMS\\Hospital Management System Server\\*.*"
    RMDir "$SMPROGRAMS\\Hospital Management System Server"
    Delete "$DESKTOP\\Hospital Management System Server.lnk"
SectionEnd

; Section descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecMain} "Core Hospital Management System Server files."
    !insertmacro MUI_DESCRIPTION_TEXT ${SecPostgres} "PostgreSQL database server."
!insertmacro MUI_FUNCTION_DESCRIPTION_END
""")
    
    # Find makensis executable
    nsis_path = shutil.which("makensis")
    if not nsis_path and platform.system() == "Windows":
        # Check common installation directories on Windows
        possible_paths = [
            r"C:\Program Files (x86)\NSIS\makensis.exe",
            r"C:\Program Files\NSIS\makensis.exe"
        ]
        for path in possible_paths:
            if os.path.exists(path):
                nsis_path = path
                break
    
    if not nsis_path:
        print("Error: makensis executable not found. Install NSIS and try again.")
        return False
    
    # Run NSIS
    subprocess.run([nsis_path, nsis_script], check=True)
    
    print("Installer created successfully: HospitalManagementSystem_Server_Setup.exe")
    return True

def create_distribution_package():
    """Create a complete distribution package"""
    print("Creating distribution package...")
    
    # Create a zip file containing the installer and documentation
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    zip_filename = f"dist/{APP_NAME}-{APP_VERSION}-{timestamp}.zip"
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add the installer
        if os.path.exists("HospitalManagementSystem_Server_Setup.exe"):
            zip_file.write("HospitalManagementSystem_Server_Setup.exe")
        
        # Add the README
        if os.path.exists("README.md"):
            zip_file.write("README.md")
    
    print(f"Distribution package created successfully: {zip_filename}")

def main():
    """Main packaging process"""
    print(f"Hospital Management System Server Packaging Script v{APP_VERSION}")
    print("=" * 50)
    
    try:
        # Setup environment
        setup_environment()
        
        # Install dependencies
        install_dependencies()
        
        # Copy config files
        copy_config_files()
        
        # Build executable
        build_executable()
        
        # Create installer
        if not create_installer():
            print("Error creating installer")
            return 1
        
        # Create distribution package
        create_distribution_package()
        
        print("\nPackaging completed successfully!")
        print(f"Installer: HospitalManagementSystem_Server_Setup.exe")
        
        return 0
    
    except Exception as e:
        print(f"\nERROR: Packaging failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())