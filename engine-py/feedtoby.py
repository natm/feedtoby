#! /usr/bin/env python

from __future__ import print_function
import argparse
from twython import Twython
import cherrypy
import time
import datetime
import logging
import FeedAction
import FeedConfig
import FeedResult
import FeedRules
import FeedStats
import FeedWebserver
import sys
from termcolor import colored, cprint
    
def commandfeed(m):
 fs.incr("feedattempt")
 if fr.allowfeed(m) == True:
  fs.incr("feedpermit")
  fa = FeedAction.FeedAction(fc)
  result = fa.DoFeed(m["user"]["screen_name"],m["user"]["profile_image_url"])

  if result.appeared == True:
   fs.incr("feedappeared")
   if fc.getboolean("twitter","allow_tweet") == True:
    cprint('Tweeting: ', 'cyan', end='')
    t.updateStatusWithMedia("fed.jpg",status=result.tweet)
    cprint('ok', 'green')
    fc.set("lastfed","username",m["user"]["screen_name"])
    fc.set("lastfed","datetime",datetime.datetime.now().strftime("%a %b %d %H:%M:%S +0000 %Y"))
  else:
   cprint(("Didnt feed: %s" % (result.reason)), 'red')
   fs.incr("feedfail")
 else:
  fs.incr("feeddecline")

def processmention(m):
 tweet = m["text"].lower().strip()
 prefix = "@feedtoby"
 cprint("@" + m["user"]["screen_name"], 'magenta', end='')
 cprint(" " + tweet, 'white')
 if tweet.startswith(prefix) == True:
  start = len(prefix)
  end = len(tweet)
  content = tweet[start:end].strip()
  if len(content) > 0:
   if content.find("feed") > -1:
    commandfeed(m)

def checkmentions():
 cprint('Polling: ', 'cyan', end='')
 lastmention = fc.get('lastmention','id')
 mentionsok = False
 try:
  mentions = t.getUserMentions(since_id=lastmention)
  mennum = len(mentions)
  mentionsok = True
 except URLError, e:
   cprint("Twitter API error %s" % (e.code),'red')
 
 if mentionsok == True:
  mentions = t.getUserMentions(since_id=lastmention)
 
  minsfed = fc.getminsince("lastfed","datetime")
  
  cprint('ok', 'green', end='')
  
  txtmention = ""
  if mennum == 0:
   txtmention= ""
  elif mennum == 1:
   txtmention = " 1 mention,"
  else:
   txtmention = " %s mentions," % (mennum)
    
  txt = "%s last fed %s mins" % (txtmention,minsfed)
  cprint(txt,'yellow')
  
  for m in reversed(mentions):
   fs.incr("mentions")
   processmention(m)
   fc.set('lastmention','id',m["id"])
   fc.set('lastmention','datetime',m["created_at"])
   fc.set('lastmention','username',m["user"]["screen_name"])

def accountstats():
 ustats = t.showUser(screen_name="feedtoby")
 fs.set("favourites",ustats["favourites_count"])
 fs.set("followers",ustats["followers_count"])
 fs.set("friends",ustats["friends_count"])
 fs.set("tweets",ustats["statuses_count"])



#main stuff...

# command line parsing
parser = argparse.ArgumentParser(description='Feedtoby daemon')
parser.add_argument('-c', help='configuration filename',action='store',dest='cfgfile',required=True)
parser.add_argument('-o', help='only run once',action="store_true",dest='once',default=False)
args = parser.parse_args()

# setup logging
#logging.basicConfig(level=logging.INFO)
#log = logging.getLogger()

# read config
fc = FeedConfig.FeedConfig(args.cfgfile)

fs = FeedStats.FeedStats(fc)
fr = FeedRules.FeedRules(fc)

if fc.getboolean('webserver', 'start') == True:
 websrv = FeedWebserver.FeedWebserver()
 websrv.webparams(fc)
 websrv.start()

fs.incr("started")

twconkey = fc.get('twitter', 'consumer_key')
twconsec = fc.get('twitter', 'consumer_secret')
twacckey = fc.get('twitter', 'access_token_key')
twaccsec = fc.get('twitter', 'access_token_secret')

t = Twython(app_key=twconkey,
            app_secret=twconsec,
            oauth_token=twacckey,
            oauth_token_secret=twaccsec)
            
cprint('Authenticating: ', 'cyan', end='')
auth_tokens = t.get_authorized_tokens()
cprint('ok', 'green')

fs.incr("twitterverifyok")

# print "Last mention %s at %s" % (fc.get('lastmention','id'),fc.get('lastmention','datetime'))

# start operations
accountstats()
checkmentions()

tmentions = time.time()
taccstats = time.time()

# main loop
doloop = True
while doloop == True:

 if args.once == True:
  doloop = False

 if (time.time() - tmentions) > 25:
  tmentions = time.time()
  checkmentions()

 if (time.time() - taccstats) > 180:
  taccstats = time.time()
  accountstats()

 time.sleep(1)

print("Exiting")
