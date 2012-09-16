using System;
using System.IO;
using System.Collections;
using System.Collections.Generic;
using Newtonsoft.Json;

namespace feederd
{

	public class FeederStore
	{
		public DateTime AppStarted;
		public DateTime AppSaved;
		public long LastMentionID = 0;
		public DateTime LastFed;
		public string LastFedBy;
		public int LoopInterval;		// seconds
		public int FeedFrom;			// hour
		public int FeedTo;				// hour
		public int FeedInterval;		// minutes
		public int HourlyLimit;
		public bool FeedWaiting;
		[JsonIgnoreAttribute]
		public List<string> FollowersKnown;
		public List<string> AdminUsers;
		[JsonIgnoreAttribute]
		public List<string> NotValidSentto;
		public bool FeedEnable;
		public string FeedDisableMsg;
		
		public FeederStore()
		{
		}
		
		public static FeederStore Load()
		{
			TextReader tr = new StreamReader("feederd.json");
			string json = tr.ReadToEnd();
			tr.Close();
			FeederStore fs = JsonConvert.DeserializeObject<FeederStore>(json);
			fs.LoadFollowers();
			return fs;
		}
		
		
		public void Save()
		{
			Save("feederd.json");
			SaveFollowers();
		}
		
		private void Save(string filename)
		{
			this.AppSaved = DateTime.Now;
			string json = JsonConvert.SerializeObject(this);
			// sometimes there are problems writing the file, maybe to do with dropbox
			bool writtenok = false;
			while (writtenok == false) {
				try {
					FileInfo fi = new FileInfo(filename);
					if (fi.Exists)
					{
						fi.Delete();
					}
					TextWriter tw = new StreamWriter(filename);
					tw.Write(json);
					tw.Close();
					writtenok = true;
				} catch  {
					System.Threading.Thread.Sleep(1000);
				}

			}
		}
		
		private void LoadFollowers()
		{
			if (FollowersKnown == null) 
			{
				FollowersKnown = new List<string>();
			}
			StreamReader or = new StreamReader("cfgfollowers.txt");
			while (or.Peek() >= 0)
			{
				string follower = or.ReadLine();
				if (follower != null)
				{
					if (follower.Length > 0) {
						FollowersKnown.Add(follower);
					}
				}
			}
			or.Close();
			
		}
		
		private void SaveFollowers()
		{
			FollowersKnown.Sort();
			File.WriteAllLines("cfgfollowers.txt",FollowersKnown.ToArray());
		}
		
		 
	}
}
