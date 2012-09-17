import Image
import urllib2, base64
from PIL import Image, ImageFont, ImageDraw
import StringIO
import datetime

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

 def GetImgFromUrl(self,url):
  request = urllib2.Request(url)
  result = urllib2.urlopen(request)
  im = Image.open(StringIO.StringIO(result.read()))
  return im

 def SnapCam2(self):
  return self.GetImgFromUrl(self.cfg.get("camera2","url"))
   
 def AssembleImage(self,frames,tooksecs,fedby,profimgurl):
  im = Image.new("RGB",(640,528))
  im.paste(frames[0], (0, 0))
  im.paste(frames[1], (213, 0))
  im.paste(frames[2], (426, 0))
  im.paste(frames[3], (0, 160))
  im.paste(frames[4], (213, 160))
  im.paste(frames[5], (426, 160))
  im.paste(frames[6], (0, 320))
  im.paste(frames[7], (213, 320))
  im.paste(frames[8], (426, 320))
  
  now = datetime.datetime.now()
  msg1 = "Fed on %s" % (now.strftime("%a %d %b %Y at %H:%M"))
  msg2 = "Got to feeder in %0.1f secs" % (tooksecs)
  msg3 = "Fed by @%s" % (fedby)
  draw = ImageDraw.Draw(im)
  font16 = ImageFont.truetype("fonts/AveriaSans-Bold.ttf", 16)
  font34 = ImageFont.truetype("fonts/AveriaSans-Bold.ttf", 34)
  draw.text((0, 500), msg3, font=font16,fill='#fff')
  draw.text((470,480), "@feedtoby", font=font34,fill='#fff')
  draw.text((210,485), msg1, font=font16,fill='#fff')
  draw.text((210,502), msg2, font=font16,fill='#fff')
  
  #draw.rectangle((480,48,460,180),fill='#0A1F73')
  imgprof = self.GetImgFromUrl(profimgurl).resize((48, 48), Image.ANTIALIAS)
  im.paste(imgprof,(0,480))
  
  del draw
  return im