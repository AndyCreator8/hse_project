import requests

import json

with open("aa.json", 'r', encoding="utf8") as file:
    data = json.load(file)

a = "https://i.redd.it/cgcghg093hsh1.jpeg"
print(a.split("/")[3])
for i in data["data"]["children"]:
    print(i["data"]["url_overridden_by_dest"])