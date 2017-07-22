#!/usr/bin/python
import time
import sys
import os
from   datetime import datetime, timedelta
from   geopy.distance import vincenty       # use the Vincenty algorithm
import MySQLdb                              # the SQL data base routines
import sqlite3                              # the SQL data base routines
import kglid
import argparse

def printfid (fid):			   # prin the list of relays
        for k in fid[key]:
		for kk in k:
        		if kk[3:9] in kglid.kglid:
                		gid=kglid.kglid[kk[3:9]]    # report the station name
        		else:
                		gid="NOSTA"             # marked as no sta
			print gid, k[kk], 
	return (';')
# 
# ----------------------------------------------------------------------------
#

print "Start RELAY analysis V0.2.7"
print "==========================="
maxdist=0.0
totdist=0.0
ncount=0
nrecs=0
relaycnt=0
fid=  {}   		                    # FLARM ID list
import config                               # import the main settings
DBname=config.DBname
DBhost=config.DBhost
DBuser=config.DBuser
DBpasswd=config.DBpasswd
MySQL=config.MySQL
fn=sys.argv[1:]                             # take the name of the second arg
fname=str(fn)[2:16]
dte=str(fn)[6:12]                           # take the date from the file name
date=datetime.now()                         # get the date

parser=argparse.ArgumentParser(description="OGN Tracker relay analysis")
parser.add_argument("-n", '--name',      required=True, dest='filename', action='store')
parser.add_argument('-i', '--intval',    required=False, dest='intval', action='store', default='05')
args=parser.parse_args()
fname=args.filename
intsec=int(args.intval)
dte=fname[4:10]                             # take the date from the file name
print "Filename:", args.filename, "Interval:", args.intval


if (MySQL):
        conn=MySQLdb.connect(host=DBhost, user=DBuser, passwd=DBpasswd, db=DBname)     # connect with the database
else:
        conn=sqlite3.connect(r'../OGN.db')  # connect with the database
curs1=conn.cursor()                         # set the cursor
curs2=conn.cursor()                         # set the cursora

print 'Filename:', fname, "at", dte, 'Process date/time:', date.strftime(" %y-%m-%d %H:%M:%S")     # display file name and time
datafilei = open(fname, 'r')                # open the file with the logged data

