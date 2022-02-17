# root user
sudo su

# install python 3
sudo apt-get update
sudo apt-get install python3.8 python3-pip

# install cscore
# https://robotpy.readthedocs.io/en/stable/install/cscore.html

echo 'deb http://download.opensuse.org/repositories/openSUSE:/Tools/xUbuntu_18.04/ /' | sudo tee /etc/apt/sources.list.d/openSUSE:Tools.list
curl -fsSL https://download.opensuse.org/repositories/openSUSE:Tools/xUbuntu_18.04/Release.key | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/openSUSE_Tools.gpg > /dev/null
sudo apt update
sudo apt install osc

# install dependencies
pip3 install pynetworktables