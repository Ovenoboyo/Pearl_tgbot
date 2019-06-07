#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import logging

import psycopg2
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

import Utils.JsonUtils as JsonUtils
import CustomMessgaes.ProgressMessage as ProgressMessage

from Constants import Constants

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)

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
    JsonUtils.get_lists()
    for i in range(len(JsonUtils.filenamelist)):
        url = JsonUtils.urllist[i]
        filename = JsonUtils.filenamelist[i]
        changelog = JsonUtils.changeloglist[i]
        ProgressMessage.progressMessage(bot, update, filename, i)
        List = JsonUtils.get_details(filename, update, url)
        version = List[0]
        date = List[1]
        maintainer = List[2]
        xda = List[3]
        link = List[4]
        name = filename.split(".")
        name = name[0].capitalize()

        if JsonUtils.toggle == 1 or debug == 1:
            ProgressMessage.updateMessage(bot, filename)
        
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
                    JsonUtils.toggle = 0
                elif debug == 0 and JsonUtils.toggle == 1:
                    bot.sendMessage(chat_id='@Project_Pearl', text=str(kek), parse_mode=telegram.ParseMode.MARKDOWN)
                    bot.sendSticker(chat_id='@Project_Pearl', sticker='CAADBQADmwADiYk3GUJzG4UKA2TLAg')
                    JsonUtils.toggle = 0
        else:
            JsonUtils.exceptionDetails = False
    ProgressMessage.checkCompletedMessage(bot)


def build_menu(buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu


def editJson(bot, update):
    button_list = [
        InlineKeyboardButton("Maintainer Tools", callback_data='old'),
        InlineKeyboardButton("Admin Tools", callback_data='new')
    ]
    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=1))
    update.message.reply_text("Henlo User", reply_markup=reply_markup)


def commit_or_not(update, date, link, version):
    button_list = [
        InlineKeyboardButton("Commit to device json", callback_data='commit'),
        InlineKeyboardButton("Cancel", callback_data='no_commit')
    ]
    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=1))
    update.message.reply_text("Commit or not?\n\nDatetime: "+str(date)+"\nDownload link: "+str(link)+"\nVersion: "+str(version), reply_markup=reply_markup)


def run(updater):
    PORT = int(os.environ.get("PORT", "8443"))
    HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=Constants.TOKEN)
    updater.bot.set_webhook("https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, Constants.TOKEN))


def edit_button_old(bot, update):
    query = update.callback_query
    user = query.message.chat
    conn = psycopg2.connect(Constants.DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM USERLIST")
    entry = cursor.fetchall()
    for row in entry:
        if str(row[0]) == str(user['id']):
            JsonUtils.save_state_to_database(0, user)
            query.message.reply_text("Enter new datetime or send now to use current timestamp")
            query.message.delete()
            return
    query.message.reply_text("Unauthorised user :''(")
    query.message.delete()


def edit_button_new(bot, update):
    query = update.callback_query
    user = query.message.chat
    conn = psycopg2.connect(Constants.DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    cursor.execute("SELECT NAMEID from USERLIST WHERE TYPE LIKE (%s)", (str("admin"),))
    entry = cursor.fetchall()
    for row in entry:
        if str(row[0]) == str(user['id']):
            button_list = [
                InlineKeyboardButton("Add Maintainer", callback_data='add'),
                InlineKeyboardButton("Remove Maintainer", callback_data='remove')
            ]
            reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=1))
            query.message.reply_text("Henlo Admin", reply_markup=reply_markup)
            query.message.delete()
            conn.close()
            return
        else:
            continue
    query.message.reply_text("Unauthorised user :''(")
    query.message.delete()
    conn.close()


def add_maintainer_button(bot, update):
    query = update.callback_query
    user = query.message.chat
    JsonUtils.save_state_to_database(3, user)
    query.message.reply_text("Enter maintainer's TG id")
    query.message.delete()


def commit_data(bot,update):
    query = update.callback_query
    user = query.message.chat
    query.message.reply_text("Enter device name")
    JsonUtils.save_state_to_database(5, user)
    query.message.delete()



def no_commit_data(bot, update):
    query = update.callback_query
    user = query.message.chat
    query.message.reply_text("Hardluck, m8")
    JsonUtils.save_state_to_database(99, user)
    query.message.delete()


def remove_maintainer_button(bot, update):
    query = update.callback_query
    user = query.message.chat
    JsonUtils.save_state_to_database(4, user)
    query.message.reply_text("Enter maintainer's TG id")
    query.message.delete()


def main():
    updater = Updater(Constants.TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("update", update))
    dp.add_handler(CommandHandler("testoff", testoff))
    dp.add_handler(CommandHandler("teston", teston))
    dp.add_handler(CommandHandler("edit", editJson))

    edit_callback_handler_old = CallbackQueryHandler(edit_button_old, pattern='old')
    edit_callback_handler_new = CallbackQueryHandler(edit_button_new, pattern='new')

    dp.add_handler(edit_callback_handler_old)
    dp.add_handler(edit_callback_handler_new)

    maintainer_callback_handler_add = CallbackQueryHandler(add_maintainer_button, pattern='add')
    maintainer_callback_handler_remove = CallbackQueryHandler(remove_maintainer_button, pattern='remove')

    dp.add_handler(maintainer_callback_handler_add)
    dp.add_handler(maintainer_callback_handler_remove)

    maintainer_callback_handler_commit = CallbackQueryHandler(commit_data, pattern='commit')
    maintainer_callback_handler_nocommit = CallbackQueryHandler(no_commit_data, pattern='no_commit')

    dp.add_handler(maintainer_callback_handler_commit)
    dp.add_handler(maintainer_callback_handler_nocommit)

    message_handler = MessageHandler(Filters.text, JsonUtils.set_details)
    dp.add_handler(message_handler, 1)

    dp.add_error_handler(error)

    run(updater)


if __name__ == '__main__':
    main()
