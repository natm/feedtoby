import FeedResult
import CamWrapper

class FeedAction:
 """Control routine for doing the feed"""
 cfg = None
 
 def __init__(self,cfg):
  self.cfg = cfg
  return
  
 def DoFeed(self,twusername,twimg):
  print "feed him!!"
  
  cw = CamWrapper.CamWrapper(self.cfg)
  
  l = []
  l.append(cw.SnapCam2())
  l[0].save("blah2.jpg","JPEG")
  
  res = FeedResult.FeedResult()
  res.appeared = True
  return res