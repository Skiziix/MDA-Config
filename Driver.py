from PowerAppEntity import PowerAppEntity
import json
import sys

configure = json.load(open(sys.argv[1]))

gobal_choice = "b0a161bd-409f-ee11-be37-6045bd0064ab"

table = PowerAppEntity(configure, "MoweryCRM")

#table.post_global_choice_attribute("SampleChoice4", "Sample Choice 4.0", gobal_choice)
table.post_text_attribute("SampleText", "Sample Text")