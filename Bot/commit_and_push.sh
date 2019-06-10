#!/bin/sh
cd /app/Bot/OTA/
git add -A
git commit -m "Automated update"
git push --force https://username:password@github.com/PearlOS-devices/official_devices.git pie
cd ../
