import time
import requests
import requests_random_user_agent
from bs4 import BeautifulSoup as soup
from tqdm import tqdm
from pipeline import *
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import json
import re
session = requests.session()
# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')  # Replace with your MongoDB URI if necessary
db = client['OLX_5156']  # Replace with your database name
collection_prov = db['OLX_5156_property_provinsi']  # Replace with your collection name
collection_kabkot = db['OLX_5156_property_kabkot']  # Replace with your collection name
collection_kec = db['OLX_5156_property_kecamatan']  # Replace with your collection name
collection_prop = db['OLX_5156_property']  # Replace with your collection name
def updateProvinsi() -> list:
    """Update Provisi List"""

    # Setup Selenium WebDriver
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run headless browser
    driver = webdriver.Chrome()

    # Fetch the URL
    url = "https://www.olx.co.id/api/locations/popular?limit=40&type=STATE"
    driver.get(url)

    # Extract the HTML content
    html_content = driver.page_source

    # Close the browser
    driver.quit()

    # Extract JSON string from HTML
    # The JSON is contained within <pre> tags, so we use a regex to extract it
    json_match = re.search(r'<pre>(.*?)</pre>', html_content, re.DOTALL)
    if json_match:
        json_string = json_match.group(1).strip()
        
        # Convert JSON string to Python dictionary
        try:
            data = json.loads(json_string)
            if 'data' in data:
                collection_prov.insert_many(data['data'])
            return [{"province":p['name'], "id":p['id']} for p in data['data']]
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
    else:
        print("No JSON data found in the HTML.")

def updateKabkot(prov_id:str) -> list:
    """Update Kabupaten/Kota List"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run headless browser
    driver = webdriver.Chrome()
    try:
        url = f"https://www.olx.co.id/api/locations/popular?limit=40&type=CITY&parent={prov_id}"
        # Fetch the URL
        driver.get(url)

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
                if 'data' in data:
                    collection_kabkot.insert_many(data['data'])
                    return [{"kabupaten":p['name'], "id":p['id']} for p in data['data']]
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
        else:
            print("No JSON data found in the HTML.")
    except Exception as e:
            print(e)

def updateKecamatan(parent_kab:str, parent_id:str, trial:int=0) -> list:
    """Update Kecamatan List""" 
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run headless browser
    driver = webdriver.Chrome()
    try:
        url = f"https://www.olx.co.id/{parent_kab.lower().replace(' ','-')}_g{parent_id}"
        # Fetch the URL
        driver.get(url)
        time.sleep(10)

        # Extract the HTML content
        html_content = driver.page_source

        # Close the browser
        driver.quit()
        html = soup(html_content, 'html.parser')
        # print(html)

        if html:
            # Convert JSON string to Python dictionary
            try:
                kecList = html.find('ul',{'data-aut-id':'ulLevel_3'})
                # if kecList:
                #     kecList = kecList.findAll('a')
                # elif trial<20: #20 times of trial
                #     trial += 1
                #     return updateKecamatan(parent_kab, parent_id, trial)
                kecList = [kec.get('href') for kec in kecList]
                kecList = [prepKec(kec) for kec in kecList]
                data    = [{'id':int(kec[1][1:]), 'name':kec[0], 'type':"DISTRICT", 'parentId':parent_id} for kec in kecList]
                collection_kec.insert_many(data)
                # print(data)
                # insert_mongo(data=data, collection_name=kecamatan_collection, replace=False) # insert into db
                
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
        else:
            print("No JSON data found in the HTML.")
    except Exception as e:
            print(e)
        
def prepKec(url):
    """Extract Kecamatan Name and ID"""
    target_text = url.split('/')[1]
    kecamatan, id = target_text.replace('-',' ').split('_')
    return [kecamatan,id]

def main():
    """Updating Areas"""
    #Update Provinsi List
    prov_list = updateProvinsi()
    print(f"{len(prov_list)} provinces found!")
    
    #Update Kabupaten/Kota List
    # replace_collection(kabkot_collection) #empty collection
    kabkot_list = list()
    tmp = updateKabkot("2000007")
    kabkot_list.extend(tmp)
    print(f"{len(kabkot_list)} kabkots found!")
    
    #Update Kecamatan List
    # replace_collection(kecamatan_collection) #empty collection
    # for kab in tqdm(kabkot_list):
    #     # print(kab)
    #     updateKecamatan(kab['kabupaten'],"2000007")
    # print(f"{count_mongo(kecamatan_collection)} kecamatans found!")

if __name__ == "__main__":
    start_time = time.time()
    main()
    client.close()
    session.close()
    print("%s minutes elapsed time" % round((time.time() - start_time)/60, 2))



"""Script by: Wahyu Calvin Frans M."""