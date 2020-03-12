# -*- coding: utf-8 -*-
"""
Created on Fri Jun 16 09:51:31 2017

@author: v-stpurc
"""
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QRadioButton, QVBoxLayout, QCheckBox, QProgressBar,
    QGroupBox, QComboBox, QLineEdit, QPushButton, QMessageBox, QInputDialog, QDialog, QDialogButtonBox, QSlider)
from PyQt5.QtGui import QIcon, QPainter, QPen, QFont, QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QCoreApplication, QObject, QRunnable, QThread, QThreadPool, pyqtSignal, pyqtSlot

sys.path.append("C:\\Users\\v-stpurc\\Documents\\Python_Port\\instrument_Libraries\\")

#import visa
import time
#import threading 
import waveFormLib
import chromaLib
import tekScopeLib
import socket_instrument
#import xlsxwriter
import timerThread
import dutInfoDialog

version_Info = "Python PyQt5 Slammer Frequency Sweep V0.1"

        
class MainWindow(QWidget):

    StartFreq = 0
    StopFreq = 0
    Steps = 0
    
    Scope = 0
    Waveform = 0
    Loade = 0
    
    slammer = 0

    duty = 0
    edgeTimes = 0
    amplitude = 0
    configID = 0
    pcbaSN = 0
    productSN = 0
    scopeType = 0
    probeType = 0 
    runNotes = 0 
    vregText = 0 
    vregSelection = 0

#    workBook = 0 
#    workSheet = 0 
    vout_DC_Value = 0  
    limitsGood = 0 
    

    sense_Resistor = 0
    
    slamLoad = 0
    chromaLoad = 0
    
    scopeShot_Signal = pyqtSignal(str)
    
    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.initUI()
#        self.openInstruments()
        self.createRadioButtonGroup()
        #Bring up a default look on scope
