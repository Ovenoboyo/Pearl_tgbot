import subprocess


def commit_file(filename ,userid):
    subprocess.Popen(["git config --global user.name \"Project-PearlOS\" "], shell=True)
    subprocess.Popen(["git config --global user.email \"projectpearl69@gmail.com\""], shell=True)
    proc = subprocess.Popen([". /app/Bot/commit_and_push.sh"], shell=True)
    proc.wait()
