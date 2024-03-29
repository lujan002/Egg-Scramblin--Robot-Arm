# -*- coding: utf-8 -*-
"""
Created on Wed Mar  6 22:46:24 2024

@author: 20Jan
"""

import requests
from bs4 import BeautifulSoup
import os
import shutil
import re
from selenium import webdriver
import time

# Initialize empty downloaded urls 
downloaded_urls = set()

def sanitize_filename(url):
    """
    Extracts a clean filename from a URL, ignoring query parameters and sanitizing against invalid characters.
    """
    # Extract filename before any query parameters
    base_name = os.path.basename(url).split('?')[0]
    # Remove characters that are not valid in filenames for Windows OS
    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', base_name)
    # Ensure the filename ends with a proper extension
    if not sanitized.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
        sanitized += '.jpg'  # Default to .jpg if no valid extension is present
    return sanitized

def unique_file_name(directory, name):
    """Generates a unique file name if the proposed one already exists."""
    base_name, extension = os.path.splitext(name)
    counter = 2
    unique_name = name
    # unique_name = sanitize_filename(name)
    while os.path.exists(os.path.join(directory, unique_name)):
        unique_name = f"{base_name}_{counter}{extension}"
        counter += 1
    return unique_name

# # Using a session to maintain cookies across requests
# session = requests.Session()

# def download_images(page_url):
#     # Get Response 
#     # response = session.get(url, headers=headers)
#     # response.raise_for_status()
#     response = requests.get(url, headers=headers)
#     if response.status_code == 200:
#         print("Success!")
#     else:
#         print("Error:", response.status_code)
        
#     # Parse the response content using BeautifulSoup
#     # soup = BeautifulSoup(response.text, 'html.parser')
#     soup = BeautifulSoup(driver.page_source, 'html.parser')

#     # Find all image tags
#     image_tags = soup.find_all('img')
#     print(f"Number of image tags found: {len(image_tags)}")

#     # Loop through all found image tags
#     for img in image_tags:
#         # Get the image source URL
#         img_url = img.get('src')
#         if img_url is None:  # Check if the img_url is None and continue to the next iteration if it is
#             continue
#         # Complete the image URL if it's relative
#         if not img_url.startswith(('http:', 'https:')):
#             img_url = url + img_url
#         # Get the image binary content
#         img_data = requests.get(img_url).content
#         # Get the image file name
#         img_name = os.path.basename(img_url)
#         # Sanitize
#         sanitized_img_name = sanitize_filename(img_name)
#         # Generate a unique file name if necessary
#         unique_img_name = unique_file_name(download_directory, sanitized_img_name)
#         # Write the image data to a file in the download directory
#         with open(os.path.join(download_directory, unique_img_name), 'wb') as file:
#             file.write(img_data)
#         print(f"Downloaded {unique_img_name}")
    
#     print("All images have been downloaded.")

def download_images(page_url):
    response = requests.get(page_url, headers=headers)
    if response.status_code == 200:
        print("Success!")
    else:
        print("Error:", response.status_code)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    image_tags = soup.find_all('img', attrs={'jsname': 'Q4LuWd'}) # Noticing that all images in google image search results have 'jsname': 'Q4LuWd'
    print(f"Number of image tags found: {len(image_tags)}")

    for img in image_tags:
        img_url = img.get('src')
        alt_text = img.get('alt', '')  # Use the alt attribute, default to an empty string if not present
        if img_url is None or img_url in downloaded_urls or img_url.startswith('data:image'):  # Skip if no URL or already downloaded or the image is base-64 encoded (starting w/"data:image")
            print(f"Image {img_url} already downloaded")    
            continue
        if not img_url.startswith(('http:', 'https:')):
            img_url = page_url + img_url
        # Ensure you're not downloading the same image again
        if img_url not in downloaded_urls:
            img_data = requests.get(img_url).content
            # Use alt text if available and non-empty after sanitization; otherwise, use the URL's basename
            img_name = sanitize_filename(alt_text) if alt_text else os.path.basename(img_url)
            sanitized_img_name = sanitize_filename(img_name)
            unique_img_name = unique_file_name(download_directory, sanitized_img_name)
            with open(os.path.join(download_directory, unique_img_name), 'wb') as file:
                file.write(img_data)
            print(f"Downloaded {unique_img_name}")
            downloaded_urls.add(img_url)  # Add the URL to the set after downloading            
    print("All images have been downloaded.")