#        self.configureScope()
 
       
    def initUI(self):
        
        self.setGeometry(300, 300, 1000, 300)
        self.setWindowTitle('Micro Slammer Frequency Sweep Test')
        self.setWindowIcon(QIcon('xbox_icon.ico')) 
        
        self.scopeLabel = QLabel(self)
        self.scopeLabel.setGeometry(10,15,200,10)
        self.scopeLabel.setText("Scope")
    
        self.waveformLabel = QLabel(self)
        self.waveformLabel.setGeometry(10,30,200,10)
        self.waveformLabel.setText("Waveform Generator")
    
        self.loadLabel = QLabel(self)
        self.loadLabel.setGeometry(10,45,200,10)
        self.loadLabel.setText("Chroma Load")
  
        self.IP1 = QLabel(self)
        self.IP1.setGeometry(155, 2, 50, 10)
        self.IP1.setText("IP1")
    
        self.IP2 = QLabel(self)
        self.IP2.setGeometry(190, 2, 50, 10)
        self.IP2.setText("IP2")
    
        self.IP3 = QLabel(self)
        self.IP3.setGeometry(225, 2, 50, 10)
        self.IP3.setText("IP3")
    
        self.IP4 = QLabel(self)
        self.IP4.setGeometry(260, 2, 50, 10)
        self.IP4.setText("IP4")
    
        self.Port = QLabel(self)
        self.Port.setGeometry(295, 2, 50, 10)
        self.Port.setText("Port")
    
        self.scopeAddr1LineEdit = QLineEdit(self)
        self.scopeAddr1LineEdit.setGeometry(150, 15, 30, 13)
        self.scopeAddr1LineEdit.setText("10")
        
        self.scopeAddr2LineEdit = QLineEdit(self)
        self.scopeAddr2LineEdit.setGeometry(185, 15, 30, 13)
        self.scopeAddr2LineEdit.setText("178")
        
        self.scopeAddr3LineEdit = QLineEdit(self)
        self.scopeAddr3LineEdit.setGeometry(220, 15, 30, 13)
        self.scopeAddr3LineEdit.setText("77")
        
        self.scopeAddr4LineEdit = QLineEdit(self)
        self.scopeAddr4LineEdit.setGeometry(255, 15, 30, 13)
        self.scopeAddr4LineEdit.setText("105")
        
        self.scopePortLineEdit = QLineEdit(self)
        self.scopePortLineEdit.setGeometry(290, 15, 40, 13)
        self.scopePortLineEdit.setText("4000")
        
        self.waveAddr1LineEdit = QLineEdit(self)
        self.waveAddr1LineEdit.setGeometry(150, 30, 30, 13)
        self.waveAddr1LineEdit.setText("10")
        
        self.waveAddr2LineEdit = QLineEdit(self)
        self.waveAddr2LineEdit.setGeometry(185, 30, 30, 13)
        self.waveAddr2LineEdit.setText("178")
        
        self.waveAddr3LineEdit = QLineEdit(self)
        self.waveAddr3LineEdit.setGeometry(220, 30, 30, 13)
        self.waveAddr3LineEdit.setText("76")
        
        self.waveAddr4LineEdit = QLineEdit(self)
        self.waveAddr4LineEdit.setGeometry(255, 30, 30, 13)
        self.waveAddr4LineEdit.setText("127")
        
        self.wavePortLineEdit = QLineEdit(self)
        self.wavePortLineEdit.setGeometry(290, 30, 40, 13)
        self.wavePortLineEdit.setText("5025")
        
        self.loadAddr1LineEdit = QLineEdit(self)
        self.loadAddr1LineEdit.setGeometry(150, 45, 30, 13)
        self.loadAddr1LineEdit.setText("10")
        
        self.loadAddr2LineEdit = QLineEdit(self)
        self.loadAddr2LineEdit.setGeometry(185, 45, 30, 13)
        self.loadAddr2LineEdit.setText("178")
        
        self.loadAddr3LineEdit = QLineEdit(self)
        self.loadAddr3LineEdit.setGeometry(220, 45, 30, 13)
        self.loadAddr3LineEdit.setText("76")
        
        self.loadAddr4LineEdit = QLineEdit(self)
        self.loadAddr4LineEdit.setGeometry(255, 45, 30, 13)
        self.loadAddr4LineEdit.setText("102")
        
        self.loadPortLineEdit = QLineEdit(self)
        self.loadPortLineEdit.setGeometry(290, 45, 40, 13)
        self.loadPortLineEdit.setText("2101")
        
        self.font = QFont()
        self.font.setBold(False)
        self.font.setPointSize(10)
        self.getInstrumentsButton = QPushButton('Get Instruments', self)
        self.getInstrumentsButton.setFont(self.font)
        self.getInstrumentsButton.setGeometry(350, 20, 100, 30)
        self.getInstrumentsButton.clicked.connect(self.openInstruments)
        
        self.slammerGroupBox = QGroupBox(self)
        self.slammerGroupBox.setGeometry(10, 65, 120, 65)
        self.slammerGroupBox.setTitle("Slammer Rev Selection")
        
        self.enableExtraFeatures = QCheckBox('Enable Extra Features', self)
        self.enableExtraFeatures.move(500, 10)
        self.enableExtraFeatures.stateChanged.connect(self.extraFeatures)
        
        self.progressBar = QProgressBar(self)
        self.progressBar.setGeometry(500, 40, 500, 10)
        
        self.progressLabel = QLabel(self)
        self.progressLabel.setGeometry(700, 22, 100, 10)
        self.progressLabel.setText("Test Progress")
        
        vregLabel = QLabel(self)
        vregLabel.setGeometry(150, 60, 80, 20)
        vregLabel.setText("Vreg Selection")
        
        self.vregComboBox = QComboBox(self)
        self.vregComboBox.setGeometry(150, 85, 80, 20)
        
        self.vregComboBox.addItem("V_MEMPHY")
        self.vregComboBox.addItem("V_MEMIO")
        self.vregComboBox.addItem("V_3P3")
        self.vregComboBox.addItem("V_FUSE")
        self.vregComboBox.addItem("V_SOCPHY")
        self.vregComboBox.addItem("V_SOC1P8")
        self.vregComboBox.addItem("V_NBCORE")
        self.vregComboBox.addItem("V_GFXCORE")
        self.vregComboBox.addItem("V_CPUCORE")
        self.vregComboBox.setCurrentIndex(7)
        
        self.vregComboBox.currentIndexChanged.connect(self.vregSelectionChange)

        slamLabel = QLabel(self)
        slamLabel.setGeometry(250, 60, 80, 20)
        slamLabel.setText("Slammer Load")
        
        self.slamComboBox = QComboBox(self)
        self.slamComboBox.setGeometry(250, 85, 60, 20)
        
        self.slamComboBox.addItem("200")
        self.slamComboBox.addItem("150")
        self.slamComboBox.addItem("100")
        self.slamComboBox.addItem("50")
       
        self.slamComboBox.currentIndexChanged.connect(self.slamSelectionChange)

        chromaLabel = QLabel(self)
        chromaLabel.setGeometry(335, 60, 80, 20)
        chromaLabel.setText("Chroma Load")
        
        self.chromaComboBox = QComboBox(self)
        self.chromaComboBox.setGeometry(335, 85, 60, 20)
        
        self.chromaComboBox.addItem("0")
       
        self.chromaComboBox.currentIndexChanged.connect(self.chromaSelectionChange)

        startFreqLabel = QLabel(self)
        startFreqLabel.setGeometry(420, 60, 95, 20)
        startFreqLabel.setText("Starting Frequency")
        
        self.startFreqLineEdit = QLineEdit(self)
        self.startFreqLineEdit.setGeometry(420, 85, 95, 20)
        self.startFreqLineEdit.setText("70000")
        
        stopFreqLabel = QLabel(self)
        stopFreqLabel.setGeometry(535, 60, 95, 20)
        stopFreqLabel.setText("Ending Frequency")
        
        self.stopFreqLineEdit = QLineEdit(self)
        self.stopFreqLineEdit.setGeometry(535, 85, 95, 20)
        self.stopFreqLineEdit.setText("130000")
        
        stepsLabel = QLabel(self)
        stepsLabel.setGeometry(650, 60, 150, 20)
        stepsLabel.setText("Number of Frequency Steps")
        
        self.stepsLineEdit = QLineEdit(self)
        self.stepsLineEdit.setGeometry(650, 85, 95, 20)
        self.stepsLineEdit.setText("60")
        
        self.startStopButton = QPushButton('Start Test', self)
        self.startStopButton.setGeometry(800, 70, 180, 50)

        self.font.setBold(True)
        self.font.setPointSize(16)
        self.startStopButton.setFont(self.font)
        self.startStopButton.setStyleSheet("background-color: lightgray")
        self.startStopButton.setText("Start Test")
        self.startStopButton.clicked[bool].connect(self.startStopTest)
        self.startStopButton.setEnabled(False)
        
        self.slammer = 2
        
        self.pictureLabel = QLabel(self)
        self.pictureLabel.setGeometry(10, 140, 200, 150)
        self.pictureLabel.setText("Current Scope Shot")
        self.pictureLabel.setScaledContents(True)
        pixmap = QPixmap("xbox_icon.ico")
        self.pictureLabel.setPixmap(pixmap)

        self.stepLabel = QLabel(self)
        self.stepLabel.setGeometry(230, 140, 150, 15)
        self.stepLabel.setText("Step")

        self.freqLabel = QLabel(self)
        self.freqLabel.setGeometry(230, 160, 150, 15)
        self.freqLabel.setText("Frequency")

        self.pktopkLabel = QLabel(self)
        self.pktopkLabel.setGeometry(230, 180, 150, 15)
        self.pktopkLabel.setText("Peak to Peak")

        self.maxLabel = QLabel(self)
        self.maxLabel.setGeometry(230, 200, 150, 15)
        self.maxLabel.setText("Maximum")

        self.minLabel = QLabel(self)
        self.minLabel.setGeometry(230, 220, 150, 15)
        self.minLabel.setText("Minimum")

        self.overLabel = QLabel(self)
        self.overLabel.setGeometry(230, 240, 150, 15)
        self.overLabel.setText("Overshoot")

        self.underLabel = QLabel(self)
        self.underLabel.setGeometry(230, 260, 150, 15)
        self.underLabel.setText("Undershoot")
        
        self.dutyCycleSlider = QSlider(Qt.Horizontal, self)
        self.dutyCycleSlider.setFocusPolicy(Qt.NoFocus)
        self.dutyCycleSlider.setRange(1, 50)
        self.dutyCycleSlider.setValue(50)
        self.dutyCycleSlider.setGeometry(720, 150, 200, 20)
        self.dutyCycleSlider.setEnabled(False)
        self.dutyCycleSlider.valueChanged[int].connect(self.dutyChanged)
        
        self.dutyLabel = QLabel(self)
        self.dutyLabel.setGeometry(795, 134, 100, 15)
        self.dutyLabel.setText("Duty Cycle")

        self.dutyLineEdit = QLineEdit(self)
        self.dutyLineEdit.setGeometry(930, 150, 50, 20)
        self.dutyLineEdit.setText("50%")
        self.dutyLineEdit.setReadOnly(True)

        self.edgeTimeSlider = QSlider(Qt.Horizontal, self)
        self.edgeTimeSlider.setFocusPolicy(Qt.NoFocus)
        self.edgeTimeSlider.setRange(3, 500)
        self.edgeTimeSlider.setValue(200)
        self.edgeTimeSlider.setGeometry(720, 180, 200, 20)
        self.edgeTimeSlider.setEnabled(False)
        self.edgeTimeSlider.valueChanged[int].connect(self.edgeTimeChanged)
        
        self.edgeTimeLabel = QLabel(self)
        self.edgeTimeLabel.setGeometry(795, 164, 100, 15)
        self.edgeTimeLabel.setText("Edge Times")

        self.edgeTimeLineEdit = QLineEdit(self)
        self.edgeTimeLineEdit.setGeometry(930, 180, 50, 20)
        self.edgeTimeLineEdit.setText("200ns")
        self.edgeTimeLineEdit.setReadOnly(True)

        self.singleFreqCheckBox = QCheckBox('Single Frequency Slam', self)
        self.singleFreqCheckBox.move(400, 150)
        self.singleFreqCheckBox.stateChanged.connect(self.singleFrequencySlam)
        self.singleFreqCheckBox.setEnabled(False)
        self.singleFreqCheckBox.setChecked(False)
        
        self.font.setPointSize(14)
        self.scopeShotButton = QPushButton('Get Scope Shot', self)
        self.scopeShotButton.setGeometry(530, 143, 160, 30)
        self.scopeShotButton.setFont(self.font)
        self.scopeShotButton.setStyleSheet('QPushButton {background-color: #A3C1DA; color: black;}')
        self.scopeShotButton.clicked[bool].connect(self.getScopeShot)
        self.scopeShotButton.setEnabled(False)
        self.scopeShotButton.setStyleSheet("background-color: lightgray")
        
        self.useChromaCheckBox = QCheckBox('Use Chroma Load', self)
        self.useChromaCheckBox.move(400, 180)
        self.useChromaCheckBox.stateChanged.connect(self.singleFrequencySlam)
        self.useChromaCheckBox.setEnabled(False)
        self.useChromaCheckBox.setChecked(False)
 
        self.font.setPointSize(12)
        self.quitButton = QPushButton('Quit', self)
        self.quitButton.setFont(self.font)
        self.quitButton.setGeometry(890, 260, 100, 30)
        self.quitButton.clicked[bool].connect(self.closeEvent)

        self.show()

    def GetIPScope(self):
        ipString = self.scopeAddr1LineEdit.text() + '.' + self.scopeAddr2LineEdit.text() + '.' + self.scopeAddr3LineEdit.text() + '.' + self.scopeAddr4LineEdit.text()
        return ipString

    def GetIPWave(self):
        ipString = self.waveAddr1LineEdit.text() + '.' + self.waveAddr2LineEdit.text() + '.' + self.waveAddr3LineEdit.text() + '.' + self.waveAddr4LineEdit.text()
        return ipString

    def GetIPLoad(self):
        ipString = self.loadAddr1LineEdit.text() + '.' + self.loadAddr2LineEdit.text() + '.' + self.loadAddr3LineEdit.text() + '.' + self.loadAddr4LineEdit.text()
        return ipString

    def closeEvent(self, event):
        self.close()

    def getScopeShot(self):
        returnString = self.startStopButton.text()
        if returnString.find("Start Test") != -1:
            QMessageBox.about(self, "Test Not Started","Click the Start Test Button Before Capturing Scope Shot")
        else:
            self.scopeShot_Signal.emit('hi from main thread')
            self.scopeShotButton.setEnabled(False)
            self.scopeShotButton.setStyleSheet("background-color: lightgray")

    def singleFrequencySlam(self):
        if self.singleFreqCheckBox.isChecked():
