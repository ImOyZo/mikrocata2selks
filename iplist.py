#!/usr/bin/env python3

import requests
import json
import os

# SID config can be seen here https://sidallocation.org/
start_sid = 1000001
api_key = 'YOUR_API_KEY'
output_file = '/srv/SELKS/docker/containers-data/nginx/custom-rules/abuseipdb_blacklist.rules'


def abuseipdb_blacklist2suricata():
    # API parameters
    url = 'https://api.abuseipdb.com/api/v2/blacklist'
    headers = {
        'Key': api_key,
        'Accept': 'application/json'
    }
    params = {
        'confidenceMinimum': 100,
        'limit': 10000, 
        'ipVersion': 4
    }

    try:
        print("Fetching data from AbuseIPDB...")
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raises exception for 4XX/5XX errors

        data = response.json()
        ip_list = [entry['ipAddress'] for entry in data['data']]
        print(f"Successfully retrieved {len(ip_list)} IPs from AbuseIPDB.")

        # Write to Suricata rules file
        with open(output_file, 'w') as f:  
            for idx, ip in enumerate(ip_list, start=start_sid):
                rule = f'alert ip {ip} any -> any any (msg:"AbuseIPDB Blacklisted IP"; sid:{idx}; rev:1;)\n'
                f.write(rule)
        
        print(f"Successfully wrote {len(ip_list)} rules to {output_file}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except json.JSONDecodeError:
        print("Failed to decode JSON response")
    except KeyError:
        print("Unexpected response format from API")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))
    abuseipdb_blacklist2suricata()