This is the code behind the Twitter @feedtoby service.

You can follow Toby - http://twitter.com/feedtoby

And watch the original Youtube video - http://youtu.be/l2OkOEffdp0

Dev on Debian Wheezy
====================
In a clean netinst'd vm:

    apt-get install openssh-server sudo git-core python python-argparse python-oauth2 python-cherrypy python-imaging python-setuptools

Add yourself to /etc/sudoers

Install twython:

    cd ~
    git clone git://github.com/ryanmcgrath/twython.git
    cd twython
    sudo python setup.py install

Grab the latest feedtoby code:

    cd ~
    git clone https://github.com/natm/feedtoby

Create yourself a configuration file or edit the example dev.cfg

    cd ~/feedtoby/engine-py
    ./feedtoby.py -c live.cfg

Dev on Raspbian
===============

Todo

Dev on OSX 10.8
===============

Get GCC tools from here: https://github.com/kennethreitz/osx-gcc-installer/downloads

* CherryPy-3.2.2
* Imaging-1.1.7

Todo - install notes
