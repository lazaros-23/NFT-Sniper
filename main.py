from utils import *

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ChromeOptions
from fake_useragent import UserAgent

import datetime
import time
import re
import os
import threading
import json
import pandas

# Base url
url = 'https://app.traitsniper.com/?status=unrevealed'

# First, go to base url with all NFT projects and gather all project info
projects_df, urls, floor_prices = get_nft_projects(url)

# Initialize browser with approporiate options
options = ChromeOptions()
options.headless = True
user_agent = UserAgent().random
options.add_argument(f'user-agent={user_agent}')
options.add_experimental_option("detach", True)
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--disable-blink-features=AutomationControlled")
browser = webdriver.Chrome("C:\\Program Files (x86)\\Google\\Chrome\\Application\\chromedriver.exe", options = options)

final_data = {}

for i, url in enumerate(urls[:5]):
    
    project_name = projects_df.loc[i]['nft_name']
    
    print(f'Going in: {project_name}\n')
    
    nfts_data = organise_data(browser, url)
    
    # if not nfts_data.empty:
    #     best_nfts = select_best_NFTs(nfts_data, floor_prices[i], project_name)
    #     final_data[project_name] = best_nfts
    final_data[project_name] = nfts_data
        
    time.sleep(3)