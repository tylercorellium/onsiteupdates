# Setup
Modify `config.json` with the information from your credentials file
```json
{
    "username": "CHANGEME",
    "password": "CHANGEME",
    "domain": "https://CHANGEME.enterprise.corellium.com"
  }
```

# Usage
You can either run this utility directly on top of your Corellium appliance, where it will try and match its hostname against the list of available appliances. If the script does not detect your hostname in the returned list, it will alert you like so:

`[!] Could not find this unit's hostname in the files portal, are you running this directly on the appliance?`

If it does match, it will return only results pertaining to that appliance. Otherwise, you must select the correct update and transfer it onto your appliance. 

Lastly, it gives you a clean `wget` command to run directly from your appliance. 

Example output:
```bash
$ python3.8 main.py
[+] Found 1 files for appliance-1
6.3.0 Update 
Download link: wget https://not-a-real-domain.enterprise.corellium.com/api/v1/deployments/eyRestOfJWTHere -O appliance-1-6.3.0-rc12-onsite.tar.xz
Size: 13.440742332488298 GB
SHA256: a434e9aaa105b6e11329c720e59efa63106198d122b36177bb334f059a64e6fc
```
