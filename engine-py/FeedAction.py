import FeedResult
import CamWrapper
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
  
  frames = []
  frames.append(cw.SnapCam1())
  #l[0].save("blah2.jpg","JPEG")
  
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
  
  print "c"
  

  res.appeared = True
  return res