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
   print lastfed
   #  doesn't work from here on ************

  return permit