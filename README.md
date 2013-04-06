This is the code behind the Twitter @feedtoby service.

You can follow Toby - http://twitter.com/feedtoby

And watch the original Youtube video - http://youtu.be/l2OkOEffdp0

Installation notes
------------------

### Debian Wheezy - Vanilla install

In a clean netinst'd vm:

    apt-get install openssh-server sudo screen git-core python python-argparse python-oauth2 python-cherrypy python-imaging python-setuptools

Add yourself to /etc/sudoers

Install twython:

    cd ~
    git clone git://github.com/ryanmcgrath/twython.git
    cd twython
    sudo python setup.py install

Install termcolor:

    curl -O http://pypi.python.org/packages/source/t/termcolor/termcolor-1.1.0.tar.gz
    tar -xvzf termcolor-1.1.0.tar.gz
    cd termcolor-1.1.0
    sudo python setup.py install
    
Grab the latest feedtoby code:

    cd ~
    git clone https://github.com/natm/feedtoby

Create yourself a configuration file or edit the example dev.cfg

    cd ~/feedtoby/engine-py
    ./feedtoby.py -c live.cfg

### Raspbian Wheezey 

Grab 2012-08-16-wheezy-raspbian.zip, extract and dd it onto an SD following notes similar to:

    http://spicecoaster.wordpress.com/2012/09/14/raspberry-pi-installing-raspbian-os-preparing-sd-card/
    
Change the default password and hostname, add IPv6 support:

    echo ipv6 >>/etc/modules
    
Follow normal Wheezy vanilla install instructions above.

### OSX 10.7

Get GCC tools from here: https://github.com/kennethreitz/osx-gcc-installer/downloads

Install a git client.

Install freetype: 

    curl -O http://ftp.igh.cnrs.fr/pub/nongnu/freetype/freetype-2.4.5.tar.gz
    tar -xvzf freetype-2.4.5.tar.gz
    cd freetype-2.4.5
    ./configure
    make
    sudo make install
    cd ../

Install PIL:

    curl -O http://effbot.org/downloads/Imaging-1.1.7.tar.gz
    tar -xvzf Imaging-1.1.7.tar.gz
    cd Imaging-1.1.7
    sudo python setup.py install
 
Install termcolor:

    curl -O http://pypi.python.org/packages/source/t/termcolor/termcolor-1.1.0.tar.gz
    tar -xvzf termcolor-1.1.0.tar.gz
    cd termcolor-1.1.0
    sudo python setup.py install
 
Todo - install notes, CherryPy-3.2.2 etc

Remote access to the Pi Feeder
------------------------------

This creates a reverse SSH tunnel out from the Pi, so it can be plugged in on any home or NAT'd network and accessed remotely.

Create /home/nat/reverse-ssh.sh

    #!/bin/sh
    
    set -x
    TARGET_HOST=${1}
    TARGET_PORT=${2}
    while true
    do
        echo "$(date -d "today" +"%Y-%m-%d %H:%M") establishing reverse ssh tunnel to ${TARGET_HOST}:${TARGET_PORT}"
        ssh -R ${TARGET_PORT}:localhost:22 -N ${TARGET_HOST} -o ServerAliveInterval=30
        sleep 1
    done

Add public + private SSH keys to /home/nat/.ssh, create a dedicated user for this!

Append these lines to /etc/rc.local

    su -l nat -c "/home/nat/reverse-ssh.sh microserf.flarg.net 2221" >/tmp/reverse-ssh.log &
<<<<<<< HEAD
=======
    
    
    
    
Setting up dev environment
--------------------------

    ssh git@github.com
    git clone git@github.com:natm/feedtoby.git

See whats changed

    git status
    
Commit and push

    git commit -a -m "blah blah"
    git push origin master
>>>>>>> Updated readme
