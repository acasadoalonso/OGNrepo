#!/bin/bash

if [ -z $CONFIGDIR ]
then 
     export CONFIGDIR=/etc/local/
fi
DBpath=$(echo    `grep '^DBpath '   $CONFIGDIR/SARconfig.ini` | sed 's/=//g' | sed 's/^DBpath //g' | sed 's/ //g' )
if [ $# = 0 ]; then
	city='lemd'
else
	city=$1
fi

cd $DBpath
python3 ~/src/SARsrc/SARfcst.py $city			>>SARfcst$(date +%y%m%d).log
echo $(date +%H:%M:%S)      				>>SARfcst$(date +%y%m%d).log
echo "============="        				>>SARfcst$(date +%y%m%d).log
echo "======"$(hostname)"======="  			>>SARfcst$(date +%y%m%d).log
/bin/echo '/bin/bash ~/src/SARsrc/sh/SARfcst.sh '$city | at -M $(date +%H:%M)+ 6 hours
cd 
