import json
import psycopg2
import subprocess
import os
import re
import time

from Constants import Constants

import bot as MainBot
from Utils.NetworkUtils import downloadFile
import Utils.GitUtils as GitUtils

exceptionDetails = False

filenamelist = []
urllist = []
changeloglist = []

toggle = 0
filename = ""


def extract_details_from_file(filename, fileurl):
    global toggle
    with open(fileurl) as jsonDoc:
        data = json.load(jsonDoc)
        response = data['response'][0]
        datetime = response['datetime']
        maintainer = response['maintainer']
        xda = response['xda']
        download = response['url']
        version = response['version']

        conn = psycopg2.connect(Constants.DATABASE_URL, sslmode='require')
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
        return arrayList


def get_lists():
    global filenamelist, urllist, changeloglist

    proc = subprocess.Popen([". /app/Bot/files.sh"], shell=True)
    proc.wait()
    f = open(Constants.PATH+'files.txt')
    lines = f.readlines()
    filenames = lines[0].split(" ")
    for i in range(0, len(filenames)):
        filenamelist.insert(i, filenames[i])
        urllist.insert(i, "https://raw.githubusercontent.com/PearlOS-devices/official_devices/pie/" + filenames[i])
        changeloglist.insert(i, "https://raw.githubusercontent.com/PearlOS-devices/official_devices/pie/" + filenames[
            i].replace(".json", ".md"))


def get_details(filename, update, url):
    global exceptionDetails
    array_list = []
    if os.path.isfile(Constants.OTA_PATH + filename):
        try:
            array_list = extract_details_from_file(filename, '/app/Bot/OTA/' + filename)
        except Exception as e:
            update.message.reply_text("Error in: " + filename)
            update.message.reply_text(str(e))
            exceptionDetails = True

    else:
        downloadFile(url, filename)
        try:
            array_list = extract_details_from_file(filename, filename)
        except Exception as e:
            update.message.reply_text("Error in: " + filename)
            update.message.reply_text(str(e))
            exceptionDetails = True

    return array_list


