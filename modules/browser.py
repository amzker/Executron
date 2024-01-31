import webbrowser
import requests
import urllib.parse as parser
import configparser
from .notification import notification

config = configparser.ConfigParser()
config.read("config.paper")

google_qurl = config.get("Default", "google_qurl")
gimage_reverse_url = config.get("Default", "gimage_reverse_url")

def google_search(term):
    term = term.replace("google", "")
    search = parser.quote(term)
    webbrowser.open(google_qurl + search)

import time

def search_image(filePath):
    print(filePath)
    searchUrl = gimage_reverse_url
    multipart = {'encoded_image': (filePath, open(filePath, 'rb')), 'image_content': ''}
    response = requests.post(searchUrl, files=multipart, allow_redirects=True)
    print(response.status_code)
    #print(response.content)
    if response.status_code == 502:
        # Handle the 502 server error gracefully
        print("Received a 502 (Server Error). Will retry in 30 seconds.")
        time.sleep(30)
        search_image(filePath)  # Retry the request
    elif b"url=" in response.content:
        # Handle success case
        text = response.content.decode('utf-8')
        print(text)
        text = text.split("URL=", 1)[1].replace("/></head></html>\'", "")
        webbrowser.open(text)
        notification("Check the browser")
    else:
        # Handle other cases or notify the user
        notification("Failed to find the image URL in the response")
