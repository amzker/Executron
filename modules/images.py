import os
import datetime
import subprocess
from .notification import notification
from PIL import ImageGrab
import platform
import configparser
import importlib

config = configparser.ConfigParser()
config.read("config.executron")
screenshot_dir = config.get("Default", "screenshot_dir")


def capture_screenshot():
    try:
        screenshot_image = ImageGrab.grab()
        current_time = datetime.datetime.now()
        file_name = f"screenshot-{current_time}.png"
        full_path = os.path.join(screenshot_dir, file_name)
        screenshot_image.save(full_path)
        notification(f"Screenshot saved at: {full_path}\nImage copied to clipboard")
        return full_path
    except Exception as e:
        notification(f"Error capturing screenshot: {e}")




        
        
#reason for having open_image into image module is to reduce complexity see
#because see right now i dont think so making one open.py module and making ai to decide to give open.application(imageapplication, image) is not logical but i can do like image.open(image_path), and that image_path we can get from other function output , such as from clipboard.py or even from image.py
# in short my current model plan will only be able to know order of execution but wont be able to give input by itself , it will
#rely on other function output and after my idea works i will extend it to inputs also , and this total modular code wil also be 
# useful that time i wont need to make any drastic changes into the code

def open_image(image_path):
    try:
        if platform.system() == "Linux":
            # For Linux
            subprocess.Popen(['xdg-open', image_path])
        elif platform.system() == "Darwin":
            # For macOS
            subprocess.Popen(['open', image_path])
        elif platform.system() == "Windows":
            # For Windows (Note: Image preview might vary)
            subprocess.Popen(['start', image_path], shell=True)
    except Exception as e:
        notification(f"Error opening image: {e}")


def execute(execution_context):
    action = execution_context["action"]
    if action == "capture_screenshot":
        return capture_screenshot()
    elif action == "open_image":
        image_path = execution_context.get("image_path")
        if image_path:
            open_image(image_path)
        else:
            notification("Image path is missing.")
    else:
        notification(f"Unknown action: {action}")

# Executron function to execute actions based on the provided execution context.
# right now just function i will implement laterwards