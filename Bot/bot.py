#!/usr/bin/env python
# -*- coding: utf-8 -*-
import stat
import os
import logging
import telegram
import array 
import Utils.JsonUtils as JsonUtils
from Utils.NetworkUtils import downloadFile

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)

TOKEN = os.getenv("TOKEN")
DATABASE_URL = os.environ['DATABASE_URL']

toggle = 0
debug = 0

def error(bot, update):
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def help(bot, update):
    update.message.reply_text('ono')

def teston(bot, update):
    global debug
    user = update.message.from_user
    if user['id'] == 423070089:
        debug = 1
        update.message.reply_text('Debug on')
    else: 
        update.message.reply_text('Unauthorised user')

def testoff(bot, update):
    global debug
    user = update.message.from_user
    if user['id'] == 423070089:
        debug = 0
        update.message.reply_text('Debug off')
    else: 
        update.message.reply_text('Unauthorised user')

def update(bot, update):
    JsonUtils.getLists()
    for i in range(len(JsonUtils.filenamelist)):
        url = JsonUtils.urllist[i]
        filename = JsonUtils.filenamelist[i]
        changelog = JsonUtils.changeloglist[i]
        List = JsonUtils.getDetails(filename, update, url)
        version = List[0]
        date = List[1]
        maintainer = List[2]
        xda = List[3]
        link = List[4]
        name = filename.split(".")
        name = name[0].capitalize()
        
        if not JsonUtils.exceptionDetails:
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
            JsonUtils.exceptionDetails = False

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

if __name__ == '__main__':
    main()