#            print "do single Freq"
            self.stopFreqLineEdit.setEnabled(False)
            self.stopFreqLineEdit.clear()
            self.stepsLineEdit.setEnabled(False)
            self.stepsLineEdit.clear()
            self.scopeShotButton.setEnabled(True)
            self.scopeShotButton.setStyleSheet("background-color: yellow")
        else:
#            print "don't do single Freq"
            self.stopFreqLineEdit.setEnabled(True)
            self.stepsLineEdit.setEnabled(True)
            self.scopeShotButton.setEnabled(False)
            self.scopeShotButton.setStyleSheet("background-color: lightgray")
            
    def dutyChanged(self):
        dutyCycle = self.dutyCycleSlider.value()        
        self.dutyLineEdit.setText(str(dutyCycle) + "%")
      
    def edgeTimeChanged(self):
        edgeTime = self.edgeTimeSlider.value()        
        self.edgeTimeLineEdit.setText(str(edgeTime) + "ns")
        
    def extraFeatures(self):
        print "enable/disable extra features"
        if self.enableExtraFeatures.isChecked():
            self.dutyCycleSlider.setEnabled(True)
            self.edgeTimeSlider.setEnabled(True)
            self.singleFreqCheckBox.setEnabled(True)
            self.useChromaCheckBox.setEnabled(True)
        else:
            self.dutyCycleSlider.setEnabled(False)
            self.edgeTimeSlider.setEnabled(False)
            self.dutyCycleSlider.setValue(50)
            self.edgeTimeSlider.setValue(200)
            self.dutyLineEdit.setText("50%")
            self.edgeTimeLineEdit.setText("200ns")
            self.singleFreqCheckBox.setEnabled(False)
            self.singleFreqCheckBox.setChecked(False)
            self.stopFreqLineEdit.setEnabled(True)
            self.useChromaCheckBox.setEnabled(False)
            self.useChromaCheckBox.setChecked(False)

    def runLoop(self, stepCount, fileName, frequency, pktopk, maximum, minimum, overshoot, undershoot):
        pixmap = QPixmap(fileName)
        self.pictureLabel.setPixmap(pixmap)
        self.progressBar.setValue(int(stepCount))
        self.stepLabel.setText  ("Step:\t\t" + str(stepCount))
        self.freqLabel.setText  ("Frequency:\t" + str(frequency))
        self.pktopkLabel.setText("Peak to Peak:\t" + str(pktopk))
        self.maxLabel.setText   ("Maximum:\t" + str(maximum))
        self.minLabel.setText   ("Minimum:\t\t" + str(minimum))
        self.overLabel.setText  ("Overshoot:\t" + str(overshoot))
        self.underLabel.setText ("Undershoot:\t" + str(undershoot))

        if self.singleFreqCheckBox.isChecked():
            self.scopeShotButton.setEnabled(True)
            self.scopeShotButton.setStyleSheet("background-color: yellow")

    def quitLoop(self):
        
        self.progressBar.setValue(0)
        pixmap = QPixmap("xbox_icon.ico")
        self.pictureLabel.setPixmap(pixmap)
        self.stepLabel.setText  ("Step:")
        self.freqLabel.setText  ("Frequency:")
        self.pktopkLabel.setText("Peak to Peak:")
        self.maxLabel.setText   ("Maximum:")
        self.minLabel.setText   ("Minimum:")
        self.overLabel.setText  ("Overshoot:")
        self.underLabel.setText ("Undershoot:")

        chromaLib.setLoadOff(self.Load, 1)
        chromaLib.setLoadOff(self.Load, 5)
        chromaLib.setLoadOff(self.Load, 9)
        waveFormLib.pulseGen_Set_OutputOff(self.Waveform)
        
        self.startStopButton.setStyleSheet('QPushButton {background-color: #A3C1DA; color: black;}')
        self.startStopButton.setText("Start Test")
        
        self.thread.quit()
        print("Got quit signal")
        while self.thread.isFinished():
            print ("thread still here after quit")

    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False   
        
    def configureScope(self):
        
        returnString = self.Scope.query("*IDN?")
        if returnString.find("4104") != -1:
            self.messageXpos = 650
            self.messageYpos = 720
        elif returnString.find("3014") != -1:
            self.messageXpos = 20
            self.messageYpos = 20

        self.vregText = self.vregComboBox.currentText()
        tekScopeLib.scope_SetAnnotation(self.Scope, self.vregText, self.messageXpos, self.messageYpos)
        tekScopeLib.scope_SetChannel_Label(self.Scope, "CH1", self.vregText)
        tekScopeLib.scope_SetChannel_OnOff(self.Scope, "CH1", "ON")
        tekScopeLib.scope_SetChannel_Position(self.Scope, "CH1", "1")
        tekScopeLib.scope_SetChannel_Label(self.Scope, "CH2", "SW Node")
        tekScopeLib.scope_SetChannel_OnOff(self.Scope, "CH2", "ON")
        tekScopeLib.scope_SetChannel_Position(self.Scope, "CH2", "-3")
        tekScopeLib.scope_SetChannel_Label(self.Scope, "CH3", "Sense V")
        tekScopeLib.scope_SetChannel_OnOff(self.Scope, "CH3", "ON")
        tekScopeLib.scope_SetChannel_Position(self.Scope, "CH3", "-2")
        tekScopeLib.scope_SetChannel_Label(self.Scope, "CH4", "Sig Gen")
        tekScopeLib.scope_SetChannel_OnOff(self.Scope, "CH4", "ON")
        tekScopeLib.scope_SetChannel_Position(self.Scope, "CH4", "-4")
         
        tekScopeLib.scope_SetChannel_Bandwidth(self.Scope, "CH1", "TWEnty")
        tekScopeLib.scope_SetChannel_Bandwidth(self.Scope, "CH2", "TWEnty")
        tekScopeLib.scope_SetChannel_Bandwidth(self.Scope, "CH3", "TWEnty")
        tekScopeLib.scope_SetChannel_Bandwidth(self.Scope, "CH4", "TWEnty")
        
        tekScopeLib.scope_Set_Measurement(self.Scope, "1", "CH1", "MINIMUM")
        tekScopeLib.scope_Set_Measurement(self.Scope, "2", "CH1", "MAXIMUM")
        tekScopeLib.scope_Set_Measurement(self.Scope, "3", "CH1", "MEAN")
        tekScopeLib.scope_Set_Measurement(self.Scope, "4", "CH1", "pk2pk")
        tekScopeLib.scope_Set_Measurement(self.Scope, "5", "CH3", "MAXIMUM")
        tekScopeLib.scope_Set_Measurement(self.Scope, "6", "CH3", "RISE")
        tekScopeLib.scope_Set_Measurement(self.Scope, "7", "CH3", "FALL")
        
        tempString = "*CLS"
        self.Scope.write(tempString)
        tempString = "SAVe:ASSIgn:TYPe IMAGe"
        self.Scope.write(tempString)
        tempString = "SAVe:IMAGe:FILEFormat PNG"
        self.Scope.write(tempString)
        tempString = "HARDCOPY:PORT ETHERnet"
        self.Scope.write(tempString)
        tempString = "HARDCOPY START"
        self.Scope.write(tempString)
        time.sleep(2)

        print "before read raw"
        raw_data = self.Scope.read_raw()
        print "after read raw"

        fid = open("testfileName", 'wb')
        fid.write(raw_data)
        fid.close()    


        tekScopeLib.scope_Set_Statistics_Off(self.Scope)
        
    def startStopTest(self):
        returnString = self.startStopButton.text()
        if returnString.find("Start Test") != -1:
        
            dialog = dutInfoDialog.DutInfoDialog()
            dialog.setWindowModality(Qt.ApplicationModal)
            dialog.exec_()
            self.configID, self.pcbaSN, self.productSN, self.scopeType, self.probeType, self.runNotes, self.sense_Resistor = dialog.returnInfo()
 
            print "Test Started"

            self.startStopButton.setStyleSheet('QPushButton {background-color: #FF2000; color: black;}')
            self.startStopButton.font()
            self.startStopButton.setText("Abort Test")
            
            self.limitsGood = False
            if self.checkFreqLimits() == True:
                self.limitsGood = True
                print("limits Ok")
                
                self.vregText = self.vregComboBox.currentText()
                self.vregSelection = self.vregComboBox.currentIndex()
        
