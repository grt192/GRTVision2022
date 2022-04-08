#!/bin/sh
echo "startup.sh running"
# Write the current date and time. Note that the Jetson is not connected to the internet and thus has inaccurate time/date.
date +"%r" >> ~/GRT2022Vision/output.log
echo "edited output.log"
# Run the python script with -u, meaning that the logged content should be flushed.
# Normally, logs are written to the file after the script has ended. -u writes the logs to the file even though the script doesn't end.
python3 -u ~/GRT2022Vision/JetsonMain.py >> ~/GRT2022Vision/output.log
echo "python script ended"


# Line endings in this bash script should be changed to LF (Unix) not CRLF (Windows) otherwise errors.
# (Can use Notepad++ or pull file directly from GitHub.)

# To run this script on boot:
# https://stackoverflow.com/questions/40861280/what-is-the-best-way-to-start-a-script-in-boot-time-on-linux
# chmod +x ~/startup.sh (to make it executable) 
# crontab -e
# Add: @reboot ~/startup.sh
# Or, if you didn't make it executable: @reboot sh ~/startup.sh should also work

# Crontab does not require user login to run: https://stackoverflow.com/questions/42304271/start-program-on-linux-without-user-login

# Check status of crontab: systemctl status cron
# https://linuxhint.com/check_working_crontab

# Check system time (Linux): timedatectl
# System date resets when rebooted


