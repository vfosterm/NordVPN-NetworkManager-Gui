#!/bin/bash

# install dependencies

if ! [ -z `which apt-get 2> /dev/null` ] && [ `nmcli networking` = "enabled" ] ; # Debian
then sudo apt-get install network-manager-openvpn network-manager-openvpn-gnome
fi

if ! [ -z `which dnf 2> /dev/null` ] && [ `nmcli networking` = "enabled" ]; # Fedora
then sudo dnf install NetworkManager-openvpn NetworkManager-openvpn-gnome
fi

if ! [ -z `which pacman 2> /dev/null` ] && [ `nmcli networking` = "enabled" ]; # Arch Linux
then sudo pacman -Sy networkmanager-openvpn
fi

current_dir=`pwd`

# check which path to desktop files exists
if [ -d /usr/local/share/applications ]
then
    DESK_PATH=/usr/local/share/applications
else
    DESK_PATH=/usr/share/applications
fi
echo "Saving desktop shortcut in "$DESK_PATH

echo "[Desktop Entry]
Type=Application
Version=0.2-beta
Name=Nord VPN
Comment=NordVPN client
Path="$current_dir"
Exec="$current_dir"/nord_vpn/launch_nord
Icon="$current_dir"/nord_vpn/nordvpnicon.ico
Terminal=false
Categories=Internet;System;Utilities;" | sudo tee $DESK_PATH/nordvpn.desktop > /dev/null

sudo chmod +x $DESK_PATH/nordvpn.desktop

