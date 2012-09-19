import ConfigParser
import datetime

class FeedConfig:
 """Feeder configuration routines"""
 cfg = None
 cfgname = ""
 
 def __init__(self,filename):
  self.cfg = ConfigParser.RawConfigParser()
  self.cfgname = filename
  self.cfg.read(self.cfgname)
  return
  
 def get(self,section,option):
  return self.cfg.get(section,option)
 
 def getint(self,section,option):
  return int(self.cfg.get(section,option))
 
 def getboolean(self,section,option):
  return self.cfg.getboolean(section,option)

 def getfloat(self,section,option):
  return float(self.cfg.get(section,option))
 
 def getminsince(self,section,option):
  val = self.cfg.get(section,option)
  valdate = datetime.datetime.strptime(val,"%a %b %d %H:%M:%S +0000 %Y")
  diff = datetime.datetime.now() - valdate
  mins = (diff.seconds + (diff.days * 86400)) / 60
  return mins

 def getlist(self,sectionname):
  l = []
  list_items = self.cfg.items(sectionname)
  for key, val in list_items:
   l.append(val)
  return l
 
 def set(self,section,option,value):
  self.cfg.set(section,option,value) 
  fsobj = open(self.cfgname, 'w')
  self.cfg.write(fsobj)
  fsobj.close()
  return
  
 def has_section(self,section):
  return self.cfg.has_section(section)
  
 def has_option(self,section,option):
  return self.cfg.has_option(section,option)
  
 def items(self,section):
  return self.cfg.items(section)