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
  
  print "Connecting to nanode, timeout %s secs" % (nanodetimeout)
  try:
   urllib2.urlopen(self.cfg.get("nanode","url"), timeout = nanodetimeout)
  except urllib2.URLError, e:
   if isinstance(e.reason, socket.timeout):
    res.reason = "Nanode timed out"
    return res
   else:
    # reraise the original error
    raise
  
  cm = CamMotion.CamMotion(self.cfg,cw)
  cm.capture(8,212,160)
  if cm.appeared == False:
			print "Didn't appear"
			res.appeared = False
  else:
			print "appeared at f%s @ %0.2fs" % (cm.appearedframe,cm.appearedsecs)
			im = cw.AssembleImage(cm.frames,cm.appearedsecs,twusername,twimg)
			im.save("fed.jpg","JPEG")
			res.appeared = True
			res.imagefile = "fed.jpg"
			res.tweet = "Fed by @%s, got to feeder in %0.2fsecs #FeedToby" % (twusername,cm.appearedsecs)
  return res