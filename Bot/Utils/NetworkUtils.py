import urllib.request as urllib2
import os

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