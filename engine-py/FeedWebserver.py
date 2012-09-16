import cherrypy
import threading

class FeedWebserver(threading.Thread):
 """Embedded web server for remote control"""
 
 def run(self):
  cherrypy.quickstart(HelloWorld())
 
 def webparams(self,fc):
  
  return

  
class HelloWorld(object):
    def index(self):
        print self
        return "<p>Feedtoby</p>"
    index.exposed = True
    
    
    
    