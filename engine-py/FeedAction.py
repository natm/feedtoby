from __future__ import print_function
import FeedResult
import CamWrapper
import CamMotion
import urllib2
import socket
import sys
from termcolor import colored, cprint

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
  
  cprint('Connecting to nanode: ', 'cyan', end='')
  try:
   urllib2.urlopen(self.cfg.get("nanode","url"), timeout = nanodetimeout)
   cprint('ok', 'green')
  except:
   cprint(("error: %s" % (sys.exc_info()[0])), 'red')
   res.reason = " error: %s (after %s secs)" % (sys.exc_info()[0],nanodetimeout)
   #print e.read()
   return res
  
  cm = CamMotion.CamMotion(self.cfg,cw)
  cm.capture(8,212,160)
  if cm.appeared == False:
			res.appeared = False
			res.reason = "Didn't appear"
  else:
			print("appeared at f%s @ %0.2fs" % (cm.appearedframe,cm.appearedsecs))
			im = cw.AssembleImage(cm.frames,cm.appearedsecs,twusername,twimg)
			im.save("fed.jpg","JPEG")
			res.appeared = True
			res.imagefile = "fed.jpg"
			res.tweet = "Fed by @%s, got to feeder in %0.2fsecs #FeedToby" % (twusername,cm.appearedsecs)
  return res