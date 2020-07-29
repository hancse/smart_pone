#!/usr/bin/python

import numpy as np
from PyQt5.QtCore import QObject, QIODevice, pyqtSignal
# from PyQt5.QtGui import
from PyQt5.QtSerialPort import QSerialPort
from dataclasses import dataclass
import re


@dataclass
class P1Results:
    UsedEnergy1: np.zeros(1)
    UsedEnergy2: np.zeros(1)
    GeneratedEnergy1: np.zeros(1)
    GeneratedEnergy2: np.zeros(1)
    UsedPower: np.zeros(1)
    GeneratedPower: np.zeros(1)
    UsedGas: np.zeros(1)

class P1Meter(QObject):

    measRead = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__()

        self.parent = parent
        self.results = P1Results(0, 0, 0, 0, 0, 0, 0)
        self.serial = QSerialPort(self)
        self.serialbuffer = [] # empty list
        # self.serialbuffer = bytearray(b'')
        self.lastKernCmd = b""


        # make connections(see Terminal example)
        self.serial.error.connect(self.handleError)
        self.serial.readyRead.connect(self.readData)

    # Getters and Setters
    def getP1Results(self):
        return self.results

    def openSerialPort(self, name, baudRate, dataBits, parity, stopBits, flowControl):
        # p = sd.getCp()
        self.serial.setPortName(name)
        self.serial.setBaudRate(baudRate)
        self.serial.setDataBits(dataBits)
        self.serial.setParity(parity)
        self.serial.setStopBits(stopBits)
        self.serial.setFlowControl(flowControl)
        if self.serial.open(QIODevice.ReadWrite):
            print("Connected to %s : %d, %d, %d, %d, %d"
                  % (name, baudRate, dataBits, parity, stopBits, flowControl))
        else:
            print("Error", self.serial.errorString())

    def closeSerialPort(self):
        if self.serial.isOpen():
            self.serial.close()

    def parseP1(self, p1data):
        # Store the vaules in a dictionary:
        tel_code_val = dict()
        for line in self.telegram:
            if re.match('\d', line):    # line starts with a number
                # print(line)
                obis_code, value_unit = self.split_obis(line)
                tel_code_val[obis_code] = value_unit


        self.results.UsedEnergy1 = tel_code_val["1-0:1.8.1"]
        self.results.UsedEnergy2 = tel_code_val["1-0:1.8.2"]
        self.results.GeneratedEnergy1 = tel_code_val["1-0:2.8.1"]
        self.results.GeneratedEnergy2 = tel_code_val["1-0:2.8.2"]
        self.results.UsedPower = tel_code_val["1-0:1.7.0"]
        self.results.GeneratedPower = tel_code_val["1-0:2.7.0"]
        self.results.UsedGas = tel_code_val["0-1:24.2.1"]

        self.measRead.emit()



# https://stackoverflow.com/questions/4894069/regular-expression-to-return-text-between-parenthesis
# https://stackoverflow.com/questions/50799964/extract-specific-pattern-from-text-python-3?noredirect=1&lq=1
# https://stackoverflow.com/questions/8040795/how-can-i-get-a-value-thats-inside-parentheses-in-a-string-in-python?noredirect=1&lq=1

    def split_obis(self, s: str):
        left = s.find("(")
        right = s.find(")")
        code = s[:left-1]
        value = s[left+1:right]
        return code, value

    def handleError(self, error):
        if error == QSerialPort.ResourceError:
            print("Critical Error", self.serial.errorString)
            self.closeSerialPort()

    def writeData(self, data):
        print(data)
        self.serial.write(data)

    def readData(self):
        while self.serial.canReadLine():
            serialdata = self.serial.readLine()   # returns bytes
            # reads in data line by line, separated by \n or  \r characters
            if re.match(b"/", serialdata):
                self.serialbuffer.clear()
                #print("Buffer cleared")
            # print(serialdata)
            # print(type(serialdata))
            self.serialbuffer.append(str(serialdata.data(), encoding='utf-8'))
            # print("line added")
            if re.match(b"!", serialdata):
                #print("telegram complete")
                #print(self.serialbuffer)            # QByteArray
                self.telegram = self.serialbuffer
                # print(type(self.telegram))
                # print("--------------------------------------")
                # for line in self.telegram:
                #    print(line.strip())

                    # self.parseP1(line)
                # print("--------------------------------------")
                self.measRead.emit(self.telegram)

# https://forum.qt.io/topic/85064/qbytearray-to-string

    # str(qba.data(), encoding='utf-8')

    def readData2(self):
        serialdata = self.serial.readAll()
        print(serialdata)
        # self.parseP1(serialdata.rstrip())


