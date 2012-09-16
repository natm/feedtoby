#! /usr/bin/env python

import CamWrapper
import CamMotion
import FeedConfig

fc = FeedConfig.FeedConfig("live.cfg")
cw = CamWrapper.CamWrapper(fc)
cm = CamMotion.CamMotion(fc,cw)

cm.capture(8,212,160)
if cm.appeared == False:
 print "Didn't appear"
else:
 print "appeared at f%s @ %0.2fs" % (cm.appearedframe,cm.appearedsecs)
 im = cw.AssembleImage(cm.frames)
 im.save("test.jpg","JPEG")
 print "written assembly"