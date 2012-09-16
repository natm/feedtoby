class FeedStats:
 """Handles counters etc for drawing nice graphs"""
 cfg = None
 
 def __init__(self,cfg):
  self.cfg = cfg
  return
  
 def incr(self,statname):
  if self.cfg.has_section("stats") == False:
   self.cfg.add_section("stats")
  statval = 0
  if self.cfg.has_option("stats",statname) == True: 
   statval = self.cfg.get("stats",statname)
  self.cfg.set("stats",statname,int(statval) + 1)
  
 def set(self,statname,statval):
  if self.cfg.has_section("stats") == False:
   self.cfg.add_section("stats")
  self.cfg.set("stats",statname,int(statval))
  