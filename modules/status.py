from .notification import notification

def start():
    notification("Started")

def stop():
    notification("Stopped")

def pause():
    notification("Paused")

def resume():
    notification("Resumed")

def status():
    pass
    # i will implement logging system laterwards which will allow easy debugging 