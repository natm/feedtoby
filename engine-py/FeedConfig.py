import ConfigParser

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