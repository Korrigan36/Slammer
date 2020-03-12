import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QRadioButton, QVBoxLayout, 
    QGroupBox, QComboBox, QLineEdit, QPushButton, QMessageBox, QInputDialog, QDialog, QDialogButtonBox)
from PyQt5.QtGui import QIcon, QPainter, QPen, QFont
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QCoreApplication, QObject, QRunnable, QThread, QThreadPool, pyqtSignal, pyqtSlot

#import visa
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
    
    timerSignal = pyqtSignal(int, str, float, float, float, float, float, float)
    quitSignal = pyqtSignal(object)
    startStop = True
    vout_DC_Value = 0
    workBook = 0 
    scopeSheet = 0 
    summarySheet = 0 

    duty = 0
    amplitude = 0
    slammer = 0
    configID = 0
    pcbaSN = 0
    productSN = 0
    scopeType = 0
    probeType = 0
    runNotes = 0
    sense_Resistor = 0
    
    rowIndex = 0
    summaryRowIndex = 0
    
    headerCellFormat = 0
    excelFileName = 0
    
    slamLoad = 0
    chromaLoad = 0
    expectedDCLevel = 0
    expectedSlamLevel = 0
    
    singleFrequencyTest = False
    frequencySweepTest = False
    sweepWidth = False
    waitScopeShot = False
    
    #This list must match 1 to 1 with Vreg names drop down list
    vregVoltageList = [0.9, 1.5, 3.3, 0.8, 0.95, 1.8, 1.04, 1.1, 1.0]
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
        
        self.Scope                  = parameterArray[0] 
        self.Load                   = parameterArray[1]  
        self.Waveform               = parameterArray[2]  
        self.StartFreq              = parameterArray[3]  
        self.StopFreq               = parameterArray[4]  
        self.Steps                  = parameterArray[5] 
        self.VregSelection          = parameterArray[6] 
        self.VregText               = parameterArray[7] 
        self.configID               = parameterArray[8]
        self.pcbaSN                 = parameterArray[9]
        self.productSN              = parameterArray[10]
        self.scopeType              = parameterArray[11]
        self.probeType              = parameterArray[12]
        self.runNotes               = parameterArray[13]
        self.duty                   = parameterArray[14] 
        self.edgeTimes              = parameterArray[15] 
        self.amplitude              = parameterArray[16] 
        self.slammer                = parameterArray[17] 
        self.sense_Resistor         = parameterArray[18] 
        self.slamLoad               = parameterArray[19] 
        self.chromaLoad             = parameterArray[20] 
        self.frequencySweepTest     = parameterArray[21] 
        self.sweepWidth             = parameterArray[22] 
        
        print ("slammer selection " + str(self.slammer))
        if self.slammer == 2:
            self.amplitude = float(self.slamLoad)/2*float(self.sense_Resistor)*10
            print ("Waveform Amplitude for " + str(self.slamLoad) + " is " + str(self.amplitude))
        else:
            self.amplitude = self.slamLoad*self.sense_Resistor
            
        loadLine = self.vregLoadLineList[self.VregSelection]
        chromaLoad = self.chromaLoad
        print "load droop " + str(float(loadLine) * float(chromaLoad))
        self.expectedDCLevel = self.vregVoltageList[self.VregSelection] - (float(self.vregLoadLineList[self.VregSelection]) * float(self.chromaLoad))
        print("expected DC level" + str(self.expectedDCLevel))
        self.expectedSlamLevel = self.expectedDCLevel - (float(self.vregLoadLineList[self.VregSelection]) * float(self.slamLoad))
        print("expected Slam level" + str(self.expectedSlamLevel))
        
        if self.StopFreq == 0:
            print "doing single frequency slam"
            self.singleFrequencyTest = True
            
        
    def __del__(self):
        print("del")
