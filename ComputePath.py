import lettucethink.workspace as ws
from lettucethink import urlcam
import lettucethink.cv
import lettucethink.planning
import lettucethink.path
import time
import imageio
from lettucethink import log

workspace = ws.Workspace(0.5, 500, 40, 1080, 1040, 710, 690)

if True:
   print("Opening camera")
   camera = urlcam.Camera("http://192.168.100.3:10103/still")
   print("Grabbing image")
   image = camera.grab()
   print(image.shape)
   print("Writing image to test.jpg")
   imageio.imwrite('topcam.jpg', image)
else:
   image = imageio.imread('00118.jpg')
   imageio.imwrite('topcam.jpg', image)
   print(image.shape)
   
log.enable();

# Here's the real processing: 
cropped = lettucethink.cv.rotate_and_crop(image, workspace)
imageio.imwrite('cropped.jpg', cropped)

mask = lettucethink.cv.calculate_plant_mask(cropped, workspace.mm2px(50), morpho_it=[0, 0])
imageio.imwrite('mask00.jpg', mask)

#mask = lettucethink.cv.calculate_plant_mask(cropped, workspace.mm2px(50), morpho_it=[2, 5])
#imageio.imwrite('mask.jpg', mask)

path = lettucethink.planning.compute_modified_boustrophedon(mask, workspace.mm2px(50), workspace)

lettucethink.path.save_to_svg(path, 'cropped.jpg', 1760, 1080, 'path.svg')

print("Done")
