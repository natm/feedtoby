using System;
using System.Collections;
using System.Collections.Generic;
using System.Drawing;
using System.Drawing.Imaging;
using System.Net;
using log4net;

namespace feederd
{

	public class FeedAction
	{
		private DateTime mFeedStarted;
		private static ILog log = LogManager.GetLogger("feederd");
		private List<Image> mFrame;
		private List<DateTime> mFrameTime;
		
		public FeedAction() { }
		
		public FeedResult DoFeed(string TwitterUsername, string ProfileImageURL)
		{
			FeedResult fr = new FeedResult();
			mFeedStarted = DateTime.Now;
			mFrame = new List<Image>();
			mFrameTime = new List<DateTime>();
			
			log.InfoFormat("Starting feed for '{0}'",TwitterUsername);
			
			mFrame.Add(CamWrapper.SnapHuntcam());
			mFrameTime.Add(DateTime.Now);
			
			// attempt to connect to feeder nanode
			try {
				WebClient w = new WebClient();
				string o = w.DownloadString("");	
			} catch {
				log.Warn("Unable to connect to feeder");
				return fr;
			}
			
			motion.MotionDetector3Optimized md = new motion.MotionDetector3Optimized();
			md.MotionLevelCalculation = true;
			
			int capsecs = 20;
			log.DebugFormat("Capturing for {0}s...",capsecs);
			DateTime capstart = DateTime.Now;
			TimeSpan ts = DateTime.Now - capstart;
			int f = 0;
			int appeared = -1;
			double appearedsecs = 0;
			while (ts.TotalSeconds < capsecs)
			{
				Image img = CamWrapper.SnapHuntcam();
				mFrame.Add(img);
				mFrameTime.Add(DateTime.Now);
				
				// motion detection
				Bitmap bmp = new Bitmap(img);
				md.ProcessFrame(ref bmp);
				if (appeared == -1)
				{
					if (md.MotionLevel > 0.100) {
						appeared = f;
						appearedsecs = ts.TotalSeconds;
						log.DebugFormat("Toby appeared @ {0:0.0}s",appearedsecs);
						if ((capsecs - ts.TotalSeconds) < 5) {
							log.Debug("Extending capture by 5s");
							capsecs = capsecs + 5;
						}
					}
				}
				System.Threading.Thread.Sleep(500);
				ts = DateTime.Now - capstart;
				f++;
			}
			
			if (appeared == -1)
			{
				log.Debug("Did not appear");
				fr.Appeared = false;
				fr.Tweet = String.Format("Sorry @{0} Toby did not appear at the feeder",TwitterUsername);
			} else {
				log.DebugFormat("Appeared at frame {0}, took {1:0.0}s",appeared,appearedsecs);
				Image[] frames = new Image[9];
				for (int x = 0; x < 8; x++) {
					frames[x] = mFrame[appeared + x];
				}
				// take pic of food hopper
				frames[8] = CamWrapper.SnapAxiscam();
				// assemble multi image
				Image assImg = AssembleImage(frames,appearedsecs,TwitterUsername,ProfileImageURL, capstart);
				assImg.Save("ass.jpg",ImageFormat.Jpeg);
				
				// upload
				string url = CamWrapper.CaptureAndPost(assImg);
				
				string tweet = String.Format("Fed by @{1}, got to feeder in {0:0.0}secs {2} #FeedToby",appearedsecs,TwitterUsername,url);
				fr.Appeared = true;
				fr.Tweet = tweet;
				fr.UploadedURL = url;
			}

			return fr;
		}
		
		
		private Image AssembleImage(Image[] frames, double appearedsecs, string tuser, string turl, DateTime FedAt)
		{
			Bitmap b1 = new Bitmap(640,528);
			Graphics g = Graphics.FromImage(b1);
			g.DrawImage(frames[0],0,0,212,160);
			g.DrawImage(frames[1],213,0,212,160);
			g.DrawImage(frames[2],426,0,212,160);
			g.DrawImage(frames[3],0,160,212,160);
			g.DrawImage(frames[4],213,160,212,160);
			g.DrawImage(frames[5],426,160,212,160);
			g.DrawImage(frames[6],0,320,212,160);
			g.DrawImage(frames[7],213,320,212,160);
			g.DrawImage(frames[8],426,320,212,160);	
			
			// twitter user
			Image twimg = GetTwitterUser(turl);
			g.DrawImage(twimg,0,480);
			string t = String.Format("Fed by @{0}",tuser);
			g.DrawString(t,new Font("Arial",11,FontStyle.Bold),new SolidBrush(Color.White),64,490);
			
			// branding
			g.DrawString("@feedtoby",new Font("Arial",17,FontStyle.Bold),new SolidBrush(Color.White),514,480);
			
			// timing
			string s = String.Format("Fed at {0:HH:mm:ss}, took {1:0.0}s to appear",FedAt,appearedsecs);
			g.DrawString(s,new Font("Arial",12,FontStyle.Bold),new SolidBrush(Color.White),320,510);
			
			
			return (Image)b1;
		}
		
		private static Image GetTwitterUser(string userurl)
		{
			WebClient wcCam = new WebClient();
			byte[] data = wcCam.DownloadData(userurl);
			ImageConverter ic = new ImageConverter();
			return (Image)ic.ConvertFrom(data);
		}
	}
}
