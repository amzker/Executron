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
                                actions_to_execute = action.split(',')
                                previous_output = None

                                for action in actions_to_execute:
                                    module_name, func_name = action.split('.')
                                    module_path = f'{modules_dir}.{module_name}'
                                    module = importlib.import_module(module_path)
                                    command_func = getattr(module, func_name)

                                    if previous_output:
                                        # Use the previous function's output
                                        previous_output = command_func(previous_output)
                                    else:
                                        # Execute the action without previous output
                                        previous_output = command_func()

                                # Store or use the final output as needed
                                final_output = previous_output

                            except Exception as e:
                                notification(str(e))
                                print("Error:", str(e))

                else:
                    print("No input sound")


except KeyboardInterrupt:
    print('Finished Recording')
except Exception as e:
    print(str(e))






