#! /usr/bin/env python

from __future__ import print_function
import tweepy     # from: https://github.com/slothyrulez/tweepy/
import argparse
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
import urllib2
import urlparse
import oauth2 as oauth
import json
import os.path
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
    uploadmedia("fed.jpg",result.tweet)
    cprint('ok', 'green')
    fc.set("lastfed","username",m["user"]["screen_name"])
    fc.set("lastfed","datetime",datetime.datetime.now().strftime("%a %b %d %H:%M:%S +0000 %Y"))
  else:
   cprint(("Didnt feed: %s" % (result.reason)), 'red')
   fs.incr("feedfail")
 else:
  fs.incr("feeddecline")

def uploadmedia(filename,statustxt):
 conkey = fc.get('twitter', 'consumer_key')
 consec = fc.get('twitter', 'consumer_secret')
 acckey = fc.get('twitter', 'access_token_key')
 accsec = fc.get('twitter', 'access_token_secret')
 auth = tweepy.OAuthHandler(conkey,consec)
 auth.set_access_token(acckey,accsec)
 twapi = tweepy.API(auth)
 twapi.status_update_with_media(filename,status=statustxt)

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
  mentions = twapi("/1.1/statuses/mentions_timeline.json?since_id=%s" % lastmention)
  mennum = len(mentions)
  mentionsok = True
 except:
   cprint("Twitter API error %s" % (sys.exc_info()[0]),'red')
 
 if mentionsok == True:
  mentions = twapi("/1.1/statuses/mentions_timeline.json?since_id=%s" % lastmention) 
  mentions = twapi("/1.1/statuses/mentions_timeline.json") 
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

def twapi(url):
 endpoint = ("https://api.twitter.com%s" % url)
 response, data = client.request(endpoint)
 jsondata = json.loads(data)
 return jsondata

def accountstats():
 cprint('Stats: ', 'cyan', end='')
 try:
		ustats = twapi("/1/users/show.json?screen_name=feedtoby")
		fs.set("favourites",ustats["favourites_count"])
		fs.set("followers",ustats["followers_count"])
		fs.set("friends",ustats["friends_count"])
		fs.set("tweets",ustats["statuses_count"])
		cprint('ok', 'green')
 except:
   cprint("Twitter API error %s" % (sys.exc_info()[0]),'red')


def oauthverify():
 cprint('OAuth setup','cyan')
 cprint('App key:     ', 'yellow', end='')
 cprint(twconkey,'green')
 cprint('App secret:  ', 'yellow', end='')
 cprint(twconsec,'green')

 consumer_key = fc.get('twitter', 'consumer_key')
 consumer_secret = fc.get('twitter', 'consumer_secret')

 request_token_url = 'https://api.twitter.com/oauth/request_token'
 access_token_url = 'https://api.twitter.com/oauth/access_token'
 authorize_url = 'https://api.twitter.com/oauth/authorize'

 consumer = oauth.Consumer(consumer_key, consumer_secret)
 client = oauth.Client(consumer)

 resp, content = client.request(request_token_url, "GET")
 if resp['status'] != '200':
  raise Exception("Invalid response %s." % resp['status'])

 request_token = dict(urlparse.parse_qsl(content))

 print("Go to the following link in your browser:")
 print("%s?oauth_token=%s" % (authorize_url, request_token['oauth_token']))

 accepted = 'n'
 while accepted.lower() == 'n':
  accepted = raw_input('Have you authorized me? (y/n) ')
 oauth_verifier = raw_input('What is the PIN? ')

 token = oauth.Token(request_token['oauth_token'],request_token['oauth_token_secret'])
 token.set_verifier(oauth_verifier)
 client = oauth.Client(consumer, token)
 resp, content = client.request(access_token_url, "POST")
 access_token = dict(urlparse.parse_qsl(content))
 print("    - oauth_token        = %s" % access_token['oauth_token'])
 print("    - oauth_token_secret = %s" % access_token['oauth_token_secret'])
 fc.set('twitter','access_token_key',access_token['oauth_token'])
 fc.set('twitter','access_token_secret',access_token['oauth_token_secret'])
 fc.set("twitter","access_token_updated",datetime.datetime.now().strftime("%a %b %d %H:%M:%S +0000 %Y"))


#main stuff...

# command line parsing
parser = argparse.ArgumentParser(description='Feedtoby daemon')
parser.add_argument('-c', help='configuration filename',action='store',dest='cfgfile',required=True)
parser.add_argument('-o', help='only run once',action="store_true",dest='once',default=False)
parser.add_argument('-a', help='oauth setup',action="store_true",dest='oauth',default=False)
args = parser.parse_args()

# setup logging
#logging.basicConfig(level=logging.INFO)
#log = logging.getLogger()

# read config
if os.path.isfile(args.cfgfile) == False:
 cprint('Config file specified does not exist', 'red')
 sys.exit()

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

# refresh access key and secret
if args.oauth == True:
 oauthverify()
 sys.exit()

twacckey = fc.get('twitter', 'access_token_key')
twaccsec = fc.get('twitter', 'access_token_secret')

cprint('Authenticating: ', 'cyan', end='')
consumer = oauth.Consumer(key=twconkey, secret=twconsec)
access_token = oauth.Token(key=twacckey, secret=twaccsec)
client = oauth.Client(consumer, access_token)
tweets = twapi("/1/statuses/home_timeline.json")

if len(tweets["errors"]) > 0:
 cprint('oauth error','red')
 sys.exit()
else:
 cprint('ok', 'green')

mentions = twapi("/1.1/statuses/mentions_timeline.json") 
print(mentions)

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

 if (time.time() - tmentions) > 30:
  tmentions = time.time()
  checkmentions()

 if (time.time() - taccstats) > 600:
  taccstats = time.time()
  accountstats()

 time.sleep(1)

print("Exiting")
sys.exit()


