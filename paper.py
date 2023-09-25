#!/usr/bin/env python
# coding: utf-8

# In[26]:


import configparser
import json 
config = configparser.ConfigParser()
config.read("config.paper")
tr_model_path = config.get('Default','tr_model_path')
username = config.get('Default','username')
asistant_name = config.get('Default','asistant_name')
synames = json.loads(config.get('Default','synames'))
screenshot_dir = config.get('Default','screenshot_dir')
modules_dir = config.get('Default','modules_dir')

import os
import sys
import importlib

from vosk import Model, KaldiRecognizer
import queue
import sounddevice as sd
import signal


from context_recognition.predict import classify
notification = importlib.import_module(f'{modules_dir}.notification').notification

import warnings
warnings.filterwarnings("ignore")


# In[15]:



def actions(term):
    # Loop through the commands dictionary and try to find a matching key
    for key, command_func in commands.items():
        if key in term:
            command_func(term)
            break  # Stop searching after the first match

            

# dynamic_module_list


commands = {}

module_files = [f for f in os.listdir(modules_dir) if f.endswith('.py')]

# Import modules and add their functions to the commands dictionary
for module_file in module_files:
    module_name = os.path.splitext(module_file)[0]
    module_path = f'{modules_dir}.{module_name}'
    module = importlib.import_module(module_path)

    
    # each module has a function with the same name as the module (e.g., screenshot.screenshot)
    if hasattr(module, module_name):
        commands[module_name] = getattr(module, module_name)


# In[ ]:



device_info = sd.query_devices(sd.default.device[0], 'input')
samplerate = int(device_info['default_samplerate'])

q = queue.Queue()

running = True


def signal_handler(signal, frame):
    global running
    running = False

signal.signal(signal.SIGINT, signal_handler)



def recordCallback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))
    

model = Model(tr_model_path)
recognizer = KaldiRecognizer(model, samplerate)
recognizer.SetWords(False)

try:
    with sd.RawInputStream(dtype='int16',
                           channels=1,

                           callback=recordCallback):
        while running:
            data = q.get()
            if recognizer.AcceptWaveform(data):
                recognizerResult = recognizer.Result()
                resultDict = json.loads(recognizerResult)
                recognized_text = resultDict.get("text", "")

                if recognized_text:
                    print(recognizerResult)
                    
                    for asname in synames:    
                        if asname in recognized_text:
                            recognized_text = recognized_text.replace(asname,"")
                            notification(username+ ": " + recognized_text)
                            action = classify(recognized_text.lower())  
                            try:
                                print(action)
                                commands[action](recognized_text.lower())
                            except Exception as e:
                                notification(str(e))
                                print("Error:", str(e))
                else:
                    print("No input sound")


except KeyboardInterrupt:
    print('Finished Recording')
except Exception as e:
    print(str(e))


# In[ ]:




