#!/bin/sh
echo "startup.sh running"
# Write the current date and time. Note that the Jetson is not connected to the internet and thus has inaccurate time/date.
date +"%r" >> ~/GRT2022Vision/output.log
echo "edited output.log"
# Run the python script with -u, meaning that the logged content should be flushed.
# Normally, logs are written to the file after the script has ended. -u writes the logs to the file even though the script doesn't end.
python3 -u ~/GRT2022Vision/JetsonMain.py >> ~/GRT2022Vision/print.log
echo "python script ended"