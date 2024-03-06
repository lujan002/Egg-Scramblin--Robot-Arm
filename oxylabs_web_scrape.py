# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 08:58:44 2024

@author: 20Jan

https://oxylabs.io/blog/scrape-images-from-website
"""

import hashlib, io, requests, pandas as pd
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from bs4 import BeautifulSoup
from pathlib import Path
from PIL import Image


def get_content_from_url(url):
    options = ChromeOptions()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)

    driver.get(url)
    page_content = driver.page_source
    driver.quit()
    return page_content

def parse_image_urls(content, classes, location, source):
    soup = BeautifulSoup(content, "html.parser")
    results = []
    for a in soup.findAll(attrs={"class": classes}):
        name = a.find(location)
        if name not in results:
            results.append(name.get(source))
    return results

def save_urls_to_csv(image_urls):
    df = pd.DataFrame({"links": image_urls})
    df.to_csv("links.csv", index=False, encoding="utf-8")

import base64

def get_and_save_image_to_file(image_url, output_dir):
    try:
        image_content = requests.get(image_url).content # if using normal images? (ebay)
        #image_content = base64.b64decode(image_url) # if using base64 images (google search)
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file).convert("RGB")
        filename = hashlib.sha1(image_content).hexdigest()[:10] + ".png"
        file_path = output_dir / filename
        image.save(file_path, "PNG", quality=80)
    except Exception as e:
        print(f"Error fetching image from URL '{image_url}': {e}")
        
def main():
    url = "https://www.istockphoto.com/photos/scrambled-eggs"
    content = get_content_from_url(url)
    image_urls = parse_image_urls(
        #Ebay Images
        #content=content, classes="s-item__image-wrapper image-treatment", location="img", source="src"
        #Google Search Images
        content=content, classes="wIvQgG_LtEHVMdJvOT7a", location="img", source="src"
    )
    save_urls_to_csv(image_urls)

    for image_url in image_urls:
        get_and_save_image_to_file(
            image_url, output_dir=Path("/Users/20Jan/OneDrive - University of Kansas/Desktop/LJ/Elegoo/Robot Arm/Scrambled Egg Dataset")
        )
        

if __name__ == "__main__":
    main()
    print("Done!")