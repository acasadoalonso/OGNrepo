#!/usr/bin/env bash

apt-get update
apt-get install -y apache2
if ! [ -L /var/www ]; then
  rm -rf /var/www
  ln -fs /vagrant /var/www
fi
if [ -f /nfs/hosts ]
then 
	sudo cat /nfs/hosts /etc/hosts
fi

if [ -f /tmp/commoninstall.sh ]
then 
	sudo bash /tmp/commoninstall.sh
fi

