import os


class Constants(object):
    TOKEN = os.getenv("TOKEN")
    DATABASE_URL = os.environ['DATABASE_URL']
    PATH = "/app/Bot/"
    OTA_PATH = PATH+'OTA/'
    USERNAME = os.environ['git_username']
    PASSWORD = os.environ['git_password']
