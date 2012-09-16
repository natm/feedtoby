import Image
import urllib2, base64
import Image
import StringIO

class CamWrapper:
 """Video functions"""
 cfg = None
 
 def __init__(self,cfg):
  self.cfg = cfg
  return
  
 def SnapCam1(self):
  username = self.cfg.get("camera1","username")
  password = self.cfg.get("camera1","password")
  request = urllib2.Request(self.cfg.get("camera1","url"))
  base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
  request.add_header("Authorization", "Basic %s" % base64string)   
  result = urllib2.urlopen(request)
  im = Image.open(StringIO.StringIO(result.read()))
  return im
  
 def SnapCam2(self):
  request = urllib2.Request(self.cfg.get("camera2","url"))
  result = urllib2.urlopen(request)
  im = Image.open(StringIO.StringIO(result.read()))
  return im