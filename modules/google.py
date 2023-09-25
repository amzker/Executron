import os
import webbrowser
import requests
import urllib.parse as parser
from urllib.request import urlopen
import datetime
import tkinter
from .notification import notification 


import configparser
config = configparser.ConfigParser()
config.read("config.paper")

google_qurl = config.get("Default","google_qurl")
gimage_reverse_url = config.get("Default", "gimage_reverse_url")
screenshot_dir = config.get("Default","screenshot_dir") 

def google(term):
    if "clipboard" in term:
        pass
    else:
        term = term.replace("google", "")
        search = parser.quote(term)
        webbrowser.open(google_qurl+search)

def save_image_from_clipboard():
    fname = screenshot_dir+"/screenshot-"+str(datetime.datetime.now())+".png"
    filePath = os.path.abspath(fname)
    image = tkinter.Tk().clipboard_get(type='image/png') 
 
    #_______________________________________________________________
    #https://stackoverflow.com/a/59862864 explaination is there.:))))
    b = bytearray()
    h = ''
    for c in image:
        if c == ' ':
            try:
                b.append(int(h, 0))
            except Exception as e:
                print('Exception:{}'.format(e))
            h = ''
        else:
            h += c

    image = b
    #______________________________________________________________
    with open(filePath, 'wb') as f:
        f.write(image)
        f.close()
    return filePath
        
def searchimg(filePath):
    searchUrl = gimage_reverse_url
    multipart = {'encoded_image': (filePath, open(filePath, 'rb')), 'image_content': ''}
    response = requests.post(searchUrl, files=multipart, allow_redirects=False)
    text = str(response.content)
    text = text.split("URL=", 1)[1].replace("/></head></html>\'","")
    webbrowser.open(text)
    notification("Check browser")
