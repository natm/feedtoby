import FeedResult

class FeedAction:
 """Control routine for doing the feed"""
 cfg = None
 
 def __init__(self,cfg):
  self.cfg = cfg
  return
  
 def DoFeed(self,twusername,twimg):
  print "feed him!!"
  res = FeedResult.FeedResult()
  res.appeared = True
  return res