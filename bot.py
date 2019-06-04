#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib.request as urllib2
import os
import stat
import re
import sqlite3
import logging
import telegram
import psycopg2
import subprocess
import json
import array 

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
exceptionDetails = False

filenamelist = []
urllist = []
changeloglist = []

def downloadFile(url, filename):
    ver = urllib2.urlopen(url)
    html = ver.read()

    update = html.decode('utf-8')
    ver.close()
    if os.path.isfile(filename):
        os.remove(filename)
    f = open(filename ,"w+")
    f.write(update)
    f.close()

def getLists():
    global filenamelist, urllist, changeloglist, debug

    os.chmod("./files.sh", 0o755)
    proc = subprocess.Popen([". /app/files.sh"], shell = True)
    proc.wait()
    f=open('files.txt')
    lines=f.readlines()
    filenames = lines[0].split(" ")
    for i in range(0, len(filenames) ):
        filenamelist.insert(i, filenames[i])
        urllist.insert(i, "https://raw.githubusercontent.com/PearlOS-devices/official_devices/pie/"+filenames[i])
        changeloglist.insert(i, "https://raw.githubusercontent.com/PearlOS-devices/official_devices/pie/"+filenames[i].replace(".json", ".md"))

def getDetails(filename, update, url):
    arrayList = ["null", 1, "null", "null", "null"]
    if os.path.isfile('/app/OTA/'+filename):
        xda = ""
        version = 0
        download = ""
        datetime = 0
        maintainer = ""
        try:
            with open('/app/OTA/'+filename) as jsonDoc:
                data = json.load(jsonDoc)
                response = data['response'][0]
                datetime = response['datetime']
                maintainer = response['maintainer']
                xda = response['xda']
                download = response['url']
                version = response['version']

                conn = psycopg2.connect(DATABASE_URL, sslmode='require')
                cursor = conn.cursor()
                cursor.execute("SELECT DATE from LIST WHERE NAME LIKE (%s)", (filename,))
                entry = cursor.fetchone()
                if entry is None:
                    cursor.execute('INSERT INTO LIST (NAME,DATE) VALUES (%s, %s)', (filename, int(datetime)))
                    toggle = 1
                    
                else:
                    if entry[0] < int(datetime):
                        cursor.execute("UPDATE LIST set DATE = (%s) where NAME = (%s)", (int(datetime), filename))
                        toggle = 1
                        
                    else:
                        toggle = 0
                    
                
                conn.commit()
                conn.close()
                
                arrayList = [version, datetime, maintainer, xda, download]
        except Exception as e:
            update.message.reply_text("Error in: "+filename)
            update.message.reply_text(str(e))
            exceptionDetails = True
            
    else: 
        downloadFile(url, filename)
        try:
            with open(filename) as jsonDoc:
                data = json.load(jsonDoc)
                response = data['response'][0]
                datetime = response['datetime']
                maintainer = response['maintainer']
                xda = response['xda']
                download = response['url']
                version = response['version']

                conn = psycopg2.connect(DATABASE_URL, sslmode='require')
                cursor = conn.cursor()
                cursor.execute("SELECT DATE from LIST WHERE NAME LIKE (%s)", (filename,))
                entry = cursor.fetchone()
                if entry is None:
                    cursor.execute('INSERT INTO LIST (NAME,DATE) VALUES (%s, %s)', (filename, int(datetime)))
                    toggle = 1
                    
                else:
                    if entry[0] < int(datetime):
                        cursor.execute("UPDATE LIST set DATE = (%s) where NAME = (%s)", (int(datetime), filename))
                        toggle = 1
                        
                    else:
                        toggle = 0
                    
                
                conn.commit()
                conn.close()
                
                arrayList = [version, datetime, maintainer, xda, download]
        except Exception as e:
            update.message.reply_text("Error in: "+filename)
            update.message.reply_text(str(e))
            exceptionDetails = True
        
        
    return arrayList

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
    global exceptionDetails
    getLists()
    for i in range(len(filenamelist)):
        url = urllist[i]
        filename = filenamelist[i]
        changelog = changeloglist[i]
        List = getDetails(filename, update, url) 
        version = List[0]
        date = List[1]
        maintainer = List[2]
        xda = List[3]
        link = List[4]
        name = filename.split(".")
        name = name[0]
        
        if not exceptionDetails:
            if not maintainer:
                update.message.reply_text(name+": Maintainer in json can not be empty")
            elif not xda:
                update.message.reply_text(name+": XDA link in json can not be empty")
            elif not version:
                update.message.reply_text(name+": Version link in json can not be empty")
            elif not date:
                update.message.reply_text(name+": Datetime in json can not be empty")
            elif not link:
                update.message.reply_text(name+": URL in json can not be empty")
            else:
                kek = "📢*New Pearl Update*\n\n📱Device: *"+str(name)+"*\n🙎‍♂Maintainer: *"+str(maintainer)+"*\nLinks ⤵️\n\n⬇️ ROM : "+"[Here]("+str(link)+")"+"\n\n📜 XDA : "+"[Here]("+str(xda)+")"+"\n\n📕Changelog: "+"[Here]("+str(changelog)+")"
                if debug == 1:
                    bot.sendMessage(chat_id='@testchannel1312324', text=str(kek), parse_mode=telegram.ParseMode.MARKDOWN)
                    bot.sendSticker(chat_id='@testchannel1312324', sticker='CAADBQADmwADiYk3GUJzG4UKA2TLAg')
                elif (debug == 0 and toggle == 1) :
                    bot.sendMessage(chat_id='@Project_Pearl', text=str(kek), parse_mode=telegram.ParseMode.MARKDOWN)
                    bot.sendSticker(chat_id='@Project_Pearl', sticker='CAADBQADmwADiYk3GUJzG4UKA2TLAg')
        else:
            exceptionDetails = False
if __name__ == '__main__':
    main()
