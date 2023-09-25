import os
import pyautogui as gui
import datetime
import subprocess
from .notification import notification 

import configparser
config = configparser.ConfigParser()
config.read("config.paper")
screenshot_dir = config.get("Default","screenshot_dir")

def screenshot(x):
    fname = screenshot_dir+"/screenshot-"+str(datetime.datetime.now())+".png"
    gui.screenshot(fname)
    path = os.path.abspath(fname)
    notification("Stored at: "+ path+"\nalso copied to clipboard")
    os.system("xclip -selection clipboard "+"'"+path+"'"+" -target image/png")
    if "open" in x:
        subprocess.Popen(['sxiv', path])
    else:
        pass


        