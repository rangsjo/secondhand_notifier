# This file has been updated to use the blocket-api.se API instead of web scraping.

import requests

API_URL = "https://api.blocket-api.se/v1/"

def get_data_from_blocket():
    response = requests.get(API_URL + "data")
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Failed to fetch data from Blocket")

if __name__ == '__main__':
    data = get_data_from_blocket()
    print(data)