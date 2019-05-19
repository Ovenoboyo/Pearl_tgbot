#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib.request as urllib2
import os
import re
import sqlite3
import logging
import telegram
import psycopg2

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.

TOKEN = os.getenv("TOKEN")
DATABASE_URL = os.environ['DATABASE_URL']

def error(bot, update):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('ono')

def teston(bot, update):
    global debug
    debug = 1
    update.message.reply_text('debug on')

def testoff(bot, update):
    global debug
    debug = 0
    update.message.reply_text('debug off')

conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()
#cur.execute('''CREATE TABLE LIST
#        (NAME           TEXT    NOT NULL,
#         DATE           INT     NOT NULL);''')
#conn.commit()
conn.close()
    
toggle = 0
debug = 0

filenamelist = []
urllist = []
changeloglist = []

def download(url, filename):
    ver = urllib2.urlopen(url)
    html = ver.read()

    update = html.decode('utf-8')
    ver.close()
    if os.path.isfile(filename):
        os.remove(filename)
    f = open(filename ,"w+")
    f.write(update)
    f.close()

def getver(filename):
    if os.path.isfile(filename):    
        lookup = 'version'
        ver = 0

        with open(filename) as myFile:
            for num, line in enumerate(myFile, 1):
                if lookup in line:
                    version = re.findall("\d+\.\d+", line)
                    ver = version
        return ver

def getLists():
    global filenamelist, urllist, changeloglist, debug
    #if debug == 0:
    download("https://raw.githubusercontent.com/PearlOS/OTA/master/list.txt", "array.txt")
    f=open('array.txt', encoding='utf-8')
    lines=f.readlines()
    filenames = lines[0].replace("[", "").replace("]", "").split(", ")
    urls = lines[1].replace("[","").replace("]", "").split(", ")
    changelogs = lines[2].replace("[","").replace("]", "").split(", ")
    for i in range(0, len(urls) ):
        filenamelist.insert(i, filenames[i])
        urllist.insert(i, urls[i])
        changeloglist.insert(i, changelogs[i])

def getlink (filename):
    if os.path.isfile(filename):
        lookup = 'url'
        url = "null"

        with open(filename) as myFile:
            for num, line in enumerate(myFile, 1):
                if lookup in line:
                    link = line.split(": ")
                    link = link[1]
                    link = link.replace("\"","");
                    link = link.replace(",","");
                    url = link
        myFile.close()            
        return url
        
def getxda (filename):
    if os.path.isfile(filename):    
        lookup = 'xda'
        url = "null"

        with open(filename) as myFile:
            for num, line in enumerate(myFile, 1):
                if lookup in line:
                    link = line.split(": ")
                    link = link[1]
                    link = link.replace("\"","");
                    link = link.replace(",","");
                    url = link
        myFile.close()            
        return url
       
def getdate (filename):
    global toggle
    if os.path.isfile(filename):    
        lookup = 'datetime'
        datetime = 0

        with open(filename) as myFile:
            for num, line in enumerate(myFile, 1):
                if lookup in line:
                    date = re.findall(r'\b\d+\b', line)
                    datetime = int(date[0])

        myFile.close()            
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cursor = conn.cursor()
        cursor.execute("SELECT DATE from LIST WHERE NAME LIKE (%s)", (filename,))
        entry = cursor.fetchone()
        if entry is None:
            print ("here")
            cursor.execute('INSERT INTO LIST (NAME,DATE) VALUES (%s, %s)', (filename, datetime))
            toggle = 1
            
        else:
            if entry[0] < datetime:
                cursor.execute("UPDATE LIST set DATE = (%s) where NAME = (%s)", (datetime, filename))
                toggle = 1
                
            else:
                toggle = 0
            
        
        conn.commit()
        conn.close()
        return datetime
        
def getmaintainer(filename):
    if os.path.isfile(filename):    
        lookup = 'maintainer'
        maintainer = 0

        with open(filename) as myFile:
            for num, line in enumerate(myFile, 1):
                if lookup in line:
                    name = line.split(": ")
                    name = name[1]
                    name = name.replace("\"","");
                    maintainer = name.replace(",","");
        return maintainer

def run(updater):
    PORT = int(os.environ.get("PORT", "8443"))
    HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TOKEN)
    updater.bot.set_webhook("https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, TOKEN))

def main():
    """Start the bot."""
    updater = Updater(TOKEN)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("update", update))
    dp.add_handler(CommandHandler("testoff", testoff))
    dp.add_handler(CommandHandler("teston", teston))

    dp.add_error_handler(error)

    run(updater)

def update(bot, update): 
    getLists()
    for i in range(len(filenamelist)):
        url = urllist[i]
        filename = filenamelist[i]
        changelog = changeloglist[i]
        download (url, filename)
        version = getver(filename)
        link = getlink(filename)
        xda = getxda(filename)
        date = getdate(filename)
        maintainer = getmaintainer(filename)
        name = filename.split(".")
        name = name[0]
        kek = "📢*New Pearl Update*\n\n📱Device: *"+str(name)+"*\n🙎‍♂Maintainer: *"+str(maintainer)+"*\nLinks ⤵️\n\n⬇️ ROM : "+"[Here]("+str(link)+")"+"\n\n📜 XDA : "+"[Here]("+str(xda)+")"+"\n\n📕Changelog: "+"[Here]("+str(changelog)+")"
        if debug == 1:
            bot.sendMessage(chat_id='@testchannel1312324', text=str(kek), parse_mode=telegram.ParseMode.MARKDOWN)
            bot.sendSticker(chat_id='@testchannel1312324', sticker='CAADBQADmwADiYk3GUJzG4UKA2TLAg')
        elif (debug == 0 and toggle == 1) :
            bot.sendMessage(chat_id='@Project_Pearl', text=str(kek), parse_mode=telegram.ParseMode.MARKDOWN)
            bot.sendSticker(chat_id='@Project_Pearl', sticker='CAADBQADmwADiYk3GUJzG4UKA2TLAg')
if __name__ == '__main__':
    main()
