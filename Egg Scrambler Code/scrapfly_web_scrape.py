import httpx
from bs4 import BeautifulSoup

# 1. Find image links on the website
image_links = []
# Scrape the first 4 pages
for page in range(4):
    # url = f"https://web-scraping.dev/products?page={page}"
    url = f"https://www.istockphoto.com/photos/scrambled-eggs"
    response = httpx.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    for image_box in soup.select("div.row.product"):
        result = {
            "link": image_box.select_one("img").attrs["src"],
            "title": image_box.select_one("h3").text,
        }
        # Append each image and title to the result array
        image_links.append(result)

# 2. Download image objects
for image_object in image_links:
    # Create a new .png image file
    with open(f"./images/{image_object['title']}.png", "wb") as file:
        image = httpx.get(image_object["link"])
        # Save the image binary data into the file
        file.write(image.content)
        print(f"Image {image_object['title']} has been scraped") 