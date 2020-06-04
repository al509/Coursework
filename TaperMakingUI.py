from PyQt5 import QtCore, QtGui, QtWidgets


import thorlabs_apt as apt
apt.list_available_devices()
import SynradLaser
import sys
import numpy as np
import threading
import winsound
import ui
import math




class Worker(QtCore.QRunnable):


    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def run(self):

        self.fn(*self.args, **self.kwargs)



class Ui_MainWindow(object):

    threadpool = QtCore.QThreadPool()

    isNotStarted = threading.Event()
    isNotStarted.set()
    isChecking = False

    timeToHeatUpTube=10 # seconds, calculated by Daria
#    NumberOfCycles=15

    frequency = 1500  # Set Frequency To 2500 Hertz
    duration = 1500  # Set Duration To 1000 ms == 1 second



    v1 = 0.32
    v2 = 0.24
    a1 = 2.0
    a2 = 1.5
    s1 = 4 ## mm
    s2 = 3 ## mm
    
    stretchButtonClicked = 0

 #   LaserCOMPort='COM14'
    LaserPowerListName="Laser Power Script 3.2.txt"


    ui = ui.Ui_MainWindow()

    def setupUi(self, MainWindow):

        self.ui.setupUi(MainWindow)
        ########## Button conections ##########
        self.ui.ConnectionLaserButton.clicked.connect(self.laserButtonClicked)
        self.ui.ConnectionStagesButton.clicked.connect(self.stagesButtonClicked)
        self.ui.StagesToZerosButton.clicked.connect(self.stagesToZerosClicked)
        self.ui.StagesToHomeButton.clicked.connect(self.stagesToHomeClicked)
        self.ui.MoveStagesButton.clicked.connect(self.moveStagesClicked)
        self.ui.StartStopButton.clicked.connect(self.startStopButtonClicked)
        self.ui.StretchButton.clicked.connect(self.stretchButtonClicked)
        self.ui.FileBox.clicked.connect(self.fileBoxClicked)
        self.ui.SetToTenButton.clicked.connect(self.SetToTenClicked)
        self.ui.MoveOutButton.clicked.connect(self.moveOutClicked)
        #######################################



    def logWarningText(self, text):
        self.ui.LogField.append("<span style=\" font-size:8pt; font-weight:600; color:#ff0000;\" >" + ">" + text + "</span>")
        self.ui.LogField.append("")
    def logText(self, text):
        self.ui.LogField.append(">" + text)
        self.ui.LogField.append("")

    def laserButtonClicked(self):
        global Laser
        try:
            Laser=SynradLaser.Laser("COM" + self.ui.PortField.text())
            self.logText('The laser was connected')
            # номер COM  порта
        except:
            self.logWarningText(str(sys.exc_info()[1]))

    def stagesButtonClicked(self):
        global motor1
        global motor2
        try:
            motor1 = apt.Motor(90864300)
            motor2 = apt.Motor(90864301)
            motor1.set_move_home_parameters(2, 1, 5.0, 0.0001)
            motor2.set_move_home_parameters(2, 1, 5.0, 0.0001)
            self.logText('Stages connected successfully')
        except:
            self.logWarningText(str(sys.exc_info()[1]))

    def stagesToZerosClicked(self):
        try:

            motor1.set_velocity_parameters(0, 3.5, 4.5)
            motor2.set_velocity_parameters(0, 3.5, 4.5)

            motor1.move_home(False)
            motor2.move_home(True)
            self.logText('Stages moved to zeros')
        except:
            self.logWarningText(str(sys.exc_info()[1]))

    def stagesToHomeClicked(self):
        try:
            motor1.backlash_distance(0)
            motor2.backlash_distance(0)

            motor1.set_velocity_parameters(0, 3.5, 4.5)
            motor2.set_velocity_parameters(0, 3.5, 4.5)

            Home_value1 = 95
            Home_value2 = 30

            motor1.move_to(Home_value1, False)
            motor2.move_to(Home_value2, True)
            self.logText('Stages moved to start position')
        except:
            self.logWarningText(str(sys.exc_info()[1]))

    def moveStagesClicked(self):
        try:
            motor1.set_velocity_parameters(0, 1.0, 0.2)
            motor2.set_velocity_parameters(0, 1.0, 0.2)
            motor1.move_by(-1*float(self.ui.MoveStagesField.text()), False)
            motor2.move_by(float(self.ui.MoveStagesField.text()), True)
            self.logText('Stages moved')
        except:
            self.logWarningText(str(sys.exc_info()[1]))

    def start(self):
        try:
            self.stretchButtonClicked = 0
            self.logText("Laser taper making started")
            self.PowerArray=np.array(np.loadtxt(self.LaserPowerListName)[:,1])
            self.isNotStarted.clear()
            Laser.SetPower(self.PowerArray[0])
            Laser.SetOn()
            self.ui.NumberOfCycleField.setText("Heating up the tube")
            self.isNotStarted.wait(self.timeToHeatUpTube)
            if self.isNotStarted.isSet():
                Laser.SetOff()
                self.isNotStarted.set()
                self.ui.NumberOfCycleField.setText("Interrupted")
                self.logWarningText("Interrupted")
                return
            i = 1
            while(i <= int(self.ui.NumberOfCyclesField.text()) * 2):
                Laser.SetPower(self.PowerArray[i-1])
                self.ui.NumberOfCycleField.setText(str(math.floor(i/ 2 + 1)))
                if (i>int(self.ui.NumberOfCyclesField.text())-2): winsound.Beep(self.frequency, self.duration)
                motor1.set_velocity_parameters(0, self.a1, self.v1)
                motor2.set_velocity_parameters(0, self.a2, self.v2)
                motor1.move_by(-self.s1, False)
                motor2.move_by(self.s2, False)
                self.isNotStarted.wait(self.s1/self.v1 + 0.3)
                if self.isNotStarted.isSet():
                    Laser.SetOff()
                    self.isNotStarted.set()
                    self.ui.NumberOfCycleField.setText("Interrupted")
                    self.logWarningText("Interrupted")
                    return
                self.ui.NumberOfCycleField.setText(str(math.floor(i/ 2 + 1)) + " half")
                i+=1
                Laser.SetPower(self.PowerArray[i-1])
                motor1.set_velocity_parameters(0, self.a2, self.v2)
                motor2.set_velocity_parameters(0, self.a1, self.v1)
                motor1.move_by(self.s2, False)
                motor2.move_by(-self.s1, False)
                self.isNotStarted.wait(self.s1/self.v1 + 0.3)
                if self.isNotStarted.isSet():
                    Laser.SetOff()
                    self.ui.NumberOfCycleField.setText("Interrupted")
                    self.logWarningText("Interrupted")
                    return
                i += 1
            Laser.SetOff()
            self.ui.NumberOfCycleField.setText("Completed")
            self.logText("Completed")
            self.isNotStarted.set()
            winsound.Beep(self.frequency, 2*self.duration)

        except:
            self.logWarningText(str(sys.exc_info()[1]))
            Laser.SetOff()
            return

    def startStopButtonClicked(self):
        try:
            if self.isNotStarted.isSet() == False:
                self.isNotStarted.set()
                return

            else:
                worker = Worker(self.start)
                self.threadpool.start(worker)
        except:
            self.logWarningText(str(sys.exc_info()[1]))

    def stretchButtonClicked(self):
         try:
            motor1.move_by(-0.01,True)
            self.stretchButtonClicked += 1
            self.logText('Stretched (' + self.stretchButtonClicked + 'times)')
         except:
            self.logWarningText(str(sys.exc_info()[1]))

    def fileBoxClicked(self):
        try:
            fname = QtWidgets.QFileDialog().getOpenFileName()[0]
            self.LaserPowerListName = fname
            self.logText("Opened: " + fname)
        except:
            self.logWarningText(str(sys.exc_info()[1]))


    def LaserForTestClicked(self):
        try:
            Laser.SetPower(10)
        except:
            self.logWarningText(str(sys.exc_info()[1]))

    def SetToTenClicked(self):
        try:
            if self.isChecking == True:
                Laser.SetOff()
                self.logText("Laser turned off")
                self.isChecking = False
                Laser.SetPower(10)
            else:
                Laser.SetOn()
                self.logText("Laser set to 10%")
                self.isChecking = True
        except:
            self.logWarningText(str(sys.exc_info()[1]))
            
    def moveOutClicked(self):
        try:
            motor1.set_velocity_parameters(0, 1.0, 0.3)
            motor2.set_velocity_parameters(0, 0.0, 0.3)
            motor1.move_by(-1*70, False)
            motor2.move_by(70, True)
            self.logText('Stages moved')
        except:
            self.logWarningText(str(sys.exc_info()[1]))



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()



    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)




    MainWindow.show()
#    apt.atexit._clear()
    sys.exit(app.exec_())
#    apt.atexit._clear()