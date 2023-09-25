import subprocess
def notification(message):
    subprocess.Popen(['notify-send', message])

