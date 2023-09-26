from .notification import notification

# i will implement these functions laterwards , right now just making structure
def pause_module(module_name):
    pass

def resume_module(module_name):
    pass

def restart_assistant():
    pass

def mute_assistant():
    pass

def unmute_assistant():
    pass

def sleep_assistant():
    pass

def wake_assistant():
    pass

def reset_assistant():
    pass

def shutdown_assistant():
    global running
    running = False
    notification("Stopping the voice assistant")