#                self.duty = 50
                self.amplitude = 0.1
                self.slamLoad = self.slamComboBox.currentText()
                self.chromaLoad = self.chromaComboBox.currentText()
                
                self.startThread()
            else:
                print("limits bad")
                #Recursive call seems to work for now
                self.startStopTest()
        else:
            print "Test Aborted"
            self.startStopButton.setStyleSheet('QPushButton {background-color: #A3C1DA; color: black;}')
            self.startStopButton.setText("Start Test")

            if self.limitsGood:
                self.thread.quit()
                self.work.stopTimer()
#               self.work.startStop = False

    def startThread(self):

        if self.singleFreqCheckBox.isChecked():
            self.StopFreq = 0
            self.Steps = 0
        
        self.duty = self.dutyCycleSlider.value()
        self.edgeTimes = self.edgeTimeSlider.value()
        
        parameterArray = [self.Scope, self.Load, self.Waveform, self.StartFreq, self.StopFreq, self.Steps, self.vregSelection,
                          self.vregText, self.configID, self.pcbaSN, self.productSN, self.scopeType, self.probeType, self.runNotes,
                          self.duty, self.edgeTimes, self.amplitude, self.slammer, self.sense_Resistor, self.slamLoad, self.chromaLoad]
#        self.work = TimerThread(self.Scope, self.Load, self.Waveform, self.StartFreq, self.StopFreq, self.Steps, self.vregSelection) 
        self.work = timerThread.TimerThread(parameterArray) 
        self.work.timerSignal.connect(self.runLoop)
        self.work.quitSignal.connect(self.quitLoop)
        self.scopeShot_Signal.connect(self.work.scopeShot_Slot)
        self.thread = QThread()

        self.work.moveToThread(self.thread)
        self.thread.started.connect(self.work.run)
        self.thread.start()

    def checkFreqLimits(self):
        returnString = self.startFreqLineEdit.text()
        if self.is_number(returnString): 
            self.StartFreq = float(returnString)
            if self.StartFreq < 1000 or self.StartFreq > 200000:
                QMessageBox.about(self, "Start Frequency Error","Start frequency must be between 1000 and 200000")
                return False
            print self.StartFreq
        else:
            QMessageBox.about(self, "Start Frequency Error","Start frequency entry is not a number")
            return False
                
        if self.singleFreqCheckBox.isChecked() == False:
            returnString = self.stopFreqLineEdit.text()
            if self.is_number(returnString): 
                self.StopFreq = float(returnString)
                if self.StopFreq < 1000 or self.StopFreq > 200000:
                    QMessageBox.about(self, "Stop Frequency Error","Stop frequency must be between 1000 and 200000")
                    return False
                print self.StopFreq
            else:
                QMessageBox.about(self, "Stop Frequency Error","Stop frequency entry is not a number")
                return False
             
            if self.StopFreq < self.StartFreq:
                QMessageBox.about(self, "Frequency Error","Stop frequency must be greater than start frequency")
                return False
               
            returnString = self.stepsLineEdit.text()
            if self.is_number(returnString): 
                self.Steps = float(returnString)
                if self.Steps < 0 or self.Steps > 300:
                    QMessageBox.about(self, "Step Count Error","Step count must be between 1 and 300")
                    return False
                print int(self.Steps)
            else:
                QMessageBox.about(self, "Step Count Error","Step count entry is not a number")
                return False
            
        progressMax = int(self.Steps)
        print "steps " + str(self.Steps)
        self.progressBar.setMaximum(progressMax)
        self.progressBar.setMinimum(0)

        return True

    def vregSelectionChange(self,index):
        print "Vreg index",index,"selection changed ",self.vregComboBox.currentText()
        if index == 7:
            self.slamComboBox.clear()  
            self.slamComboBox.addItem("200")
            self.slamComboBox.addItem("150")
            self.slamComboBox.addItem("100")
            self.slamComboBox.addItem("50")
        elif index == 8:
            self.slamComboBox.clear()  
            self.slamComboBox.addItem("25")
            self.slamComboBox.addItem("20")
            self.slamComboBox.addItem("15")
            self.slamComboBox.addItem("10")
            self.slamComboBox.addItem("5")
        else:
            self.slamComboBox.clear()  
            self.slamComboBox.addItem("20")
            self.slamComboBox.addItem("15")
            self.slamComboBox.addItem("10")
            self.slamComboBox.addItem("5")
            
            
      
    def slamSelectionChange(self,index):
        self.slamLoad = self.slamComboBox.currentText()
        print "Slam index",index,"selection changed. Slam Load ",self.slamLoad
        
        vregIndex = self.vregComboBox.currentIndex()
        if vregIndex == 7:
            if index == 0:
                self.chromaComboBox.clear()  
                self.chromaComboBox.addItem("0")
            elif index == 1:
                self.chromaComboBox.clear()  
                self.chromaComboBox.addItem("0")
                self.chromaComboBox.addItem("1")
                self.chromaComboBox.addItem("5")
            elif index == 2:
                self.chromaComboBox.clear()  
                self.chromaComboBox.addItem("0")
                self.chromaComboBox.addItem("1")
                self.chromaComboBox.addItem("5")
                self.chromaComboBox.addItem("10")
                self.chromaComboBox.addItem("15")
            else:
                self.chromaComboBox.clear()  
                self.chromaComboBox.addItem("0")
                self.chromaComboBox.addItem("1")
                self.chromaComboBox.addItem("5")
                self.chromaComboBox.addItem("10")
                self.chromaComboBox.addItem("15")
                self.chromaComboBox.addItem("20")
        elif vregIndex == 8:
            if index == 0:
                self.chromaComboBox.clear()  
                self.chromaComboBox.addItem("0")
            elif index == 1:
                self.chromaComboBox.clear()  
                self.chromaComboBox.addItem("0")
                self.chromaComboBox.addItem("1")
                self.chromaComboBox.addItem("5")
            elif index == 2:
                self.chromaComboBox.clear()  
                self.chromaComboBox.addItem("0")
                self.chromaComboBox.addItem("1")
                self.chromaComboBox.addItem("5")
                self.chromaComboBox.addItem("10")
            elif index == 3:
                self.chromaComboBox.clear()  
                self.chromaComboBox.addItem("0")
                self.chromaComboBox.addItem("1")
                self.chromaComboBox.addItem("5")
                self.chromaComboBox.addItem("10")
                self.chromaComboBox.addItem("15")
            else:
                self.chromaComboBox.clear()  
                self.chromaComboBox.addItem("0")
                self.chromaComboBox.addItem("1")
                self.chromaComboBox.addItem("5")
                self.chromaComboBox.addItem("10")
                self.chromaComboBox.addItem("15")
                self.chromaComboBox.addItem("20")
        else:
            if index == 0:
                self.chromaComboBox.clear()  
                self.chromaComboBox.addItem("0")
            elif index == 1:
                self.chromaComboBox.clear()  
                self.chromaComboBox.addItem("0")
                self.chromaComboBox.addItem("1")
                self.chromaComboBox.addItem("5")
            elif index == 2:
                self.chromaComboBox.clear()  
                self.chromaComboBox.addItem("0")
                self.chromaComboBox.addItem("1")
                self.chromaComboBox.addItem("5")
                self.chromaComboBox.addItem("10")
            elif index == 3:
                self.chromaComboBox.clear()  
                self.chromaComboBox.addItem("0")
                self.chromaComboBox.addItem("1")
                self.chromaComboBox.addItem("5")
                self.chromaComboBox.addItem("10")
                self.chromaComboBox.addItem("15")
            else:
                self.chromaComboBox.clear()  
                self.chromaComboBox.addItem("0")
                self.chromaComboBox.addItem("1")
                self.chromaComboBox.addItem("5")
                self.chromaComboBox.addItem("10")
                self.chromaComboBox.addItem("15")
                self.chromaComboBox.addItem("20")
            

      
    def chromaSelectionChange(self,index):
        self.chromaLoad = self.chromaComboBox.currentText()
        print "Chroma index",index,"selection changed. Chroma Load ",self.chromaLoad
      
    def paintEvent(self, e):
        pen = QPen(Qt.blue, 2, Qt.SolidLine)
        painter = QPainter(self)
