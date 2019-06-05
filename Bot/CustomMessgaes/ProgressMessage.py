mid = 0
cid = 0


def progressMessage(bot, update, filename, progress):
    global mid, cid
    if progress == 0:
        message = update.message.reply_text('Checking ' + filename + '...')
        mid = message.message_id
        cid = message.chat_id
    else:
        bot.edit_message_text(chat_id=cid, message_id= mid, text='Checking ' + filename + '...')


def updateMessage(bot, filename):
    bot.edit_message_text(chat_id=cid, message_id=mid, text='Found update in: ' + filename)

def checkCompletedMessage(bot):
    bot.edit_message_text(chat_id=cid, message_id=mid, text="Update check completed")
