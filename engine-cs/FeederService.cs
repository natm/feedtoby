using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;
using System.Net;
using System.Text;
using Kayak;
using Kayak.Framework;
using Owin;
using log4net;

namespace feederd
{
	class FeederService : KayakService
	{
		private static ILog log = LogManager.GetLogger("feederd");
		
		[Path("/")]
		public void Root()
		{
			StringBuilder sb = new StringBuilder();
			sb.Append("<html>");
			sb.Append("<head><title>feederd</title></head>");
			sb.Append("<body>");
			sb.Append("<h2>feederd</h2>");
			if (Worker.Instance.Uptime.TotalSeconds < 60)
			{
				sb.AppendFormat("<p>Running for {0:0} seconds",Worker.Instance.Uptime.TotalSeconds);
			} else {
				sb.AppendFormat("<p>Running for {0:0} minutes",Worker.Instance.Uptime.TotalMinutes);
			}
			sb.AppendFormat("<p>{0} cycles</p>",Worker.Instance.CycleCount);
			sb.AppendFormat("<p>{0} mentions processed</p>",Worker.Instance.MentionsProcessed);
			sb.Append("<p>&nbsp;</p>");
			sb.Append("<img src='/image'/>");	
			sb.Append("</body>");
			sb.Append("</html>");
			Response.Write(sb.ToString());
		}
		

		
	
		[Path("/cmdphoto")]
		public void Photo()
		{
		//	Worker.Instance.CommandPhoto(Worker.CommandSource.Device,"",0);
		}
		
		[Path("/cmdfeed")]
		public void Feed()
		{
		//	Worker.Instance.CommandFeed(Worker.CommandSource.Device,"",0,true);
		}
	
		[Path("/devdebug")]
		public void DevDebug()
		{
			string msg = Request.RequestUri;
			msg = msg.Replace("/devdebug?","");
			msg = msg.Replace("%20", " ");
			log.DebugFormat("{0}",msg);
		}
	}
}
