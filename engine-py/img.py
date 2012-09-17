#! /usr/bin/env python

import CamWrapper
import CamMotion
import FeedConfig
import datetime

now = datetime.datetime.now()
print now.strftime("%a %d %b %Y at %H:%M")

fc = FeedConfig.FeedConfig("live.cfg")
cw = CamWrapper.CamWrapper(fc)
cm = CamMotion.CamMotion(fc,cw)

cm.capture(8,212,160)
if cm.appeared == False:
 print "Didn't appear"
else:
 print "appeared at f%s @ %0.2fs" % (cm.appearedframe,cm.appearedsecs)
 im = cw.AssembleImage(cm.frames,cm.appearedsecs,"natmorris","http://a0.twimg.com/profile_images/2616924160/251066_506954102667872_962716002_t_normal.jpg")
 im.save("test.jpg","JPEG")
 print "written assembly"