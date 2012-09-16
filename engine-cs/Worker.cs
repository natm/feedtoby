using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Threading;
using System.Text;
using TweetSharp;
using log4net;
using Kayak;
using Kayak.Framework;
using Owin;

namespace feederd
{

	public class Worker
	{
		private static Worker instance;
		private TwitterService ts;
		private FeederStore store;
		private Dictionary<string,bool> validcmds = new Dictionary<string, bool>();
		private static ILog log = LogManager.GetLogger("feederd");
		private int cycle = 0;
		private int mentioncount = 0;
		private long followercount;
		private long feedsuccess = 0;
		private long feedattempt = 0;
		private long photosuccess = 0;
		private long aboutsuccess = 0;
		private long helpsuccess = 0;
		private long tweetcount = 0;
		private long tweetreplycount = 0;
		private long dupetweetcount = 0;
		private Dictionary<int,DateTime> devconn = new Dictionary<int, DateTime>();
		private Dictionary<int,DateTime> devlast = new Dictionary<int, DateTime>();
		private Dictionary<int,int> devhits = new Dictionary<int,int>();
		private int currentHour;
		private Dictionary<string,int> hourlytweets = new Dictionary<string, int>();
		private List<string> dupetweets = new List<string>();
		private int FollowerCheckMins = 10;
		private DateTime FollowerCheckLast;
		private int FollowingCheckMins = 10;
		private DateTime FollowingCheckLast;
		private int StatsMin = 5;
		private DateTime StatsLast;
		
		
		public enum CommandSource {
			Twitter, Device
		}
		
		private Worker()
		{
		}
		
		public static Worker Instance
		{
			get {
				if (instance == null)
				{
					instance = new Worker();
				}
				return instance;
			}
		}
		
		public void Start()
		{
			store = FeederStore.Load();
			store.AppStarted = DateTime.Now;
			store.FeedWaiting = false;
			store.Save();
				
			if (store.AdminUsers == null)
			{
				store.AdminUsers = new List<string>();
				store.AdminUsers.Add("natmorris");
				store.Save();
			}

			if (store.NotValidSentto == null) {
				store.NotValidSentto = new List<string>();
				store.Save();
			}
			
			KayakServer server = new KayakServer();
			server.UseFramework();
			server.Start(new IPEndPoint(IPAddress.Any,82));
			
			log.InfoFormat("Webserver listening on: {0}",server.EndPoint);
			
			log.InfoFormat("Checking every {0} secs",store.LoopInterval);
			
			ts = new TwitterService("","");
			/*
			OAuthRequestToken reqToken = ts.GetRequestToken();
			Uri uri = ts.GetAuthorizationUri(reqToken);
			Console.WriteLine(uri.AbsoluteUri);
			string key = Console.ReadLine();
			OAuthAccessToken access = ts.GetAccessToken(reqToken,key);
			
			Console.WriteLine(access.Token);
			Console.WriteLine(access.TokenSecret);
			*/
			validcmds.Add("about",false);
			validcmds.Add("feed",false);
			validcmds.Add("help",false);
			validcmds.Add("photo",false);
			
			string a= "";
			string b = "";
			ts.AuthenticateWith(a,b);
			currentHour = DateTime.Now.Hour;
			
			
		//	FeedAction fa = new FeedAction();
		//	FeedResult fr = fa.DoFeed("natmorris","http://a0.twimg.com/profile_images/1981121793/image_normal.jpg");
			
		//CamWrapper.VidTest();
			DoLoop();
		}
		
				
		public void DoLoop()
		{
			bool abandon = false;
			while (!abandon)
			{
				cycle++;
				CheckThrottle();
				CheckMentions(cycle);
				CheckTimings();
				try {
					CheckFollowers();
				} catch {
					log.Warn("Error checking followers");
				}
				DoStats();
				System.Threading.Thread.Sleep(store.LoopInterval * 1000);
			}
		}
		
		private void DoStats()
		{
			TimeSpan t = DateTime.Now - StatsLast;
			if (t.TotalMinutes > StatsMin)
			{
				StatPost("feedinterval",store.FeedInterval);
				StatPost("followers",store.FollowersKnown.Count);
				StatPost("mentions",mentioncount);
				StatPost("cycles",cycle);
				StatPost("feedsuccess",feedsuccess);
				StatPost("feedattempt",feedattempt);
				StatPost("photosuccess",photosuccess);
				StatPost("aboutsuccess",aboutsuccess);
				StatPost("helpsuccess",helpsuccess);
				StatPost("tweetcount",tweetcount);
				StatPost("tweetreplycount",tweetreplycount);
				StatPost("dupetweetcount",dupetweetcount);
				TimeSpan tfed = DateTime.Now - store.LastFed;
				StatPost("lastfeed",(long)tfed.TotalMinutes);
				if (ts.Response.RateLimitStatus.HourlyLimit > 0) {
					StatPost("apilimit",ts.Response.RateLimitStatus.HourlyLimit);	
				}
				if (ts.Response.RateLimitStatus.RemainingHits > 0) {
					StatPost("apiremain",ts.Response.RateLimitStatus.RemainingHits);
				}
				
				StatsLast = DateTime.Now;
			}
		}
		