# def download_images(soup, download_directory):
#     soup = BeautifulSoup(driver.page_source, 'html.parser')
#     image_tags = soup.find_all('img', attrs={'jsname': 'Q4LuWd'})
#     print(f"Number of image tags found: {len(image_tags)}")

#     for img in image_tags:
#         img_url = img.get('src')
#         alt_text = img.get('alt')  # Extract the alt text
#         if img_url is None or img_url.startswith('data:image'):
#             continue
#         # Use alt text for filename; if alt text is missing, use URL basename
#         filename = sanitize_filename(alt_text if alt_text else os.path.basename(img_url))
#         filename = unique_file_name(download_directory, filename)
        
#         response = requests.get(img_url, stream=True)
#         content_type = response.headers.get('Content-Type')
#         if content_type and 'image' in content_type:
#             with open(os.path.join(download_directory, filename), 'wb') as file:
#                 for chunk in response.iter_content(8192):
#                     file.write(chunk)
#             print(f"Downloaded {filename}")
#         else:
#             print(f"Skipped non-image URL: {img_url}")
#     print("All images have been downloaded.")
    
# URL of the webpage to scrape
# url = 'https://www.istockphoto.com/search/2/image-film?phrase=scrambled+eggs'
# url = "https://www.shutterstock.com/search/runny-scrambled-eggs"
url = "https://www.google.com/search?q=fluffy+scrambled+eggs&tbm=isch&hl=en&chips=q:fluffy+scrambled+eggs,g_1:milk:DwxauPXt5ok%3D&prmd=ivsnmbtz&rlz=1C1CHBF_enUS938US938&sa=X&ved=2ahUKEwiRxpXNuoCFAxU8wckDHRSbAugQ4lYoB3oECAEQQA&biw=1903&bih=902"
# Example headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
}

###
# # Set up Selenium driver (make sure you have the appropriate driver installed for your browser)

# .Edge, .Firefox, .Chrome
driver = webdriver.Edge()

#storing the url in driver
driver.get(url)

#giving some time to load
time.sleep(3)

#getting the height of the webpage for infinite croll web page
last_height = driver.execute_script("return document.body.scrollHeight")
# ###

    
# Number of pages you want to scrape
num_pages = 1

# Directory where you want to save the downloaded images
download_directory = 'downloaded_images'
os.makedirs(download_directory, exist_ok=True)

# Easily Delete Folder Contents (For Testing)
delete_folder_contents = True
if delete_folder_contents == True:
    # Loop over each file in the directory and delete it
    for filename in os.listdir(download_directory):
        file_path = os.path.join(download_directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
            print(f'Deleted {file_path}')
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')
            
# Loop through the desired number of pages
for page_num in range(1, num_pages + 1):
    # Construct the URL for the current page
    page_url = f"{url}?page={page_num}"
    print(f"Scraping {page_url}")
    
    
    # # Call the function to download images from this page
    # download_images(page_url)
    
    # Scroll down until no more content is loaded
    while True:
        #scrolling once code
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        #giving time to load
        time.sleep(1) # wait for content to load
        
        #checking new height of webpage
        new_height = driver.execute_script("return document.body.scrollHeight")
        

        #defining the break condition to stop the execution at the end of the webpage
        if new_height == last_height:
            break
        last_height = new_height         #while loop breaks when the last height of web page will not change 
    
        # Call the function to download images from this page
        download_images(page_url)       
    
        
    
    
    
    