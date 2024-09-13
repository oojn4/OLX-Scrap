import time
import requests
import requests_random_user_agent
from datetime import datetime
from random import  randint
from tqdm import tqdm
from pipeline import *
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import json
import re
session = requests.session()
runtime = datetime.now().strftime("%Y-%m-%d")
client = MongoClient('mongodb://localhost:27017/')  # Replace with your MongoDB URI if necessary
db = client['OLX_5156']  # Replace with your database name
collection_prov = db['OLX_5156_property_provinsi']  # Replace with your collection name
collection_kabkot = db['OLX_5156_property_kabkot']  # Replace with your collection name
collection_kec = db['OLX_5156_property_kecamatan']  # Replace with your collection name
collection_prop = db['OLX_5156_property']  # Replace with your collection name
def scrape(loc_id:str, page:int=0) -> None:
    """Scraping Data in a Location"""
    url = f"https://www.olx.co.id/api/relevance/v4/search?category=5156&facet_limit=100&location={loc_id}&location_facet_limit=20&platform=web-desktop&relaxedFilters=true&type=rumah&user=18b4b{randint(111, 999)}e13x7e09e136&page={page}"
    # 5158 dijual rumah dan apartemen
    # 5160 disewakan rumah dan apartemen
    # 5154 dijual bangunan komersil
    # 5156 disewakan bangunan komersil
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run headless browser
    driver = webdriver.Chrome()
        # Fetch the URL
    driver.get(url)
    time.sleep(5)

        # Extract the HTML content
    html_content = driver.page_source

        # Close the browser
    driver.quit()
    json_match = re.search(r'<pre>(.*?)</pre>', html_content, re.DOTALL)
    if json_match:
        json_string = json_match.group(1).strip()
        
        # Convert JSON string to Python dictionary
        try:
            data = json.loads(json_string)
            if len(data)>0:
                collection_prop.insert_many(data['data'])
                try:
                    data['metadata']['next_page_url'] #checking if next page
                    page += 1
                    scrape(loc_id,page) #next page
                except:
                    pass
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
    else:
        print("No JSON data found in the HTML.")

def main():
    """Main function"""
    #Get Kecamatan List from DB
    kec_list = list(collection_kabkot.find())
    print(kec_list)
    print(f'Found {len(kec_list)} kecamatans to scrape!')

    #Scrape The Data
    for kec in tqdm(kec_list):
        scrape(kec['id'])
        time.sleep(1)
    

if __name__ == "__main__":
    start_time = time.time()
    main()
    client.close()
    session.close()
    print("%s minutes elapsed time" % round((time.time() - start_time)/60, 2))



"""Script by: Wahyu Calvin Frans M."""