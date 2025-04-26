#!/usr/bin/env python
# hcp_setup.py - HashiCorp Cloud Platform Setup

import os
import sys
import subprocess
import platform
import tempfile
import configparser
from pathlib import Path

def install_hcp_cli():
    """Install the HashiCorp Cloud Platform CLI"""
    system = platform.system().lower()
    
    # Temporary directory for downloads
    temp_dir = Path(tempfile.mkdtemp())
    
    if system == "windows":
        # Download HCP CLI for Windows
        hcp_url = "https://releases.hashicorp.com/hcp/0.8.0/hcp_0.8.0_windows_amd64.zip"
        hcp_zip = temp_dir / "hcp.zip"
        
        print(f"Downloading HCP CLI from {hcp_url}...")
        subprocess.run(["curl", "-o", str(hcp_zip), hcp_url], check=True)
        
        # Extract the zip file
        print("Extracting HCP CLI...")
        subprocess.run(["powershell", "-command", f"Expand-Archive -Path '{hcp_zip}' -DestinationPath '{temp_dir}'"], check=True)
        
        # Install to Program Files
        install_dir = Path(os.environ.get("ProgramFiles")) / "HashiCorp" / "HCP"
        install_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy the executable
        hcp_exe = temp_dir / "hcp.exe"
        if hcp_exe.exists():
            import shutil
            shutil.copy2(hcp_exe, install_dir / "hcp.exe")
        
        # Add to PATH
        print("Adding HCP to PATH...")
        subprocess.run(["setx", "PATH", f"%PATH%;{install_dir}"], check=True)
    else:
        print("System Not Supported")   
    
    
    print("HCP CLI installed successfully")
    return True

def configure_hcp(client_id, client_secret, organization_id, project_id):
    """Configure HCP with credentials"""
    print("Configuring HCP credentials...")
    
    # Create HCP configuration directory
    config_dir = Path.home() / ".config" / "hcp"
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # Create credentials file
    credentials_file = config_dir / "credentials.hcl"
    
    with open(credentials_file, 'w') as f:
        f.write(f'''credentials "app.terraform.io" {{
  token = "{client_id}"
}}

credentials "hcp.api" {{
  client_id     = "{client_id}"
  client_secret = "{client_secret}"
}}
''')
    
    # Create config file
    config_file = config_dir / "config.hcl"
    
    with open(config_file, 'w') as f:
        f.write(f'''config "hcp" {{
  organization_id = "{organization_id}"
  project_id      = "{project_id}"
}}
''')
    
    print("HCP configured successfully")
    return True

def setup_hcp_prompt():
    """Interactive prompt for HCP setup"""
    print("HashiCorp Cloud Platform (HCP) Setup")
    print("====================================")
    print("\nThis will install and configure HCP for your Hospital Management System.")
    
    install = input("\nDo you want to install the HCP CLI? (y/n): ").lower()
    if install == 'y':
        if not install_hcp_cli():
            print("Failed to install HCP CLI. Please install it manually.")
            return False
    
    configure = input("\nDo you want to configure HCP credentials? (y/n): ").lower()
    if configure == 'y':
        client_id = input("Enter your HCP Client ID: ")
        client_secret = input("Enter your HCP Client Secret: ")
        organization_id = input("Enter your HCP Organization ID: ")
        project_id = input("Enter your HCP Project ID: ")
        
        if not configure_hcp(client_id, client_secret, organization_id, project_id):
            print("Failed to configure HCP. Please configure it manually.")
            return False
    
    print("\nHCP setup completed successfully.")
    return True

if __name__ == "__main__":
    setup_hcp_prompt()