#        self.wait()
            
    def startTimer(self):
        self.startStop = True

    def stopTimer(self):
        chromaLib.setLoadOff(self.Load, 5)
        self.startStop = False
        self.quitSignal.emit(self.quitSignal)
        self.waitScopeShot = False
        time.sleep(1)
        
    def testEnd(self):
        pktopkChart = self.workBook.add_chart({'type': 'scatter'})
        pktopkChart.add_series({'name': 'Peak to Peak', 'categories':"=Summary!$A$2:$A$" + str(int(self.Steps + 2)),'values':"=Summary!$B$2:$B$" + str(int(self.Steps + 2))})
        pktopkChart.set_title ({'name': 'Slammer Frequency Sweep Pk to Pk'})
        pktopkChart.set_x_axis({'name': 'Slammer Frequency'})
        pktopkChart.set_x_axis({'min': self.StartFreq, 'max': self.StopFreq})
        pktopkChart.set_y_axis({'name': 'Peak to Peak Voltage'})
#        pktopkChart.set_y_axis({'min': 0.005, 'max': 0.05})
        pktopkChart.set_style(13)
        self.summarySheet.insert_chart('H2', pktopkChart)

        overshootChart = self.workBook.add_chart({'type': 'scatter'})
        overshootChart.add_series({'name': 'Overshoot', 'categories':"=Summary!$A$2:$A$" + str(int(self.Steps + 2)),'values':"=Summary!$E$2:$E$" + str(int(self.Steps + 2))})
        overshootChart.set_title ({'name': 'Slammer Frequency Sweep Overshoot'})
        overshootChart.set_x_axis({'name': 'Slammer Frequency'})
        overshootChart.set_x_axis({'min': self.StartFreq, 'max': self.StopFreq})
        overshootChart.set_y_axis({'name': 'Overshoot Voltage'})
#        overshootChart.set_y_axis({'min': 0.005, 'max': 0.05})
        overshootChart.set_style(13)
        self.summarySheet.insert_chart('H18', overshootChart)
                    
        undershootChart = self.workBook.add_chart({'type': 'scatter'})
        undershootChart.add_series({'name': 'Undershoot', 'categories':"=Summary!$A$2:$A$" + str(int(self.Steps + 2)),'values':"=Summary!$F$2:$F$" + str(int(self.Steps + 2))})
        undershootChart.set_title ({'name': 'Slammer Frequency Sweep Undershoot'})
        undershootChart.set_x_axis({'name': 'Slammer Frequency'})
        undershootChart.set_x_axis({'min': self.StartFreq, 'max': self.StopFreq})
        undershootChart.set_y_axis({'name': 'Undershoot Voltage'})
#        overshootChart.set_y_axis({'min': 0.005, 'max': 0.05})
        undershootChart.set_style(13)
        self.summarySheet.insert_chart('H34', undershootChart)

        undershootChart = self.workBook.add_chart({'type': 'scatter'})
        undershootChart.add_series({'name': 'Max', 'categories':"=Summary!$A$2:$A$" + str(int(self.Steps + 2)),'values':"=Summary!$D$2:$D$" + str(int(self.Steps + 2))})
        undershootChart.set_title ({'name': 'Slammer Frequency Sweep Max'})
        undershootChart.set_x_axis({'name': 'Slammer Frequency'})
        undershootChart.set_x_axis({'min': self.StartFreq, 'max': self.StopFreq})
        undershootChart.set_y_axis({'name': 'Maximum'})
#        overshootChart.set_y_axis({'min': 0.005, 'max': 0.05})
        undershootChart.set_style(13)
        self.summarySheet.insert_chart('H49', undershootChart)

        self.workBook.close()
                    
        print("Test Finished")
        self.stopTimer()

#    @pyqtSlot(str)
    def scopeShot_Slot(self, sentence):
        print(sentence)
        self.waitScopeShot = False
        
    def run(self):
        
        chromaLib.setLoad(self.Load, 5, self.chromaLoad)
        #Turn on chroma for whole test. Slam from DC load to max
        chromaLib.setLoadOn(self.Load, 5)

        self.excelFileName = self.VregText + "_SlammerTest_" + self.runNotes + ".xlsx"
        self.workBook = xlsxwriter.Workbook(self.excelFileName)
        self.scopeSheet = self.workBook.add_worksheet(self.VregText)
        self.summarySheet = self.workBook.add_worksheet("Summary")
            
        self.headerCellFormat = self.workBook.add_format()
        self.headerCellFormat.set_font_size(16)
        self.headerCellFormat.set_bold()
        
        self.defaultWorkBookConfig()
        self.defaultScopeConfig()
        self.defaultWaveFormConfig()
        
        timeScale = 1 / (self.StartFreq * 4)
