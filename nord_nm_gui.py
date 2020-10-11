# -*- coding: utf-8 -*-
# NordVPN-NetworkManager-GUI a graphical frontend for both NordVPN and the Network Manager
# Copyright (C) 2018 Vincent Foster-Mueller
import sys
import os
import requests
import shutil
import time
import prctl
import keyring
import subprocess
import configparser
from collections import namedtuple
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QSystemTrayIcon, QStyle, QAction, qApp,  QMenu, QCheckBox
from PyQt5.QtGui import QIcon

connection_type_options = ['UDP', 'TCP']
server_type_options = ['P2P', 'Standard', 'Double VPN', 'TOR over VPN', 'Dedicated IP'] # , 'Anti-DDoS', 'Obfuscated Server']
api = "https://api.nordvpn.com/server"
ServerInfo = namedtuple('ServerInfo', 'name, country, domain, type, load, categories')


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        """
        Initialize Global Variables and login GUI
        Declare directories and paths
        """
        super(MainWindow, self).__init__()
        self.setObjectName("MainWindowObject")
        self.setWindowIcon(QtGui.QIcon('nordvpnicon.png'))
        self.base_dir = os.path.join(os.path.abspath(os.path.expanduser('~')), '.nordnmconfigs')  # /home/username/.nordnmconfigs
        self.config_path = os.path.join(os.path.abspath(self.base_dir), '.configs')
        self.scripts_path = os.path.join(os.path.abspath(self.base_dir), '.scripts')
        self.network_manager_path = '/etc/NetworkManager/dispatcher.d/'
        self.conf_path = os.path.join(self.config_path, 'nord_settings.conf')
        self.config = configparser.ConfigParser()
        self.api_data = self.get_api_data()
        self.username = None
        self.password = None
        self.sudo_password = None
        self.connection_name = None
        self.connected_server = None
        self.domain_list = []
        self.server_info_list = []
        self.login_ui()

        """
        Initialize System Tray Icon
        """
        self.trayIcon = QIcon("nordvpnicon.png")
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.trayIcon)
        show_action = QAction("Show NordVPN Network Manager", self)
        quit_action = QAction("Exit", self)
        hide_action = QAction("Minimized", self)
        show_action.triggered.connect(self.show)
        hide_action.triggered.connect(self.hide)
        quit_action.triggered.connect(self.quitAppEvent)
        self.tray_icon.activated.connect(self.resume)
        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setToolTip("NordVPN")
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        """
        Initialize GUI
        """


        self.show()

    def quitAppEvent(self):
        """
        Quit GUI from system tray
        """
        qApp.quit()

    def closeEvent(self, event):
        """
        Override default close event
        """
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "NordVPN Network Manager",
            "NordVPN Network Manager was minimized to System Tray",
            QSystemTrayIcon.Information,
            2500
        )

    def resume(self, activation_reason):
        """
        Resume from SystemTray
        """
        if activation_reason == 3:
            self.show()

    def main_ui(self):
        """
        QT form for the main GUI interface
        """
        self.resize(600, 650)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.title_label = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.title_label.sizePolicy().hasHeightForWidth())
        self.title_label.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(6)
        font.setStyleHint(QtGui.QFont.Monospace)
        self.title_label.setFont(font)
        self.title_label.setTextFormat(QtCore.Qt.RichText)
        self.title_label.setObjectName("title_label")
        self.horizontalLayout_2.addWidget(self.title_label)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.gridLayout.addLayout(self.horizontalLayout_2, 0, 0, 1, 2)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.country_list_label = QtWidgets.QLabel(self.centralwidget)
        self.country_list_label.setObjectName("country_list_label")
        self.verticalLayout_3.addWidget(self.country_list_label)
        self.line = QtWidgets.QFrame(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.line.sizePolicy().hasHeightForWidth())
        self.line.setSizePolicy(sizePolicy)
        self.line.setMinimumSize(QtCore.QSize(180, 0))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout_3.addWidget(self.line)
        self.country_list = QtWidgets.QListWidget(self.centralwidget)
        self.country_list.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.country_list.setObjectName("country_list")
        self.verticalLayout_3.addWidget(self.country_list)
        self.gridLayout.addLayout(self.verticalLayout_3, 1, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.auto_connect_box = QtWidgets.QCheckBox(self.centralwidget)
        self.auto_connect_box.setObjectName("auto_connect_box")
        self.verticalLayout.addWidget(self.auto_connect_box)
        self.mac_changer_box = QtWidgets.QCheckBox(self.centralwidget)
        self.mac_changer_box.setObjectName("mac_changer_box")
        self.verticalLayout.addWidget(self.mac_changer_box)
        self.killswitch_btn = QtWidgets.QCheckBox(self.centralwidget)
        self.killswitch_btn.setObjectName("killswitch_btn")
        self.verticalLayout.addWidget(self.killswitch_btn)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.server_type_select = QtWidgets.QComboBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.server_type_select.sizePolicy().hasHeightForWidth())
        self.server_type_select.setSizePolicy(sizePolicy)
        self.server_type_select.setObjectName("server_type_select")
        self.verticalLayout_2.addWidget(self.server_type_select)
        self.connection_type_select = QtWidgets.QComboBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.connection_type_select.sizePolicy().hasHeightForWidth())
        self.connection_type_select.setSizePolicy(sizePolicy)
        self.connection_type_select.setObjectName("connection_type_select")
        self.verticalLayout_2.addWidget(self.connection_type_select)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.connect_btn = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.connect_btn.sizePolicy().hasHeightForWidth())
        self.connect_btn.setSizePolicy(sizePolicy)
        self.connect_btn.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.connect_btn.setObjectName("connect_btn")
        self.horizontalLayout.addWidget(self.connect_btn)
        self.gridLayout.addLayout(self.horizontalLayout, 2, 0, 1, 2)
        self.disconnect_btn = QtWidgets.QPushButton(self.centralwidget)
        self.disconnect_btn.hide()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.disconnect_btn.sizePolicy().hasHeightForWidth())
        self.disconnect_btn.setSizePolicy(sizePolicy)
        self.disconnect_btn.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.disconnect_btn.setObjectName("disconnect_btn")
        self.horizontalLayout.addWidget(self.disconnect_btn)
        self.gridLayout.addLayout(self.horizontalLayout, 2, 0, 1, 2)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.verticalLayout_4.addWidget(self.label)
        self.line_2 = QtWidgets.QFrame(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.line_2.sizePolicy().hasHeightForWidth())
        self.line_2.setSizePolicy(sizePolicy)
        self.line_2.setMinimumSize(QtCore.QSize(180, 0))
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.verticalLayout_4.addWidget(self.line_2)
        self.server_list = QtWidgets.QListWidget(self.centralwidget)
        self.server_list.setObjectName("server_list")
        self.verticalLayout_4.addWidget(self.server_list)
        self.gridLayout.addLayout(self.verticalLayout_4, 1, 1, 1, 1)
        self.title_label.raise_()
        self.server_list.raise_()
        self.country_list.raise_()
        self.auto_connect_box.raise_()
        self.mac_changer_box.raise_()
        self.server_type_select.raise_()
        self.connection_type_select.raise_()
        self.country_list_label.raise_()
        self.label.raise_()
        self.line.raise_()
        self.line_2.raise_()
        self.killswitch_btn.raise_()
        self.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        # Begin of UI logic
        server_country_list = self.get_country_list(self.api_data)
        self.connection_type_select.addItems(connection_type_options)
        self.server_type_select.addItems(server_type_options)
        self.country_list.addItems(server_country_list)
        self.country_list.itemClicked.connect(self.get_server_list)
        self.server_type_select.currentTextChanged.connect(self.get_server_list)

        # Button functionality here
        self.connect_btn.clicked.connect(self.connect)
        self.disconnect_btn.clicked.connect(self.disconnect_vpn)
        self.auto_connect_box.clicked.connect(self.disable_auto_connect)
        self.killswitch_btn.clicked.connect(self.disable_kill_switch)

        self.parse_conf()
        self.repaint()
        self.get_active_vpn()
        self.center_on_screen()
        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)
        QtWidgets.QApplication.processEvents()
        self.show()

    def login_ui(self):
        """
        Login GUI form

        TODO: Add remember login checkbox + functionality
        """
        self.resize(558, 468)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setWindowTitle(" ")
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.nord_image = QtWidgets.QLabel(self.centralwidget)
        self.nord_image.setObjectName("nord_image")
        self.verticalLayout_2.addWidget(self.nord_image)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayout.setContentsMargins(-1, 0, -1, -1)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.user_label = QtWidgets.QLabel(self.centralwidget)
        self.user_label.setObjectName("user_label")
        self.horizontalLayout.addWidget(self.user_label)
        self.user_input = QtWidgets.QLineEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.user_input.sizePolicy().hasHeightForWidth())
        self.user_input.setSizePolicy(sizePolicy)
        self.user_input.setMaximumSize(QtCore.QSize(200, 30))
        self.user_input.setBaseSize(QtCore.QSize(150, 50))
        self.user_input.setAlignment(QtCore.Qt.AlignCenter)
        self.user_input.setObjectName("user_input")
        self.horizontalLayout.addWidget(self.user_input)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.password_label = QtWidgets.QLabel(self.centralwidget)
        self.password_label.setObjectName("password_label")
        self.horizontalLayout_2.addWidget(self.password_label)
        self.password_input = QtWidgets.QLineEdit(self.centralwidget)
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.password_input.sizePolicy().hasHeightForWidth())
        self.password_input.setSizePolicy(sizePolicy)
        self.password_input.setMaximumSize(QtCore.QSize(200, 30))
        self.password_input.setAlignment(QtCore.Qt.AlignCenter)
        self.password_input.setObjectName("password_input")
        self.horizontalLayout_2.addWidget(self.password_input)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3.addLayout(self.verticalLayout)
        spacerItem = QtWidgets.QSpacerItem(57, 20, QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.login_btn = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.login_btn.sizePolicy().hasHeightForWidth())
        self.login_btn.setSizePolicy(sizePolicy)
        self.login_btn.setObjectName("login_btn")
        self.verticalLayout_6.addWidget(self.login_btn)
        self.remember_checkBox = QtWidgets.QCheckBox(self.centralwidget)
        self.remember_checkBox.setObjectName("remember_checkBox")
        self.verticalLayout_6.addWidget(self.remember_checkBox)
        self.horizontalLayout_3.addLayout(self.verticalLayout_6)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.gridLayout.addLayout(self.verticalLayout_2, 0, 0, 1, 1)
        self.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        self.center_on_screen()
        self.retranslate_login_ui()
        QtCore.QMetaObject.connectSlotsByName(self)

        self.check_configs()   # do configs exist else create

        # buttons here
        self.password_input.returnPressed.connect(self.login_btn.click)
        self.login_btn.clicked.connect(self.verify_credentials)

    def check_configs(self):
        """
        Checks if config directories and files exist and creates them if they do not
        If username is found in config execute get_credentials()
        """
        try:
            if not os.path.isdir(self.base_dir):
                os.mkdir(self.base_dir)
            if not os.path.isdir(self.config_path):
                os.mkdir(self.config_path)
            if not os.path.isdir(self.scripts_path):
                os.mkdir(self.scripts_path)
            if not os.path.isfile(self.conf_path):
                self.config['USER'] = {
                    'USER_NAME': 'None'}
                self.config['SETTINGS'] = {
                    'MAC_RANDOMIZER': 'False',
                    'KILL_SWITCH': 'False',
                    'AUTO_CONNECT': 'False'}
                self.write_conf()

            self.config.read(self.conf_path)
            if (self.config.has_option('USER', 'USER_NAME') and
                    self.config.get('USER', 'USER_NAME') != 'None'):
                self.statusbar.showMessage("Fetching Saved Credentials", 1000)
                self.username = self.config.get('USER', 'USER_NAME')
                self.remember_checkBox.setChecked(True)
                self.user_input.setText(self.username)
                self.get_credentials()

        except PermissionError:
            self.statusbar.showMessage("Insufficient Permissions to create config folder", 2000)

    def get_credentials(self):
        try:
            keyring.get_keyring()
            password = keyring.get_password('NordVPN', self.username)
            self.password_input.setText(password)
        except Exception as ex:
            self.statusbar.showMessage("Error fetching keyring", 1000)

    def write_conf(self):
        """
        Writes config file
        """
        with open(self.conf_path, 'w') as configfile:
            self.config.write(configfile)

        configfile.close()

    def parse_conf(self):
        """
        Parses config and manipulates UI to match
        """
        self.config.read(self.conf_path)
        if self.config.getboolean('SETTINGS', 'mac_randomizer'):
            self.mac_changer_box.setChecked(True)
        if self.config.getboolean('SETTINGS', 'kill_switch'):
            self.killswitch_btn.setChecked(True)
        if self.config.getboolean('SETTINGS', 'auto_connect'):
            self.auto_connect_box.setChecked(True)

    def verify_credentials(self):
        """
        Requests a token from NordApi by sending the email and password in json format
        Verifies responses and updates GUI
        """
        if self.user_input.text() and self.password_input.text():
            self.username = self.user_input.text()
            self.password = self.password_input.text()

        else:
            self.statusbar.showMessage('Username or password field cannot be empty', 2000)
        try:

            # post username and password to api endpoint
            json_data = {'username': self.username, 'password': self.password}
            resp = requests.post('https://api.nordvpn.com/v1/users/tokens', json=json_data, timeout=5)
            if resp.status_code == 201:
                # check whether credentials should be saved
                if self.remember_checkBox.isChecked():
                    try:
                        keyring.set_password("NordVPN", self.username, self.password)
                        self.config['USER']['USER_NAME'] = self.username
                        self.write_conf()
                    except Exception as ex:
                        self.statusbar.showMessage("Error accessing keyring", 1000)
                        time.sleep(1)

                # Delete credentials if found
                else:
                    try:
                        keyring.delete_password("NordVPN", self.username)
                        self.config['USER']['USER_NAME'] = 'None'
                        self.write_conf()
                    except Exception as ex:
                        self.statusbar.showMessage("No saved credentials to delete", 1000)
                        time.sleep(0.5)

                self.statusbar.showMessage('Login Success', 2000)
                self.repaint()
                time.sleep(0.5)
                self.hide()
                self.main_ui()
            else:
                self.statusbar.showMessage('Invalid Username or Password', 2000)

        except Exception as ex:
            self.statusbar.showMessage("API Error: could not fetch token", 2000)
            self.get_api_data()

    def get_api_data(self):
        """
        Gets json file containing server information

        :return: server information in json format
        """
        try:
            resp = requests.get(api, timeout=5)
            if resp.status_code == requests.codes.ok:
                return resp.json()
            else:
                self.statusbar.showMessage("Get API failed", 2000)
        except Exception as ex:
            self.statusbar.showMessage("Get API failed", 2000)

    def get_country_list(self, api_data):
        """
        Parses json file for countries with servers available and displays them in the server_country_list box of the UI

        :param api_data: server information in json format
        :return: list of countries sorted alphabetically
        """
        server_country_list = []
        for server in api_data:
            country = server['country']
            if country not in server_country_list:
                server_country_list.append(country)
        return sorted(server_country_list)

    def get_server_list(self):
        """
        Displays server information in the server_list based on the given filter
        (server_type, connection_type, current_country)
        TODO: Rework this into a class
        """
        filtered = self.country_list.currentItem().text(), self.server_type_select.currentText(), self.connection_type_select.currentText()
        server_name_list = []
        self.server_list.clear()
        self.domain_list.clear()
        self.server_info_list.clear()
        for server in self.api_data:
            name       = server['name']
            load       = server['load']
            domain     = server['domain']
            country    = server['country']
            categories = server['categories']

            server_categories = ''
            server_category_list = []
            for category in categories:
                if category['name'] == 'Standard VPN servers':
                    server_categories += 'Standard '
                    server_category_list.append('Standard')
                elif category['name'] == 'P2P':
                    server_categories += category['name'] + ' '
                    server_category_list.append('P2P')
                elif category['name'] == 'Anti-DDoS':
                    server_categories += category['name'] + ' '
                    server_category_list.append('Anti-DDoS')
                elif category['name'] == 'Obfuscated Servers':
                    server_categories += 'Obfuscated'
                    server_category_list.append('Obfuscated Server')
                elif category['name'] == 'Dedicated IP':
                    server_categories += category['name'] + ' '
                    server_category_list.append('Dedicated IP')
                elif category['name'] == 'Double VPN':
                    server_categories += category['name'] + ' '
                    server_category_list.append('Double VPN')
                elif category['name'] == 'Onion Over VPN':
                    server_categories += category['name'] + ' '
                    server_category_list.append('TOR over VPN')
                else:
                    server_categories += category['name'] + ' '
            if (name not in server_name_list) and (country == filtered[0]) and (filtered[1] in server_category_list):
                server_name_list.append(name + '\n' + 'Load: ' + str(load) + '%\n' + "Domain: " + domain + '\n' + "Categories: " + server_categories)
                self.domain_list.append(domain)
                server = ServerInfo(name=name, country=country, domain=domain, type=server_category_list, load=load, categories=server_categories)
                self.server_info_list.append(server)

        if server_name_list:
            # sorts lists to be in the same order
            server_name_list, self.domain_list, self.server_info_list = (list(x) for x in zip(*sorted(zip(server_name_list, self.domain_list, self.server_info_list), key=lambda x: x[2].load)))
            self.server_list.addItems(server_name_list)
        else:
            self.server_list.addItem("No Servers Found")
        QtWidgets.QApplication.processEvents()
        self.retranslateUi()

    def get_ovpn(self):
        """
        Gets ovpn file from nord servers and saves it to a temporary location
        """
        # https://downloads.nordcdn.com/configs/files/ovpn_udp/servers/sg173.nordvpn.com.udp.ovpn
        self.ovpn_path = None
        ovpn_url = None
        udp_url = 'https://downloads.nordcdn.com/configs/files/ovpn_udp/servers/'
        tcp_url = 'https://downloads.nordcdn.com/configs/files/ovpn_tcp/servers/'
        udp_xor_url = 'https://downloads.nordcdn.com/configs/files/ovpn_xor_udp/servers/'
        tcp_xor_url = 'https://downloads.nordcdn.com/configs/files/ovpn_xor_tcp/servers/'

        if (self.server_type_select.currentText() == 'Obfuscated Server') and (self.connection_type_select.currentText() == 'UDP'):
            ovpn_url = udp_xor_url
        elif (self.server_type_select.currentText() == 'Obfuscated Server') and (self.connection_type_select.currentText() == 'TCP'):
            ovpn_url = tcp_xor_url
        elif (self.server_type_select.currentText() != 'Obfuscated Server') and (self.connection_type_select.currentText() == 'UDP'):
            ovpn_url = udp_url
        elif (self.server_type_select.currentText() != 'Obfuscated Server') and (self.connection_type_select.currentText() == 'TCP'):
            ovpn_url = tcp_url

        if self.connection_type_select.currentText() == 'UDP':
            filename = self.domain_list[self.server_list.currentRow()] + '.udp.ovpn'
            ovpn_file = requests.get(ovpn_url + filename, stream=True)
            if ovpn_file.status_code == requests.codes.ok:
                self.ovpn_path = os.path.join(self.config_path, filename)
                with open(self.ovpn_path, 'wb') as out_file:
                    shutil.copyfileobj(ovpn_file.raw, out_file)
            else: self.statusbar.showMessage('Error fetching configuration files', 2000)

        elif self.connection_type_select.currentText() == 'TCP':
            filename = self.domain_list[self.server_list.currentRow()] + '.tcp.ovpn'
            ovpn_file = requests.get(ovpn_url + filename, stream=True)
            if ovpn_file.status_code == requests.codes.ok:
                self.ovpn_path = os.path.join(self.config_path, filename)
                with open(self.ovpn_path, 'wb') as out_file:
                    shutil.copyfileobj(ovpn_file.raw, out_file)
            else: self.statusbar.showMessage('Error fetching configuration files', 2000)

        self.server_list.setFocus()

    def import_ovpn(self):
        """
        Renames and imports the ovpn to the Network Manager
        Cleans up the temporary files
        """
        try:
            self.statusbar.showMessage("Importing Connection...")
            self.repaint()
            self.connection_name = self.generate_connection_name()
            ovpn_file = self.connection_name + '.ovpn'
            path = os.path.join(self.config_path, ovpn_file) #changes name from default
            shutil.copy(self.ovpn_path, path)
            os.remove(self.ovpn_path)
            output = subprocess.run(['nmcli', 'connection', 'import', 'type', 'openvpn', 'file', path])
            output.check_returncode()
            os.remove(path)

        except subprocess.CalledProcessError:
            self.statusbar.showMessage("ERROR: Importing VPN configuration")

    def add_secrets(self):
        """
        Adds the username and Password to the configuration
        """
        try:
            self.statusbar.showMessage("Adding Secrets...", 1000)
            self.repaint()
            password_flag = subprocess.run(['nmcli', 'connection', 'modify', self.connection_name, '+vpn.data', 'password-flags=0'])
            password_flag.check_returncode()
            secrets = subprocess.run(['nmcli', 'connection', 'modify', self.connection_name, '+vpn.secrets', 'password='+self.password])
            secrets.check_returncode()
            user_secret = subprocess.run(['nmcli', 'connection', 'modify', self.connection_name, '+vpn.data', 'username='+self.username])
            user_secret.check_returncode()
            disable_ipv6 = subprocess.run(['nmcli', 'connection', 'modify', self.connection_name, '+ipv6.method', 'ignore'])
            disable_ipv6.check_returncode()
            password_flag = subprocess.run(['nmcli', 'connection', 'modify', self.connection_name, '+vpn.data', 'password-flags=0'])
            password_flag.check_returncode()
        except subprocess.CalledProcessError:
            self.statusbar.showMessage("ERROR: Secrets could not be added", 2000)

    def generate_connection_name(self):
        """
        Generates the name of the ovpn file
        """
        server = self.server_info_list[self.server_list.currentRow()]
        category_name = ''
        for i, category in enumerate(server.type):
            if i > 0:
                category_name += ' | ' + category
            else:
                category_name = category

        connection_name = server.name + ' [' + category_name + '] [' + self.connection_type_select.currentText() + ']'
        return connection_name

    def get_active_vpn(self):
        """
        Queries the Network Manager for the current connection.
        If a current Nord connection it will set the UI to the appropriate state
        """
        try:
            output = subprocess.run(['nmcli', '--mode', 'tabular', '--terse', '--fields', 'TYPE,NAME', 'connection', 'show', '--active'],
                                   stdout=subprocess.PIPE)
            output.check_returncode()
            lines = output.stdout.decode('utf-8').split('\n')

            for line in lines:
                if line:
                    elements = line.strip().split(':')

                    if elements[0] == 'vpn':
                        connection_info = elements[1].split()
                        connection_name = elements[1]
                        country = connection_info[0]
                        print(connection_info)
                        if ('[Standard' in connection_info or
                                '[Standard]' in connection_info):  # Normal servers
                            server_name = connection_info[0] + ' ' + connection_info[1]
                        elif '[Double' in connection_info:  # Double VPN server
                            server_name = connection_info[0] + ' ' + '- ' + connection_info[2] + ' ' + connection_info[3]
                        elif '[TOR' in connection_info:  # Onion Over VPN
                            server_name = connection_info[0] + ' ' + connection_info[1] + ' ' + connection_info[2]
                        elif '[Dedicated' in connection_info:  # Dedicated IP
                            server_name = connection_info[0] + ' ' + connection_info[1]
                        if self.server_info_list:  # vpn connected successfully
                            for server in self.server_info_list:
                                if server_name == server.name:
                                    self.connected_server = server.name
                                    return True
                        elif not self.server_info_list:  # existing Nordvpn connection found
                            self.connect_btn.hide()
                            self.disconnect_btn.show()
                            self.statusbar.showMessage("Fetching Active Server...", 2000)
                            self.repaint()
                            item = self.country_list.findItems(country, QtCore.Qt.MatchExactly)
                            self.country_list.setCurrentItem(item[0])
                            if ('[Standard' in connection_info or
                                    '[Standard]' in connection_info):
                                self.server_type_select.setCurrentIndex(1)
                            if "[Double" in connection_info:
                                self.server_type_select.setCurrentIndex(2)
                            if "[TOR" in connection_info:
                                self.server_type_select.setCurrentIndex(3)
                            if "[Dedicated" in connection_info:
                                self.server_type_select.setCurrentIndex(4)
                            if "[TCP]" in connection_info:
                                self.connection_type_select.setCurrentIndex(1)
                            self.get_server_list()
                            for server in self.server_info_list:
                                if server_name == server.name:
                                    server_list_item = self.server_list.findItems(server_name + '\n' + 'Load: ' + str(server.load) + '%\n' + "Domain: " + server.domain + '\n' + "Categories: " + server.categories, QtCore.Qt.MatchExactly)
                                    self.server_list.setCurrentItem(server_list_item[0])
                                    self.server_list.setFocus()
                                    self.connection_name = connection_name
                                    self.connected_server = server.name
                                    return False
                        else:
                            self.statusbar.showMessage("Warning! Unknown VPN connection found", 2000)
                            self.repaint()
                            return False

        except subprocess.CalledProcessError:
            self.statusbar.showMessage("ERROR: Network Manager query error", 2000)
            self.repaint()

    def randomize_mac(self):
        """
        Takes down network interface and brings it back with a new MAC Address
        """
        try:
            self.statusbar.showMessage("Randomizing MAC Address", 2000)
            self.repaint()
            output = subprocess.run(['nmcli', '--mode', 'tabular', '--terse', '--fields', 'TYPE,UUID', 'connection', 'show', '--active'], stdout=subprocess.PIPE)
            output.check_returncode()
            lines = output.stdout.decode('utf-8').split('\n')

            for line in lines:
                if line:
                    elements = line.strip().split(':')
                    uuid = elements[1]
                    connection_type = elements[0]
                    if type != 'vpn':
                        subprocess.run(['nmcli', 'connection', 'down', uuid])
                        subprocess.run(['nmcli', 'connection', 'modify', '--temporary', uuid, connection_type+'.cloned-mac-address', 'random'])
                        subprocess.run(['nmcli', 'connection', 'up', uuid])

            self.statusbar.showMessage("Random MAC Address assigned", 2000)
            self.write_conf()
            self.repaint()
        except subprocess.CalledProcessError:
            self.statusbar.showMessage("ERROR: Randomizer failed", 2000)
            self.repaint()

    def get_sudo(self):
        """
        Sudo dialog UI form
        TODO: Remove in favour of a DBUS based approach
        """
        sudo_dialog = QtWidgets.QDialog(self)
        sudo_dialog.setModal(True)
        sudo_dialog.resize(399, 206)
        icon = QtGui.QIcon.fromTheme("changes-prevent")
        sudo_dialog.setWindowIcon(icon)
        sudo_dialog.gridLayout = QtWidgets.QGridLayout(sudo_dialog)
        sudo_dialog.gridLayout.setObjectName("gridLayout")
        sudo_dialog.verticalLayout = QtWidgets.QVBoxLayout()
        sudo_dialog.verticalLayout.setContentsMargins(-1, 18, -1, -1)
        sudo_dialog.verticalLayout.setSpacing(16)
        sudo_dialog.verticalLayout.setObjectName("verticalLayout")
        sudo_dialog.text_label = QtWidgets.QLabel(sudo_dialog)
        sudo_dialog.text_label.setTextFormat(QtCore.Qt.RichText)
        sudo_dialog.text_label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        sudo_dialog.text_label.setWordWrap(True)
        sudo_dialog.text_label.setObjectName("text_label")
        sudo_dialog.verticalLayout.addWidget(sudo_dialog.text_label)
        sudo_dialog.sudo_password = QtWidgets.QLineEdit(self)
        sudo_dialog.sudo_password.setCursor(QtGui.QCursor(QtCore.Qt.IBeamCursor))
        sudo_dialog.sudo_password.setAlignment(QtCore.Qt.AlignCenter)
        sudo_dialog.sudo_password.setClearButtonEnabled(False)
        sudo_dialog.sudo_password.setObjectName("sudo_password")
        sudo_dialog.sudo_password.setEchoMode(QtWidgets.QLineEdit.Password)
        sudo_dialog.verticalLayout.addWidget(sudo_dialog.sudo_password)
        sudo_dialog.gridLayout.addLayout(sudo_dialog.verticalLayout, 0, 0, 1, 1)
        sudo_dialog.horizontalLayout = QtWidgets.QHBoxLayout()
        sudo_dialog.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        sudo_dialog.horizontalLayout.setContentsMargins(-1, 0, -1, 6)
        sudo_dialog.horizontalLayout.setSpacing(0)
        sudo_dialog.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(178, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        sudo_dialog.horizontalLayout.addItem(spacerItem)
        sudo_dialog.accept_box = QtWidgets.QDialogButtonBox(sudo_dialog)
        sudo_dialog.accept_box.setOrientation(QtCore.Qt.Horizontal)
        sudo_dialog.accept_box.addButton('Login', QtWidgets.QDialogButtonBox.AcceptRole)
        sudo_dialog.accept_box.addButton('Cancel', QtWidgets.QDialogButtonBox.RejectRole)
        sudo_dialog.accept_box.setObjectName("accept_box")
        sudo_dialog.horizontalLayout.addWidget(sudo_dialog.accept_box)
        sudo_dialog.gridLayout.addLayout(sudo_dialog.horizontalLayout, 1, 0, 1, 1)
        sudo_dialog.setWindowTitle("Authentication Needed")
        sudo_dialog.text_label.setText("<html><head/><body><p>VPN Network Manager requires <span style=\" font-weight:600;\">sudo</span> permissions in order to move the auto-connect script to the Network Manager directory. Please input the <span style=\" font-weight:600;\">sudo</span> Password or run the program with elevated priveledges.</p></body></html>")
        resolution = QtWidgets.QDesktopWidget().screenGeometry()
        # move to center
        sudo_dialog.move(int((resolution.width() / 2) - (sudo_dialog.frameSize().width() / 2)), int((resolution.height() / 2) - (sudo_dialog.frameSize().height() / 2)))
        # button functionality here
        sudo_dialog.accept_box.accepted.connect(self.check_sudo)
        sudo_dialog.accept_box.rejected.connect(self.close_sudo_dialog)
        QtCore.QMetaObject.connectSlotsByName(sudo_dialog)
        return sudo_dialog

    def close_sudo_dialog(self):  # added to clear sudo password when cancel is pressed
        self.sudo_password = None
        self.sudo_dialog.close()

    def check_sudo(self):
        """
        Checks validity of sudo password

        :return: True if valid False if invalid
        """
        self.sudo_password = self.sudo_dialog.sudo_password.text()
        try:
            p1 = subprocess.Popen(['echo', self.sudo_password], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
            p2 = subprocess.Popen(['sudo', '-S', 'whoami'], stdin=p1.stdout, stdout=subprocess.PIPE, encoding='utf-8', stderr=subprocess.PIPE)
            p1.stdout.close()
            output = p2.communicate()[0].strip()
            p2.stdout.close()

            if "root" in output:
                self.sudo_dialog.close()
                print('True')
                return True
            else:
                error = QtWidgets.QErrorMessage(self.sudo_dialog)
                error.showMessage("Invalid Password")
                return False
        except Exception as ex:
            print('failed', ex)
            self.sudo_password = None

    def get_interfaces(self):
        """
        Gets current Network interfaces

        :return: List of Network interfaces
        """
        try:
            output = subprocess.run(['nmcli', '--mode', 'tabular', '--terse', '--fields', 'TYPE,DEVICE', 'device', 'status'], stdout=subprocess.PIPE)
            output.check_returncode()

            lines = output.stdout.decode('utf-8').split('\n')
            interfaces = []

            for line in lines:
                if line:
                    elements = line.strip().split(':')

                    if (elements[0] == 'wifi') or (elements[0] == 'ethernet'):
                        interfaces.append(elements[1])

            return interfaces

        except subprocess.CalledProcessError:
            self.statusbar.showMessage("ERROR Fetching interfaces")

    def set_auto_connect(self):
        """
        Generates auto_connect bash script and moves it to the NetworkManager
        """
        self.config.read(self.conf_path)
        interfaces = self.get_interfaces()
        if interfaces:
            interface_string = '|'.join(interfaces)
            script =(
            '#!/bin/bash\n\n'
            'if [[ "$1" =~ ' + interface_string + ' ]] && [[ "$2" =~ up|connectivity-change ]]; then\n'
            '  nmcli con up id "' + self.generate_connection_name() + '"\n'
            'fi\n'
            )
        try:
            with open(os.path.join(self.scripts_path, 'auto_connect'), 'w') as auto_connect:
                print(script, file=auto_connect)
        except Exception as ex:
            print(ex)
            self.statusbar.showMessage("ERROR building script file")
        try:
            p1 = subprocess.Popen(['echo', self.sudo_password], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
            p2 = subprocess.Popen(['sudo', '-S', 'mv', self.scripts_path + '/auto_connect', self.network_manager_path + 'auto_connect'], stdin=p1.stdout, stdout=subprocess.PIPE)
            p1.stdout.close()
            p2.stdout.close()
            p3 = subprocess.Popen(['echo', self.sudo_password], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
            p4 = subprocess.Popen(['sudo', '-S', 'chown', 'root:root', self.network_manager_path + 'auto_connect'], stdin=p3.stdout, stdout=subprocess.PIPE)
            p3.stdout.close()
            p4.stdout.close()
            p5 = subprocess.Popen(['echo', self.sudo_password], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
            p6 = subprocess.Popen(['sudo', '-S', 'chmod', '744', self.network_manager_path + 'auto_connect'], stdin=p5.stdout, stdout=subprocess.PIPE)
            p5.stdout.close()
            p6.stdout.close()
            self.config['SETTINGS']['auto_connect'] = 'True'
            self.write_conf()
        except Exception as ex:
            print(ex)

    def disable_auto_connect(self):
        """
        Handles the enabling and disabling of auto-connect depending on UI state
        Called everytime the auto-connect box is clicked
        """
        self.config.read(self.conf_path)

        if not self.auto_connect_box.isChecked() and not self.sudo_password and self.config.getboolean('SETTINGS', 'auto_connect'):
            self.sudo_dialog = self.get_sudo()
            self.sudo_dialog.text_label.setText("<html><head/><body><p>VPN Network Manager requires <span style=\" font-weight:600;\">sudo</span> permissions in order to remove the auto-connect script from the Network Manager directory. Please input the <span style=\" font-weight:600;\">sudo</span> Password or run the program with elevated priveledges.</p></body></html>")
            self.sudo_dialog.exec_()
            if not self.sudo_password:  # dialog was canceled
                return False
            try:
                p1 = subprocess.Popen(['echo', self.sudo_password], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
                p2 = subprocess.Popen(['sudo', '-S', 'rm', self.network_manager_path + 'auto_connect'], stdin=p1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                p1.stdout.close()
                p2.stdout.close()
                self.config['SETTINGS']['auto_connect'] = 'False'
                self.write_conf()
            except Exception as ex:
                print(ex)

        elif not self.auto_connect_box.isChecked() and self.sudo_password and self.config.getboolean('SETTINGS', 'auto_connect'):

            try:
                p1 = subprocess.Popen(['echo', self.sudo_password], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
                p2 = subprocess.Popen(['sudo', '-S', 'rm', self.network_manager_path + 'auto_connect'], stdin=p1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                p1.stdout.close()
                p2.stdout.close()
                self.config['SETTINGS']['auto_connect'] = 'False'
                self.write_conf()
            except Exception as ex:
                print(ex)

        elif self.auto_connect_box.isChecked() and self.get_active_vpn() and self.sudo_password:
            self.set_auto_connect()

        elif self.auto_connect_box.isChecked() and self.get_active_vpn() and not self.sudo_password:
            self.sudo_dialog = self.get_sudo()
            self.sudo_dialog.exec_()
            if self.sudo_password:
                self.set_auto_connect()
            else:
                self.auto_connect_box.setChecked(False)
                return False

    def set_kill_switch(self):
        """
        Generates bash killswitch script and moves it to the NetworkManager
        """
        script = (
            '#!/bin/bash\n'
            'PERSISTENCE_FILE=' + os.path.join(self.scripts_path, '.killswitch_data') + '\n\n'
            'case $2 in'
            '  vpn-up)\n'
            '    nmcli -f type,device connection | awk \'$1~/^vpn$/ && $2~/[^\-][^\-]/ { print $2; }\' > "${PERSISTENCE_FILE}"\n'
            '  ;;\n'
            '  vpn-down)\n'
            '    xargs -n 1 -a "${PERSISTENCE_FILE}" nmcli device disconnect\n'
            '  ;;\n'
            'esac\n'
        )

        try:
            with open(os.path.join(self.scripts_path, 'kill_switch'), 'w') as kill_switch:
                print(script, file=kill_switch)

            p1 = subprocess.Popen(['echo', self.sudo_password], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            p2 = subprocess.Popen(['sudo', '-S', 'mv', self.scripts_path + '/kill_switch', self.network_manager_path + 'kill_switch'], stdin=p1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            p1.stdout.close()
            p2.stdout.close()
            time.sleep(0.5)
            p3 = subprocess.Popen(['echo', self.sudo_password], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            p4 = subprocess.Popen(['sudo', '-S', 'chown', 'root:root', self.network_manager_path + 'kill_switch'], stdin=p3.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(0.5)
            p3.stdout.close()
            p4.stdout.close()
            p5 = subprocess.Popen(['echo', self.sudo_password], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            p6 = subprocess.Popen(['sudo', '-S', 'chmod', '744', self.network_manager_path + 'kill_switch'], stdin=p5.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            p5.stdout.close()
            p6.stdout.close()
            self.config['SETTINGS']['kill_switch'] = 'True'
            self.write_conf()

            self.statusbar.showMessage('Kill switch activated', 2000)
            self.repaint()
        except Exception as ex:
            print(ex)

    def disable_kill_switch(self):
        """
        Enables or disables Killswitch depending on UI state
        Called everytime the Killswitch button is pressed
        """
        if not self.killswitch_btn.isChecked() and not self.sudo_password and self.config.getboolean('SETTINGS', 'kill_switch'):
            self.sudo_dialog = self.get_sudo()
            self.sudo_dialog.text_label.setText("<html><head/><body><p>VPN Network Manager requires <span style=\" font-weight:600;\">sudo</span> permissions in order to remove the kill switch script from the Network Manager directory. Please input the <span style=\" font-weight:600;\">sudo</span> Password or run the program with elevated priveledges.</p></body></html>")
            self.sudo_dialog.exec_()

            if not self.sudo_password:  # dialog was canceled
                self.killswitch_btn.setChecked(False)
                return False
            try:
                p1 = subprocess.Popen(['echo', self.sudo_password], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                p2 = subprocess.Popen(['sudo', '-S', 'rm', self.network_manager_path + 'kill_switch'], stdin=p1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                p1.stdout.close()
                p2.stdout.close()
                self.statusbar.showMessage('Kill switch disabled', 2000)
                self.repaint()
                self.config['SETTINGS']['kill_switch'] = 'False'
                self.write_conf()

            except subprocess.CalledProcessError:
                self.statusbar.showMessage('ERROR disabling kill switch', 2000)
                self.repaint()

        elif not self.killswitch_btn.isChecked() and self.sudo_password and self.config.getboolean('SETTINGS', 'kill_switch'):

            try:
                p1 = subprocess.Popen(['echo', self.sudo_password], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                p2 = subprocess.Popen(['sudo', '-S', 'rm', self.network_manager_path + 'kill_switch'], stdin=p1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                p1.stdout.close()
                p2.stdout.close()
                self.statusbar.showMessage('Kill switch disabled', 2000)
                self.repaint()
                self.config['SETTINGS']['kill_switch'] = 'False'
                self.write_conf()

            except subprocess.CalledProcessError:
                self.statusbar.showMessage('ERROR disabling kill switch', 2000)
                self.repaint()

        elif self.killswitch_btn.isChecked() and self.get_active_vpn() and self.sudo_password:
            self.set_kill_switch()

        elif self.killswitch_btn.isChecked() and self.get_active_vpn() and not self.sudo_password:
            self.sudo_dialog = self.get_sudo()
            self.sudo_dialog.text_label.setText("<html><head/><body><p>VPN Network Manager requires <span style=\" font-weight:600;\">sudo</span> permissions in order to move the kill switch script to the Network Manager directory. Please input the <span style=\" font-weight:600;\">sudo</span> Password or run the program with elevated priveledges.</p></body></html>")
            self.sudo_dialog.exec_()
            if self.sudo_password:
                self.set_kill_switch()
            else:
                self.killswitch_btn.setChecked(False)
                return False

    def disable_ipv6(self):
        """
        Disables IPV6 system wide
        """
        if self.sudo_password:
            try:
                p1 = subprocess.Popen(['echo', self.sudo_password], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                p2 = subprocess.Popen(['sudo', '-S', 'sysctl', '-w', 'net.ipv6.conf.all.disable_ipv6=1', '&&', 'sysctl', '-w', 'net.ipv6.conf.default.disable_ipv6=1'], stdin=p1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                p1.stdout.close()
                p2.stdout.close()
            except subprocess.CalledProcessError:
                self.statusbar.showMessage("ERROR: disabling IPV6 failed", 2000)
        else:
            self.sudo_dialog = self.get_sudo()
            self.sudo_dialog.text_label.setText("<html><head/><body><p>VPN Network Manager requires <span style=\" font-weight:600;\">sudo</span> permissions in order to disable IPV6. Please input the <span style=\" font-weight:600;\">sudo</span> Password or run the program with elevated priveledges.</p></body></html>")
            self.sudo_dialog.exec_()

            if self.sudo_password:
                try:
                    p1 = subprocess.Popen(['echo', self.sudo_password], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                    p2 = subprocess.Popen(['sudo', '-S', 'sysctl', '-w', 'net.ipv6.conf.all.disable_ipv6=1', '&&', 'sysctl', '-w', 'net.ipv6.conf.default.disable_ipv6=0'], stdin=p1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    p1.stdout.close()
                    p2.stdout.close()
                except subprocess.CalledProcessError:
                    self.statusbar.showMessage("ERROR: disabling IPV6 failed", 2000)

    def enable_ipv6(self):
        """
        Re-enables ipv6 system wide
        """
        if self.sudo_password:
            try:
                p1 = subprocess.Popen(['echo', self.sudo_password], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                p2 = subprocess.Popen(['sudo', '-S', 'sysctl', '-w', 'net.ipv6.conf.all.disable_ipv6=0', '&&', 'sysctl', '-w', 'net.ipv6.conf.default.disable_ipv6=0'], stdin=p1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                p1.stdout.close()
                p2.stdout.close()
            except subprocess.CalledProcessError:
                self.statusbar.showMessage("ERROR: disabling IPV6 failed", 2000)
        else:
            self.sudo_dialog = self.get_sudo()
            self.sudo_dialog.text_label.setText("<html><head/><body><p>VPN Network Manager requires <span style=\" font-weight:600;\">sudo</span> permissions in order to enable IPV6. Please input the <span style=\" font-weight:600;\">sudo</span> Password or run the program with elevated priveledges.</p></body></html>")
            self.sudo_dialog.exec_()

            if self.sudo_password:
                try:
                    p1 = subprocess.Popen(['echo', self.sudo_password], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                    p2 = subprocess.Popen(['sudo', '-S', 'sysctl', '-w', 'net.ipv6.conf.all.disable_ipv6=0', '&&', 'sysctl', '-w', 'net.ipv6.conf.default.disable_ipv6=0'], stdin=p1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    p1.stdout.close()
                    p2.stdout.close()
                except subprocess.CalledProcessError:
                    self.statusbar.showMessage("ERROR: Enabling IPV6 failed", 2000)

    def check_connection_validity(self):
        """
        Checks if connection is a double_vpn and forces the connection to TCP
        """
        if self.server_type_select.currentText() == 'Double VPN':  # perhaps add pop up to give user the choice
            self.connection_type_select.setCurrentIndex(1)  # set to TCP

    def enable_connection(self):
        """
        Enable vpn connection in NetworkManager
        """
        try:
            self.statusbar.showMessage("Connecting...", 1000)
            self.repaint()
            connection = subprocess.run(['nmcli', 'connection', 'up', self.connection_name])
            connection.check_returncode()
        except subprocess.CalledProcessError:
            self.statusbar.showMessage("ERROR: Connection Failed", 2000)

    def disable_connection(self):
        """
        Disconnect vpn connection in NetworkManager
        """
        try:
            self.statusbar.showMessage("Disconnecting...", 1000)
            self.repaint()
            connection = subprocess.run(['nmcli', 'connection', 'down', self.connection_name])
            connection.check_returncode()
        except subprocess.CalledProcessError:
            self.statusbar.showMessage("ERROR: Disconnection Failed", 2000)

    def remove_connection(self):
        """
        Remove connection from network manager
        """
        try:
            connection = subprocess.run(['nmcli', 'connection', 'delete', self.connection_name])
            connection.check_returncode()
        except subprocess.CalledProcessError:
            self.statusbar.showMessage("ERROR: Failed to remove Connection", 2000)

    def connect(self):
        """
        Steps through all of the UI Logic for connecting to VPN
        """
        if self.mac_changer_box.isChecked():
            self.randomize_mac()
            self.config['SETTINGS']['mac_randomizer'] = 'True'
            self.write_conf()
        else:
            self.config['SETTINGS']['mac_randomizer'] = 'False'
            self.write_conf()

        if self.auto_connect_box.isChecked() and not self.sudo_password:  # prompt for sudo password
            self.sudo_dialog = self.get_sudo()
            self.sudo_dialog.exec_()

            if self.sudo_password: #valid password exists
                self.set_auto_connect()
            else:
                self.auto_connect_box.setChecked(False)
                return False
        elif self.auto_connect_box.isChecked() and self.sudo_password:  # sudo password exists in memory
            self.set_auto_connect()
        self.check_connection_validity()
        self.disable_ipv6()
        self.get_ovpn()
        self.import_ovpn()
        self.add_secrets()
        self.enable_connection()
        self.statusbar.clearMessage()
        self.repaint()

        if self.killswitch_btn.isChecked() and not self.sudo_password:
            self.sudo_dialog = self.get_sudo()
            self.sudo_dialog.text_label.setText("<html><head/><body><p>VPN Network Manager requires <span style=\" font-weight:600;\">sudo</span> permissions in order to move the kill switch script to the Network Manager directory. Please input the <span style=\" font-weight:600;\">sudo</span> Password or run the program with elevated priveledges.</p></body></html>")
            self.sudo_dialog.exec_()
            if not self.sudo_password:  # dialog was closed
                self.killswitch_btn.setChecked(False)
                return False
            self.set_kill_switch()

        elif self.killswitch_btn.isChecked() and self.sudo_password:
            self.set_kill_switch()

        # UI changes here
        if self.get_active_vpn():  # if connection successful
            self.connect_btn.hide()
            self.disconnect_btn.show()
            self.retranslateUi()

    def disconnect_vpn(self):
        """
        Steps through all of the UI logic to disconnect VPN
        """
        if self.killswitch_btn.isChecked():
            self.killswitch_btn.setChecked(False)
            self.statusbar.showMessage("Disabling Killswitch...", 5000)
            self.repaint()
            self.disable_kill_switch()
            time.sleep(5)  # sleep time to mitigate NetworkManager still killing connection
        if self.auto_connect_box.isChecked():
            self.auto_connect_box.setChecked(False)
            self.statusbar.showMessage("Disabling auto-connect...", 1000)
            self.disable_auto_connect()
        self.disable_connection()
        self.remove_connection()
        self.enable_ipv6()
        self.statusbar.clearMessage()
        self.repaint()

        # UI changes here
        self.disconnect_btn.hide()
        self.connect_btn.show()
        self.retranslateUi()

    def center_on_screen(self):
        """
        Function to find the center of the users screen
        """
        resolution = QtWidgets.QDesktopWidget().screenGeometry()
        self.move(int((resolution.width() / 2) - (self.frameSize().width() / 2)), int((resolution.height() / 2) - (self.frameSize().height() / 2)))

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", " "))
        self.title_label.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\"><img src=\"nord-logo.png\"/></p></body></html>"))
        self.country_list_label.setText(_translate("MainWindow", "Countries"))
        self.auto_connect_box.setStatusTip(_translate("MainWindow", "Network Manager will auto-connect on system start"))
        self.auto_connect_box.setText(_translate("MainWindow", "Auto connect"))
        self.mac_changer_box.setStatusTip(_translate("MainWindow", "Randomize MAC address"))
        self.mac_changer_box.setText(_translate("MainWindow", "Randomize MAC"))
        self.killswitch_btn.setStatusTip(_translate("MainWindow", "Disables internet connection if VPN connectivity is lost"))
        self.killswitch_btn.setText(_translate("MainWindow", "Kill Switch"))
        self.server_type_select.setStatusTip(_translate("MainWindow", "Select Server Type"))
        self.connection_type_select.setStatusTip(_translate("MainWindow", "Select connection type"))
        self.connect_btn.setText(_translate("MainWindow", "Connect"))
        self.disconnect_btn.setText(_translate("MainWindow", "Disconnect"))
        self.label.setText(_translate("MainWindow", "Servers"))

    def retranslate_login_ui(self):
        _translate = QtCore.QCoreApplication.translate
        self.nord_image.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\"><img src=\"nordvpnicon.png\"/></p><p align=\"center\"><br/></p></body></html>"))
        self.user_label.setText(
            _translate("MainWindow", "<html><head/><body><p align=\"right\">Email:     </p></body></html>"))
        self.password_label.setText(
            _translate("MainWindow", "<html><head/><body><p align=\"right\">Password:     </p></body></html>"))
        self.login_btn.setText(_translate("MainWindow", "Login"))
        self.remember_checkBox.setText(_translate("MainWindow", "Remember"))


if __name__ == '__main__':
    app_name = "NordVPN"
    prctl.set_name(app_name)
    prctl.set_proctitle(app_name)
    app = QtWidgets.QApplication(sys.argv)
    ui = MainWindow()
    sys.exit(app.exec_())
