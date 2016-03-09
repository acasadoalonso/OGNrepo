#!/usr/bin/python
#
# Python code to show access to OGN Beacons
#
# Version for gathering all the records for Spain 

from libfap import *
from ctypes import *
from datetime import datetime
import socket
import time
import settings
import string
import datetime
import ephem
import pytz
import sys
import os
import kglid                                # import the list on known gliders
from   parserfuncs import *                 # the ogn/ham parser functions 

def shutdown(sock, datafile, tmaxa, tmaxt, tmid):
                                        # shutdown before exit
    libfap.fap_cleanup()                # close lifap in order to avoid memory leaks
    sock.shutdown(0)                    # shutdown the connection
    sock.close()                        # close the connection file
    datafile.close()                    # close the data file 
    print 'Records read:',cin, ' Ids found: ',cout    # report number of records read and IDs discovered
    k=list(fid.keys())                  # list the IDs for debugging purposes
    k.sort()                            # sort the list
    for key in k:                       # report data
        gid='Noreg '                    # for unknown gliders
        if spanishsta(key) or frenchsta(key):
            if key in kglid.kglid:
                gid=kglid.kglid[key]    # report the station name
            else:
                gid="NOSTA"             # marked as no sta
        else:
            if key != None and key[3:9] in kglid.kglid: # if it is a known glider ???                                       
            	gid=kglid.kglid[key[3:9]]   # report the registration

        if fmaxs[key] > 0:
            print key, '=>', fsta[key], gid, fid[key], "Max alt:", fmaxa[key], "Max speed:", fmaxs[key] # report FLARM ID, station used, registration and record counter
        else:
            print key, '=>', fsta[key], gid, fid[key], "Max alt:", fmaxa[key]

                                        # report now the maximun altitude for the day
    if tmid[3:9] in kglid.kglid:        # if it is a known glider ???
        gid=kglid.kglid[tmid[3:9]]      # report the registration
    else:
        gid=tmid                        # use the ID instead       
    print "Maximun altitude for the day:", tmaxa, ' meters MSL at:', tmaxt, 'by:', gid, 'Station:', tmsta
    local_time = datetime.datetime.now()
    print "Time now:", local_time
    return

#########################################################################

fid=  {'NONE  ' : 0}                    # FLARM ID list
fsta= {'NONE  ' : 'NONE  '}             # STATION ID list
fmaxa={'NONE  ' : 0}                    # maximun altitude
fmaxs={'NONE  ' : 0}                    # maximun speed
cin   = 0                               # input record counter
cout  = 0                               # output file counter
i     = 0                               # loop counter
err   = 0
tmaxa = 0                               # maximun altitude for the day
tmaxt = 0                               # time at max altitude
tmid  = 'None     '                     # glider ID obtaining max altitude
tmsta = '         '                     # station capturing max altitude


#----------------------ogn_main.py start-----------------------
 
print "Start ognES SPAIN V1.9"
print "======================"

prtreq =  sys.argv[1:]
if prtreq and prtreq[0] == 'prt':
    prt = True
else:
    prt = False
    
# create socket & connect to server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((settings.APRS_SERVER_HOST, settings.APRS_SERVER_PORT))
print "Socket sock connected"
 
# logon to OGN APRS network    

login = 'user %s pass %s vers Py-SPAIN 1.9 %s'  % (settings.APRS_USER, settings.APRS_PASSCODE , settings.APRS_FILTER_DETAILS)
sock.send(login)    
 
# Make the connection to the server
sock_file = sock.makefile()
 
# Initialise libfap.py for parsing returned lines
print "libfap_init"
libfap.fap_init()
start_time = time.time()
local_time = datetime.datetime.now()
fl_date_time = local_time.strftime("%y%m%d")
OGN_DATA = "DATA" + fl_date_time+'.log'
print "OGN data file is: ", OGN_DATA
datafile = open (OGN_DATA, 'a')
keepalive_count = 1
keepalive_time = time.time()

#
#-----------------------------------------------------------------
# Initialise API for computing sunrise and sunset
#-----------------------------------------------------------------
#
location = ephem.Observer()
location.pressure = 0
location.horizon = '-0:34'	# Adjustments for angle to horizon

location.lat, location.lon = settings.FLOGGER_LATITUDE, settings.FLOGGER_LONGITUDE
date = datetime.datetime.now()
next_sunrise = location.next_rising(ephem.Sun(), date)
next_sunset = location.next_setting(ephem.Sun(), date)
print "Sunrise today is at: ", next_sunrise, " UTC "
print "Sunset  today is at: ", next_sunset,  " UTC "
print "Time now is: ", date

