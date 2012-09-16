import FeedConfig
from PIL import Image, ImageChops
import time
import math

class CamMotion:
 """Motion capture stuff"""
 cfg = None
 cw = None
 appeared = False
 appearedframe = -1
 appearedsecs = -1
 frames = []
 
 def __init__(self,cfg,cw):
  self.cfg = cfg
  self.cw = cw
  return
  
 def capture(self,framesreq,resizex,resizey):
		# load some settings
		capsecs = self.cfg.getfloat("motion","capturesecs")
		entropylevel = self.cfg.getfloat("motion","entropy")
		extendsecs = self.cfg.getfloat("motion","extendsecs")
		betweenframes = self.cfg.getfloat("motion","betweenframes")
		saveframes = self.cfg.getboolean("motion","saveframes")
		# store results here
		frames = []
		frameappeared = -1
		timeappeared = ""
		taken = 0
		frame = 0
		started = time.time()
		frames.append(self.cw.SnapCam1()) # grab first shot

		while taken < capsecs:
			time.sleep(betweenframes)
			frames.append(self.cw.SnapCam1())
			taken = time.time() - started
			frame = frame + 1
			
			if saveframes == True:
				frames[len(frames)-1].save(("img%s.jpg" % (frame)),"JPEG")
			
			# calculate difference between the images
			img = ImageChops.difference(frames[len(frames)-1],frames[len(frames)-2])
			ent = self.image_entropy(img)
			print "f%s %0.2fe %0.1fs / %0.1fs" % (frame,ent,taken,capsecs)
			
			if frameappeared == -1:
				if float(ent) > entropylevel:
					frameappeared = frame
					timeappeared = taken
					print "appeared."
					if (capsecs - taken) < extendsecs:
					 # increase capture window as near the end
						capsecs = capsecs + extendsecs
						print "extending cap seconds"
			else:
			 if frame > (frameappeared + framesreq):
			  # taken enough now
			  capsecs = taken
			 
		if frameappeared == -1:
		 self.appeared = False
		else:
		 self.appeared = True
		 self.appearedframe = frameappeared
		 self.appearedsecs = timeappeared
		 framesused = []
		 for num in range(0,framesreq):
		  framesused.append(frames[frameappeared + num].resize((212, 160), Image.ANTIALIAS)) 
		 framesused.append(self.cw.SnapCam2().resize((212, 160), Image.ANTIALIAS))
		 self.frames = framesused
		
  
  
 # Function below is from: http://stackoverflow.com/questions/5524179/how-to-detect-motion-between-two-pil-images-wxpython-webcam-integration-exampl
 # Credit: http://stackoverflow.com/users/31676/paul
 def image_entropy(self,img):
		"""calculate the entropy of an image"""
		# this could be made more efficient using numpy
		histogram = img.histogram()
		histogram_length = sum(histogram)
		samples_probability = [float(h) / histogram_length for h in histogram]
		return -sum([p * math.log(p, 2) for p in samples_probability if p != 0])
