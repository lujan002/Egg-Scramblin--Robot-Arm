import hashlib, io, requests
from bs4 import BeautifulSoup  
from pathlib import Path
from PIL import Image


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
        
def getdata(url):  
    r = requests.get(url)  
    return r.text  
    
htmldata = getdata("https://www.istockphoto.com/search/2/image-film?phrase=bowl%20of%20beaten%20eggs")  
soup = BeautifulSoup(htmldata, 'html.parser')  
for item in soup.find_all('img'): 
    image_url = item['src']
    print(image_url)
    get_and_save_image_to_file(
            image_url, output_dir=Path("Users/20Jan/Robot Arm Copy/Egg Scrambler Code/Scrambled Egg Dataset")
        )
    