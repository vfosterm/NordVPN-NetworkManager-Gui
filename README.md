# NordVPN Network Manager GUI
![License Badge](https://img.shields.io/github/license/vfosterm/NordVPN-NetworkManager-Gui)
![Issues](https://img.shields.io/github/issues-closed/vfosterm/NordVPN-NetworkManager-Gui)
![Release](https://img.shields.io/github/release/vfosterm/NordVPN-NetworkManager-Gui)
![commits-since](https://img.shields.io/github/commits-since/vfosterm/NordVPN-NetworkManager-Gui/latest)

![Login Screen](./screenshots/loginscreen.png)
![Main Screen](./screenshots/mainscreen.png)
#### About
NordVPN Network Manager GUI is a graphical frontend for both NordVPN and the system Network Manager.
All connections are handled directly by the network manager and user secrets are only stored in memory before being passed to the Network Manager.
Currently it operates 100% as a user process with no need for root privileges. 

This project was inspired by [NordVPN-NetworkManager](https://github.com/Chadsr/NordVPN-NetworkManager) by Chadsr. Many thanks for the code and knowledge that they published into the public domain.

#### Features
* Light - Uses the system Network Manager, application doesn't need to be running
* Clean - All configuration files are deleted after disconnection
* Secure - User secrets are passed directly from memory to the Network manager, root access is not required
* Powerful - Supports a variety of different protocols and server types with more on the way.
* Kill Switch - internet connection is disabled if VPN connection is lost
* Auto Connect - VPN is connection is established on system start
* Randomize MAC - Random MAC address is assigned before establishing connection

#### Using Installation Script
Installation script should support Debian, Fedora, and Arch Linux. It will attempt to install the one dependency this program has (networkmanager-openvpn). It will also add a menu entry pointing to the current working directory of the installation script. So make sure you place the folder where you want the install to be located. Installation script is only intended for the release version, not the python script itself.

Usage: `sudo ./install.sh`

#### Known Issues
* No support for obfuscated servers

### WARNING
Make sure to disable webrtc in your browser of choice. Using WebRTC may leak your original IP address.
