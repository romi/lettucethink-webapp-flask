import cv2
import numpy as np
from matplotlib import pyplot as plt
import sys
import os
import urllib
import CNCVelocityControl
import time
import svg
from WorkspaceCoordinates import WorkspaceCoordinates


def makeDebugDir(path):
   (dirname, filename) = os.path.split(path)
   (name, ext) = os.path.splitext(filename)   
   debugdir = os.path.join(dirname, name)
   if not os.path.exists(debugdir):
       os.mkdir(debugdir)
   return dirname, name, debugdir


def grabImage(url, path, debugdir=None):
   req = urllib.request.urlopen("http://10.20.30.33:10000/image.jpg")
   arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
   image = cv2.imdecode(arr, -1)
   #image = cv2.resize(image, (820, 616))
   if debugdir:
      cv2.imwrite("%s/00-topcam.jpg" % debugdir, image)
   if path:
      cv2.imwrite(path, image)
   return image


def rotateAndCropImage(infile, outfile, workspace, debugdir=None):
   image = cv2.imread(infile)

   (ih, iw) = image.shape[:2]
   M = cv2.getRotationMatrix2D((workspace.x0, ih-workspace.y0), workspace.theta, 1)

   rotated = cv2.warpAffine(image, M, (iw, ih))
   if debugdir:
      cv2.imwrite("%s/01-rotate.jpg" % debugdir, rotated)

   crop = image[ih - workspace.y0 - workspace.height:ih-workspace.y0,
                workspace.x0:workspace.x0 + workspace.width]
   if debugdir:
      cv2.imwrite("%s/02-crop.jpg" % debugdir, crop)
   cv2.imwrite(outfile, crop)

   
# Calculates the plantmask of the image given as input and saves the
# mask to a file. All of the work is done in the calculatePlantMask
# function.
def generateMaskFile(infile, outfile, debugdir=None):
   image = cv2.imread(infile)
   mask = calculatePlantMask(image, 50, morpho_it=[5, 2], debugdir=debugdir) #try 50 for tool size
   cv2.imwrite(outfile, mask)
   return mask


def calculatePlantMask(image, toolsize, bilf=[11, 5, 17], morpho_it=[5, 5], debugdir=None):

   ExG = calculateExcessGreen(image)
   M = ExG.max()
   m = ExG.min()
        
   # Scale all values to the range (0, 255)
   colorIndex = (255 * (ExG - m) / (M - m)).astype(np.uint8)
        
   # Smooth the image using a bilateral filter
   colorIndex = cv2.bilateralFilter(colorIndex, bilf[0], bilf[1], bilf[2])

   if debugdir:
      cv2.imwrite("%s/03-exgnorm.jpg" % debugdir, colorIndex)
        
   # Calculte the mask using Otsu's method (see
   # https://docs.opencv.org/3.0-beta/doc/py_tutorials/py_imgproc/py_thresholding/py_thresholding.html)
   th, mask = cv2.threshold(colorIndex, 0, 255, cv2.THRESH_OTSU)

   if debugdir:
      cv2.imwrite("%s/04-mask1.jpg" % debugdir, mask)

   if debugdir:
      plt.subplot(1, 5, 1), plt.imshow(image)
      plt.title("image"), plt.xticks([]), plt.yticks([])
        
      plt.subplot(1, 5, 2), plt.imshow(ExG, 'gray')
      plt.title("ExG"), plt.xticks([]), plt.yticks([])
        
      plt.subplot(1, 5, 3), plt.imshow(colorIndex, 'gray')
      plt.title("filtered"), plt.xticks([]), plt.yticks([])
        
      plt.subplot(1, 5, 4), plt.hist(colorIndex.ravel(), 256), plt.axvline(x=th, color="red", linewidth=0.1)
      plt.title("histo"), plt.xticks([]), plt.yticks([])
      
      plt.subplot(1, 5, 5), plt.imshow(mask, 'gray')
      plt.title("mask"), plt.xticks([]), plt.yticks([])
      
      plt.savefig("%s/05-plot.jpg" % debugdir, dpi=300)

   # The kernel is a cross:
   #   0 1 0
   #   1 1 1
   #   0 1 0
   kernel = np.ones((3, 3)).astype(np.uint8)
   kernel[[0, 0, 2, 2], [0, 2, 2, 0]] = 0

   # See https://docs.opencv.org/3.0-beta/doc/py_tutorials/py_imgproc/py_morphological_ops/py_morphological_ops.html
   mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=morpho_it[0])
   if debugdir:
      cv2.imwrite("%s/06-mask2.jpg" % debugdir, mask)

   mask = cv2.dilate(mask, kernel=kernel, iterations=morpho_it[1])
   if debugdir:
      cv2.imwrite("%s/07-mask3.jpg" % debugdir, mask)

   # Invert the mask and calculate the distance to the closest black pixel.  
   # See https://docs.opencv.org/2.4.8/modules/imgproc/doc/miscellaneous_transformations.html#distancetransform
   dist = cv2.distanceTransform(255 - (mask.astype(np.uint8)),
                                cv2.DIST_L2,
                                cv2.DIST_MASK_PRECISE)
   # Turn white all the black pixels that are less than half the
   # toolsize away from a white (=plant) pixel
   mask = 255 * (1 - (dist > toolsize/2)).astype(np.uint8)

   if debugdir:
      cv2.imwrite("%s/08-mask.jpg" % debugdir, mask)
         
   return mask


