# -*- coding: utf-8 -*-

import sys
import requests
from collections import namedtuple
from PyQt5 import QtCore, QtGui, QtWidgets

connection_type_options = ['UDP', 'TCP']
server_type_options = ['P2P', 'Standard', 'Double VPN', 'TOR over VPN', 'Dedicated IP', 'Anti-DDoS']
ServerInfo = namedtuple('ServerInfo', 'name, domain, country, server_type, connection_type')
api = "https://api.nordvpn.com/server"

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setObjectName("MainWindowObject")
        self.resize(600, 650)
        self.setWindowIcon(QtGui.QIcon('nordvpnicon.png'))
        QtWidgets.QApplication.setStyle("breeze")
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
        self.center_on_screen()
        self.show()

        self.api_data = self.get_api_data()
        server_country_list = self.get_country_list(self.api_data)
        self.connection_type_select.addItems(connection_type_options)
        self.server_type_select.addItems(server_type_options)
        self.country_list.addItems(server_country_list)
        self.country_list.setCurrentRow(0)
        item = self.country_list.currentItem()
        self.country_list.itemClicked.connect(self.get_server_list)


        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)
        QtWidgets.QApplication.processEvents()


    def get_api_data(self):
        try:
            resp = requests.get(api, timeout=5)
            if resp.status_code is requests.codes.ok:
                return resp.json()
            else:
                print("Get API failed")
        except Exception as ex:
            print("Get API failed")

    def get_country_list(self, api_data):
        server_country_list = []
        for server in api_data:
            country = server['country']
            if country not in server_country_list:
                server_country_list.append(country)
        return sorted(server_country_list)

    def get_server_list(self):
        server_name_list = []
        filtered = self.country_list.currentItem().text()
        self.server_list.clear()
        for server in self.api_data:
            name = server['name']
            load = server['load']
            country = server['country']
            categories = server['categories']
            server_categories = ''
            for category in categories:
                if category['name'] == 'Standard VPN servers':
                    server_categories += 'Standard '
                else:
                    server_categories += category['name'] + ' '
            if (name not in server_name_list) and (country == filtered):
                server_name_list.append(name + '\n' + 'Load: ' + str(load) + '%\n' + "Categories: " + server_categories)
        self.server_list.addItems(sorted(server_name_list))
        QtWidgets.QApplication.processEvents()
        self.retranslateUi()



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


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ui = MainWindow()
    sys.exit(app.exec_())
