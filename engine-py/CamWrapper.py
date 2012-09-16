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
  
 def SnapHuntcam():
  return