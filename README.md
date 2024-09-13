# OLXProperty Scraper
This repo contains the code for scraping property/realestate data from <b>OLX</b> (https://www.olx.co.id) using Python with Requests library. The data scraping method is done by utilizing the APIs available on web pages in Kecamatan level.

## Setup
1) pip install -r requirements.txt
2) Create a new MongoDB database named <b>OLX</b>
3) Setup .env file configurations

## Run
1) RUN <code>python update_area.py</code> <small>(*Optional if the current area already in the DB)</small>
2) RUN <code>python olx_property.py</code>
