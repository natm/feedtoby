using System;
using System.Collections;
using System.Collections.Generic;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;
using System.Net;
using System.Text;
using System.Xml;
using log4net;
using AForge.Video;
using AForge.Video.VFW;

namespace feederd
{
	/// <summary>
	/// Description of CamWrapper.
	/// </summary>
	public class CamWrapper
	{
		private static ILog log = LogManager.GetLogger("feederd");
	
		public static Image Combined1()
		{
			Image c1 = SnapAxiscam();
			Image c2 = SnapHuntcam();
			Bitmap b1 = new Bitmap(1280,480);
			Graphics g = Graphics.FromImage(b1);
			g.DrawImage(c1,0,0);
			g.DrawImage(c2,640,0);
			return (Image)b1;
		}
		
		public static Image Combined2()
		{
			Image c2 = SnapAxiscam();
			Image c1 = SnapHuntcam();
			Bitmap b1 = new Bitmap(640,480);
			Graphics g = Graphics.FromImage(b1);
			g.DrawImage(c1,0,0);
			g.DrawImage(c2,400,300,240,180);
			return (Image)b1;
		}

		
		
		
		private static Image GetTwitterUser(string userurl)
		{
			WebClient wcCam = new WebClient();
			byte[] data = wcCam.DownloadData(userurl);
			ImageConverter ic = new ImageConverter();
			return (Image)ic.ConvertFrom(data);
		}
		
		public static Image SnapAxiscam()
		{
			WebClient wcCam = new WebClient();
			byte[] data = wcCam.DownloadData("http://");
			ImageConverter ic = new ImageConverter();
			return (Image)ic.ConvertFrom(data);
		}
		
		public static Image SnapHuntcam()
		{
			int errors = 0;
			int errormax = 3;
			Exception e = new Exception();
			while (errors < errormax) {
				try {
					WebClient wcCam = new WebClient();
					wcCam.Credentials = new NetworkCredential("","");
					byte[] data = wcCam.DownloadData("http://");
					ImageConverter ic = new ImageConverter();
					return (Image)ic.ConvertFrom(data);	
				} catch (Exception ex) {
					e = ex;
					errors++;
				}
			}
			throw e;
		}
		
		public static string CaptureAndPost(Image img)
		{
			//string uploadurl = "http://yfrog.com/api/upload";
			string twitusername = "feedtoby";
			string twitpassword = "";
			string yfrogkey = "";

			MemoryStream ms = new MemoryStream();
			img.Save(ms,ImageFormat.Jpeg);
			byte[] data = new byte[ms.Length];
			ms.Position = 0;
			ms.Read(data,0,(int)ms.Length);
			
	        string url = "";
	        int attempts = 4;
	        for (int a = 1; a < attempts; a++) {
	        	url = DoPost(data,twitusername,twitpassword,yfrogkey);
	        	if (url != "") {
	        		break;
	        	}
	        	log.WarnFormat("Failed to upload image, attempt {0}",a);
	        	System.Threading.Thread.Sleep(2000);
	        }
	        if (url == "")
	        {
	        	log.FatalFormat("Unable to upload after {0} attempts",attempts);
	        }
	        
	        return url;
		}
		
		public static string  DoPost(byte[] data, string twitusername, string twitpassword, string yfrogkey)
		{
			// Generate post objects
	        Dictionary<string, object> postParameters = new Dictionary<string, object>();
	        postParameters.Add("username", twitusername);
	        postParameters.Add("password", twitpassword);
	        postParameters.Add("key",yfrogkey);
	        postParameters.Add("media", data);
			string url = "";
	
	        // Create request and receive response
	        string postURL = "http://yfrog.com/api/upload";
	        string userAgent = "feederd";
	        HttpWebResponse webResponse;
	        try {
		        webResponse = WebHelpers.MultipartFormDataPost(postURL, userAgent, postParameters);
	        	
	        } catch {
	    
	        	return "";
	        }
	
	        // Process response
	        StreamReader responseReader = new StreamReader(webResponse.GetResponseStream());
	        string fullResponse = responseReader.ReadToEnd();
	        webResponse.Close();
	        XmlDocument doc = new XmlDocument();
	        doc.LoadXml(fullResponse);
	        
	        try {
	        	XmlNode node = doc.SelectSingleNode("//rsp/mediaurl");
	        	url = node.InnerText;		
	        } catch {
	        	
	        }
	       
	        return url;
		}
		
		
		public static void VidTest()
		{
			List<Bitmap> frames = new List<Bitmap>();
			
			AVIWriter aw = new AVIWriter("DIB ");
			aw.FrameRate = 15;
			aw.Open("test2.avi",320,240);
			int i = 0;
			string surl = "";
			MJPEGStream ms = new MJPEGStream();
			ms.Login = "";
			ms.Password = "";
			ms.Source = surl;
			ms.NewFrame += (sender, e) =>
	        {
				i++;
				//frames.Add(e.Frame);
				aw.AddFrame(e.Frame);
				e.Frame.Save("test" + i.ToString() + ".jpg", ImageFormat.Jpeg);

//	            ((MJPEGStream)sender).Stop();
	        };
			
			ms.Start();
			System.Threading.Thread.Sleep(4000);
			ms.Stop();
			aw.Close();
			
			
			// 
		}
	}
}
