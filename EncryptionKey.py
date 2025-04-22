import requests
import os
import subprocess
from dotenv import load_dotenv

def getKeys():
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
    keys = [] 

    if not token:
        raise ValueError("HCP_API_TOKEN environment variable not found!")

    # 2. Define the HCP Secrets API URL
    url = "https://api.cloud.hashicorp.com/secrets/2023-11-28/organizations/37081b52-54bf-44cf-8874-5234ee366ba0/projects/17499756-a1d2-4bf0-bebb-7f8fae636b94/apps/hosDB/secrets:open"

    # 3. Set headers with the Bearer token
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
        }

    try:
        # 4. Make the GET request
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise HTTP errors as exceptions

        # 5. Parse and return secrets
        secrets = response.json()
        for secret in secrets['secrets']:
            keys.append(secret['static_version']['value'])
        return keys

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
    except Exception as e:
        print(f"Error: {e}")