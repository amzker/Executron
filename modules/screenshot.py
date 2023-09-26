import configparser
config = configparser.ConfigParser()
config.read("config.paper")
screenshot_dir = config.get("Default","screenshot_dir")

import os
import datetime
import subprocess
from .notification import notification  
from PIL import ImageGrab  

import platform



def screenshot(x):
    try:
        screenshot_image = ImageGrab.grab()
        current_time = datetime.datetime.now()
        file_name = f"screenshot-{current_time}.png"
        full_path = os.path.join(screenshot_dir, file_name)
        screenshot_image.save(full_path)
        notification(f"Screenshot saved at: {full_path}\nImage copied to clipboard")

        if "open" in x:
            # Open the image using the default image viewer
            if platform.system() == "Linux":
                # For Linux
                subprocess.Popen(['xdg-open', full_path])
            elif platform.system() == "Darwin":
                # For macOS
                subprocess.Popen(['open', full_path])
            elif platform.system() == "Windows":
                # For Windows (Note: Image preview might vary)
                subprocess.Popen(['start', full_path], shell=True)
        return full_path
    except Exception as e:
        notification(f"Error capturing or opening screenshot: {e}")

