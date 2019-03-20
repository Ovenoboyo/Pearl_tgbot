#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib.request as urllib2
import os
import re
import sqlite3
import logging
import telegram

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


if not os.path.exists('list.db'):
    conn = sqlite3.connect('list.db')
    conn.execute('''CREATE TABLE LIST
            (NAME           TEXT    NOT NULL,
             DATE           INT     NOT NULL);''')
    conn.close()
    
toggle = 0

filenamelist = ["Mido.txt"]     
urllist = ["https://raw.githubusercontent.com/PearlOS/OTA/master/mido.json"]
changeloglist = ["https://github.com/PearlOS/OTA/blob/master/mido.md"]

def download(url, filename):
    ver = urllib2.urlopen(url)
    html = ver.read()

    update = html.decode("utf8")
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
                    
        conn = sqlite3.connect('list.db')
        cursor = conn.execute("SELECT DATE from LIST WHERE (NAME=?)", (filename,))
        entry = cursor.fetchone()
        if entry is None:
            print ("here")
            cursor.execute('INSERT INTO LIST (NAME,DATE) VALUES (?,?)', (filename, datetime))
            toggle = 1
            
        else:
            if entry[0] < datetime:
                cursor.execute("UPDATE LIST set DATE = (?) where NAME = (?)", (datetime, filename))
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

def main():
    """Start the bot."""
    updater = Updater("TOKEN", use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("update", update))

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()

def update(update, context): 
    for i in range(len(urllist)):
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
        kek = "📢*New Pearl Update*\n\n📱Device: *"+str(name)+"*\n🙎‍♂Maintainer: "+str(maintainer)+"\nLinks ⤵️\n\n⬇️ ROM : [Here]("+str(link)+")\n\n📜 XDA : [Here]("+str(xda)+")\n\nChangelog: "+"[Here]("+str(changelog)+")" 
        if toggle == 1 :
            context.bot.sendMessage(chat_id='@testchannel1312324', text=str(kek), parse_mode=telegram.ParseMode.MARKDOWN)

if __name__ == '__main__':
    main()          