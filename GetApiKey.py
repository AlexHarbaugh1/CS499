
import os
from dotenv import load_dotenv
import subprocess

load_dotenv()
client_id = os.getenv("HCP_CLIENT_ID")
client_secret = os.getenv("HCP_CLIENT_SECRET")

ps_command = f"""
    $response = curl.exe --location "https://auth.idp.hashicorp.com/oauth2/token" `
        --header "Content-Type: application/x-www-form-urlencoded" `
        --data-urlencode "client_id={client_id}" `
        --data-urlencode "client_secret={client_secret}" `
        --data-urlencode "grant_type=client_credentials" `
        --data-urlencode "audience=https://api.hashicorp.cloud"
    $response | ConvertFrom-Json | Select -ExpandProperty access_token
    """

try:
    # Execute PowerShell command
    result = subprocess.run(["powershell", "-Command", ps_command], 
                          capture_output=True, text=True, check=True)
        
    # Clean and parse the token
    token = result.stdout.strip()
    if not token:
        raise ValueError("No access token received")
except subprocess.CalledProcessError as e:
        print(f"PowerShell Error: {e.stderr}")
        exit(1)
except Exception as e:
    print(f"Error: {str(e)}")
    exit(1)

print(token)
