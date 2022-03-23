#!/bin/sh

# Run the vision code for the Jetson
python3 ./JetsonMain.py

# Startup setup
# sudo su
# vi /etc/rc.local

# /etc/rc.local CONTENTS:
# /path/to/script.sh || exit 1
# exit 0

# uhh if that doesn't work try https://stackoverflow.com/questions/40861280/what-is-the-best-way-to-start-a-script-in-boot-time-on-linux
