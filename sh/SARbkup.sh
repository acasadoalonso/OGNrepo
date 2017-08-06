#!/bin/bash

sudo mount -t nfs casadonfs:/nfs/NFS/Backups /bkups
if [  -d /bkups ]
then
	tar -czvf /bkups/OGN/BKUP_$(hostname)_$(date +%y.%m.%d).tar /home/pi --exclude="/home/pi/google_drive"
fi
cd ..
