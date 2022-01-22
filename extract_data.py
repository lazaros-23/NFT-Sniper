import requests
import pandas as pd
from requests.api import head
from bs4 import BeautifulSoup
import urllib.request
import json
import xmltojson
import re
import pandas

#url = "https://app.traitsniper.com/?status=unrevealed"


def extractLinks(links):
    
    listLinks = []
    for link in links:
        url = 'https://app.traitsniper.com' + str(link['href']) + '?min_price=0.01'
        listLinks.append(url)

    return listLinks


def getProjects(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urllib.request.urlopen(req).read()

    soup = BeautifulSoup(webpage, 'html.parser')
    strhtm = soup.prettify() # The whole HTTML is string heref

    # Finds the spesific tag that we want
    tag =  soup.find_all('script', {'id' : '__NEXT_DATA__'})
    
    # Find the link for every project and save it in a list
    links = soup.find_all('a', {'class' : 'table_image__2hDeD'})
    links = extractLinks(links)


    # Make some replacements that they might be needed
    tag = str(tag).replace('script id="__NEXT_DATA__" type="application/json">', '')
    tag = str(tag).replace('/script', '')
    tag = tag.replace('<', '')
    tag = tag.replace('>', '')

    # Reads the tag in the JSON format
    json_file = json.loads(tag)
    # Create an empty list
    data = []
    floor_prices = []

    # If you want to see all the types of the data that we have, please do replace print(project['nft_name']) with print(project.keys())
    # In case you decide that you want to see other kind of data, please replace nft_name with the type of data(key) that you want to see
    for project in json_file[0]['props']['pageProps']['projects']:

        dict = {"nft_name": project['nft_name'], "supply": project['supply'], "total_revealed": project['total_revealed'], 
                "status": project['status'],"floor_price": project['floor_price'], "one_day_volume": project['one_day_volume'], 
                "one_day_sales": project['one_day_sales'], "total_sales": project['total_sales'],"total_volume": project['total_volume'], 
                "num_owners": project['num_owners'], "market_cap": project['market_cap'], "expecting_reveal_time": project['expecting_reveal_time']}

        data.append(dict)
        floor_prices.append(project['floor_price'])

    # Creates the dataframe and prints the first 10 rows
    data = pandas.DataFrame(data)
    return data, links, floor_prices


# Probably this function is useless
def getProjectNames(data, links_lengh: int):
    projectNames = []
    for project_name in data[:links_lengh]['nft_name']:
        projectNames.append(project_name)
    
    return projectNames  

if __name__== '__main__':
     url = 'https://app.traitsniper.com/?status=unrevealed'

     data, links = getProjects(url)