def calculateExcessGreen(colorImage):
   # ExcessGreen (ExG) is defined for a given pixel as
   #   ExG=2g-r-b
   # with r, g, b the normalized red, green and blue components:
   #   r = Rn/(Rn+Gn+Bn)   
   #   g = Gn/(Rn+Gn+Bn)   
   #   b = Bn/(Rn+Gn+Bn)
   # 
   # Rn, Gn, Bn are the normalized color values in the range of (0, 1):
   #   Rn=R/max(R), Gn=G/max(G), ...
   #
   # R, G, B are the non-normalized or "raw" color values.
   #
   # 2g-r-b can be rewritten as
   # 2g-r-b = 2G/(R+G+B) - G/(R+G+B) - B/(R+G+B)
   #        = (2G-R-B) / (R+G+B)
   #        = (3G-(R+G+B)) / (R+G+B)
   #        = 3G/(R+G+B) - 1
   #
   # See also Meyer & Neto, Verification of color vegetation indices
   # for automated crop imaging applications,
   # https://www.agencia.cnptia.embrapa.br/Repositorio/sdarticle_000fjtyeioo02wyiv80sq98yqrwt3ej2.pdf
   
   # Ms = [Bm, Gm, Rm], with Bm=max(B(i,j)), Gm=max(G(i,j)), ... 
   Ms = np.max(colorImage, axis = (0, 1)).astype(np.float) 

   # normalizedImage: all rgb values in the range (0, 1):
   #    e(i,j) = [Bn(i,j), Gn(i,j), Rn(i,j)]
   # with Bn(i,j) = B(i,j)/Bm, ...
   normalizedImage = colorImage / Ms

   # L is a 2-dimensional array with L(i,j) = Bn(i,j) + Gn(i,j) + Rn(i,j) 
   L = normalizedImage.sum(axis = 2)

   # ExG is a 2-dimensional array with
   #   e(i,j) = 3 * Gn(i,j) / L(i,j) - 1
   #   e(i,j) = 3 * Gn(i,j) / (Bn(i,j) + Gn(i,j) + Rn(i,j)) - 1
   ExG = 3 * normalizedImage[:, :, 1] / L - 1
   ExG = np.nan_to_num(ExG) # handle division by zero if L(i,j)=0 
      
   return ExG

    
def fillWithPoints(xy, numberOfPoints):
   ts = np.linspace(0, len(xy[0]), num=len(xy[0]), endpoint=True)
   nts = np.linspace(0, len(xy[0]), num=numberOfPoints, endpoint=True)
   fx = np.interp(nts, ts, xy[0])
   fy = np.interp(nts, ts, xy[1])
   return np.array([fx, fy])


