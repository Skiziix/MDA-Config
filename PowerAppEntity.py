import sys  # For simplicity, we'll read config file from 1st CLI param sys.argv[1]
import json
import logging
import time

import requests
import msal


# Optional logging
# logging.basicConfig(level=logging.DEBUG)  # Enable DEBUG log for entire script
# logging.getLogger("msal").setLevel(logging.INFO)  # Optionally disable MSAL DEBUG logs

#config = json.load(open(sys.argv[1]))


class PowerAppEntity:

    def __init__(self, config, solution_name):

        # If for whatever reason you plan to recreate same ClientApplication periodically,
        # you shall create one global token cache and reuse it by each ClientApplication
        global_token_cache = msal.TokenCache()  # The TokenCache() is in-memory.
            # See more options in https://msal-python.readthedocs.io/en/latest/#tokencache

        # Create a preferably long-lived app instance, to avoid the overhead of app creation
        self.global_app = msal.ConfidentialClientApplication(
            self.config["client_id"], authority=self.config["authority"],
            client_credential=self.config["secret"],
            token_cache=global_token_cache,  # Let this app (re)use an existing token cache.
                # If absent, ClientApplication will create its own empty token cache
            )
        
        self.config = config
        self.solution_name = solution_name

    def post_global_choice_attribute(self, schema_name, label_name, global_option_id):

        # Json model of attribute to be created
        body = {
            "@odata.type": "Microsoft.Dynamics.CRM.PicklistAttributeMetadata",
            "AttributeType": "Picklist",
            "AttributeTypeName": {
                "Value": "PicklistType"
            },
            "SourceTypeMask": 0,
            "GlobalOptionSet@odata.bind": "/GlobalOptionSetDefinitions(" + global_option_id + ")",
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
                    "Label": label_name,
                    "LanguageCode": 1033,
                    "IsManaged": False
                }
                ],
                "UserLocalizedLabel": {
                "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel",
                "Label": label_name,
                "LanguageCode": 1033,
                "IsManaged": False
                }
            },
            "RequiredLevel": {
                "Value": "None",
                "CanBeChanged": False,
                "ManagedPropertyLogicalName": "canmodifyrequirementlevelsettings"
            },
            "SchemaName": "mow_" + schema_name
        }
        

        self.post_attirbute(body)

    def post_text_attribute(self, schema_name, label_name):

        body = {  
            "AttributeType": "String",  
            "AttributeTypeName": {  
            "Value": "StringType"  
            },  
            "Description": {  
            "@odata.type": "Microsoft.Dynamics.CRM.Label",  
            "LocalizedLabels": [  
            {  
                "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel",  
                "Label": "Text field",  
                "LanguageCode": 1033  
            }  
            ]  
            },  
            "DisplayName": {  
            "@odata.type": "Microsoft.Dynamics.CRM.Label",  
            "LocalizedLabels": [  
            {  
                "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel",  
                "Label": label_name,  
                "LanguageCode": 1033  
            }  
            ]  
            },  
            "RequiredLevel": {  
            "Value": "None",  
            "CanBeChanged": True,  
            "ManagedPropertyLogicalName": "canmodifyrequirementlevelsettings"  
            },  
            "SchemaName": schema_name,  
            "@odata.type": "Microsoft.Dynamics.CRM.StringAttributeMetadata",  
            "FormatName": {  
            "Value": "Text"  
            },   
        }  

        self.post_attirbute(body)


    def acquire_token(self):
        # Since MSAL 1.23, acquire_token_for_client(...) will automatically look up
        # a token from cache, and fall back to acquire a fresh token when needed.
        token = self.global_app.acquire_token_for_client(scopes=self.config["scope"])        
        
        return token

    def post_attirbute(self, post_body):

        token = self.acquire_token()

        post_headers = {
            'MSCRM.SolutionName': self.solution_name,
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

            # Posting attribute to table
            response = requests.post(
                self.config["endpoint"],
                headers=post_headers, json=post_body)
            
            # Successful POST
            if response.status_code == 200:
                print("Success!")
                print(response.headers)

            # Unauthorized to POST
            elif response.status_code == 401:
                print("Unauthorized.")

            # Other Error
            else:
                print(response.content)

        # Unable to acquire token            
        else:
            print(f'Token acquisition failed:\n\t{token["error_description"]}')  # Examine token["error_description"] etc. to diagnose error

