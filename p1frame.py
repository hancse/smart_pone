#! /usr/bin/python3


import sys
import os
import platform

from PyQt5.QtCore import Qt, QTimer, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QFrame, QToolButton, QGroupBox, QHBoxLayout, QVBoxLayout
from PyQt5.QtWidgets import QPlainTextEdit
from PyQt5.QtSerialPort import QSerialPort
import qtawesome as qta
import fontawesome as fa

from p1meter import P1Meter, P1Results


class P1Frame(QFrame):

    cmdAvailable = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__()

        self.parent = parent
        self.lastCmd = ""
        self.meter = P1Meter(self)
        self.p1Timer = QTimer(self)
        self.interval = 2000
        # self.sd = SerialDialog(self)

        self.initUI()
        self.setWindowTitle('Smart P1')

        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)

        gbConnect = QGroupBox("Connection", self)
        mainLayout.addWidget(gbConnect)

        connectLayout = QHBoxLayout()
        gbConnect.setLayout(connectLayout)

        font1 = QFont("Font Awesome 5 Free Solid", 24)
        font2 = QFont("Font Awesome 5 Free Solid", 32)

        self.btnConfig = QToolButton()
        self.btnConfig.setFont(font1)
        self.btnConfig.setText(fa.icons['cog'])
        # self.btnConfig.setGe

        self.btnConnect = QToolButton()
        self.btnConnect.setFont(font1)
        self.btnConnect.setText(fa.icons['link'])
        self.btnConnect.clicked.connect(self.onConnect)

        self.btnDisconnect = QToolButton()
        self.btnDisconnect.setFont(font1)
        self.btnDisconnect.setText(fa.icons['unlink'])
        self.btnDisconnect.clicked.connect(self.onDisconnect)

        connectLayout.addWidget(self.btnConnect)
        connectLayout.addWidget(self.btnDisconnect)
        connectLayout.addWidget(self.btnConfig)

        self.pte = QPlainTextEdit()
        self.pte.setMinimumSize(500, 700)
        mainLayout.addWidget(self.pte)

        self.p1Timer.setInterval(self.interval)

        self.meter.measRead.connect(self.displayMeas)
        self.cmdAvailable.connect(self.meter.writeData)
        # self.p1Timer.timeout.connect(on_btnWeigh_clicked()));

        print(sys.platform)
        # print(platform.uname())  # alternative
        if sys.platform == 'linux':
            self.portName = "/dev/ttyUSB0"
        elif sys.platform == "win32":
            self.portName = "COM4"

    def initUI(self):
        self.setGeometry(300, 300, 400, 300)


    def displayMeas(self, strList):
        self.pte.clear()
        for line in strList:
            self.pte.appendPlainText(line.strip())
        """
        mr = self.meter.getP1results()
        if (mr.kernError):
            self.lblResult.setStyleSheet("QLabel { background-color : black; color : red; }");
        else:
            self.lblResult.setText( QString("%1%2").arg(kr.kernWeight, 0, 'f', 2).arg(ustr) );
            if (mr.kernStable):
                self.lblResult.setStyleSheet("QLabel { background-color : black; color : lime; }");
            else:
                # self.lblResult.setStyleSheet("QLabel { background-color : black; color : orange; }");
        """

    def onConnect(self):
        # p = sd.getCp()
        print(self.portName)
        self.meter.openSerialPort(self.portName, 115200,
                                  QSerialPort.Data8,
                                  QSerialPort.NoParity,
                                  QSerialPort.OneStop,
                                  QSerialPort.NoFlowControl)


    def onDisconnect(self):
        self.meter.closeSerialPort()


    def config(self):
        ...
        # sd->setModal(true);
        # sd->show();


    def auto(self, checked):
        if (checked):
            self.p1Timer.start()
        else:
            self.p1Timer.stop()

if __name__ == "__main__":
    app = QApplication([])
    test_frame = P1Frame()
    test_frame.show()
    app.exec_()

