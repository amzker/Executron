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

def copy_image_to_clipboard(image):
    # For Linux
    if platform.system() == "Linux":
        image_path = "screenshot_temp.png"
        image.save(image_path)
        subprocess.run(['xclip', '-selection', 'clipboard', '-t', 'image/png', image_path])
        os.remove(image_path)
    # For Windows
    elif platform.system() == "Windows":
        import win32clipboard
        from io import BytesIO
        img_io = BytesIO()
        image.save(img_io, 'PNG')
        img_data = img_io.getvalue()
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, img_data)
        win32clipboard.CloseClipboard()

def screenshot(x):
    try:
        screenshot_image = ImageGrab.grab()
        current_time = datetime.datetime.now()
        file_name = f"screenshot-{current_time}.png"
        full_path = os.path.join(screenshot_dir, file_name)
        screenshot_image.save(full_path)
        copy_image_to_clipboard(screenshot_image)
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
    except Exception as e:
        notification(f"Error capturing or opening screenshot: {e}")

