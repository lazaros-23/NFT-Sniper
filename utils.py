from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException

from requests.api import head
from bs4 import BeautifulSoup
import urllib.request

import threading
import datetime
import time
import re
import os
import json
import pandas as pd


def log(msg, logging = True):
    
    """
    Prints messages to console and to a logging.txt file
    
    Parameters
    ----------
    msg : (str)
        log message to be printed on the screen and logged with time in file logging.txt.
    logging : (boolean)
        a boolean argument (True/False) which default is True. Use it when verbose is a
        demand by printing scraping steps and failures (if any).

    Returns
    -------
    None

    """
    
    if logging == True:
        current_time = datetime.datetime.today().strftime('%Y-%m-%d_%H:%M:%S')
        logging_message = msg + " @" + current_time + "\n"
        print(logging_message)
        with open("logging.txt", 'a+') as logging:
            logging.write(logging_message)


def force_render(browser, logging = True):
    
    """
    Nft pages do not render completely unless they are scrolled up/down
    To make sure all data points are visible this function zooms out
    from css content.


    Parameters
    ----------
    browser : (webdriver instance)
        Selenium webdriver instance

    logging : (boolean)
        A boolean argument (True/False) which default is True. Use it when verbose is a
        demand by printing scraping steps and failures (if any).


    Returns
    -------
    None

    """
    
    browser.maximize_window()
    browser.execute_script("window.scrollTo(0, 1080);")
    browser.execute_script("window.scrollTo(0, 0);")
    browser.find_element_by_tag_name("html").send_keys(Keys.CONTROL,Keys.SUBTRACT)
    browser.find_element_by_tag_name("html").send_keys(Keys.CONTROL,Keys.SUBTRACT)
    browser.find_element_by_tag_name("html").send_keys(Keys.CONTROL,Keys.SUBTRACT)
    browser.find_element_by_tag_name("html").send_keys(Keys.CONTROL,Keys.SUBTRACT)
    browser.find_element_by_tag_name("html").send_keys(Keys.CONTROL,Keys.SUBTRACT)


def get_elements(browser, by, selector):
    
    """
    Uses WebDriverWait method to wait for 10 seconds for elements to load on the page
    and, if found, returns all elements for given selector


    Parameters
    ----------
    browser : (webdriver instance)
        Selenium webdriver instance to
    by : (selenium.webdriver.common.by.By  instance)
        Set of supported locator strategies that tells the borwser which strategy to use in
        finding an element (CLASS_NAME, XPATH, CSS_SELECTOR)
    selector : (str)
        A string representing the element selector from the DOM whichever xpath, class name
        or css selector.

    Returns
    -------
    (Webdrive element)
        A found element which can be processed later by procedures such as .click() and
        has attributes such as .text which represent the innerHTML text of an element.

    """
    
    try:
        elements = WebDriverWait(browser, 10).until(EC.presence_of_all_elements_located((by, selector)))
        return elements
    except TimeoutException:
        return None


def get_nft_page(browser, nft_url, logging = True):
    
    """
    Opens the nft url in the browser instance created previously

    Parameters
    ----------
    browser : (webdriver instance)
        Selenium webdriver instance
    nft_url : (str)
        The nft page url.
    logging : (boolean)
        A boolean argument (True/False) which defaults to True. Use it when verbose is a
        demand by printing scraping steps and failures (if any).

    Returns
    -------
    None
        It returns None, however it brings up the browser instance to the nft url
        to be ready for scraping.

    """
    
    browser.get(nft_url)
    log(f"Got {nft_url} page!", logging)
    force_render(browser, logging)


def transform_text_to_dict(text):
            
    rows = text.splitlines()
    nft_dict = {"Id": rows[0], 'Score': rows[1].replace('OpenSea ',""), 'Rank': int(rows[2]),
               'Price': float(rows[3].replace('Ξ', "").replace(',', '')), 'Traits': {}}
        
    # If NFT has traits, fill them
    for trait in rows[6:]:
        
        trait = trait.split(':')

        key = trait[0]
        value = float(re.search("\[.*d*%" , trait[1]).group()[1:-1])

        nft_dict['Traits'][key] = value

    return nft_dict


def extract_links(links_html):
    
    links_list = []
    
    for link in links_html:
        url = 'https://app.traitsniper.com' + str(link['href']) + '?min_price=0.01'
        links_list.append(url)

    return links_list


def get_nft_projects(url):
    
    # Setup and make a request to given url and read response
    req = urllib.request.Request(url, headers = {'User-Agent': 'Mozilla/5.0'})
    webpage = urllib.request.urlopen(req).read()

    # Parse HTML response
    soup = BeautifulSoup(webpage, 'html.parser')
    
    # The whole HTML is string here
    strhtm = soup.prettify()

    # Finds the spesific tag that we want
    tag =  soup.find_all('script', {'id' : '__NEXT_DATA__'})
    
    # Find the link for every project and save it in a list
    links_html = soup.find_all('a', {'class' : 'table_image__2hDeD'})
    links = extract_links(links_html)

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

        nft_dict = {"nft_name": project['nft_name'], "supply": project['supply'], "total_revealed": project['total_revealed'], 
                "status": project['status'],"floor_price": project['floor_price'], "one_day_volume": project['one_day_volume'], 
                "one_day_sales": project['one_day_sales'], "total_sales": project['total_sales'],"total_volume": project['total_volume'], 
                "num_owners": project['num_owners'], "market_cap": project['market_cap'], "expecting_reveal_time": project['expecting_reveal_time']}

        data.append(nft_dict)
        floor_prices.append(project['floor_price'])

    # Creates the dataframe and returns
    projects_df = pd.DataFrame(data)
    
    return projects_df, links, floor_prices


def organise_data(browser, url):
    
    # Go to project's page
    get_nft_page(browser, url)
    
    # Get all active NFT's rows and extract their text elements
    try:
        active_rows = get_elements(browser, by = By.CSS_SELECTOR, selector = ".table_highlight__3TB-I")
        active_nfts_list = [x.text for x in active_rows]
    
    except:
        log("Site probably blocked us!")
        return pd.DataFrame([])

    # Do a bit of cleanup on the extracted text and keep it in a list
    data = []

    for nft in active_nfts_list:
        data.append(transform_text_to_dict(nft))

    # Create the df from the transformed data and return
    nfts_df = pd.DataFrame(data)
    
    return nfts_df 


def select_best_NFTs(nfts, floor_price, project_name):
    
    best_NFTs = nfts.loc[nfts['Price'] < floor_price]
    
    # for i in best_NFTs.index:
    #     print(f"The nft with id {best_NFTs.loc[i]['Id']} of the {project_name} project has a price lower than floor value {floor_price}")
    
    return best_NFTs


def get_total_pages(browser):
    
    pages_container = get_elements(browser, by = By.CSS_SELECTOR, selector = ".pagination-module_container__1VCbr")[0]
    total_pages = pages_container.text[4:]
    
    return total_pages
    
def go_to_next_page(browser):
    
    pages_container = get_elements(browser, by = By.CSS_SELECTOR, selector = ".pagination-module_container__1VCbr")[0]
    next_button = pages_container.find_element_by_css_selector('.button-module_button__3MTAs.outline-module_normal__2UWTT.size-module_medium__3lKxN.border-module_radius__3oqnj.outset-module_main__P_UrM.none-module_outset__2cMD2')
    next_button.click()
    