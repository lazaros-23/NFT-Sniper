import requests
import pandas as pd
from requests.api import head
from bs4 import BeautifulSoup
import urllib.request
import json
import xmltojson
import re

url = "https://app.traitsniper.com"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
webpage = urllib.request.urlopen(req).read()

soup = BeautifulSoup(webpage, 'html.parser')
strhtm = soup.prettify() # The whole HTTML is string here

# Finds the spesific tag that we want
tag =  soup.find_all('script', {'id' : '__NEXT_DATA__'})

# Make some replacements that they might be needed
tag = str(tag).replace('script id="__NEXT_DATA__" type="application/json">', '')
tag = str(tag).replace('/script', '')
tag = tag.replace('<', '')
tag = tag.replace('>', '')

# Tries to read the tag in the json formal and here the errors appear
data = json.loads(tag)
print(data[0]['props']['pageProps'].keys())

# If you want to see all the types of the data that we have, please do replace print(project['nft_name']) with print(project.keys())
# In case you decide that you want to see other kind of data, please replace nft_name with the type of data(key) that you want to see
for project in data[0]['props']['pageProps']['projects']:
    print(project['nft_name'])