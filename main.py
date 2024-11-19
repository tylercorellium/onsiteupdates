import json
import requests
import subprocess
import argparse
import re


def load_config(config_path):
    """Load credentials from config file"""
    with open(config_path, "r") as config_file:
        config = json.load(config_file)
    return config


def authenticate(domain, username, password):
    """Authenticate and get JWT"""
    auth_url = f"{domain}/api/v1/tokens"
    headers = {"Content-Type": "application/json"}
    payload = {"username": username, "password": password}
    response = requests.post(auth_url, headers=headers, json=payload)

    if response.status_code == 200:
        token = response.json().get("token")
        return token
    else:
        raise Exception(
            f"Authentication failed: {response.status_code} {response.text}"
        )


def get_deployments(domain, token):
    """Get deployments using the JWT"""
    deployments_url = f"{domain}/api/v1/deployments"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.get(deployments_url, headers=headers)

    if response.status_code == 200:
        deployments = response.json()
        return deployments
    else:
        raise Exception(
            f"Failed to fetch deployments: {response.status_code} {response.text}"
        )


def extract_version(name):
    """Extract version number from the filename, return as a tuple for comparison."""
    version_match = re.search(r"(\d+\.\d+\.\d+)", name)
    if version_match:
        return tuple(map(int, version_match.group(1).split(".")))
    return (0, 0, 0)


def retrieve_info(appliance, config, latest=False, download=False):
    """Print download info or download the latest file if specified."""
    files = appliance["files"]
    if latest and files:
        # Find the file with the highest version
        latest_file = max(files, key=lambda f: extract_version(f["name"]))
        files = [latest_file]  # Only keep the latest file

    print(f"[+] Found {len(files)} file(s) for {appliance['id']}")
    for update in files:
        download_command = (
            f"wget {config['domain']}{update['url']} -O {update['filename']}"
        )

        if download:
            print(f"Initiating download for {update['name']}")
            print(f"Running command: {download_command}")
            subprocess.run(download_command, shell=True)
        else:
            print(f"{update['name']}")
            print(f"Download link: {download_command}")
            print(f"Size: {update['size'] / 1024 / 1024 / 1024:.2f} GB")
            print(f"SHA256: {update['sha256-checksum']}\n")
    print("-" * 20)


def main():
    parser = argparse.ArgumentParser(description="Firmware retrieval script.")
    parser.add_argument(
        "--latest",
        action="store_true",
        help="Only display the latest download for each appliance.",
    )
    parser.add_argument(
        "--client", type=str, help="Specify the appliance to filter by."
    )
    parser.add_argument(
        "--download", action="store_true", help="Download the specified file."
    )
    args = parser.parse_args()

    config = load_config("config.json")
    domain = config["domain"]
    username = config["username"]
    password = config["password"]

    try:
        token = authenticate(domain, username, password)
        deployments = get_deployments(domain, token)

        if args.client:
            # Filter deployments by client ID
            deployments = [
                appliance for appliance in deployments if appliance["id"] == args.client
            ]
            if not deployments:
                print(f"[!] No deployment found for client '{args.client}'")
                return

        for appliance in deployments:
            retrieve_info(appliance, config, latest=args.latest, download=args.download)

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()

