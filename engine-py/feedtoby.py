#! /usr/bin/env python

import argparse
from twython import Twython
import cherrypy
import time
import logging
import FeedAction
import FeedConfig
import FeedResult
import FeedRules
import FeedStats
import FeedWebserver
    
def commandfeed(m):
 fs.incr("feedattempt")
 if fr.allowfeed(m) == True:
  fs.incr("feedpermit")
  fa = FeedAction.FeedAction(fc)
  result = fa.DoFeed(m["user"]["screen_name"],m["user"]["profile_image_url"])

  if result.appeared == True:
   print "Appeared"
   fs.incr("feedappeared")
   if fc.getboolean("twitter","allow_tweet") == True:
    t.updateStatusWithMedia("fed.jpg",status=result.tweet)
    fc.set("lastfed","username",m["user"]["screen_name"])
    fc.set("lastfed","datetime",m["created_at"])
  else:
   print "Didnt feed: %s" % (result.reason)
   fs.incr("feedfail")
 else:
  fs.incr("feeddecline")

def processmention(m):
 #log.info("%s %s %s" % (m["id"],m["created_at"],m["user"]["screen_name"]))
 tweet = m["text"].lower().strip()
 prefix = "@feedtoby"
 print "%s - %s" % (m["user"]["screen_name"],tweet)
 print ""
 if tweet.startswith(prefix) == True:
  start = len(prefix)
  end = len(tweet)
  content = tweet[start:end].strip()
  if len(content) > 0:
   if content.find("feed") > -1:
    commandfeed(m)

def checkmentions():
 lastmention = fc.get('lastmention','id')
 mentions = t.getUserMentions(since_id=lastmention)
 log.debug("%s mentions" % (len(mentions)))
 for m in reversed(mentions):
  fs.incr("mentions")
  fc.set('lastmention','id',m["id"])
  fc.set('lastmention','datetime',m["created_at"])
  fc.set('lastmention','username',m["user"]["screen_name"])
  processmention(m)

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
logging.basicConfig(level=logging.INFO)
log = logging.getLogger()

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

auth_tokens = t.get_authorized_tokens()


fs.incr("twitterverifyok")
print ""
print "Authenticated ok"
print ""
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

print "Exiting"