#        print("timescale " + str(timeScale))
#        if timeScale <= 0.0002 and timeScale > 0.0001:
#            timeScale = 0.0002
#        elif timeScale <= 0.0001 and timeScale > 0.00004:
#            timeScale = 0.0001
#        elif timeScale <= 0.00004 and timeScale > 0.00002:
#            timeScale = 0.00004
        tekScopeLib.scope_SetTimescale(self.Scope, timeScale)
        #Force Scope to Clear Screen
        tekScopeLib.scope_Set_Single_Capture(self.Scope)
        tekScopeLib.scope_Start(self.Scope)
#                tekScopeLib.scope_Force_Trigger(self.Scope)
        tekScopeLib.scope_Stop(self.Scope)
                
        tekScopeLib.scope_Set_Trigger_Auto(self.Scope)
#        tekScopeLib.scope_Clear_Persist(self.Scope)
#        print("clear persist long time")
#        time.sleep(20)
        tekScopeLib.scope_Set_Multiple_Capture(self.Scope)
        tekScopeLib.scope_Start(self.Scope)
#        tekScopeLib.scope_Clear_Persist(self.Scope)
        tekScopeLib.scope_Clear_Statistics(self.Scope)
        time.sleep(8)
        tekScopeLib.scope_Stop(self.Scope)
        
        self.vout_DC_Value = float(tekScopeLib.scope_Get_Measurement(self.Scope, 3, "VAL"))
        
        print "Vreg Selection " + str(self.VregSelection)
        print "DC Value " + str(self.vout_DC_Value)
        
#        if self.vout_DC_Value > self.vregVoltageList[self.VregSelection]* 1.1 or self.vout_DC_Value < self.vregVoltageList[self.VregSelection]* 0.9:
#            print "DC Value off, Check Probe location and Board Power"
#            self.stopTimer()
#            #This delay required. It is believed that it could be because the thread completes too quickly 
#            #and the call in mainwindow self.thread.isFinished(): doesn't work for some reason?? 
#            time.sleep(2)
#        else:
            
        tekScopeLib.scope_Set_Single_Capture(self.Scope)
        tekScopeLib.scope_Start(self.Scope)
        tekScopeLib.scope_Stop(self.Scope)

        tekScopeLib.scope_Set_Offset(self.Scope, "CH2", 0.114)
#        tekScopeLib.scope_Set_Offset(self.Scope, "CH1", self.vout_DC_Value)
        tekScopeLib.scope_Set_Offset(self.Scope, "CH1", 0)
#        tekScopeLib.scope_Set_Channel_Voltage(self.Scope, "CH1", 0.02)
        tekScopeLib.scope_Set_Channel_Voltage(self.Scope, "CH1", 0.05)
        tekScopeLib.scope_Set_Channel_Voltage(self.Scope, "CH2", 0.2)
        tekScopeLib.scope_Set_Channel_Voltage(self.Scope, "CH3", self.amplitude/40)
        tekScopeLib.scope_Set_Channel_Voltage(self.Scope, "CH4", self.amplitude)

        tekScopeLib.scope_SetTimescale(self.Scope, timeScale)
                    
        waveFormLib.pulseGen_Set_Duty(self.Waveform, self.duty)
        
        if self.frequencySweepTest == True:
            tekScopeLib.scope_SetUp_Trigger(self.Scope, "CH4", self.amplitude/2, "FALL", 10)
        else:
            tekScopeLib.scope_SetUp_Trigger(self.Scope, "CH4", self.amplitude/2, "FALL", 30)
        
        tekScopeLib.scope_Set_Trigger_Normal(self.Scope)
#           tekScopeLib.scope_Clear_Statistics(self.Scope)
#           tekScopeLib.scope_Clear_Persist(self.Scope)
#           print("clear persist long time")
#           time.sleep(20)
        #Clear Persistance        
