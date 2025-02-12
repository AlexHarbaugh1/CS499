import requests
import os
from dotenv import load_dotenv

def getKeys():
    keys = [] 
    load_dotenv()
    APIkey = os.getenv("HCP_API_TOKEN")
    if not APIkey:
        raise ValueError("HCP_API_TOKEN environment variable not found!")

    # 2. Define the HCP Secrets API URL (use your specific URL)
    url = "https://api.cloud.hashicorp.com/secrets/2023-11-28/organizations/37081b52-54bf-44cf-8874-5234ee366ba0/projects/17499756-a1d2-4bf0-bebb-7f8fae636b94/apps/hosDB/secrets:open"

    # 3. Set headers with the Bearer token
    headers = {
        "Authorization": f"Bearer {APIkey}",
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