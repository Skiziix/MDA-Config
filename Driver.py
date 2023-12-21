from PowerAppEntity import PowerAppEntity
import json
import sys

# Configuration file with correct endpoint and environment
configure = json.load(open(sys.argv[1]))

# Picklist ID
global_choice = "9de86e6b-45a0-ee11-be37-6045bd006eaf"

# PowerAppEntity object for posting data to PowerApps
table = PowerAppEntity(configure, "MoweryCRM")

# JSON file of all attributes: schema_name, label, type
f = open("./SkillsFields.json", "r", encoding='utf-8')

# Loading file in as JSON
attributes = json.load(f)

# Loop over every attribute
for attribute in attributes:
    
    # If the attribute is of type choice post a choice attribute
    if attributes[attribute]["type"] == "choice":
        table.post_global_choice_attribute(attribute, attributes[attribute]["label"], global_choice)

    # If the attribute is of type text post a memo attribute
    elif attributes[attribute]["type"] == "text":
        table.post_memo_attribute(attribute, attributes[attribute]["label"])