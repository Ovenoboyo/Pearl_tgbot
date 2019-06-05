import json
import psycopg2
import subprocess
import os
from bot import debug, DATABASE_URL
from Utils.NetworkUtils import downloadFile

exceptionDetails = False

filenamelist = []
urllist = []
changeloglist = []

def extractDetailsfromFile(filename, fileurl):
    with open(fileurl) as jsonDoc:
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
        return arrayList


def getLists():
    global filenamelist, urllist, changeloglist

    proc = subprocess.Popen([". /app/Bot/files.sh"], shell = True)
    proc.wait()
    f=open('/app/Bot/files.txt')
    lines=f.readlines()
    filenames = lines[0].split(" ")
    for i in range(0, len(filenames) ):
        filenamelist.insert(i, filenames[i])
        urllist.insert(i, "https://raw.githubusercontent.com/PearlOS-devices/official_devices/pie/"+filenames[i])
        changeloglist.insert(i, "https://raw.githubusercontent.com/PearlOS-devices/official_devices/pie/"+filenames[i].replace(".json", ".md"))

def getDetails(filename, update, url):
    global exceptionDetails
    arrayList = []
    if os.path.isfile('/app/Bot/OTA/'+filename):
        xda = ""
        version = 0
        download = ""
        datetime = 0
        maintainer = ""
        try:
            arrayList = extractDetailsfromFile(filename, '/app/Bot/OTA/'+filename)
        except Exception as e:
            update.message.reply_text("Error in: "+filename)
            update.message.reply_text(str(e))
            exceptionDetails = True
            
    else: 
        downloadFile(url, filename)
        try:
            arrayList = extractDetailsfromFile(filename, filename)
        except Exception as e:
            update.message.reply_text("Error in: "+filename)
            update.message.reply_text(str(e))
            exceptionDetails = True
        
        
    return arrayList
