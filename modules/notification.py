import subprocess

def notification(message):
    try:
        import platform

        if platform.system() == "Windows":
            from plyer import notification as plyer_notification
            plyer_notification.notify(title='Notification', message=message)
        else:
            subprocess.Popen(['notify-send', message])
    except ImportError:
        subprocess.Popen(['notify-send', message])