#        painter.begin(self)
        painter.setPen(pen)
        painter.drawLine(5, 60, 995, 60)
        painter.drawLine(5, 130, 995, 130)
#        painter.end()
        
    def openInstruments(self):
        
        self.Scope = socket_instrument.Socket_Instrument(self.GetIPScope(), int(self.scopePortLineEdit.text()))
        returnString = self.Scope.query("*IDN?")
        if returnString.find("MSO4104B") != -1:
            print("found scope")
            countComma = 0
            for i, c in enumerate(returnString):
                if "," == c:
                    countComma = countComma + 1
                if countComma == 1:
                    endOfString = i + 1
            self.scopeLabel.setText(returnString[0:endOfString])
            scopeGood = True
        else:
            scopeGood = False
            QMessageBox.about(self, "Scope Instrument not found: Check IP Address and Connection")
            

        self.Waveform = socket_instrument.Socket_Instrument(self.GetIPWave(), int(self.wavePortLineEdit.text()))
        returnString = self.Waveform.query("*IDN?")
        if returnString.find("33621A") != -1:
            print("found waveform generator")
            countComma = 0
            for i, c in enumerate(returnString):
                if "," == c:
                    countComma = countComma + 1
                if countComma == 1:
                    endOfString = i + 1
            self.waveformLabel.setText(returnString[0:endOfString]) 
            waveGood = True
        else:
            waveGood = False
            QMessageBox.about(self, "Waveform Instrument not found: Check IP Address and Connection")

        self.Load = socket_instrument.Socket_Instrument(self.GetIPLoad(), int(self.loadPortLineEdit.text()))
        returnString = self.Load.query("*IDN?")
        if returnString.find("CHROMA") != -1:
            print("found load")
            countComma = 0
            for i, c in enumerate(returnString):
                if "," == c:
                    countComma = countComma + 1
                if countComma == 1:
                    endOfString = i + 1
            self.loadLabel.setText(returnString[0:endOfString]) 
            loadGood = True
        else:
            loadGood = False
            QMessageBox.about(self, "Load Instrument not found: Check IP Address and Connection")
            
        if scopeGood and waveGood and loadGood:
            self.startStopButton.setEnabled(True)
            self.startStopButton.setStyleSheet('QPushButton {background-color: #A3C1DA; color: black;}')
            self.configureScope()
             

    def createRadioButtonGroup(self):
        
        slammerRevA = QRadioButton("Slammer Rev A")
        slammerRevB = QRadioButton("Slammer Rev B")

        slammerRevB.setChecked(True)

        vbox = QVBoxLayout()
        vbox.addWidget(slammerRevA)
        vbox.addWidget(slammerRevB)
        vbox.addStretch(1)
        self.slammerGroupBox.setLayout(vbox)
        
        slammerRevA.clicked.connect(self.onSlammerRevA)
        slammerRevB.clicked.connect(self.onSlammerRevB)

    def onSlammerRevA(self, value):
        self.slammer = 1
        print("Got to here Slam A")

    def onSlammerRevB(self, value):
        self.slammer = 2
        print("Got to here Slam B")  
        
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = MainWindow()
    app.exec_()  
#    sys.exit(app.exec_())  
