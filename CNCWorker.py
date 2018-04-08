import CNCVelocityControl
import time
from threading import Thread, Lock

class CNCWorker(object):
    def __init__(self):
        self.mutex = Lock()
        self.haveData = False
        self.nextBed = False
        self.nextZone = False
        self.nextTrajectory = False
        self.nextCallback = False
        self.status = "initializing"
        self.progress = 0
        self.thread = Thread(target = self.__run, args = ())
        self.thread.start()
        #self.cnc = CNCVelocityControl.CNCVelocityControl("/dev/ttyACM0")
        self.cnc = False

        
    def nextRun(self, bed, zone, trajectory, callback = False):
        print("CNCWorker: nextRun");
        self.mutex.acquire()
        self.nextBed = bed
        self.nextZone = zone
        self.nextTrajectory = trajectory
        self.nextCallback = callback
        self.haveData = True
        self.mutex.release()
        print("CNCWorker: nextRun done");

        
    def getStatus(self):
        self.mutex.acquire()
        s = self.status
        p = self.progress
        self.mutex.release()
        return s, p

    
    def __run(self):
        time.sleep(5)   
        print("CNCWorker: Starting CNC");
        self.cnc = CNCVelocityControl.CNCVelocityControl("/dev/ttyACM0")
        
        self.mutex.acquire()
        self.status = "ready"
        self.mutex.release()

        while True:
            self.mutex.acquire()
            if self.haveData:
                bed = self.nextBed
                zone = self.nextZone
                trajectory = self.nextTrajectory
                callback = self.nextCallback
                self.haveData = False
                self.status = "running"
                self.progress = 0
                self.mutex.release()
                
                print("CNCWorker: have data");

                self.__startWeeding(bed, zone, trajectory)
                if callback != False:
                    callback(bed, zone)

                self.mutex.acquire()
                self.status = "ready"
                self.progress = 100.0
                self.mutex.release()
                
            else:
                self.mutex.release()
                time.sleep(0.5)   

                
    def __incrProgress(self, dp):
        self.mutex.acquire()
        self.progress += dp
        if self.progress > 99.0:
            self.progress = 99.0
        self.mutex.release()

        
    def __startWeeding(self, bed, zone, trajectory):
        print("Starting weeding bed %s, zone %s, trajectory %s" % (bed, zone, trajectory));
        if trajectory == "boustrophedon":
            self.__runBoustrophedon()

        
    def __runBoustrophedon(self):
        print("runBoustrophedon start")
        rounds = 1
        xoff = 0
        dp = 100.0 / (3 + rounds * 4 - 1)
        self.cnc.moveto([0, 0, 100], [0, 0, 10])
        self.__incrProgress(dp)
        for round in range(rounds):
            self.cnc.moveto([xoff, -600, 0], [0, -50, 0])
            self.__incrProgress(dp)
            self.cnc.moveto([xoff - 50, -600, 0], [-20, 0, 0])
            self.__incrProgress(dp)
            self.cnc.moveto([xoff - 50, -24, 0], [0, 50, 0])
            self.__incrProgress(dp)
            if (round < rounds - 1):
                self.cnc.moveto([xoff - 100, -24, 0], [-20, 0, 0])
                self.__incrProgress(dp)
            xoff -= 100
        self.cnc.moveto([0, 0, 0], [0, 0, -10])
        self.__incrProgress(dp)
        self.cnc.moveto([10, 0, 0], [20, 1, 0])
        print("runBoustrophedon end")
