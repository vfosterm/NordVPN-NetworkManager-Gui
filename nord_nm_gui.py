# -*- coding: utf-8 -*-

import sys
import os
import requests
import shutil
import json
import hashlib
import time
import tempfile
import subprocess
from network_manager import ConnectionConfig, get_current_user
from collections import namedtuple
from PyQt5 import QtCore, QtGui, QtWidgets

connection_type_options = ['UDP', 'TCP']
server_type_options = ['P2P', 'Standard', 'Double VPN', 'TOR over VPN', 'Dedicated IP', 'Anti-DDoS', 'Obfuscated Server']
api = "https://api.nordvpn.com/server"
tmp = os.path.join(tempfile.gettempdir(), '.nordnm_gui_conf')
ServerInfo = namedtuple('ServerInfo', 'name, country, domain, type, load')


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setObjectName("MainWindowObject")
        self.setWindowIcon(QtGui.QIcon('nordvpnicon.png'))
        self.config_path = os.path.join(os.path.abspath(os.getcwd()), '.configs')
        self.api_data = self.get_api_data()
        self.username = None
        self.password = None
        self.domain_list = []
        self.server_info_list = []
        self.login_ui()
        self.show()

    def main_ui(self):
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

        server_country_list = self.get_country_list(self.api_data)
        self.connection_type_select.addItems(connection_type_options)
        self.server_type_select.addItems(server_type_options)
        self.country_list.addItems(server_country_list)
        self.country_list.itemClicked.connect(self.get_server_list)
        self.server_type_select.currentTextChanged.connect(self.get_server_list)
        self.connect_btn.clicked.connect(self.connect)

        self.center_on_screen()
        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)
        QtWidgets.QApplication.processEvents()
        self.show()

    def login_ui(self):
        self.resize(558, 468)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setWindowTitle("")
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
        spacerItem = QtWidgets.QSpacerItem(80, 20, QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.login_btn = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.login_btn.sizePolicy().hasHeightForWidth())
        self.login_btn.setSizePolicy(sizePolicy)
        self.login_btn.setObjectName("login_btn")
        self.horizontalLayout_3.addWidget(self.login_btn)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.gridLayout.addLayout(self.verticalLayout_2, 0, 0, 1, 1)
        self.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        self.center_on_screen()
        self.retranslate_login_ui()
        QtCore.QMetaObject.connectSlotsByName(self)

        self.password_input.returnPressed.connect(self.login_btn.click)
        self.login_btn.clicked.connect(self.verify_credentials)

    def verify_credentials(self):
        try:
            resp = requests.get('https://api.nordvpn.com/token/token/' + self.user_input.text(), timeout=5)
            if resp.status_code == requests.codes.ok:
                token_json = json.loads(resp.text)
                token = token_json['token']
                salt = token_json['salt']
                key = token_json['key']

                password_hash = hashlib.sha512(salt.encode() + self.password_input.text().encode())
                final_hash = hashlib.sha512(password_hash.hexdigest().encode() + key.encode())

                try:
                    resp = requests.get('https://api.nordvpn.com/token/verify/' + token + '/' + final_hash.hexdigest(), timeout=5)
                    if resp.status_code == requests.codes.ok:
                        self.statusbar.showMessage('Login Success', 2000)
                        self.username = self.user_input.text()
                        self.password = self.password_input.text()
                        time.sleep(0.5)
                        self.hide()
                        self.main_ui()
                    else:
                        self.statusbar.showMessage('Invalid Credentials', 2000)
                        self.user_input.clear()
                        self.password_input.clear()
                        self.user_input.setFocus()
                except Exception as ex:
                    self.statusbar.showMessage('Invalid Credentials', 2000)
                    self.user_input.clear()
                    self.password_input.clear()
                    self.user_input.setFocus()
            else:
                self.statusbar.showMessage("API Error: could not fetch token", 2000)
        except Exception as ex:
            self.statusbar.showMessage("API Error: could not fetch token", 2000)

    def get_api_data(self):
        try:
            resp = requests.get(api, timeout=5)
            if resp.status_code == requests.codes.ok:
                return resp.json()
            else:
                self.statusbar.showMessage("Get API failed", 2000)
        except Exception as ex:
            self.statusbar.showMessage("Get API failed", 2000)

    def get_country_list(self, api_data):
        server_country_list = []
        for server in api_data:
            country = server['country']
            if country not in server_country_list:
                server_country_list.append(country)
        return sorted(server_country_list)

    def get_server_list(self):

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

                elif category['name'] == 'Onion over VPN':
                    server_categories += category['name'] + ' '
                    server_category_list.append('TOR over VPN')
                else:
                    server_categories += category['name'] + ' '
            if (name not in server_name_list) and (country == filtered[0]) and (filtered[1] in server_category_list):
                server_name_list.append(name + '\n' + 'Load: ' + str(load) + '%\n' + "Domain: " + domain + '\n' + "Categories: " + server_categories)
                self.domain_list.append(domain)
                server = ServerInfo(name=name, country=country, domain=domain, type=server_category_list, load=load)
                self.server_info_list.append(server)

        if server_name_list:
            server_name_list, self.domain_list, self.server_info_list = (list(x) for x in zip(*sorted(zip(server_name_list, self.domain_list, self.server_info_list), key=lambda x: x[2].load)))
            self.server_list.addItems(server_name_list)
        else:
            self.server_list.addItem("No Servers Found")
        QtWidgets.QApplication.processEvents()
        self.retranslateUi()

    def get_ovpn(self):
        # https://downloads.nordcdn.com/configs/files/ovpn_udp/servers/sg173.nordvpn.com.udp.ovpn
        self.ovpn_path = None
        if self.connection_type_select.currentText() == 'UDP':
            filename = self.domain_list[self.server_list.currentRow()] + '.udp.ovpn'
            ovpn_file = requests.get('https://downloads.nordcdn.com/configs/files/ovpn_udp/servers/' + filename, stream=True)
            if ovpn_file.status_code == requests.codes.ok:
                self.ovpn_path = os.path.join(self.config_path, filename)
                with open(self.ovpn_path, 'wb') as out_file:
                    shutil.copyfileobj(ovpn_file.raw, out_file)
            else: self.statusbar.showMessage('Error fetching configuration files', 2000)
        elif self.connection_type_select.currentText() == 'TCP':
            filename = self.domain_list[self.server_list.currentRow()] + '.tcp.ovpn'
            ovpn_file = requests.get('https://downloads.nordcdn.com/configs/files/ovpn_tcp/servers/' + filename, stream=True)
            if ovpn_file.status_code == requests.codes.ok:
                self.ovpn_path = os.path.join(self.config_path, filename)
                with open(self.ovpn_path , 'wb') as out_file:
                    shutil.copyfileobj(ovpn_file.raw, out_file)
            else: self.statusbar.showMessage('Error fetching configuration files', 2000)
        self.server_list.setFocus()

    def generate_connection_name(self):
        server = self.server_info_list[self.server_list.currentRow()]
        category_name = ''
        for i, category in enumerate(server.type):
            if i > 0:
                category_name += ' | ' + category
            else:
                category_name = category

        connection_name = server.name + ' [' + category_name + '] [' + self.connection_type_select.currentText() + ']'
        return connection_name

    def import_connection(self):
        connection_name = self.generate_connection_name()
        ovpn_file = connection_name + '.ovpn'

        path = os.path.join(self.config_path, ovpn_file)
        shutil.copy(self.ovpn_path, os.path.join(path))
        output = subprocess.run(['nmcli', 'connection', 'import', 'type', 'openvpn', 'file', path])
        output.check_returncode()

        config = ConnectionConfig(connection_name)
        if config.path:
            if self.username and self.password:
                config.set_credentials(self.username, self.password)
            config.disable_ipv6()
            config.set_dns_nameservers(dns_list=None)
            user = get_current_user()
            config.set_user(user)
            config.save()
        else:
            print("error")

    def connect(self):
        self.get_ovpn()
        self.import_connection()

    def center_on_screen(self):
        resolution = QtWidgets.QDesktopWidget().screenGeometry()
        self.move(int((resolution.width() / 2) - (self.frameSize().width() / 2)), int((resolution.height() / 2) - (self.frameSize().height() / 2)))

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", " "))
        self.title_label.setText(_translate("MainWindow", "<html><head/><body><pre align=\"center\" style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a name=\"maincontent\"/><span style=\" font-family:\'SF Mono\'; font-size:6pt;\">█</span><span style=\" font-family:\'SF Mono\'; font-size:6pt;\">██╗   ██╗ ██████╗ ██████╗ ██████╗ ██╗   ██╗██████╗ ███╗   ██╗</span></pre><pre align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SF Mono\'; font-size:6pt;\">████╗  ██║██╔═══██╗██╔══██╗██╔══██╗██║   ██║██╔══██╗████╗  ██║</span></pre><pre align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SF Mono\'; font-size:6pt;\">██╔██╗ ██║██║   ██║██████╔╝██║  ██║██║   ██║██████╔╝██╔██╗ ██║</span></pre><pre align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SF Mono\'; font-size:6pt;\">██║╚██╗██║██║   ██║██╔══██╗██║  ██║╚██╗ ██╔╝██╔═══╝ ██║╚██╗██║</span></pre><pre align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SF Mono\'; font-size:6pt;\">██║ ╚████║╚██████╔╝██║  ██║██████╔╝ ╚████╔╝ ██║     ██║ ╚████║</span></pre><pre align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SF Mono\'; font-size:6pt;\">╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝╚═════╝   ╚═══╝  ╚═╝     ╚═╝  ╚═══╝</span></pre></body></html>"))
        self.country_list_label.setText(_translate("MainWindow", "Country List"))
        self.auto_connect_box.setStatusTip(_translate("MainWindow", "Network Manager will auto-connect on system start"))
        self.auto_connect_box.setText(_translate("MainWindow", "Auto connect"))
        self.mac_changer_box.setStatusTip(_translate("MainWindow", "Randomize MAC address"))
        self.mac_changer_box.setText(_translate("MainWindow", "Randomize MAC"))
        self.killswitch_btn.setStatusTip(_translate("MainWindow", "Disables internet connection if VPN connectivity is lost"))
        self.killswitch_btn.setText(_translate("MainWindow", "Kill Switch"))
        self.server_type_select.setStatusTip(_translate("MainWindow", "Select Server Type"))
        self.connection_type_select.setStatusTip(_translate("MainWindow", "Select connection type"))
        self.connect_btn.setText(_translate("MainWindow", "Connect"))
        self.label.setText(_translate("MainWindow", "Server List"))

    def retranslate_login_ui(self):
        _translate = QtCore.QCoreApplication.translate
        self.nord_image.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\"><img src=\"nordvpnicon.png\"/></p><p align=\"center\"><br/></p></body></html>"))
        self.user_label.setText(
            _translate("MainWindow", "<html><head/><body><p align=\"right\">Email:     </p></body></html>"))
        self.password_label.setText(
            _translate("MainWindow", "<html><head/><body><p align=\"right\">Password:     </p></body></html>"))
        self.login_btn.setText(_translate("MainWindow", "Login"))


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ui = MainWindow()
    sys.exit(app.exec_())
