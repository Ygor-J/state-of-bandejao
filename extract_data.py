from bs4 import BeautifulSoup
import bs4
import requests
import sys
import dotenv
import pandas as pd
import os
import json
import pprint

dotenv.load_dotenv()

URL = os.environ['URL']

def get_meal_type(soup: bs4.element.Tag) -> str:
    return soup.find('h2').text.strip()

def get_menu_item_name(soup: bs4.element.Tag) -> str:
    return soup.find('div', class_='menu-item-name').text.strip()

def get_menu_item_details(soup: bs4.element.Tag) -> str:
    description = soup.find('div', class_='menu-item-description').text.strip()
    description_lines = description.split('\n')

    new_description_lines = list()

    for i, line in enumerate(description_lines):
        line_strip = line.strip()
        if line_strip != '':
            new_description_lines.append(line_strip)

    menu_description = list()

    index = 0

    for i, element in enumerate(new_description_lines):
        if "Observa" in element:
            index = i
            break
        else:
            menu_description.append(element)
    

    return (menu_description, new_description_lines[index:])

def extract_data():
    #response = requests.get(URL)
    #if response.status_code != 200:
        # Send to my email telling me something went wrong
        # But for now, just raise exception
    #    raise requests.exceptions.RequestException

    with open('html_web.txt', 'r') as f:
        html_file = f.read()
    
    soup = BeautifulSoup(html_file, 'html.parser')
    
    menus = soup.find_all('div', class_='menu-section')

    data = {'meal_type': list(), 'menu_item_name': [], 'menu_description': [], 'menu_obs': []}

    for menu in menus:
        data['meal_type'].append(get_meal_type(menu))
        data['menu_item_name'].append(get_menu_item_name(menu))
        
        menu_details = get_menu_item_details(menu)
        data['menu_description'].append('|'.join(menu_details[0]))
        data['menu_obs'].append('|'.join(menu_details[1]))

    return data


if __name__ == '__main__':
    pprint.pp(extract_data())