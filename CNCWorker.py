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
        self.dz = 0
        self.z1 = -100
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

    
    def changeZ(self, dz):
        self.mutex.acquire()
        self.dz = dz
        self.z1 += dz
        self.mutex.release()

    
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

                self.mutex.acquire()
                self.status = "ready"
                self.progress = 100.0
                self.mutex.release()

                if callback != False:
                    callback(bed, zone)
                
            else:
                self.mutex.release()
                time.sleep(0.5)   

                
    def __checkZ(self):
        self.mutex.acquire()
        dz = self.dz
        self.dz = 0
        self.mutex.release()

        if dz != 0:
            print("dz: %d" % dz)
            pos = self.cnc.getPosition()
            z = pos[2] + dz
            vz = 5
            if dz < 0: vz = -5
            self.cnc.moveto_z(z, vz);

                        
    def __waitStopMoving(self):
        time.sleep(0.1)   
        self.cnc.updateStatus()
        while self.cnc.getStatus() == "moving":
            print("status: %s" % self.cnc.getStatus())
            time.sleep(0.1)
            self.__checkZ()
            self.cnc.updateStatus()

            
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
        elif trajectory == "between_seeds":
            self.__runBetweenSeeds()

    def __moveto(self, pos, vel, prog):
        self.cnc.moveto(pos, vel)
        self.__waitStopMoving()
        self.__incrProgress(prog)
        
    def __runBoustrophedon(self):
        print("runBoustrophedon start")
        rounds = 8
        xoff = 0
        vy = 100
        vx = 40
        dx = 45
        z0 = 0
        vz = 10

        # A rough estimate of the amount of progress after each
        # segment
        delta_progress = 100.0 / (3 + rounds * 4 - 1)

        print("Start spindle");
        self.cnc.startSpindle()
        print("Tool down");
        self.__moveto([0, 0, self.z1], [0, 0, -vz], delta_progress)
        print("Starting boustrophedon");
        for round in range(rounds):
            x0 = xoff
            x1 = xoff - dx + vx/2
            x2 = xoff - 2 * dx + vx/2
            y0 = vy / 2 # not zero because the arm slows down starting at vy/2
            y1 = 650
            self.__moveto([x0, -y1, 0], [0, -vy, 0], delta_progress)
            self.__moveto([x1, -y1, 0], [-vx, 0, 0], delta_progress)
            self.__moveto([x1, -y0, 0], [0, vy, 0], delta_progress)
            if (round < rounds - 1):
                self.__moveto([x2, -y0, 0], [-vx, 0, 0], delta_progress)
            xoff -= 100
        print("Stop spindle");
        self.cnc.stopSpindle()
        print("Tool up");
        self.__moveto([0, 0, z0], [0, 0, vz], delta_progress)
        self.__moveto([20, 5, 0], [20, 1, 0], delta_progress)
        self.cnc.home()
        print("runBoustrophedon end")

        
    def __runBetweenSeeds(self):
        print("runBoustrophedon start")
        vy = 50
        vx = 20
        dx = 50
        z0 = 0
        vz = 10
        y0 = vy / 2 # not zero because the arm slows down starting at vy/2
        y1 = 650
        xoff1 = 150
        xoff2 = 350
        delta_progress = 7
        
        # Start position
        self.__moveto([-xoff1, 0, 0], [-vx, 0, 0], delta_progress)
        
        # Tool down and start spindle
        self.__moveto([-xoff1, 0, self.z1], [0, 0, -vz], delta_progress)
        self.cnc.startSpindle()
        
        # One up and down
        self.__moveto([-xoff1, -y1, self.z1], [0, -vy, 0], delta_progress)
        self.__moveto([-xoff1 - dx, -y1, self.z1], [-vx, 0, 0], delta_progress)
        self.__moveto([-xoff1 - dx, -y0, self.z1], [0, vy, 0], delta_progress)
        
        # Stop spindle and tool up
        self.cnc.stopSpindle()
        self.__moveto([0, 0, z0], [0, 0, vz], delta_progress)
        
        # Start position 2
        self.__moveto([-xoff2, -y0, self.z1], [-vx, 0, 0], delta_progress)
        
        # Tool down and start spindle
        self.__moveto([-xoff2, -y0, self.z1], [0, 0, -vz], delta_progress)
        self.cnc.startSpindle()

        # One up and down
        self.__moveto([-xoff2, -y1, self.z1], [0, -vy, 0], delta_progress)
        self.__moveto([-xoff2 - dx, -y1, self.z1], [-vx, 0, 0], delta_progress)
        self.__moveto([-xoff2 - dx, -y0, self.z1], [0, vy, 0], delta_progress)

        # Stop spindle and tool up
        self.cnc.stopSpindle()
        self.__moveto([0, 0, z0], [0, 0, vz], delta_progress)
        
        # Going home
        self.__moveto([20, 5, 0], [20, 1, 0], delta_progress)
        self.cnc.home()
        print("runBoustrophedon end")
                                                                                                                                                                                                                                                                                                                                
