#! /usr/bin/env python

import CamWrapper
import urllib2, base64
import Image
import StringIO

username = "admin"
password = "admin"

request = urllib2.Request("http://huntcam1.6wl.flarg.net/GetImage.cgi?CH=0")
base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
request.add_header("Authorization", "Basic %s" % base64string)   
result = urllib2.urlopen(request)

#f = open("out.jpg", 'wb')
#f.write(result.read())
#f.close()

im = Image.open(StringIO.StringIO(result.read()))
im.save("blah.jpg","JPEG")