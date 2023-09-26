import threading
import time
import tkinter as tk
from tkinter import ttk, filedialog
import pyperclip
from PIL import Image, ImageTk
import json
from .notification import notification
import platform
import subprocess
import os
import datetime


clipboard_history = []

# Create global listbox variables and initialize them as None
listbox = None
image_listbox = None
monitoring_clipboard = False
global listbox, image_listbox, monitoring_clipboard



def add_imagepath_to_clipboard_history(filePath):
    image_entry = "image:" + filePath
    if image_entry not in clipboard_history:
        clipboard_history.append(image_entry)


def add_text_to_clipboard_history(text):
    if text not in clipboard_history:
        clipboard_history.append(text)
        
def copy_text_to_clipboard(text):
    pyperclip.copy(text)
    add_text_to_clipboard_history(text)

def copy_text_from_clipboard(placeholder):
    data = pyperclip.paste()
    return data
    
def copy_image_to_clipboard(image_path):
    # For Linux
    if platform.system() == "Linux":
        subprocess.run(['xclip', '-selection', 'clipboard', '-t', 'image/png', image_path])
    # For Windows
    # i think this is wrong code for windows , i dont have windows so cant test it 
    elif platform.system() == "Windows":
        import win32clipboard
        from io import BytesIO
        img_io = BytesIO()
        image_path.save(img_io, 'PNG')
        img_data = img_io.getvalue()
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, img_data)
        win32clipboard.CloseClipboard()
    
    add_imagepath_to_clipboard_history(image_path)

        

def save_image_from_clipboard_and_copy_path():
    fname = "screenshot-" + str(datetime.datetime.now()) + ".png"
    filePath = os.path.join(screenshot_dir, fname)
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
    add_imagepath_to_clipboard_history(filePath)
    return filePath

def start_clipboard_monitoring():
    def monitor_clipboard():

        previous_clipboard = pyperclip.paste()
        while monitoring_clipboard:
            notification("clipboard monitoring is started")
            current_clipboard = pyperclip.paste()
            if current_clipboard != previous_clipboard:
                clipboard_history.append(current_clipboard)
            previous_clipboard = current_clipboard
            time.sleep(1)  # Check clipboard every 1 second

    # Create a new thread for clipboard monitoring
    clipboard_monitor_thread = threading.Thread(target=monitor_clipboard)
    clipboard_monitor_thread.start()

    
def stop_clipboard_monitoring():
    monitoring_clipboard = False
    notification("clipboard monitoring is stopped")
    
def save_history_to_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
    if file_path:
        with open(file_path, "w") as file:
            json.dump(clipboard_history, file)

def load_history_from_file():
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
    if file_path:
        with open(file_path, "r") as file:
            loaded_history = json.load(file)
            clipboard_history.extend(loaded_history)
            update_tabs()

def on_select(event):
    selected_index = listbox.curselection()
    if selected_index and listbox is not None:
        selected_item = listbox.get(selected_index[0])
        if selected_item.startswith("image:"):
            image = Image.open(selected_item)
            image.show()
        else:
            pyperclip.copy(selected_item)

    selected_index_image = image_listbox.curselection()
    if selected_index_image and image_listbox is not None:
        selected_item_image = image_listbox.get(selected_index_image[0])
        if selected_item_image.startswith("image:"):
            image = Image.open(selected_item_image.replace("image:", ""))
            image.show()

def update_tabs():
    global listbox, image_listbox
    if listbox is not None:
        listbox.delete(0, tk.END)
    if image_listbox is not None:
        image_listbox.delete(0, tk.END)

    for item in clipboard_history:
        if item.startswith("image:"):
            if image_listbox is not None:
                image_listbox.insert(tk.END, item)
        else:
            if listbox is not None:
                listbox.insert(tk.END, item)

def display_clipboard_history():
    root = tk.Tk()
    root.title("Clipboard History")

    style = ttk.Style()
    style.configure("TNotebook", background="white")
    style.configure("TFrame", background="white")
    style.configure("TButton", background="lightgrey", padding=5)
    style.configure("TLabel", background="white", padding=5)

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    text_frame = tk.Frame(notebook)
    global listbox
    listbox = tk.Listbox(text_frame, bg="lightgrey", fg="black", selectbackground="darkblue", selectforeground="white")
    listbox.bind("<Double-1>", on_select)
    listbox.pack(fill="both", expand=True)
    text_frame.pack(fill="both", expand=True)
    notebook.add(text_frame, text="Text")

    image_frame = tk.Frame(notebook)
    global image_listbox
    image_listbox = tk.Listbox(image_frame, bg="lightgrey", fg="black", selectbackground="darkblue", selectforeground="white")
    image_listbox.bind("<Double-1>", on_select)
    image_listbox.pack(fill="both", expand=True)
    image_frame.pack(fill="both", expand=True)
    notebook.add(image_frame, text="Images")

    menu_frame = tk.Frame(root, bg="lightgrey")
    menu_frame.pack(fill="x")
    
    save_button = tk.Button(menu_frame, text="Save History", command=save_history_to_file, bg="lightblue")
    save_button.pack(side="left", padx=10, pady=5)

    load_button = tk.Button(menu_frame, text="Load History", command=load_history_from_file, bg="lightblue")
    load_button.pack(side="left", padx=10, pady=5)
    
    def delete_selected():
        selected_indices = listbox.curselection()
        for index in selected_indices:
            listbox.delete(index)
            clipboard_history.pop(index)
            
        selected_indices_image = image_listbox.curselection()
        for index in selected_indices_image:
            image_listbox.delete(index)
            clipboard_history.pop(index)
    
    delete_button = tk.Button(menu_frame, text="Delete", command=delete_selected, bg="lightcoral")
    delete_button.pack(side="left", padx=10, pady=5)
    
    def refresh_list():
        update_tabs()
    
    refresh_button = tk.Button(menu_frame, text="Refresh", command=refresh_list, bg="lightgreen")
    refresh_button.pack(side="left", padx=10, pady=5)

    update_tabs()

    root.mainloop()