try:

    while True:
        #Loop for a long time with a count, illustrative only
        current_time = time.time()
        elapsed_time = current_time - keepalive_time
        if (current_time - keepalive_time) > 300:        # keepalives every 5 mins
            try:
                rtn = sock_file.write("#Python ognES App\n\n")
                # Make sure keepalive gets sent. If not flushed then buffered
                sock_file.flush()
                datafile.flush()
                run_time = time.time() - start_time
                if prt:
                    print "Send keepalive no: ", keepalive_count, " After elapsed_time: ", int((current_time - keepalive_time)), " After runtime: ", int(run_time), " secs"
                keepalive_time = current_time
                keepalive_count = keepalive_count + 1
            except Exception, e:
                print ('something\'s wrong with socket write. Exception type is %s' % (`e`))
     
        location.date = ephem.Date(datetime.datetime.utcnow())
        date = datetime.datetime.now()
        s = ephem.Sun()
        s.compute(location)
        twilight = -6 * ephem.degree	# Defn of Twilight is: Sun is 6, 12, 18 degrees below horizon (civil, nautical, astronomical)
        if s.alt < twilight:
            print "At Sunset now ... Time is:", date, " Next sunset is: ", next_sunset,  " UTC"
            shutdown(sock, datafile, tmaxa, tmaxt,tmid)
            print "At Sunset ... Exit"
            exit(0)
   
        if prt:
            print "In main loop. Count= ", i
            i += 1
        try:
            # Read packet string from socket
            packet_str = sock_file.readline()
            if len(packet_str) > 0 and packet_str[0] <> "#":
                datafile.write(packet_str)
                
        except socket.error:
            print "Socket error on readline"
            continue
        # A zero length line should not be return if keepalives are being sent
        # A zero length line will only be returned after ~30m if keepalives are not sent
        if len(packet_str) == 0:
            err +=1
            if err > 9:
                print "Read returns zero length string. Failure.  Orderly closeout"
                date = datetime.datetime.now()
                print "UTC now is: ", date
                break
            else:
                continue
     
        # Parse packet using libfap.py into fields to process, eg:
        packet = libfap.fap_parseaprs(packet_str, len(packet_str), 0)
        if  len(packet_str) > 0 and packet_str[0] <> "#":
            callsign=packet[0].src_callsign     # get the call sign FLARM ID
            id=callsign                         # id
            longitude = get_longitude(packet)
            latitude  = get_latitude(packet)
            altitude  = get_altitude(packet)
            speed     = get_speed(packet)
            course    = get_course(packet)
            path      = get_path(packet)
            type      = get_type(packet)
            dst_callsign = get_dst_callsign(packet)
            destination  = get_destination(packet)
            header       = get_header(packet)
            if path == 'qAS':                   # if std records
                station = packet_str[19:23]     # get the station identifier
                if station == 'LECI' or station == 'CREA':
                    station=packet_str[19:24]   # just a hack !!!
		if station == 'Madr':
                    station=packet_str[19:25]   # just a hack !!!
		    
            else:
                station=id                      # just the station itself 
            if prt:
                print 'Packet returned is: ', packet_str
                print 'Callsign is: ', callsign, 'DST CallSign:', dst_callsign, 'Dest: ', destination, 'header: ', header
                print 'Parsed data: POS: ', longitude, latitude, altitude,' Speed:',speed,' Course: ',course,' Path: ',path,' Type:', type
                print 
            if not id in fid :                  # if we did not see the FLARM ID
                fid[id]=0                       # init the counter
                fsta[id]=station                # init the station receiver
                fmaxa[id]=altitude              # maximun altitude
                fmaxs[id]=speed                 # maximun speed
                cout += 1                       # one more file to create
            cin += 1                            # increase total input records
            fid[id] +=1                         # increase the number of records read
            if altitude >= fmaxa[id]:
                fmaxa[id] = altitude
                if altitude > tmaxa and (not spanishsta(id) and not frenchsta(id)):
                        tmaxa = altitude        # maximum altitude for the day
                        tmaxt = date            # and time
                        tmid  = id              # who did it
                        tmsta = station         # station capturing the max altitude
            if speed >= fmaxs[id]:
                fmaxs[id] = speed
        

except KeyboardInterrupt:
    print "Keyboard input received, ignore"
    pass

# Close libfap.py to avoid memory leak
libfap.fap_cleanup()
 
# close socket -- must be closed to avoid buffer overflow

print 'Counters:', cin, cout                # report number of records read and files generated
shutdown(sock, datafile, tmaxa, tmaxt,tmid)
print "Exit now ..."
exit(1)