#        tekScopeLib.scope_Set_Single_Capture(self.Scope)
#        tekScopeLib.scope_Start(self.Scope)
#        tekScopeLib.scope_Stop(self.Scope)

        tekScopeLib.scope_Set_Multiple_Capture(self.Scope)
        

        
        self.scopeSheet.write(self.rowIndex, 0, "DC Value:", self.headerCellFormat)
        self.rowIndex = self.rowIndex + 1
        self.scopeSheet.write(self.rowIndex, 1, self.vout_DC_Value)
        self.rowIndex = self.rowIndex + 1
        
        self.write_Measurement_Header()
        self.rowIndex = self.rowIndex + 1
        
        self.summaryRowIndex = 1
        fileName = "xbox_icon.ico"
        
        self.waitScopeShot = True
 
       
        self.countLoop = 1
        while self.startStop:
            if self.singleFrequencyTest == False: 
                self.freqStep = (self.StopFreq - self.StartFreq)/self.Steps
            else:
                print "in thread doing single freq test"
                self.freqStep = 0
                while self.waitScopeShot:
                    print "waiting for scope shot command"
                    time.sleep(1)
                    if self.startStop == False:
                        self.countLoop = 2
                        break
      
            if self.countLoop == 1:
                tekScopeLib.scope_Clear_Statistics(self.Scope)
#                   tekScopeLib.scope_Reset_Persistance(self.Scope)
#                   time.sleep(0.2)

                    
                currentFreq = self.StartFreq + self.freqStep*self.countStep
                if self.frequencySweepTest == True:
                    print "doing frequency sweep"
                    timeScale = 1 / (currentFreq * 2)
                    tekScopeLib.scope_SetTimescale(self.Scope, timeScale)
#                    waveFormLib.pulseGen_Set_Duty(self.Waveform, self.duty)
                    waveFormLib.pulseGen_Set_FreqSweep(self.Waveform, currentFreq, currentFreq + self.sweepWidth, 0.25)    
                    tekScopeLib.scope_SetAnnotation(self.Scope, "Sweep " + str(currentFreq) + " to " + str(currentFreq + self.sweepWidth), 650, 720)
                else:
                    timeScale = 1 / (currentFreq * 4)
                    tekScopeLib.scope_SetTimescale(self.Scope, timeScale)
                    tekScopeLib.scope_SetAnnotation(self.Scope, str(int(currentFreq)) + "Hz", 650, 720)
#                    waveFormLib.pulseGen_Set_Duty(self.Waveform, self.duty)
                    waveFormLib.pulseGen_Set_Freq(self.Waveform, currentFreq)
                
                waveFormLib.pulseGen_Set_OutputOn(self.Waveform)
                tekScopeLib.scope_Start(self.Scope)
                time.sleep(0.1)
#                   tekScopeLib.scope_Clear_Persist(self.Scope)
            
                self.countStep = self.countStep + 1
            elif self.countLoop == 2:
                waveFormLib.pulseGen_Set_OutputOff(self.Waveform)
                tekScopeLib.scope_Stop(self.Scope)
            elif self.countLoop == 100:
