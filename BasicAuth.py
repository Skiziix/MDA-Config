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
    token = global_app.acquire_token_for_client(scopes=config["scope"])

    # Json model of attribute to be created
    picklist_global_choice = {
        "@odata.type": "Microsoft.Dynamics.CRM.PicklistAttributeMetadata",
        "AttributeType": "Picklist",
        "AttributeTypeName": {
            "Value": "PicklistType"
        },
        "SourceTypeMask": 0,
        "OptionSet": {
            "@odata.type": "Microsoft.Dynamics.CRM.OptionSetMetadata",
            "Options": [
            {
                "Value": 727000000,
                "Label": {
                "@odata.type": "Microsoft.Dynamics.CRM.Label",
                "LocalizedLabels": [
                    {
                    "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel",
                    "Label": "Bravo",
                    "LanguageCode": 1033,
                    "IsManaged": False
                    }
                ],
                "UserLocalizedLabel": {
                    "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel",
                    "Label": "Bravo",
                    "LanguageCode": 1033,
                    "IsManaged": False
                }
                }
            },
            {
                "Value": 727000001,
                "Label": {
                "@odata.type": "Microsoft.Dynamics.CRM.Label",
                "LocalizedLabels": [
                    {
                    "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel",
                    "Label": "Delta",
                    "LanguageCode": 1033,
                    "IsManaged": False
                    }
                ],
                "UserLocalizedLabel": {
                    "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel",
                    "Label": "Delta",
                    "LanguageCode": 1033,
                    "IsManaged": False
                }
                }
            },
            {
                "Value": 727000002,
                "Label": {
                "@odata.type": "Microsoft.Dynamics.CRM.Label",
                "LocalizedLabels": [
                    {
                    "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel",
                    "Label": "Alpha",
                    "LanguageCode": 1033,
                    "IsManaged": False
                    }
                ],
                "UserLocalizedLabel": {
                    "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel",
                    "Label": "Alpha",
                    "LanguageCode": 1033,
                    "IsManaged": False
                }
                }
            },
            {
                "Value": 727000003,
                "Label": {
                "@odata.type": "Microsoft.Dynamics.CRM.Label",
                "LocalizedLabels": [
                    {
                    "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel",
                    "Label": "Charlie",
                    "LanguageCode": 1033,
                    "IsManaged": False
                    }
                ],
                "UserLocalizedLabel": {
                    "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel",
                    "Label": "Charlie",
                    "LanguageCode": 1033,
                    "IsManaged": False
                }
                }
            },
            {
                "Value": 727000004,
                "Label": {
                "@odata.type": "Microsoft.Dynamics.CRM.Label",
                "LocalizedLabels": [
                    {
                    "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel",
                    "Label": "Foxtrot",
                    "LanguageCode": 1033,
                    "IsManaged": False
                    }
                ],
                "UserLocalizedLabel": {
                    "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel",
                    "Label": "Foxtrot",
                    "LanguageCode": 1033,
                    "IsManaged": False
                }
                }
            }
            ],
            "IsGlobal": True,
            "OptionSetType": "Picklist"
        },
        "Description": {
            "@odata.type": "Microsoft.Dynamics.CRM.Label",
            "LocalizedLabels": [
            {
                "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel",
                "Label": "Choice Attribute",
                "LanguageCode": 1033,
                "IsManaged": False
            }
            ],
            "UserLocalizedLabel": {
            "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel",
            "Label": "Choice Attribute",
            "LanguageCode": 1033,
            "IsManaged": False
            }
        },
        "DisplayName": {
            "@odata.type": "Microsoft.Dynamics.CRM.Label",
            "LocalizedLabels": [
            {
                "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel",
                "Label": "Sample Choice 2.0",
                "LanguageCode": 1033,
                "IsManaged": False
            }
            ],
            "UserLocalizedLabel": {
            "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel",
            "Label": "Sample Choice 2.0",
            "LanguageCode": 1033,
            "IsManaged": False
            }
        },
        "RequiredLevel": {
            "Value": "None",
            "CanBeChanged": False,
            "ManagedPropertyLogicalName": "canmodifyrequirementlevelsettings"
        },
        "SchemaName": "SampleChoice2"
    }

    # Json model of headers needed to post to projects table in Sandbox_Mowery
    post_headers = headers = {
        'MSCRM.SolutionName': 'MoweryCRM',
        'OData-MaxVersion': '4.0',
        'OData-Version': '4.0',
        'If-None-Match': 'null',
        'Accept': 'application/json',
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': 'Bearer ' + token['access_token'],
    }
    
    # Existent token
    if "access_token" in token:
        print("Token was obtained from:", token["token_source"])  # Since MSAL 1.25
        # Calling graph using the access token
        response = requests.get(  # Use token to call downstream service
            config["endpoint"],
            headers=post_headers,).json()
        
        if response.status_code == 200:
            print("Success!")
            print("Graph API call token: %s" % json.dumps(response, indent=2))

        elif response.status_code == 401:
            print("Unauthorized.")

        else:
            print("Error!")

        
    else:
        print("Token acquisition failed")  # Examine token["error_description"] etc. to diagnose error


while True:  # Here we mimic a long-lived daemon
    acquire_and_use_token()
    print("Press Ctrl-C to stop.")
    time.sleep(5)  # Let's say your app would run a workload every X minutes