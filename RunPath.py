import lettucethink.workspace as ws
import xml.etree.ElementTree as ET
#import CNCVelocityControl
#from WorkspaceCoordinates import WorkspaceCoordinates
import numpy as np
import time
from lettucethink import grbl

def runPath(x, y, z):
   print("Creating Grbl CNC");
   cnc = grbl.CNC("/dev/ttyACM0", homing=True)
   
   print("Homing");
   cnc.home()
   
   print("Start spindle");
   cnc.startSpindle()
   
   print("Tool down, Z1 %d" % z);
   cnc.moveto(0, 0, z)
   
   print("Starting boustrophedon");
   cnc.run_path(x, y, z)
      
   print("Tool up, Z0 %d" % 0);
   px, py, pz = self.cnc.get_position()
   cnc.moveto(px, py, 0)
   
   print("Stop spindle");
   cnc.stopSpindle()
   
   print("Move close to zero");
   cnc.moveto(10, 10, 0)

   print("Homing");
   cnc.home()

   print("Done")

   
tree = ET.parse('path.svg')
root = tree.getroot()
path = root.find('{http://www.w3.org/2000/svg}path')
d = path.attrib['d']
components = d.split()

state = 0
xi, yi = 0, 0
x, y = [], []
for component in components:
   if component == 'M':
      state = "M"
   elif component == 'm':
      state = "m"
   elif component == 'L':
      state = "L"
   elif component == 'l':
      state = "l"
   elif component == 'H':
      state = "H"
   elif component == 'h':
      state = "h"
   elif component == 'V':
      state = "V"
   elif component == 'v':
      state = "v"
   elif component == 'Z':
      state = "Z"
   elif component == 'z':
      state = "z"
   elif component == 'C':
      state = -1
   elif component == 'c':
      state = -1
   elif component == 'S':
      state = -1
   elif component == 's':
      state = -1
   elif component == 'T':
      state = -1
   elif component == 't':
      state = -1
   elif component == 'Q':
      state = -1
   elif component == 'q':
      state = -1
   elif component == 'A':
      state = -1
   elif component == 'a':
      state = -1
   else:
      numbers = component.split(",")
      coordinates = [float(i) for i in numbers]
      if state == "M":
         xi = coordinates[0]
         yi = coordinates[1]
      elif state == "m":
         xi = xi + coordinates[0]
         yi = yi + coordinates[1]
      elif state == "L":
         xi = coordinates[0]
         yi = coordinates[1]
      elif state == "l":
         xi = xi + coordinates[0]
         yi = yi + coordinates[1]
      elif state == "H":
         xi = coordinates[0]
      elif state == "h":
         xi = xi + coordinates[0]
      elif state == "V":
         yi = coordinates[0]
      elif state == "v":
         yi = yi + coordinates[0]
      elif state == "Z" or state == "z":
         xi = x[0]
         yi = y[0]
      x.append(xi)
      y.append(yi)
   if state == -1:
      print("An error occured")


#workspace = WorkspaceCoordinates(-2.2, 908, 454, 1350, 1350, 650, 650)
#workspace = WorkspaceCoordinates(-1.7, 908, 504, 1374, 1390, 660, 660)
#workspace = ws.Workspace(-2.1, 958, 546, 1318, 1336, 660, 660)
workspace = ws.Workspace(0.15, 160, 0, 1760, 1080, 917, 56)
x = workspace.px2mm(np.array(x))
y = workspace.px2mm(workspace.height - np.array(y))
print(x)
print(y)

runPath(x, y, -100)


    
