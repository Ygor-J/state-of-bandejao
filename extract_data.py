from bs4 import BeautifulSoup
import bs4
import requests
#import dotenv
import pandas as pd
import os
import logging
import datetime
import pprint
import google.cloud.storage as storage

#dotenv.load_dotenv()

#os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'sa.json'

URL='https://sistemas.prefeitura.unicamp.br/apps/cardapio/index.php'
BUCKET=os.environ['GCP_BUCKET_ID']
PROJECT_ID=os.environ['GCP_PROJECT_ID']
GOOGLE_APPLICATION_CREDENTIALS=os.environ['GOOGLE_APPLICATION_CREDENTIALS']

def get_meal_type(soup: bs4.element.Tag) -> str:
    return soup.find('h2').text.strip()

def get_menu_item_name(soup: bs4.element.Tag) -> str:
    return soup.find('div', class_='menu-item-name').text.strip()

def get_menu_item_details(soup: bs4.element.Tag) -> str:
    description = soup.find('div', class_='menu-item-description').text.strip()
    return description.replace('\r', '').replace('\n', '')

def extract_data():
    response = requests.get(URL)
    if response.status_code != 200:
        raise requests.exceptions.RequestException
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    menus = soup.find_all('div', class_='menu-section')

    data = {'extraction_date': [], 'meal_type': list(), 'menu_item_name': [], 'menu_description': []}

    for menu in menus:
        data['extraction_date'].append(datetime.datetime.now().isoformat())

        data['meal_type'].append(get_meal_type(menu))
        data['menu_item_name'].append(get_menu_item_name(menu))
        
        data['menu_description'].append(get_menu_item_details(menu))

    return data

def send_data_to_bucket(data: dict):
    storage_client = storage.Client(project=PROJECT_ID).from_service_account_json(GOOGLE_APPLICATION_CREDENTIALS)

    date = datetime.datetime.now().strftime('%Y-%m-%d')

    blob_name = f'menu-{date}'
    folder_name = 'state-of-bandejao'

    blob = storage_client.bucket(BUCKET).blob(folder_name + '/' + blob_name)
    blob.upload_from_string(str(data), content_type='text/plain; charset=utf-8')
    logging.info(f"Blob {blob_name} was uploaed to bucket {BUCKET}/{folder_name}/")

def main(message, context):
    try:
        data = extract_data()
    except:
        data = requests.get(URL).text
    send_data_to_bucket(data)
