from .notification import notification
def stop(x):
    global running
    running = False
    notification("Stopping the voice assistant")