#                   time.sleep(8)
                     
                Min = float(tekScopeLib.scope_Get_Measurement(self.Scope, 1, "VAL"))
                Max = float(tekScopeLib.scope_Get_Measurement(self.Scope, 2, "VAL"))
                Mean = float(tekScopeLib.scope_Get_Measurement(self.Scope, 3, "VAL"))
                PktoPk = float(tekScopeLib.scope_Get_Measurement(self.Scope, 4, "VAL"))
                SlamMax = float(tekScopeLib.scope_Get_Measurement(self.Scope, 5, "VAL"))
                Rise = float(tekScopeLib.scope_Get_Measurement(self.Scope, 6, "VAL"))
                Fall = float(tekScopeLib.scope_Get_Measurement(self.Scope, 7, "VAL"))
                     
                tekScopeLib.scope_Set_HCursor(self.Scope, Min, Max)
                tekScopeLib.scope_Set_CursorOn(self.Scope, "CH1")
                time.sleep(1)
                
                #Use measured DC value for max calculation
                overshoot = Max - self.vout_DC_Value
                undershoot = Min - self.expectedSlamLevel
                peakTopeak = tekScopeLib.scope_Get_HCursor_Delta(self.Scope)
                self.summarySheet.write(self.summaryRowIndex, 0, float(currentFreq))
                self.summarySheet.write(self.summaryRowIndex, 1, float(peakTopeak))
                self.summarySheet.write(self.summaryRowIndex, 2, float(Min))
                self.summarySheet.write(self.summaryRowIndex, 3, float(Max))
                self.summarySheet.write(self.summaryRowIndex, 4, float(overshoot))
                self.summarySheet.write(self.summaryRowIndex, 5, float(undershoot))
                self.summaryRowIndex = self.summaryRowIndex + 1
                
                if currentFreq % 1000 == 0 or self.singleFrequencyTest == True:
                
                    measureArray = [currentFreq, self.chromaLoad, self.slamLoad, self.chromaLoad+self.slamLoad, self.expectedDCLevel, self.expectedSlamLevel, Min,
                                       Max, Mean, PktoPk, Max - self.expectedDCLevel, self.expectedSlamLevel - Min, "over %", "under %", Rise, Fall, SlamMax, "slam2Max"]
                       
                    for columnIndex in range (0, 18):
                        self.scopeSheet.write(self.rowIndex, columnIndex, measureArray[columnIndex])
                    self.rowIndex = self.rowIndex + 1
                        
                    print("saving scope shot " + str(currentFreq))
                    fileName = str(int(currentFreq)) + "Hz_" + str(self.countStep) + ".png"
                    tekScopeLib.scope_ScreenShot_Copy(self.Scope, fileName)
                    self.scopeSheet.insert_image(self.rowIndex, 0, fileName, {'x_scale': 0.5, 'y_scale': 0.5})
                    self.rowIndex = self.rowIndex + 20
                    self.write_Measurement_Header()
                    self.rowIndex = self.rowIndex + 1
                
                self.timerSignal.emit(self.countStep, fileName, float(currentFreq), float(peakTopeak), float(Max), float(Min), float(overshoot), float(undershoot))
                    
                waveFormLib.pulseGen_Set_OutputOff(self.Waveform)
                self.countLoop = 0
                tekScopeLib.scope_Stop(self.Scope)
#                timeScale = 1 / (currentFreq * 4)
#                tekScopeLib.scope_SetTimescale(self.Scope, timeScale)
#                tekScopeLib.scope_SetTimescale(self.Scope, "100E-6")
                tekScopeLib.scope_Set_Single_Capture(self.Scope)
                tekScopeLib.scope_Start(self.Scope)
                tekScopeLib.scope_Stop(self.Scope)
                tekScopeLib.scope_Set_Multiple_Capture(self.Scope)
                
#                    tekScopeLib.scope_Clear_Persist(self.Scope)
#                   print("clear persist long time")
#                   time.sleep(20)
                self.waitScopeShot = True
                if self.countStep > self.Steps and self.singleFrequencyTest == False:
                    self.testEnd()
                    
            else:
                waveFormLib.pulseGen_Set_OutputOff(self.Waveform)
#                   tekScopeLib.scope_Stop(self.Scope)
#                   tekScopeLib.scope_Reset_Persistance(self.Scope)
#                   time.sleep(0.2)
               

#            self.timerSignal.emit(self.timerSignal, self.countStep)
            self.countLoop = self.countLoop + 1
            time.sleep(0.25)
#            time.sleep(1)

    def defaultWorkBookConfig(self):

        self.scopeSheet.write('A1', self.excelFileName, self.headerCellFormat)
        self.scopeSheet.write('A2', version_Info, self.headerCellFormat)
        self.scopeSheet.write('A3', "Config ID", self.headerCellFormat)
        self.scopeSheet.write('B3', self.configID)
        self.scopeSheet.write('A4', "PCBA S.N.", self.headerCellFormat)
        self.scopeSheet.write('B4', self.pcbaSN)
        self.scopeSheet.write('A5', "Product S.N.", self.headerCellFormat)
        self.scopeSheet.write('B5', self.productSN)
        self.scopeSheet.write('A6', "Scope Type", self.headerCellFormat)
        self.scopeSheet.write('B6', self.scopeType)
        self.scopeSheet.write('A7', "Probe Type", self.headerCellFormat)
        self.scopeSheet.write('B7', self.probeType)
        self.scopeSheet.write('A8', "Date:", self.headerCellFormat)
        self.scopeSheet.write('A9', "Notes:", self.headerCellFormat)
        self.scopeSheet.write('B9', self.runNotes)
        self.scopeSheet.write('A10', "RLL", self.headerCellFormat)
        
        self.rowIndex = 11

        self.summarySheet.write(0, 0, "Frequency", self.headerCellFormat)
        self.summarySheet.write(0, 1, "Peak to Peak", self.headerCellFormat)
        self.summarySheet.write(0, 2, "Minimum", self.headerCellFormat)
        self.summarySheet.write(0, 3, "Maximum", self.headerCellFormat)
        self.summarySheet.write(0, 4, "Overshoot", self.headerCellFormat)
        self.summarySheet.write(0, 5, "Undershoot", self.headerCellFormat)

    def defaultScopeConfig(self):
        tekScopeLib.scope_SetAnnotation(self.Scope, self.VregText, 650, 720)
