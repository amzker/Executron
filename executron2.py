import os
import sys
import importlib
import argparse
import json
import queue
import sounddevice as sd
import signal
from vosk import Model, KaldiRecognizer
from context_recognition.predict import classify
import configparser

config = configparser.ConfigParser()
config.read("config.executron")
tr_model_path = config.get('Default', 'tr_model_path')
username = config.get('Default', 'username')
asistant_name = config.get('Default', 'assistant_name')
synames = json.loads(config.get('Default', 'synames'))
screenshot_dir = config.get('Default', 'screenshot_dir')
modules_dir = config.get('Default', 'modules_dir')
notification = importlib.import_module(f'{modules_dir}.notification').notification

def signal_handler(signal, frame):
    global running
    running = False

def record_callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

def process_voice_input(q, model, synames, modules_dir, username):
    model = Model(model)
    recognizer = KaldiRecognizer(model, samplerate)
    recognizer.SetWords(False)

    with sd.RawInputStream(dtype='int16', channels=1, callback=record_callback):
        while running:
            data = q.get()
            if recognizer.AcceptWaveform(data):
                recognizer_result = recognizer.Result()
                result_dict = json.loads(recognizer_result)
                recognized_text = result_dict.get("text", "")

                if recognized_text:
                    print(recognizer_result)

                    for asname in synames:
                        if asname in recognized_text:
                            recognized_text = recognized_text.replace(asname, "")
                            notification(username + ": " + recognized_text)
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
                                        previous_output = command_func(previous_output)
                                    else:
                                        previous_output = command_func()

                                final_output = previous_output

                            except Exception as e:
                                notification(str(e))
                                print("Error:", str(e))

                else:
                    print("No input sound")

def main():
    global running
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", action="store_true", help="Use text input instead of voice")
    args = parser.parse_args()

    device_info = sd.query_devices(sd.default.device[0], 'input')
    samplerate = int(device_info['default_samplerate'])

    q = queue.Queue()
    running = True

    if args.text:
        while True:
            try:
                # Use text input
                text_input = input("Enter your text command: ")
                actions = classify(text_input.lower())
                print(actions)
                #actions_to_execute = action.split(',')
                previous_output = None

                for action in actions:
                    module_name, func_name = action.split('.')
                    module_path = f'{modules_dir}.{module_name}'
                    module = importlib.import_module(module_path)
                    command_func = getattr(module, func_name)

                    if previous_output:
                        previous_output = command_func(previous_output)
                    else:
                        previous_output = command_func()

            except Exception as e:
                notification(str(e))
                print("Error:", str(e))
    else:
        process_voice_input(q, tr_model_path, synames, modules_dir, username)

if __name__ == "__main__":
    main()
