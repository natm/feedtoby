#! /usr/bin/env python

import CamWrapper
import CamMotion
import FeedConfig
from PIL import Image, ImageChops
import time
import math

# Function below is from: http://stackoverflow.com/questions/5524179/how-to-detect-motion-between-two-pil-images-wxpython-webcam-integration-exampl
# Credit: http://stackoverflow.com/users/31676/paul
def image_entropy(img):
    """calculate the entropy of an image"""
    # this could be made more efficient using numpy
    histogram = img.histogram()
    histogram_length = sum(histogram)
    samples_probability = [float(h) / histogram_length for h in histogram]
    return -sum([p * math.log(p, 2) for p in samples_probability if p != 0])


fc = FeedConfig.FeedConfig("live.cfg")
cw = CamWrapper.CamWrapper(fc)

# load some settings
capsecs = fc.getfloat("motion","capturesecs")
entropylevel = fc.getfloat("motion","entropy")
extendsecs = fc.getfloat("motion","extendsecs")
betweenframes = fc.getfloat("motion","betweenframes")
saveframes = fc.getboolean("motion","saveframes")
frames = []
frameappeared = -1
timeappeared = ""
taken = 0
frame = 0
started = time.time()
frames.append(cw.SnapCam1())
loop = True
while taken < capsecs:
 time.sleep(betweenframes)
 frames.append(cw.SnapCam1())
 taken = time.time() - started
 frame = frame + 1
 
 if saveframes == True:
  frames[len(frames)-1].save(("img%s.jpg" % (frame)),"JPEG")
 
 # calculate difference between the images
 img = ImageChops.difference(frames[len(frames)-1],frames[len(frames)-2])
 ent = image_entropy(img)
 print "f%s %0.2fe %0.1fs / %0.1fs" % (frame,ent,taken,capsecs)
 
 if frameappeared == -1:
  if float(ent) > entropylevel:
   frameappeared = frame
   timeappeared = taken
   print "appeared."
   if (capsecs - taken) < extendsecs:
    capsecs = capsecs + extendsecs
    print "extending cap seconds"

if frameappeared == -1:
 print "didn't appeared"
else:
 print "appeared at f%s @ %0.2fs" % (frameappeared,timeappeared)
