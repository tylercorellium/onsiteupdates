import json
import requests
import socket

def load_config(config_path):
    """Load credentials from config file"""
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)
    return config


def authenticate(domain, username, password):
    """Authenticate and get JWT"""
    auth_url = f"{domain}/api/v1/tokens"
    headers = {'Content-Type': 'application/json'}
    payload = {
        'username': username,
        'password': password
    }
    response = requests.post(auth_url, headers=headers, json=payload)
    
    if response.status_code == 200:
        token = response.json().get('token')
        return token
    else:
        raise Exception(f"Authentication failed: {response.status_code} {response.text}")

def get_deployments(domain, token):
    """Get deployments using the JWT"""
    deployments_url = f"{domain}/api/v1/deployments"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    response = requests.get(deployments_url, headers=headers)
    
    if response.status_code == 200:
        deployments = response.json()
        return deployments
    else:
        raise Exception(f"Failed to fetch deployments: {response.status_code} {response.text}")

def retrieve_info(appliance, config):
    """Print the download info out for each file"""
    files: list = appliance["files"]
    print("[+] Found %d files for %s" % (len(files), appliance["id"]))
    for update in files:
        print("%s " % update["name"])
        print("Download link: wget " + config["domain"] + update["url"] + " -O " + update["filename"])
        print("Size: " + str(update["size"] / 1024 / 1024 / 1024) + " GB")
        print("SHA256: %s" % update["sha256-checksum"])
        print("\n")
    print("-" * 20)


def main():
    config = load_config('config.json')
    
    domain = config['domain']
    username = config['username']
    password = config['password']
    hostname = socket.gethostname().split(".")[0]
    
    try:
        token = authenticate(domain, username, password)

        deployments = get_deployments(domain, token)
        print("-" * 20)
        
        if hostname not in [appliance["id"] for appliance in deployments]:
            print("[!] Could not find this unit's hostname in the files portal, are you running this directly on the appliance?")
            
        for appliance in deployments:
            if appliance["id"] == hostname:
                retrieve_info(appliance, config)

            else:
                retrieve_info(appliance, config)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
    