def plantContours(mask):
   # See https://docs.opencv.org/3.0.0/d4/d73/tutorial_py_contours_begin.html
   im, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
   # Reorganise the arrays + remove contours with less than 10 points???
   contours = [np.vstack([ci[:,0], ci[:,0][0]]) for ci in contours if (len(ci) > 10)]
   return contours


def point_line_distance(point, start, end):
    if (start == end).all():
        return np.linalg.norm(point-start)
    else:
        n = np.linalg.norm(np.linalg.det([end - start, start - point]))
        d = np.linalg.norm(end-start)
        return n/d

     
def rdp(points, epsilon):
    """
    Cartographic generalization is achieved with the Ramer-Douglas-Peucker algorithm
    pseudo-code: http://en.wikipedia.org/wiki/Ramer-Douglas-Peucker_algorithm
    python port: http://github.com/sebleier/RDP
    """
    dmax = 0.0
    index = -1
    for i in range(1, len(points) - 1):
        d = point_line_distance(points[i], points[0], points[-1])
        if d > dmax:
            index = i
            dmax = d
    if dmax >= epsilon:
        res1 = rdp(points[:index+1], epsilon)
        res2 = rdp(points[index:], epsilon)
        return np.vstack([res1[:-1],res2])
    else:
        return np.vstack([points[0], points[-1]])

# Make a boustrophedon. The path goes up and down along the y-axis,
# and slowly moves forward in the x-direction.
# 
# xstart, ystart: the coordinates of the starting point 
#
# dx: the amount to move forward in the x-direction. The path starts
# at xstart, and advance by dx after every sweep along the y-axis.
#
# dy: the amount to move in the y-direction. The path with go back and
# forth between ystart and ystart+dy.
#
# xmax: the maximum value of x, at which the path should stop.
def makeBoustrophedon(xstart, ystart, dx, dy, xmax):
   xoff = xstart
   x = [xstart]
   y = [ystart]
   while xoff < xmax:
      x0 = xoff
      x1 = xoff + dx
      x2 = xoff + 2 * dx
      y0 = ystart
      y1 = ystart + dy
      x.append(x0), y.append(y1)
      if x1 < xmax:
         x.append(x1), y.append(y1)
         x.append(x1), y.append(y0)
      if x2 < xmax:
         x.append(x2), y.append(y0)
      xoff += 2 * dx
   return np.array([x,y])

 
def corrected_path(pi,po,tr,Nfp=200):
   """
   Substitute path passing through plants by shortest contour connecting i/o points 
   """
   longtr = fillWithPoints(tr.T, Nfp) 
   pi_idx = ((pi[:,np.newaxis]-longtr)**2).sum(axis=0).argmin()
   po_idx = ((po[:,np.newaxis]-longtr)**2).sum(axis=0).argmin()

   if (pi_idx < po_idx):
      p1 = longtr[:,pi_idx:po_idx]
      p2 = longtr.take(range(-(Nfp-po_idx), pi_idx), axis=1, mode="wrap")[:,::-1]
   else:
      p1 = longtr[:,::-1][:,Nfp-pi_idx:Nfp-po_idx]
      p2 = longtr.take(range(-(Nfp-pi_idx), po_idx), axis=1, mode="wrap")

   d1 = (np.diff(p1,axis=1)**2).sum()
   d2 = (np.diff(p2,axis=1)**2).sum()
   if (d1 <= d2):
      return p1
   else:
      return p2

   
