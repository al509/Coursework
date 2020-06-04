import serial
import winsound
import time

frequency = 750  # Set Frequency To 2500 Hertz
duration = 100  # Set Duration To 1000 ms == 1 second

class Laser(serial.Serial):
    def __init__(self,COMPort):
        super().__init__(port=COMPort,
             baudrate=9600,
             parity=serial.PARITY_NONE,
             stopbits=serial.STOPBITS_ONE,
             bytesize=serial.EIGHTBITS,
             timeout = 0.4)
        self.pause=0.01
        self.repeat=0.1
        self. maxAttempts = 10;

        
    def GetStatus(self):
        time.sleep(self.pause)
        return self.read(1)
        
    def writeP(self, byte):
        self.write(byte)
        time.sleep(self.pause)

    def SetOn(self):
        winsound.Beep(frequency, duration)
        attempt = 0
        print('Turning on laser')
        while True:
            attempt+=1
            self.writeP(b'\x5B')
            self.writeP(b'\x75')
            self.writeP(b'\x8A')
            time.sleep(self.repeat)
            if self.GetStatus() == b'\xaa':
                print('Laser is on (',attempt,')')
                break
            if attempt == self.maxAttempts:
                print('WARNING!!! Could not set the laser on; PLEASE TURN OFF THE LASER MANUALLY')
                break
            time.sleep(self.repeat)

    def SetOff(self):
        winsound.Beep(frequency*2, duration)
        attempt = 0
        print('Turning off laser')
        while True:
            attempt+=1
            self.writeP(b'\x5B')
            self.writeP(b'\x76')
            self.writeP(b'\x89')
            if self.GetStatus() == b'\xaa':
                print('Laser is off (', attempt, ')')
                break
            if attempt == self.maxAttempts:
                print('WARNING!!! COULD NOT TURN THE LASER OFF; PLEASE TURN OFF MANUALLY')
                break
            time.sleep(self.repeat)
        

    def SetOnForShort(self,PulseDuration):
        self.SetOn()
        time.sleep(PulseDuration)
        self.SetOff()
        print('Laser pulse was applied')

    def SetMode(self,ModeKey):
        ModeKeys={
                'Manual':0x70,
                'ANC':0x71,
                'ANV':0x72,
                'MANCLOSED':0x73,
                'ANVCLOSED':0x74}

        Command=ModeKeys[ModeKey]
        CheckSumCommand=(255-int(Command))
        attempt = 0
        print('Changing mode of laser')
        while True:
            attempt+=1
            self.writeP(b'\x5B')
            self.writeP(Command.to_bytes(1,byteorder='big'))
            self.writeP(CheckSumCommand.to_bytes(1,byteorder='big'))
            if self.GetStatus() == b'\xaa':
                print('Laser operation mode changed ( ', attempt, ')')
                break
            if attempt == self.maxAttempts:
                print('WARNING!!! COULD NOT CHANGE THE STATE; PLEASE TURN OFF THE LASER MANUALLY')
                break
            time.sleep(self.repeat)

    def SetPower(self,Power):
        
        
        Command = int(Power*2)
        attempt = 0
        print('Setting power of laser')
        while True:
            attempt+=1
            CheckSumCommand=(255-(0x7F + Command) & (2**8 - 1))
            self.writeP(b'\x5B')
            self.writeP(b'\x7F')
            self.writeP(Command.to_bytes(1,byteorder='big'))
            self.writeP(CheckSumCommand.to_bytes(1,byteorder='big'))
            if self.GetStatus() == b'\xaa':
                print('Laser power is set to ',Power, '% (', attempt, ')')
                break
            if attempt == self.maxAttempts:
                print('WARNING!!! COULD NOT CHANGE THE POWER; PLEASE TURN OFF THE LASER MANUALLY')
                break
            time.sleep(self.repeat)



if __name__ == "__main__":
    Laser=Laser('COM12')
    try:
        Laser.SetMode('MANCLOSED')
        Laser.SetOn()
        Laser.SetPower(3)
        Laser.SetOff()      
        Laser.SetOnForShort(0.1)  
        Laser.close()
    except:
        Laser.SetOff()
        Laser.close()
#################################### CLOSE CONNECTION #######################################



#plt.grid(True)
#plt.plot(Data[1], Data[0])
#plt.xlabel("Wavelength (nm)")
#plt.ylabel("Power (dBm)")
#plt.show()
