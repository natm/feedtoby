import datetime

class FeedRules:
 """Rules on if Toby can be fed or not"""
 c = None
 
 def __init__(self,cfg):
  self.c = cfg
  return
  
  
 def allowfeed(self,m):
  alwaysusers = self.c.getlist("alwaysfeed")
  permit = False;
  if m["user"]["screen_name"].lower() in alwaysusers:
   permit = True
  if m["user"]["verified"] == True:
   permit = True
  if m["user"]["followers_count"] > self.c.get("rules","followersoverride"):
   permit = True
 
  now = datetime.datetime.now()
  allowfrom = self.c.getint("rules","time_from")
  allowto = self.c.getint("rules","time_to")
  if now.hour >= allowfrom and now.hour < allowto:
   # timeok, check when fed last
   lastfed = self.c.get("lastfed","datetime")
   t = datetime.datetime.strptime(lastfed,"%a %b %d %H:%M:%S +0000 %Y")
   diff = datetime.datetime.now() - t
   diffmins = (diff.seconds + (diff.days * 86400)) / 60
   feedinterval = self.c.getint("rules","feed_interval")
   
   if diffmins > feedinterval:
    permit = True
  
  return permit