def set_details(bot, update):
    message = update.message.text
    user = update.message.from_user
    conn = psycopg2.connect(Constants.DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    cursor.execute("SELECT STATEID from STATE WHERE USERIDID LIKE (%s)", (str(user['id']),))
    entry = cursor.fetchone()
    if entry is None:
        cursor.execute('INSERT INTO STATE (USERIDID,STATEID,DATE,LINK,VERSION) VALUES (%s, %s, %s, %s, %s)', (str(user['id']), 0, 0, 0, 0))
        conn.commit()
        conn.close()
        state = 0
    else:
        state = entry[0]
        conn.close()

    if state == 0:
        set_date(update, message)
    elif state == 1:
        set_link(update, message)
    elif state == 2:
        set_version(update, message)
    elif state == 3:
        set_maintainer(update, message)
    elif state == 4:
        remove_maintainer(update, message)
    elif state == 5:
        update_json_file(bot, update, message)
    elif state == 6:
        set_changelog_device(update, message)
    elif state == 7:
        set_changelog(update, message)


def set_date(update, message):
    if date_check(message):
        if (str(message)).lower() == "now":
            message = int(time.time())
        user = update.message.from_user
        update.message.reply_text("Enter new link")
        save_value_to_database(message, 0, user)
        save_state_to_database(1, user)
    else:
        update.message.reply_text("Invalid datetime format. Please re-enter")


def date_check(timestamp):
    if str(timestamp).lower() == "now":
        return True
    elif len(timestamp) == 9:
        try:
            int(timestamp)
            return True

        except ValueError:
            return False
    else:
        return False


def set_link(update, message):
    if link_check(message):
        user = update.message.from_user
        update.message.reply_text("Enter new version")
        save_value_to_database(message, 1, user)
        save_state_to_database(2, user)
    else:
        update.message.reply_text("Invalid link format. Please re-enter")


def link_check(message):
    x = re.search("^(http://www.|https://www.|http://|https://)?"
                  "[a-z0-9]+([-.]{1}[a-z0-9]+)*.[a-z]{2,5}(:[0-9]{1,5})?(/.*)?", message)
    if not x:
        return False
    else:
        return True


def set_version(update, message):
    user = update.message.from_user
    update.message.reply_text("All details set.")
    save_value_to_database(message, 2, user)
    save_state_to_database(99, user)
    commit_or_not_show(update)


def commit_or_not_show(update):
    date, link, version = 0, "", ""
    user = update.message.from_user
    conn = psycopg2.connect(Constants.DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    cursor.execute("SELECT * from STATE WHERE USERIDID LIKE (%s)", (str(user['id']),))
    values = cursor.fetchall()
    for row in values:
        date = row[2]
        link = row[3]
        version = row[4]
    conn.close()
    MainBot.commit_or_not(update, date, link, version)


def set_maintainer(update, message):
    user = update.message.from_user
    conn = psycopg2.connect(Constants.DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    cursor.execute("SELECT TYPE from USERLIST WHERE NAMEID LIKE (%s)", (str(message),))
    entry = cursor.fetchone()
    if entry is None:
        cursor.execute('INSERT INTO USERLIST (NAMEID,TYPE) VALUES (%s, %s)', (str(message), str("maintainer")))
        update.message.reply_text("Set user as maintainer successfully")
    else:
        update.message.reply_text("User already exists")
    conn.commit()
    conn.close()
    save_state_to_database(99, user)


def remove_maintainer(update, message):
    user = update.message.from_user
    conn = psycopg2.connect(Constants.DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    cursor.execute("SELECT TYPE from USERLIST WHERE NAMEID LIKE (%s)", (str(message),))
    entry = cursor.fetchone()
    if entry is None:
        update.message.reply_text("No such ID found")
    else:
        cursor.execute("DELETE FROM USERLIST WHERE NAMEID LIKE (%s)", (str(message),))
        update.message.reply_text("Removed user from maintainer")
    conn.commit()
    conn.close()
    save_state_to_database(99, user)


def update_json_file(bot, update, message):
    date, link, version = 0, "", ""
    message = message.lower()
    if os.path.isfile(Constants.OTA_PATH + message + ".json"):
        user = update.message.from_user
        conn = psycopg2.connect(Constants.DATABASE_URL, sslmode='require')
        cursor = conn.cursor()
        cursor.execute("SELECT * from STATE WHERE USERIDID LIKE (%s)", (str(user['id']),))
        values = cursor.fetchall()
        for row in values:
            date = row[2]
            link = row[3]
            version = row[4]
        conn.close()
        try:
            with open(Constants.OTA_PATH + message+".json") as jsonDoc:
                data = json.load(jsonDoc)

            data['response'][0]['datetime'] = int(date)
            data['response'][0]['url'] = str(link)
            data['response'][0]['version'] = str(version)
            jsonDoc.close()

            with open(Constants.OTA_PATH + message + ".json", "w") as jsonDoc:
                jsonDoc.seek(0)
                json.dump(data, jsonDoc)
                jsonDoc.truncate()
                jsonDoc.close()
            reply = update.message.reply_text("Wrote changes locally...")
            mid = reply.message_id
            cid = reply.chat_id
            GitUtils.commit_file(message+'.json', str(user['id']))
            bot.edit_message_text(chat_id=cid, message_id=mid, text='Pushed changes to Github :)')
            MainBot.update(bot, update)

        except Exception as e:
            update.message.reply_text('Error: '+str(e))
    else:
        update.message.reply_text("No such file found, enter again.")


def set_changelog_device(update, message):
    global filename
    message = message.lower()
    user = update.message.from_user
    filename = message+".md"
    update.message.reply_text("Enter Changelog in one message")
    save_state_to_database(7, user)


def set_changelog(update, message):
    GitUtils.pull()
    try:
        user = update.message.from_user
        with open(Constants.OTA_PATH+filename, 'w') as f:
            f.seek(0)
            f.write(message)
            f.truncate()
        update.message.reply_text("Wrote Changelog to "+filename)

        GitUtils.commit_file(message + '.json', str(user['id']))
        save_state_to_database(99, user)
    except IOError as e:
        update.message.reply_text("Error: "+e)


def save_state_to_database(state, user):
    conn = psycopg2.connect(Constants.DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    cursor.execute("UPDATE STATE set STATEID = (%s) where USERIDID = (%s)", (int(state), str(user['id'])))
    conn.commit()
    conn.close()


def save_value_to_database(value, type, user):
    conn = psycopg2.connect(Constants.DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    if type == 0:
        cursor.execute("UPDATE STATE set DATE = (%s) where USERIDID = (%s)", (int(value), str(user['id'])))
    elif type == 1:
        cursor.execute("UPDATE STATE set LINK = (%s) where USERIDID = (%s)", (value, str(user['id'])))
    elif type == 2:
        cursor.execute("UPDATE STATE set VERSION = (%s) where USERIDID = (%s)", (value, str(user['id'])))
    conn.commit()
    conn.close()

