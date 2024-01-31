import subprocess

def notify_windows(message):
    try:
        from plyer import notification as plyer_notification
        plyer_notification.notify(title='Notification', message=message)
    except ImportError:
        subprocess.Popen(['toast.exe', '-t', 'Notification', '-m', message])

def notify_linux(message):
    subprocess.Popen(['notify-send', message])

def notification(message):
    try:
        import platform

        if platform.system() == "Windows":
            notify_windows(message)
        else:
            notify_linux(message)
    except Exception as e:
        print(f"Error displaying notification: {e}")

# Usage: notification("Your notification message here")
