using System;
using log4net;

namespace feederd
{
	class Program
	{
		private static ILog log = LogManager.GetLogger("feederd");
			
		public static void Main(string[] args)
		{
			log4net.Config.XmlConfigurator.Configure();
            log.Info("--");	

			Worker.Instance.Start();
		}
	}
}