		private void StatPost(string name, long val)
		{
			WebClient wcstat = new WebClient();
			string u = String.Format("http://127.0.0.1/add?type=stat&format=num&key=feeder_{0}&value={1}",name,val);
			string x = wcstat.DownloadString(u);
		}
		
		private void CheckFollowers()
		{
			TimeSpan t = DateTime.Now - FollowerCheckLast;
			int f = 0;
			int fnew = 0;
			
			if (t.TotalMinutes > FollowerCheckMins)
			{
				TwitterCursorList<TwitterUser> followers = ts.ListFollowers();
				if (followers != null) {
		
						foreach (TwitterUser tu in followers)
						{
							if (tu != null) {
								f++;
								if (!store.FollowersKnown.Contains(tu.ScreenName)) {
									// new follower
									fnew++;
									string newfollower = tu.ScreenName;
									store.FollowersKnown.Add(newfollower);
								}
							}
						
					}
					store.Save();
					FollowerCheckLast = DateTime.Now;
					
					if (fnew > 0)
					{
						log.InfoFormat("{0} followers, {1} new!",store.FollowersKnown.Count,fnew);
					} else {
						log.InfoFormat("{0} followers", store.FollowersKnown.Count);
					}
					followercount = f;
				}
			}

			
		}
		
		private void CheckFollowing()
		{
			TimeSpan t = DateTime.Now - FollowingCheckLast;
			
			if (t.TotalMinutes > FollowingCheckMins)
			{
				List<TwitterUser> friends = ts.ListFriends();
				foreach (TwitterUser friend in friends) {
					
				}
				FollowingCheckLast = DateTime.Now;
			}
		}
		
		private void CheckThrottle()
		{
			if (currentHour != DateTime.Now.Hour) {
				if (hourlytweets.Count > 0) {
					// reset hourly limits
					log.DebugFormat("Resetting tweet throttling for {0} users",hourlytweets.Count);
					log.DebugFormat("Resetting dupe tweets {0}",dupetweets.Count);
					
					currentHour = DateTime.Now.Hour;
					hourlytweets.Clear();
					dupetweets.Clear();
					store.Save();
				}
				
			}
		}
		
		private void CheckTimings()
		{
			int notfed = 2;
			TimeSpan t = DateTime.Now - store.LastFed;
			if (t.TotalHours > notfed) {
				if (DateTime.Now.Hour > (store.FeedFrom + notfed)) {
					string s = String.Format("Not been fed for over {0} hours, last fed by @{1} at {2:HH:mm}",notfed,store.LastFedBy,store.LastFed);
					//Tweet(s);
				}
			}
		}
		
		private void CheckMentions(int cycle)
		{
			TimeSpan t = DateTime.Now - store.LastFed;
			log.DebugFormat("Cycle {0} at {1:HH:mm:ss} last fed {2:0} mins ago",cycle,DateTime.Now,t.TotalMinutes);
			IEnumerable<TwitterStatus> mentions;
			if (store.LastMentionID == 0)
			{
				mentions = ts.ListTweetsMentioningMe(10);
			} else {
				mentions  = ts.ListTweetsMentioningMeSince(store.LastMentionID);
			}
			
			//log.DebugFormat("{0} {1}",ts.Response.RateLimitStatus.HourlyLimit,ts.Response.RateLimitStatus.RemainingHits);
			if (mentions != null) {
				ProcessMentions(mentions);
				
			}
			
		}
		
		private void ProcessMentions(IEnumerable<TwitterStatus> mentions)
		{
			foreach (TwitterStatus mention in mentions)
			{				
					ProcessMention(mention);
			}
		}
		
		private void ProcessMention(TwitterStatus mention) {
			mentioncount++;
				long id = mention.Id;
				store.LastMentionID = id;
				store.Save();

				// only process requests directed at me
				string prefix = "@feedtoby ";
				if (mention.Text != null) {
				if (mention.Text.ToLower().StartsWith(prefix))
					{
						string content = mention.Text.Substring(prefix.Length,mention.Text.Length - prefix.Length).Trim();
						string user = mention.User.ScreenName;
						
						while (content.Contains("  ")) {
							content = content.Replace("  "," ");
						}
						
						if (hourlytweets.ContainsKey(user)) {
							hourlytweets[user]++;
						} else {
							hourlytweets.Add(user,1);
						}
						
						log.InfoFormat("{2}  @{1} {0}",mention.Text,user,hourlytweets[user]);
						
						
						// throttling
						if (hourlytweets[user] > store.HourlyLimit) {
						//	TweetInReplyTo(id,"@{0} Hourly tweet limit exceeded",user);
							store.Save();
							return;
						}
						
						string[] cparts = content.Split(' ');
						string command = cparts[0].ToLower();
						//log.DebugFormat("Command = '{0}'",command);
						if (command.ToLower().Contains("feed")) {
							CommandFeed(CommandSource.Twitter,mention.User,id,false);
						}
					}
				}
				
				store.Save();
		}
		
		
		public void CommandFeed(CommandSource cmdsrc, TwitterUser tu, long StatusID, bool AllowOverride)
		{
			feedattempt++;

			string twuser = tu.ScreenName.ToLower();
			
			bool allow = AllowFeed(tu);
			
			
			if (allow) {
				FeedAction fa = new FeedAction();
				FeedResult fr = fa.DoFeed(tu.ScreenName,tu.ProfileImageUrl);
				if (fr.Appeared) {
					Tweet(fr.Tweet);
					store.LastFed = DateTime.Now;
					store.LastFedBy = twuser;
					feedsuccess++;
				} else {
					
				}
				store.Save();
			}
	
		}
		
