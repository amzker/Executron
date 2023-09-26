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

def search_image(filePath):
    search_url = gimage_reverse_url
    multipart = {'encoded_image': (filePath, open(filePath, 'rb')), 'image_content': ''}
    response = requests.post(search_url, files=multipart, allow_redirects=False)
    text = str(response.content)
    text = text.split("URL=", 1)[1].replace("/></head></html>\'", "")
    webbrowser.open(text)
    notification("Check browser")
