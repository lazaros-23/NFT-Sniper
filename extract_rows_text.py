import datetime
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver import ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
import re
import os
import threading
import json
import pandas


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
    log("Got nft page!", logging)
    force_render(browser, logging)


url = "https://app.traitsniper.com/8sian-main-collection?page=1&min_price=0.01"

# Initialize a browser instance with Firefox and go to the url page
#options =  ChromeOptions()
#options.headless = True
#browser = webdriver(ChromeDriverManager().install(), options = option)
options = ChromeOptions()
options.headless = True
browser = webdriver.Chrome(ChromeDriverManager().install())#, options=options)
options.add_experimental_option("detach", True)


get_nft_page(browser, url)
active_rows = get_elements(browser, by = By.CSS_SELECTOR, selector = ".table_highlight__3TB-I")

# Extract text from rows
active_nfts_list = [x.text for x in active_rows]

def find_between_r( s, first, last ):
    try:
        start = s.rindex( first ) + len( first )
        end = s.rindex( last, start )
        return s[start:end]
    except ValueError:
        return ""

def make_dataframe(data, dictionary: dict):
    for element in data[6:]:
        element = element.split(':')

        key = element[0]
        value = element[1]

        dictionary[key] = value

    return(dictionary)    

data = []

for row in active_nfts_list:
    score = row[1].replace('OpenSea ',"")
    row = row.splitlines()
    new_dir = {"id": row[0], 'Score': float(score.replace(',', '')), 'Rank': int(row[2]),
               'Price': float(row[3].replace('Ξ', "").replace(',', ''))}
    data.append(make_dataframe(row, new_dir))


data = pandas.DataFrame(data)
print(data.head(10))