#        tekScopeLib.scope_SetChannel_Label(self.Scope, "CH1", self.VregText)
        tekScopeLib.scope_SetChannel_Label(self.Scope, "CH1", "CSR Phase 1")

        tekScopeLib.scope_SetChannel_OnOff(self.Scope, "CH1", "ON")
        if self.frequencySweepTest == True:
            tekScopeLib.scope_SetChannel_Position(self.Scope, "CH1", "3")
        else:
            tekScopeLib.scope_SetChannel_Position(self.Scope, "CH1", "2")
            
        tekScopeLib.scope_SetChannel_Label(self.Scope, "CH2", "IMON R244")
        tekScopeLib.scope_SetChannel_OnOff(self.Scope, "CH2", "ON")
        tekScopeLib.scope_SetChannel_Position(self.Scope, "CH2", "-3")
        tekScopeLib.scope_SetChannel_Label(self.Scope, "CH3", "Sense V")
        tekScopeLib.scope_SetChannel_OnOff(self.Scope, "CH3", "ON")
        tekScopeLib.scope_SetChannel_Position(self.Scope, "CH3", "0")
        tekScopeLib.scope_SetChannel_Label(self.Scope, "CH4", "Sig Gen")
        tekScopeLib.scope_SetChannel_OnOff(self.Scope, "CH4", "ON")
        tekScopeLib.scope_SetChannel_Position(self.Scope, "CH4", "-4")
#        tekScopeLib.scope_SetChannel_Position(self.Scope, "CH4", "0")

        tekScopeLib.scope_SetAnnotation(self.Scope, "DC Level", 650, 720)
        tekScopeLib.scope_SetAcquisitionEnvelope(self.Scope)
        tekScopeLib.scope_Setuprecordlength(self.Scope, 1000000)
        tekScopeLib.scope_SetTimescale(self.Scope, "100E-6")

    def defaultWaveFormConfig(self):
#        self.duty = 50

        waveFormLib.pulseGen_Set_OutputOff(self.Waveform)
        waveFormLib.pulseGen_Set_Duty(self.Waveform, self.duty)
        waveFormLib.pulseGen_Set_Mode_Pulse(self.Waveform)
        waveFormLib.pulseGen_Set_Both_Edge(self.Waveform, self.edgeTimes)
            
#        self.pulseGen_Set_Burst_Mode_Trig(self.Waveform)
#        self.pulseGen_Set_Volt_High_Low(self.Waveform, self.amplitude, self.slammer)
#        self.pulseGen_Set_Burst_Period(self.Waveform, 11)
#        self.pulseGen_Zero_Output(self.Waveform)
#        self.pulseGen_Set_Burst_On(self.Waveform)
#        self.pulseGen_Set_OutputOn(self.Waveform)
        waveFormLib.pulseGen_Set_Volt_High_Low(self.Waveform, self.amplitude, self.slammer)
            
    def write_Measurement_Header(self):
        
        headerArray = ["Freq", "DC Load", "Slammer Load", "Total Load", "vout_DC_expected", "vout_Slam_expected", "min",
                       "max", "mean", "pk-pk", "over mV", "under mV", "over %", "under %", "rise", "fall", "slam1Max", "slam2Max"]
        
        for columnIndex in range (0, 18):
            self.scopeSheet.write(self.rowIndex, columnIndex, headerArray[columnIndex], self.headerCellFormat)