def computeModifiedBoustrophedon(mask, toolsize, workspace,
                                 eps_contours=1, eps_toolpath=1,
                                 numFillPoints=5000, debugdir=None):

   # Compute boustrophedon ignoring the plants. All coordinates are in
   # image pixels. The boustrophedon start at y=0 (top of image),
   # because that is where the CNC arm is when the image is taken.
   boustro = makeBoustrophedon(0, 0, int(toolsize), workspace.height - 1, workspace.width)

   # Detect i/o points of paths passing through plants
   dense_boustro = fillWithPoints(boustro, numFillPoints)
   pval = mask[(dense_boustro[1]).astype(int), (dense_boustro[0]).astype(int)]

   if pval[0]: 
      fpath = np.where(pval==0)[0]  
      dense_boustro = dense_boustro[:,fpath[0]:]
      pval = pval[fpath[0]:]
      
   if pval[-1]: 
      fpath = np.where(pval==0)[0]  
      dense_boustro = dense_boustro[:,:fpath[-1]]
      pval = pval[:fpath[-1]]

   idxs = np.where(np.diff(pval) > 0)[0]
   io_points = dense_boustro[:, idxs]

   # Extract, downsample and compute center of plant contours 
   contours = plantContours(mask.copy())
   s_tr = []
   trc = []

   for tri in contours:
      s_tr.append(rdp(tri, eps_contours))
      if len(trc):
         trc = np.vstack([trc, s_tr[-1].mean(axis=0)])
      else:
         trc = s_tr[-1].mean(axis=0)

   # Generate the mofified boustrophedon
   toolPath = np.array([dense_boustro[:,0]]).T
   toolPath = np.hstack([toolPath,dense_boustro[:,:idxs[0]]])
   
   for k in range(int(len(io_points[0])//2)):
      pi = io_points[:,2*k]   #in point
      po = io_points[:,2*k+1] #out point
      plant = ((.5*(pi+po)-trc)**2).sum(axis=1).argmin() #plant attached to i/o points
      cor_path = corrected_path(pi,po,s_tr[plant])      
      toolPath = np.hstack([toolPath,cor_path])
      if k < (len(io_points[0])/2-1):
         toolPath = np.hstack([toolPath, dense_boustro[:,idxs[2*k+1]:idxs[2*k+2]]])

   toolPath = np.hstack([toolPath, dense_boustro[:,idxs[2*k+1]:]])
   toolPath = rdp(toolPath.T, 1)
   return toolPath.T



def printPath(mask, path, workspace, debugdir):
   #1
   stp = np.round(path.T, 0).reshape((-1,1,2)).astype(np.int32)
   cv2.polylines(mask, [stp], False, [145,235,229],8)
   cv2.imwrite("%s/09-toolpath.jpg" % debugdir, mask)
   #2
   doc = svg.SVGDocument("%s/09-toolpath.svg" % debugdir, workspace.width, workspace.height)
   doc.addImage("02-crop.jpg", 0, 0, workspace.width, workspace.height)
   doc.addPath(path[0], path[1])
   doc.close()


def waitCNC(cnc):
   time.sleep(0.1)
   cnc.updateStatus()
   while cnc.getStatus() == "moving":
      time.sleep(0.1)
      cnc.updateStatus()

      
def runPath(x, y):
   cnc = CNCVelocityControl.CNCVelocityControl("/dev/ttyACM0")
   
   print("Start spindle");
   cnc.startSpindle()
   #print("Tool down, Z1 %d" % self.z1);
   #if self.__moveto([0, 0, self.z1], [0, 0, -vz], delta_progress): return

   print("Starting boustrophedon");
   for i in range(len(x)):
      print("xi %d, yi %d" % (int(x[i]), int(y[i])));
      cnc.moveto2(int(x[i]), int(y[i]), 0, 50)
      waitCNC(cnc)
      
   print("Stop spindle");
   cnc.stopSpindle()
      #print("Tool up, Z0 %d" % self.z0);
      #if self.__moveto([0, 0, self.z0], [0, 0, vz], delta_progress): return
   print("Homing");
   cnc.home()



      
# main
dirname, name, debugdir = makeDebugDir("static/workspace.jpg")
workspace = WorkspaceCoordinates(-2.2, 908, 454, 1350, 1350, 650, 650)

#grabImage("http://10.20.30.33:10000/image.jpg", "static/topcam.jpg", debugdir)
rotateAndCropImage("static/topcam.jpg", "static/workspace.jpg", workspace, debugdir)
mask = generateMaskFile("static/workspace.jpg", "static/mask.jpg", debugdir)
path = computeModifiedBoustrophedon(mask, workspace.mm2px(50), workspace, debugdir=debugdir)
printPath(mask, path, workspace, debugdir)

x = workspace.px2mm(path[0])
y = workspace.px2mm(workspace.height - path[1])
#runPath(x, y)
print(x)
print(y)


