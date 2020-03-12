import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QRadioButton, QVBoxLayout, 
    QGroupBox, QComboBox, QLineEdit, QPushButton, QMessageBox, QInputDialog, QDialog, QDialogButtonBox)
from PyQt5.QtGui import QIcon, QPainter, QPen, QFont
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QCoreApplication, QObject, QRunnable, QThread, QThreadPool, pyqtSignal, pyqtSlot

import visa
import time
import threading 
import waveFormLib
import chromaLib
import tekScopeLib
import xlsxwriter

version_Info = "Python PyQt5 Slammer Frequency Sweep V0.1"

class TimerThread(QObject):

    countLoop = 0
    countStep = 0
    amplitude = 0
    freqStep = 0
    Scope = 0 
    Load = 0 
    Waveform = 0 
    StartFreq = 0 
    StopFreq = 0 
    Steps = 0
    VregSelection = 0
    VregText = 0
    
    timerSignal = pyqtSignal(object)
    quitSignal = pyqtSignal(object)
    startStop = True
    vout_DC_Value = 0
    
    #This list must match 1 to 1 with Vreg names drop down list
    vregVoltageList = [0.9, 1.5, 3.3, 0.8, 0.95, 1.8, 1.1, 0.9, 1.0]
    vregLoadLineList = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0004, 0.002]
    

#    def __init__(self, Scope, Load, Waveform, StartFreq, StopFreq, Steps, VregSelection):
    def __init__(self, parameterArray):
        QThread.__init__(self)
        
#        self.Scope = Scope 
#        self.Load = Load 
#        self.Waveform = Waveform 
#        self.StartFreq = StartFreq 
#        self.StopFreq = StopFreq 
#        self.Steps = Steps
#        self.VregSelection = VregSelection
#        self.VregText = VregText
        
        self.Scope = parameterArray[0] 
        self.Load = parameterArray[1]  
        self.Waveform = parameterArray[2]  
        self.StartFreq = parameterArray[3]  
        self.StopFreq = parameterArray[4]  
        self.Steps = parameterArray[5] 
        self.VregSelection = parameterArray[6] 
#        self.VregText = parameterArray[7] 
        
    def startTimer(self):
        self.startStop = True

    def stopTimer(self):
        self.startStop = False
        self.quitSignal.emit(self.quitSignal)

    def run(self):
        tekScopeLib.scope_Set_Trigger_Auto(self.Scope)
        tekScopeLib.scope_Reset_Persistance(self.Scope)
        time.sleep(1)
        tekScopeLib.scope_Set_Multiple_Capture(self.Scope)
        tekScopeLib.scope_Start(self.Scope)
        tekScopeLib.scope_Clear_Statistics(self.Scope)
        time.sleep(8)
        tekScopeLib.scope_Stop(self.Scope)
        self.vout_DC_Value = float(tekScopeLib.scope_Get_Measurement(self.Scope, 3, "MEAN"))
        
        print "Vreg Selection " + str(self.VregSelection)
        print "DC Value " + str(self.vout_DC_Value)
        
        if self.vout_DC_Value > self.vregVoltageList[self.VregSelection]* 1.1 or self.vout_DC_Value < self.vregVoltageList[self.VregSelection]* 0.9:
            print "DC Value off, Check Probe location and Board Power"
            self.stopTimer()
        
        while self.startStop:
            self.freqStep = (self.StopFreq - self.StartFreq)/self.Steps
      
            self.countLoop = self.countLoop + 1
            if self.countLoop == 1:
                currentFreq = self.StartFreq + self.freqStep*self.countStep
                waveFormLib.pulseGen_Set_Freq(self.Waveform, currentFreq)
                waveFormLib.pulseGen_Set_OutputOn(self.Waveform)
#               self.pulseGen_Set_Volt_High_Low(self.Waveform, self.amplitude, self.slammer)
            
                self.countStep = self.countStep + 1
            elif self.countLoop == 11:
#               self.pulseGen_Set_Burst_Off(self.Waveform)
                waveFormLib.pulseGen_Set_OutputOff(self.Waveform)
                self.countLoop = 0
                if self.countStep > self.Steps:
                    print("Test Finished")
                    self.startStop = False
                    self.quitSignal.emit(self.quitSignal)

            else:
#               self.pulseGen_Set_Burst_Off(self.Waveform)
                waveFormLib.pulseGen_Set_OutputOff(self.Waveform)
                

#            if self.countLoop == 1:
#                self.setLoad(self.loadObject, 1, 10)
#                self.setLoad(self.loadObject, 5, 10)
#                self.setLoad(self.loadObject, 9, 10)
#                self.setLoadOn(self.loadObject, 1)
#                self.setLoadOn(self.loadObject, 5)
#                self.setLoadOn(self.loadObject, 9)
#                print("Turn Load On")
#            elif self.countLoop == 10:
#                self.setLoadOff(self.loadObject, 1)
#                self.setLoadOff(self.loadObject, 5)
#                self.setLoadOff(self.loadObject, 9)
#                self.pulseGen_Set_OutputOff(self.waveformObject)
#                print("Turn Load Off")
#            elif self.countLoop == 20:
#                self.countLoop = 0
            self.timerSignal.emit(self.timerSignal)
            time.sleep(1)

