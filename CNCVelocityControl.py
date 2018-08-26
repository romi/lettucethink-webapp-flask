import serial
import json
import time
import threading
#from threading import Lock

# cmp() is no longer defined in Python3 (silly)
def cmp(a, b):
    return (a > b) - (a < b)

class CNCVelocityControl(object):

    def __init__(self, port="/dev/ttyUSB0", homing=True):
        #self.mutex = Lock()
        self.port = port
        #self.mutex.acquire()
        self.serial_port = serial.Serial(self.port, 115200)
        # read '#ready'
        while self.serial_port.in_waiting == 0:
            time.sleep(0.1)   
        r = self.serial_port.readline() 
        #self.mutex.release()
        self.home()
        self.setZero()
        self.status = "idle"
        self.p = [0, 0, 0]
        self.v = [0, 0, 0]
        self.updateStatus()
        

    def home(self):
        self.__sendCommand('h')

        
    def setZero(self):
        self.__sendCommand('0')

        
    def startSpindle(self, ):
        self.__sendCommand('S1')

                
    def stopSpindle(self, ):
        self.__sendCommand('S0')

        
    def getStatus(self):
        #self.mutex.acquire()
        self.updateStatus()
        s = self.status
        #self.mutex.release()
        return s

    
    def getPosition(self):
        #self.mutex.acquire()
        self.updateStatus()
        p = self.p
        #self.mutex.release()
        return p

    
    def moveat(self, vx, vy, vz):
        self.__sendCommand("x%d" % vx)
        self.__sendCommand("y%d" % vy)
        self.__sendCommand("z%d" % vz)

        
    def setTargetPos(self, x, y, z):
        self.__sendCommand("X%d" % x)
        self.__sendCommand("Y%d" % y)
        self.__sendCommand("Z%d" % z)


    def moveto2(self, x, y, z, v):
        self.__sendCommand("X%d" % x)
        self.__sendCommand("Y%d" % y)
        self.__sendCommand("Z%d" % z)
        self.__sendCommand("M%d" % v)

        
    def wait(self):
        self.__sendCommand("W")

        
    def moveto(self, x, y, z):
        # set speed according to direction
        v = list(map(lambda p, t: 50 * cmp(t, p), self.p, [x, y, z]))
        self.setTargetPos(x, y, z)
        self.moveat(v[0], v[1], v[2])

        
    def moveto(self, p, v):
        self.setTargetPos(p[0], p[1], p[2])
        self.moveat(v[0], v[1], v[2])

                
    def moveto_z(self, z, vz):
        self.__sendCommand("Z%d" % z)
        self.__sendCommand("z%d" % vz)

        
    def waitStopMoving(self):
        time.sleep(0.1)   
        self.updateStatus()
        while self.status == "moving":
            time.sleep(0.1)   
            self.updateStatus()

            
    def updateStatus(self):
        s = self.__sendCommand("s")
        #self.mutex.acquire()
        try:
            stat = json.loads(s.decode("utf-8"))
            self.status = stat["status"]
            self.p = stat["p"]
            self.v = stat["v"]
        except KeyError as k:
            print("Failed to parse the JSON: missing key")
        except Exception as e:
            print("Failed to parse the JSON: " + str(e))
        finally:
            dummy = 0 # dummy statement to avoid empty 'finally' clause
            #self.mutex.release()
        #print('status=%s, p=%s, v=%s' % (self.status, str(self.p), str(self.v)))

        
    def __sendCommand(self, s):
        r = False
        #self.mutex.acquire()
        try:
            self.serial_port.write(bytes('%s\n' % s, 'utf-8'))
            time.sleep(0.01)   
            r = self.serial_port.readline()
        finally:
            dummy = 0 # dummy statement to avoid empty 'finally' clause
            #self.mutex.release()
        if r != False:
            print('cmd=%s, reply=%s' % (s, r))
        else:
            print('cmd=%s: failed' % (s))
        return r;

    
if __name__ == "__main__":
    cnc = CNCVelocityControl("/dev/ttyACM0")
    rounds = 3
    xoff = 0
    for round in range(rounds):
        cnc.moveto([xoff, -600, 0], [0, -50, 0])
        cnc.moveto([xoff - 50, -600, 0], [-20, 0, 0])
        cnc.moveto([xoff - 50, 10, 0], [0, 50, 0])
        if (round < rounds - 1):
            cnc.moveto([xoff - 100, 10, 0], [-20, 0, 0])
        xoff -= 100


