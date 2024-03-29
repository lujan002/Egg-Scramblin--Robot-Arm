# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 08:49:57 2024

@author: 20Jan
"""

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
import urllib
import time

!apt-get update 
!apt install chromium-chromedriver

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome('chromedriver',chrome_options=chrome_options)

url = ("https://www.google.com/search?q=
{s}&tbm=isch&tbs=sur%3Afc&hl=en&ved=0CAIQpwVqFwoTCKCa1c6s4-
oCFQAAAAAdAAAAABAC&biw=1251&bih=568")

driver.get(url.format(s='Pets'))

driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
time.sleep(5)

imgResults = driver.find_elements(By.XPATH,"//img[contains(@class,'Q4LuWd')]")

src = []
for img in imgResults:
    src.append(img.get_attribute('src'))
    
for i in range(10):    
urllib.request.urlretrieve(str(src[i]),"sample_data/pets{}.jpg".format(i))