lasttime=''
while True:                                 # until end of file
        data=datafilei.readline()           # read one line
        if not data:                        # end of file ???
                break
	relpos= data.find("APRS,RELAY*")    # look for old RELAY messages
        if relpos != -1:
		relaycnt += 1		    # just increas the counter and leva
                continue

        relpos= data.find("*,qAS")	    # look for the new RELAY message that tell us who the the station making the RELAY
        if relpos == -1:
                continue		    # nothing to do
        nrecs += 1			    # increase the counter of RELAY messages
	ogntracker=data[relpos-9:relpos]    # OGN tracker doing the RELAY
        flrmid=data[0:9]		    # device (either flarm or tracker) that has been done the RELAY
        dtepos=data.find(":/")+2	    # position report
	station=data[relpos+6:dtepos-2]	    # OGN station receiving the RELAY message
	if data[dtepos+6] == 'h':	    # check the time format
        	timefix=data[dtepos:dtepos+6]
	elif data[dtepos+6] == 'z':
        	timefix=data[dtepos+2:dtepos+6]+'00'
	else:
		continue		    # unkown format ... nothing to do
        if timefix == lasttime:
                continue
        lasttime=timefix
	p2=data.find('/A=')+3               # scan for the altitude on the body of the message
        altif=data[p2+1:p2+6]               # get the altitude in feet
        altim=int(int(altif)*0.3048)        # convert the altitude in meters
        if altim > 15000 or altim < 0:
            altim=0
        alti='%05d' % altim                 # convert it to an string

        if flrmid[3:9] in kglid.kglid:      # if it is a known glider ???
                        reg=kglid.kglid[flrmid[3:9]]     # get the registration
        else:
                        reg='NOREG '        # no registration
        if ogntracker[3:9] in kglid.kglid:  # if it is a known glider ???
                        trk=kglid.kglid[ogntracker[3:9]]
        else:
                        trk=ogntracker	    # no tracker registration
        inter=timedelta(seconds=intsec)
        Y=int(dte[0:2]) + 2000		    # build the datetime
        M=int(dte[2:4])
        D=int(dte[4:6])
        h=int(timefix[0:2])
        m=int(timefix[2:4])
        s=int(timefix[4:6])
	#print flrmid, ogntracker, data
        T=datetime(Y,M,D,h,m,s)			# in formate datetime in order to handle the intervals
        T1=T-inter				# +/- interval to look into database
        T2=T+inter
        timefix1=T1.strftime("%H%M%S")		# now in string format
        timefix2=T2.strftime("%H%M%S")
						# build the SQL commands
        sql1="select latitude, longitude from OGNDATA where idflarm ='"+flrmid+"'     and date = '"+dte+"' and time= '"+timefix+"';"
        sql2="select latitude, longitude from OGNDATA where idflarm ='"+ogntracker+"' and date = '"+dte+"' and time>='"+timefix1+"' and time <='"+timefix2+"';"
        #print "SSS", nrecs, dte, timefix, flrmid, ogntracker, sql1, sql2
        curs1.execute(sql1)
        row1=curs1.fetchone()			# should be one one record
	#print "R1", row1
        if (row1) != None:			# should be always one record
                latlon1=(row1[0], row1[1])	# position of the glider
                curs2.execute(sql2)		# look for all the OGN trackers positions in that interval
                rows2=curs2.fetchall()		# get all position
                nr=0
                maxrr=0
                for row2 in rows2:		# scan all the posible records
                        nr +=1			# number of OGN tracker reconds found
                        maxrr=0			# maximun range
                        latlon2=(row2[0], row2[1])		# position of the OGN tracker
                        distance=vincenty(latlon1, latlon2).km	# get the distance from the flarm to the tracker
                        distance=round(distance,3)		# round it to 3 decimals
                        if distance > maxdist:			# maximun absolute distance
                                maxdist=distance
                        if distance > maxrr and distance > 0.050:	# max distance for this scan
                                maxrr=distance
                        else:
                                continue
                if maxrr > 0:			# if we found something
			maxrange={}			# build the dict
			maxrange[ogntracker]=maxrr	# just the ogn tracker and max dist
                	if not flrmid in fid :          # if we did not see the FLARM ID
				maxlist=[]	# init the list
				maxlist.append(maxrange)
                                fid[flrmid]=maxlist
			else:
				mm= fid[flrmid]	# the maxlist
				#print "TTT", flrmid, mm
				idx=0
				found=False
				for entry in mm:
					if ogntracker in entry: 
						found=True
						if entry[ogntracker] < maxrr:
							mm[idx]=maxrange
                                			fid[flrmid]=mm
							break
					idx += 1
						
				if not found :		# if that tracker is not on the list, just add it
					fid[flrmid].append(maxrange)
                        ncount += 1
                        print  "N:%3d:%3d  OGNTRK: %9s %9s  FlrmID: %9s %9s Max. dist.: %6.3f Kms. at: %sZ Altitud: %s from: %s" % (ncount, nr, trk, ogntracker, reg, flrmid, maxrr, timefix, alti, station)
                totdist += maxrr		# add the total distance

if ncount > 0:
	print "Max. distance", maxdist, "Avg. distance", totdist/ncount, "Total number of records", nrecs
print "Old relays", relaycnt
print "\n\n", fid, "\n\n"
k=list(fid.keys())                  # list the IDs for debugging purposes
k.sort()                            # sort the list
for key in k:                       # report data
        if key[3:9] in kglid.kglid:
                gid=kglid.kglid[key[3:9]]    # report the glider reg
        else:
                gid="NOSTA"             # marked as no sta
        print key, ':', gid ,"==>" , printfid(fid)

datafilei.close()                           # close the input file
conn.close()                                # Close the database
