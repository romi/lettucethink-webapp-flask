import serial
import json
import time
import threading
from threading import Lock

# cmp() is no longer defined in Python3 (silly)
def cmp(a, b):
    return (a > b) - (a < b)

class CNCVelocityControl(object):

    def __init__(self, port="/dev/ttyUSB0", homing=True):
        self.mutex = Lock()
        self.port = port
        self.serial_port = serial.Serial(self.port, 115200)
        # read '#ready'
        while self.serial_port.in_waiting == 0:
            time.sleep(0.1)   
        r = self.serial_port.readline() 
        self.home()
        self.setZero()
        self.status = "idle"
        self.p = [0, 0, 0]
        self.v = [0, 0, 0]
        self.__updateStatus()
        

    def home(self):
        self.__sendCommand('h')

        
    def setZero(self):
        self.__sendCommand('0')

        
    def getStatus(self):
        self.mutex.acquire()
        s = self.status
        self.mutex.release()
        return s

    
    def getPosition(self):
        self.mutex.acquire()
        p = self.p
        self.mutex.release()
        return p

    
    def moveat(self, vx, vy, vz):
        self.__sendCommand("x%d" % vx)
        self.__sendCommand("y%d" % vy)
        self.__sendCommand("z%d" % vz)

        
    def setLimitPos(self, x, y, z):
        self.__sendCommand("X%d" % x)
        self.__sendCommand("Y%d" % y)
        self.__sendCommand("Z%d" % z)

        
    def moveto(self, x, y, z):
        # set speed according to direction
        v = list(map(lambda p, t: 50 * cmp(t, p), self.p, [x, y, z]))
        self.setLimitPos(x, y, z)
        self.moveat(v[0], v[1], v[2])
        self.waitStopMoving()

        
    def moveto(self, p, v):
        self.setLimitPos(p[0], p[1], p[2])
        self.moveat(v[0], v[1], v[2])
        self.waitStopMoving()

        
    def waitStopMoving(self):
        time.sleep(0.1)   
        self.__updateStatus()
        while self.status == "moving":
            time.sleep(0.1)   
            self.__updateStatus()

            
    def __updateStatus(self):
        s = self.__sendCommand("s")
        self.mutex.acquire()
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
            self.mutex.release()
        #print('status=%s, p=%s, v=%s' % (self.status, str(self.p), str(self.v)))

        
    def __sendCommand(self, s):
        r = False
        self.mutex.acquire()
        try:
            self.serial_port.write(bytes('%s\n' % s, 'utf-8'))
            time.sleep(0.01)   
            r = self.serial_port.readline()
        finally:
            self.mutex.release()
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