		private bool AllowFeed(TwitterUser tu)
		{
			List<string> always = new List<string>();
			always.Add("natmorris");
			always.Add("flangey");
			always.Add("bijalsanghani");
			//always.Add("tmenari");
			always.Add("ElizaSkelding");
			//always.Add("gregoryfenton");
			
			bool permitfeed = false;
			if (always.Contains(tu.ScreenName.ToLower())) {
			    	permitfeed = true;
			}
			    	
			if (tu.FollowersCount > 2000) 
			{
				permitfeed = true;
			}
			if (tu.IsVerified == true) {
				permitfeed = true;
			}
				if (!ValidTime())
				{
					// out of hourst
					if (DateTime.Now.Hour < store.FeedFrom) {
						//	TweetInReplyTo(StatusID,"@{0} sorry Toby can only be fed between {1:00}:00 and {2:00}:00 GMT, he's probably still asleep now",twuser,store.FeedFrom,store.FeedTo);
					} else if (DateTime.Now.Hour > store.FeedTo) {
						//	TweetInReplyTo(StatusID,"@{0} sorry Toby can only be fed between {1:00}:00 and {2:00}:00 GMT, he'll be sleeping now",twuser,store.FeedFrom,store.FeedTo);
					} else {
						//	TweetInReplyTo(StatusID,"@{0} sorry Toby can only be fed between {1:00}:00 and {2:00}:00 GMT",twuser,store.FeedFrom,store.FeedTo);
					}
					
					
				} else {
					TimeSpan t = DateTime.Now - store.LastFed;
					if (t.TotalMinutes < store.FeedInterval)
					{
						// too soon	
					} else {
						// feed toby
						permitfeed = true;
					}
				}
			return permitfeed;
		}
		
		private void CommandEnable(TwitterUser tu, long twid, string content)
		{
			if (ValidAdminUser(tu) == false) {
				TweetInReplyTo(twid,"@{0} sorry you're not permitted to use that command",tu.ScreenName);
				return;
			}
			store.FeedEnable = true;
			store.Save();
		}
		
		private void CommandDisable(TwitterUser tu, long twid, string content)
		{
			if (ValidAdminUser(tu) == false) {
				TweetInReplyTo(twid,"@{0} sorry you're not permitted to use that command",tu.ScreenName);
				return;
			}
			string msg = "";
			
			if (msg == "") {
				store.FeedDisableMsg = "";
			} else {
				store.FeedDisableMsg = msg;
			}
			
			store.FeedEnable = false;
			store.Save();
		}
		
		private bool ValidAdminUser(TwitterUser tu)
		{
			bool found = false;
			foreach (string s in store.AdminUsers) {
				if (s.ToLower().Trim() == tu.ScreenName.ToLower().Trim()) {
					found = true;
				}
			}
			return found;
		}
		
		private bool ValidTime()
		{
			int hour = DateTime.Now.Hour;
			if (hour >= store.FeedFrom && hour < store.FeedTo) 
			{
				return true;
			}
			return false;
		}
		
		private void TweetInReplyTo(long id, string msgfmt, params Object[] args)
		{
			
			string msg = String.Format(msgfmt,args);
			if (dupetweets.Contains(msg)) {
				log.WarnFormat("Dupe tweet: {0}",msg);
				dupetweetcount++;	
			} else {
				tweetreplycount++;
				log.InfoFormat("Tweeting: {0}",msg);
				TwitterStatus stat = ts.SendTweet(msg,id);
			}
		}
		
		private void Tweet(string msgfmt, params Object[] args)
		{
			string msg = String.Format(msgfmt,args);
			if (dupetweets.Contains(msg)) {
				log.WarnFormat("Dupe tweet: {0}",msg);
				dupetweetcount++;
			} else {
				tweetcount++;
				log.InfoFormat("Tweeting: {0}",msg);
				ts.SendTweet(msg);
				
			}

		}

		public TimeSpan Uptime {
			get {
				TimeSpan up = DateTime.Now - store.AppStarted;
				return up;				
			}
		}
		
		public int CycleCount {
			get { return cycle; }
		}
		
		public int MentionsProcessed {
			get { return mentioncount; }
		}
	}
	
	
}
