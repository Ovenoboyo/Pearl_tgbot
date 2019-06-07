#!/bin/sh
cd /app/Bot/OTA
git pull https://github.com/PearlOS-devices/official_devices pie
if [ $? -eq 0 ]; then
    echo $(ls -C *.json) >| ../files.txt
    cd ../
else
   cd ../
   rm -f OTA
   git clone https://github.com/PearlOS-devices/official_devices -b pie OTA
fi