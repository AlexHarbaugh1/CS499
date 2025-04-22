#!/usr/bin/env python
# package_client.py - Packaging Script for Hospital Management System Client

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
APP_NAME = "HospitalManagementSystem_Client"
APP_VERSION = "1.0.0"
MAIN_SCRIPT = "Client/GUI499.py"  # Changed to relative path with proper format
ICON_PATH = os.path.join("assets", "icon.ico")

def setup_environment():
    """Set up the packaging environment"""
    global MAIN_SCRIPT  # Add this line to access the global variable
    print("Setting up packaging environment...")
    
    # Create necessary directories
    os.makedirs("build", exist_ok=True)
    os.makedirs("dist", exist_ok=True)
    os.makedirs("assets", exist_ok=True)
    
    # Create a simple icon if it doesn't exist
    if not os.path.exists(ICON_PATH):
        print(f"Creating a placeholder icon at {ICON_PATH}...")
        os.makedirs(os.path.dirname(ICON_PATH), exist_ok=True)
        with open(ICON_PATH, "wb") as f:
            # Write a small transparent .ico file (1x1 pixel)
            f.write(b'\x00\x00\x01\x00\x01\x00\x01\x01\x00\x00\x01\x00\x18\x00\x0A\x00\x00\x00\x16\x00\x00\x00\x28\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x18\x00\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    
    # Check if main script exists
    if not os.path.exists(MAIN_SCRIPT):
        print(f"Warning: Main script {MAIN_SCRIPT} not found in current directory.")
        # Check in Client directory
        client_script = os.path.join("Client", os.path.basename(MAIN_SCRIPT))
        if os.path.exists(client_script):
            print(f"Found main script at {client_script}")
            MAIN_SCRIPT = client_script
        else:
            print(f"Error: Main script not found in Client directory either.")
            print("Available files in current directory:", os.listdir('.'))
            if os.path.exists('Client'):
                print("Files in Client directory:", os.listdir('Client'))
    
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

# The rest of the file remains unchanged
# (You would copy the remaining functions from the original file)

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
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Warning: Failed to install some dependencies: {e}")
        print("Continuing anyway...")

def copy_config_files():
    """Copy configuration files to the Client directory"""
    print("Copying configuration files...")
    
    # Create Client directory if it doesn't exist
    os.makedirs("Client", exist_ok=True)
    
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
    
    # Copy files to the Client directory
    for file in ["config_handler.py", "dbconfig.py"]:
        if os.path.exists(file):
            shutil.copy(file, os.path.join("Client", file))
    
    # Copy .env file to Client directory
    env_file = ".env"
    if os.path.exists(env_file):
        shutil.copy(env_file, os.path.join("Client", env_file))
        print(f"Copied {env_file} to Client directory")
    
    print("Configuration files copied successfully")
    
    # Collect all UI files
    ui_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.ui'):
                ui_files.append(os.path.join(root, file))
    
    # Copy UI files to Client directory
    for ui_file in ui_files:
        dest_file = os.path.join("Client", os.path.basename(ui_file))
        if not os.path.exists(dest_file):
            shutil.copy(ui_file, dest_file)
            print(f"Copied UI file: {ui_file} to {dest_file}")

def build_executable():
    """Build the executable using PyInstaller"""
    global MAIN_SCRIPT  # Add this line to access the global variable
    print("Building executable with PyInstaller...")
    
    # Check if PyInstaller is installed
    try:
        subprocess.run([sys.executable, "-m", "PyInstaller", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("PyInstaller not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    # Find all UI files in the Client directory
    ui_files = []
    if os.path.exists('Client'):
        for file in os.listdir('Client'):
            if file.endswith('.ui'):
                ui_files.append(os.path.join('Client', file))
    print(f"Found {len(ui_files)} UI files")
    
    # Create data files list for PyInstaller
    data_files = []
    for ui_file in ui_files:
        data_files.append((ui_file, '.'))
    
    # Add Python files in Client directory
    python_files = []
    if os.path.exists('Client'):
        for file in os.listdir('Client'):
            if file.endswith('.py'):
                python_files.append(os.path.join('Client', file))
    print(f"Found {len(python_files)} Python files in Client directory")
    
    for py_file in python_files:
        data_files.append((py_file, '.'))
    
    # Add .env file to data files
    env_file = os.path.join('Client', '.env')
    if os.path.exists(env_file):
        data_files.append((env_file, '.'))
        print("Added .env file to PyInstaller data files")
    else:
        print(f"Warning: {env_file} not found, .env will not be included in the package")
    
    # Create temporary spec file
    data_specs = ""
    for src, dest in data_files:
        data_specs += f"    (r'{src}', r'{dest}'),\n"
    
    spec_content = f"""
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    [r'{MAIN_SCRIPT}'],
    pathex=[],
    binaries=[],
    datas=[
{data_specs}
        (r'assets/*', r'assets/'),
        (r'config_handler.py', r'.'),
        (r'dbconfig.py', r'.'),
        ('Client/setup.ui', '.'),
        ('Client/login1.ui', '.'),
        ('Client/MainScreen.ui', '.'),
        ('Client/admin.ui', '.'),
        ('Client/ApplicationScreen.ui', '.'),
        ('Client/auditlog.ui', '.'),
        ('Client/insertpat.ui', '.'),
        ('Client/insertstaff.ui', '.'),
        ('Client/patientsearch.ui', '.'),
        ('Client/registeradmission.ui', '.'),
        ('Client/registerlocation.ui', '.'),
        ('Client/lockScreen.ui', '.'),
        ('Client/stafflookup.ui', '.'),
        (r'.env', r'.')  # Include .env file in the root directory
    ],
    hiddenimports=[
        'PyQt5', 
        'PyQt5.QtWidgets', 
        'PyQt5.QtCore', 
        'PyQt5.QtGui', 
        'psycopg2', 
        'pandas', 
        'dotenv', 
        'python-dotenv',
        'requests'
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
    console=True,  # Set to True for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=r'{ICON_PATH}' if os.path.exists(r'{ICON_PATH}') else None,
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
    
    # Write the spec file
    spec_file = f"{APP_NAME}.spec"
    with open(spec_file, "w") as f:
        f.write(spec_content)
    
    print(f"Created PyInstaller spec file: {spec_file}")
    
    # Run PyInstaller
    try:
        print("Running PyInstaller...")
        subprocess.run([sys.executable, "-m", "PyInstaller", spec_file, "--noconfirm"], check=True)
        print(f"Executable built successfully: dist/{APP_NAME}/{APP_NAME}.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running PyInstaller: {e}")
        return False

def create_installer():
    """Create the installer using NSIS"""
    print("Creating installer with NSIS...")
    
    # Check if dist directory exists
    dist_path = f"dist/{APP_NAME}"
    if not os.path.exists(dist_path):
        print(f"ERROR: PyInstaller output directory not found: {dist_path}")
        print("Cannot create installer. PyInstaller must succeed first.")
        return False
    
    # Check if executable exists
    exe_path = os.path.join(dist_path, f"{APP_NAME}.exe")
    if not os.path.exists(exe_path):
        print(f"ERROR: Executable not found: {exe_path}")
        print("Cannot create installer. PyInstaller must succeed first.")
        return False
    
    # Define the NSIS script path
    nsis_script = "client_installer.nsi"
    
    # Create NSIS script
    with open(nsis_script, "w") as f:
        f.write(r"""
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
        print("Error: makensis executable not found.")
        print("Please install NSIS from https://nsis.sourceforge.io/Download")
        return False
    
    try:
        # Run NSIS
        subprocess.run([nsis_path, nsis_script], check=True)
        
        print("Installer created successfully: HospitalManagementSystem_Client_Setup.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running NSIS: {e}")
        return False
    except FileNotFoundError:
        print(f"NSIS executable not found at {nsis_path}")
        return False

def create_distribution_package():
    """Create a complete distribution package"""
    print("Creating distribution package...")
    
    # Create a zip file containing the installer and documentation
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    zip_filename = f"dist/{APP_NAME}-{APP_VERSION}-{timestamp}.zip"
    
    try:
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add the installer
            if os.path.exists("HospitalManagementSystem_Client_Setup.exe"):
                zip_file.write("HospitalManagementSystem_Client_Setup.exe")
            
            # Add the README
            if os.path.exists("README.md"):
                zip_file.write("README.md")
        
        print(f"Distribution package created successfully: {zip_filename}")
    except Exception as e:
        print(f"Error creating distribution package: {e}")

def main():
    """Main packaging process"""
    print(f"Hospital Management System Client Packaging Script v{APP_VERSION}")
    print("=" * 50)
    
    try:
        # Setup environment
        setup_environment()
        
        # Install dependencies
        install_dependencies()
        
        # Copy config files
        copy_config_files()
        
        # Build executable
        if not build_executable():
            print("Error building executable")
            return 1
        
        # Create installer
        if not create_installer():
            print("Error creating installer")
            return 1
        
        # Create distribution package
        create_distribution_package()
        
        print("\nPackaging completed successfully!")
        print(f"Installer: HospitalManagementSystem_Client_Setup.exe")
        
        return 0
    
    except Exception as e:
        print(f"\nERROR: Packaging failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())