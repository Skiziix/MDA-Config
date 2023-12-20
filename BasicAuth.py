import sys  # For simplicity, we'll read config file from 1st CLI param sys.argv[1]
import json
import logging
import time

import requests
import msal


# Optional logging
# logging.basicConfig(level=logging.DEBUG)  # Enable DEBUG log for entire script
# logging.getLogger("msal").setLevel(logging.INFO)  # Optionally disable MSAL DEBUG logs

config = json.load(open(sys.argv[1]))

# If for whatever reason you plan to recreate same ClientApplication periodically,
# you shall create one global token cache and reuse it by each ClientApplication
global_token_cache = msal.TokenCache()  # The TokenCache() is in-memory.
    # See more options in https://msal-python.readthedocs.io/en/latest/#tokencache

# Create a preferably long-lived app instance, to avoid the overhead of app creation
global_app = msal.ConfidentialClientApplication(
    config["client_id"], authority=config["authority"],
    client_credential=config["secret"],
    token_cache=global_token_cache,  # Let this app (re)use an existing token cache.
        # If absent, ClientApplication will create its own empty token cache
    )


def acquire_and_use_token():
    # Since MSAL 1.23, acquire_token_for_client(...) will automatically look up
    # a token from cache, and fall back to acquire a fresh token when needed.
    result = global_app.acquire_token_for_client(scopes=config["scope"])

    
    if "access_token" in result:
        print("Token was obtained from:", result["token_source"])  # Since MSAL 1.25
        # Calling graph using the access token
        graph_data = requests.get(  # Use token to call downstream service
            config["endpoint"],
            headers={'Authorization': 'Bearer ' + result['access_token']},).json()
        print("Graph API call result: %s" % json.dumps(graph_data, indent=2))
    

    else:
        print("Token acquisition failed")  # Examine result["error_description"] etc. to diagnose error


while True:  # Here we mimic a long-lived daemon
    acquire_and_use_token()
    print("Press Ctrl-C to stop.")
    time.sleep(5)  # Let's say your app would run a workload every X minutes