#import CNCVelocityControl
from lettucethink import dummy, path
import time
from threading import Thread, Lock

class CNCWorker(object):
    def __init__(self):
        self.mutex = Lock()
        self.haveData = False
        self.doHoming = False
        self.doMoveZ = False
        self.doCancel = False
        self.nextBed = False
        self.nextZone = False
        self.nextTrajectory = False
        self.nextCallback = False
        self.status = "initializing"
        self.progress = 0
        self.dz = 0
        self.z0 = 0
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

        
    def moveZ(self, vz):
        self.mutex.acquire()
        if self.status == "running" or self.status == "homing":
            self.mutex.release()
            return
        self.doMoveZ = True
        self.vz = vz
        self.mutex.release()

        
    def setZ0(self):
        self.mutex.acquire()
        if self.status != "ready":
            self.mutex.release()
            return
        pos = self.cnc.getPosition()
        self.z0 = pos[2]
        self.mutex.release()
        print("CNCWorker: Z0 set to %d" % self.z0);

        
    def setZ1(self):
        self.mutex.acquire()
        if self.status != "ready":
            self.mutex.release()
            return
        pos = self.cnc.getPosition()
        self.z1 = pos[2]
        self.mutex.release()
        print("CNCWorker: Z1 set to %d" % self.z1);

        
    def cancel(self):
        self.mutex.acquire()
        self.doCancel = True
        self.mutex.release()

    
    def homing(self):
        self.mutex.acquire()
        self.doHoming = True
        self.mutex.release()

    
    def __run(self):
        time.sleep(5)   
        #print("CNCWorker: Starting CNC");
        #self.cnc = CNCVelocityControl.CNCVelocityControl("/dev/ttyACM0")

        print("Creating dummy CNC");
        self.cnc = dummy.CNC("/dev/ttyACM0")
        
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
                
            elif self.doHoming:
                self.doHoming = False
                self.status = "homing"
                self.progress = 0
                self.mutex.release()
                self.cnc.home()

                self.mutex.acquire()
                self.status = "ready"
                self.progress = 100.0
                self.mutex.release()
                
            elif self.doMoveZ:
                self.doMoveZ = False
                #self.cnc.moveat(0, 0, self.vz)
                #if self.vz == 0:
                self.status = "ready"
                #else:
                #    self.status = "movingz"
                self.mutex.release()
                
            else:
                self.mutex.release()
                time.sleep(0.5)   

                
    def __checkCancel(self):
        self.mutex.acquire()
        r = self.doCancel
        if self.doCancel:
            self.cnc.stop_spindle()
            # FIXME self.cnc.moveat(0, 0, 0)
            self.status = "ready"
            # FIXME self.cnc.updateStatus()
            self.doCancel = False
        self.mutex.release()
        return r

    
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
        #time.sleep(0.1)   
        #self.cnc.updateStatus()
        #while self.cnc.getStatus() == "moving":
        #    print("status: %s" % self.cnc.getStatus())
        #    time.sleep(0.1)
        #    if self.__checkCancel(): return True
        #    self.__checkZ()
        #    self.cnc.updateStatus()
        return False
    
            
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

            
    def __moveto(self, x, y, z):
        self.cnc.moveto(x, y, z)
        return False
        
        
#    def __runBoustrophedon(self):
#        print("runBoustrophedon start")
#        rounds = 7
#        xoff = 0
#        vy = 60
#        vx = 60
#        dx = 50
#        vz = 10
#
#        # A rough estimate of the amount of progress after each
#        # segment
#        delta_progress = 100.0 / (3 + rounds * 4 - 1)
#
#        print("Start spindle");
#        self.cnc.start_spindle()
#        if self.__checkCancel(): return                
#        print("Tool down, Z1 %d" % self.z1);
#        if self.__moveto(0, 0, self.z1): return
#        
#        print("Starting boustrophedon");
#        for round in range(rounds):
#            x0 = xoff
#            x1 = xoff + dx
#            x2 = xoff + 2 * dx
#            y0 = 0
#            y1 = 650
#            self.__moveto(x0, y1, 0)
#            self.__moveto(x1, y1, 0)
#            self.__moveto(x1, y0, 0)
#            if (round < rounds - 1):
#                self.__moveto(x2, y0, 0)
#            xoff += 2 * dx
#        print("Stop spindle");
#        self.cnc.stop_spindle()
#        print("Tool up, Z0 %d" % self.z0);
#        if self.__moveto(0, 0, self.z0): return
#        #print("Move close to zero");
#        #if self.__moveto(10, 5, 0): return
#        print("Homing");
#        self.cnc.home()
#        print("runBoustrophedon end")


        
    def __runBoustrophedon(self):
        print("runBoustrophedon start")

        dx = 50
        dy = 500
        xmax = 500
        p = path.make_boustrophedon(0, 0, dx, dy, xmax)
        
        print("Going to (0,0)");
        if self.__moveto(0, 0, self.z0): return
        
        print("Start spindle");
        self.cnc.start_spindle()
        
        print("Tool down, Z1 %d" % self.z1);
        if self.__moveto(0, 0, self.z1): return

        self.cnc.run_path(p[0], p[1], self.z1)

        print("Stop spindle");
        self.cnc.stop_spindle()
        
        print("Tool up, Z0 %d" % self.z0);
        x, y, z = self.cnc.get_position()
        if self.__moveto(x, y, self.z0): return
        
        print("Move close to zero");
        if self.__moveto(10, 10, self.z0): return
        
        print("Homing");
        self.cnc.home()
        
        print("runBoustrophedon end")
