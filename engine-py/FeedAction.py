import FeedResult
import CamWrapper
import CamMotion
import urllib2
import socket

class FeedAction:
 """Control routine for doing the feed"""
 cfg = None
 
 def __init__(self,cfg):
  self.cfg = cfg
  return
  
 def DoFeed(self,twusername,twimg):
  
  res = FeedResult.FeedResult()
  cw = CamWrapper.CamWrapper(self.cfg)
  
  nanodetimeout = float(self.cfg.get("nanode","timeout"))
  
  print "Connecting to nanode..."
  try:
   urllib2.urlopen(self.cfg.get("nanode","url"), timeout = nanodetimeout)
   print "Connected"
  except URLError, e:
   print e.code
   res.reason = "Unable to connect %s (after %s secs)" % (e.code,nanodetimeout)
   #print e.read()
   return res
  
  cm = CamMotion.CamMotion(self.cfg,cw)
  cm.capture(8,212,160)
  if cm.appeared == False:
			res.appeared = False
			res.reason = "Didn't appear"
  else:
			print "appeared at f%s @ %0.2fs" % (cm.appearedframe,cm.appearedsecs)
			im = cw.AssembleImage(cm.frames,cm.appearedsecs,twusername,twimg)
			im.save("fed.jpg","JPEG")
			res.appeared = True
			res.imagefile = "fed.jpg"
			res.tweet = "Fed by @%s, got to feeder in %0.2fsecs #FeedToby" % (twusername,cm.appearedsecs)
  return res