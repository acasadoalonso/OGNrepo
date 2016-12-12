#!/usr/bin/python
#
# This program reads the the records received from the OGN APRS server for SPAIN
# and generates IGC files for each flight
# It runs 30 minutes after the sunset in Lillo(TO) - LELT
#
# Author: Angel Casado - May 2015
#
import datetime 
import time
import sys
import socket

sys.path.insert(0,'/nfs/OGN/src')
datapath    ='/nfs/OGN/DIRdata/'

import os
import kglid                                # import the list on known gliders
from   libfap import *                      # the packet parsing function 
from   parserfuncs import *                 # the ogn/ham parser functions 
from   geopy.distance import vincenty       # use the Vincenty algorithm
from   geopy.geocoders import GeoNames      # use the Nominatim as the geolocator
from   geopy.geocoders import Nominatim	    # we need it for resolving the geppositions

#
# ---------- main code ---------------
#
 
fid=  {'NONE  ' : 0}                        # FLARM ID list
fsta= {'NONE  ' : 'NONE  '}                 # STATION ID list
ffd=  {'NONE  ' : None}                     # file descriptor list
ftkot={'NONE  ' : 0}                        # take off time
flndt={'NONE  ' : 0}                        # take off time
fsloc={'NONE  ' : (0.0, 0.0)}               # station location
fsmax={'NONE  ' : 0.0}                      # maximun coverage
ftkok={datetime.datetime.utcnow(): 'NONE  '}  # Take off time 
tmaxa = 0                                   # maximun altitude for the day
tmaxt = 0                                   # time at max altitude
tmid  = 0                                   # glider ID obtaining max altitude
tmsta = ''
tmp=''
mlong=0.0                                   # longitude on the max altiutde point
mlati=0.0                                   # latitude of idem
blacklist = ['FLR5B8041']		    # blacklist
www=False
prt=True

geolocator = Nominatim(timeout=5)           # create the instance

if 'SERVER_SIGNATURE' in os.environ:        # check if www
	
	www=True
	prt=False
	tmp='tmp/'

if prt:
    print "Start process OGN records V1.10"
    print "==============================="
dtereq =  sys.argv[1:]
if dtereq and dtereq[0] == 'date':
    dter = True                             # request the date
else:
    dter = False                            # do not request the date
if dtereq and dtereq[0] == 'name':
    name = True                             # request the date
else:
    name = False                            # do not request the date
cin  = 0                                    # input record counter
cout = 0                                    # output file counter
date=datetime.datetime.now()                         # get the date
dte=date.strftime("%y%m%d")                 # today's date
fname='DATA'+dte+'.log'                     # file name from logging

hostname=socket.gethostname()

#fname='DATA170515.log'                     # example of file name 

if not dter:                                # check if we need to request date
    
    fname='DATA'+dte+'.log'                 # build the file name with today's date
else:
    dte=raw_input('Enter date:')            # otherwise ask for the date
    if dte == '':                           # if no input 
        dte=date.strftime("%y%m%d")         # use the default
    fname='DATA'+dte+'.log'                 # build the file name with the date entered
if name:
    fn=sys.argv[2:]                         # take the name of the second arg
    fname=str(fn)[2:20]
if prt:    
    print 'File name: ', fname, 'Process date/time:', date.strftime(" %y-%m-%d %H:%M:%S")     # display file name and time

geolocator=GeoNames(country_bias='Spain', username='acasado' )
datafilei = open(datapath+fname, 'r')       # open the file with the logged data

 
if prt: print "libfap_init"
libfap.fap_init()

while True:                                 # until end of file 
    data=datafilei.readline()               # read one line
    if not data:                            # end of file ???
                                            # report the findings and close the files
        if prt: print 'Input records: ',cin, 'Ouput files:',cout # report number of records read and files generated
        k=list(fid.keys())                  # list the IDs for debugging purposes
        k.sort()                            # sort the list
        
        for key in k:                       # report data by flarm id
            if key[3:9] in kglid.kglid:          # if it is a known glider ???
                r=kglid.kglid[key[3:9]]          # get the registration
            else:
                r='NOREG '                  # no registration
            ttime=0                         # flying time 
            if ftkot[key] != 0  and flndt[key] != 0: 
                ttime = flndt[key] - ftkot[key]
            else:
                ttime = ' '
            if flndt[key]  != 0 :
                ltime=flndt[key]
            else:
                ltime = ' '
            if prt: print key, '=>', 'Base:', fsta[key], 'Reg:', r, 'Take off:', ftkot[key], 'Landing:', ltime, ttime, 'Nrecs:', fid[key]
                                            # report FLARM ID, station used,  record counter, registration, take off time and landing time
            if  ffd[key] != None:
                ffd[key].close()            # and close all the file
            
 
        k=list(ftkok.keys())                # list the takes off times
        k.sort()                            # sort the list
        for to in k:                        # report by take off time
                key= ftkok[to]
                if key[3:9] in kglid.kglid:      # if it is a known glider ???
                    r=kglid.kglid[key[3:9]]      # get the registration
                else:
                    r='Noreg '              # no registration
                ttime=0                     # flying time 
                if ftkot[key] != 0  and flndt[key] != 0:  # if both
                    ttime = flndt[key] - ftkot[key]
                else:
                    ttime= ' '
                if flndt[key]  != 0 :
                    ltime=flndt[key]
                else:
                    ltime = ' '
                if prt: print to, ':::>', key, fsta[key], r, ftkot[key], ltime, ttime
                
        k=list(fsloc.keys())                # list the receiving stations
        k.sort()                            # sort the list
        for key in k:                       # report data distances
            if fsmax[key] > 0:              # only if we have measured distances
                if prt: print key, '==>', fsmax[key], ' Kms. '      # distance
                
        break                               # work done, finish the reporting now ... 

    if len(data) < 40:                      # that is the case of end of file when the ognES.py process is still running
        continue                            # nothing else to do
    

    ix=data.find('>')
    cc= data[0:ix]
    cc=cc.upper()
    data=cc+data[ix:]
    packet       = libfap.fap_parseaprs(data, len(data), 0) # parser the information
                                            # get the information once parsed 
    longitude    = get_longitude(packet)
    latitude     = get_latitude(packet)
    altitude     = get_altitude(packet)
    speed        = get_speed(packet)
    course       = get_course(packet)
    path         = get_path(packet)
    ptype        = get_type(packet)
    dst_callsign = get_dst_callsign(packet)
    destination  = get_destination(packet)
    header       = get_header(packet)
    otime        = get_otime(packet)
    
    callsign=packet[0].src_callsign         # get the call sign FLARM ID
    
    if (data.find('TCPIP*') != -1):         # ignore the APRS lines
        id=callsign                         # stasion ID
        if not id in fsloc :
            fsloc[id]=(latitude, longitude) # save the loction of the station
            fsmax[id]=0.0                   # initial coverage zero
	    #print "ID:", id, data[0:10], latitude, longitude
	if id == None:
	    id= data[0:data.find('>')]
	    print "ID:", id, data[0:10]
            fsloc[id]=(latitude, longitude) # save the loction of the station
            fsmax[id]=0.0                   # initial coverage zero
        continue                            # go for the next record
    if cc in blacklist:
	continue
    id=data[0:9]                            # exclude the FLR part
    idname=data[3:9]                        # exclude the FLR part
    scolon=data.find(':')		    # find the colon
    station=data[data.find('qAS')+4:scolon]
    station=station.upper()		    # translate to uppercase
    if hostname == "CHILEOGN" or spanishsta(station) or frenchsta(station):  # only Chilean or Spanish or frenchstations
        if not id in fid :                  # if we did not see the FLARM ID
            fid  [id]=0                     # init the counter
            fsta [id]=station               # init the station receiver
            ftkot[id]=0                     # take off time/ initial seeing  - null for the time being
            flndt[id]=0                     # landing  time - null for the time being
            cout += 1                       # one more file to create
                                            # prepare the IGC header
            if id[3:9] in kglid.kglid:      # if it is a known glider ???
                fd = open(datapath+tmp+'FD'+dte+'.'+station+'.'+kglid.kglid[id[3:9]].strip()+'.'+idname+'.IGC', 'w')
            else:
                fd = open(datapath+tmp+'FD'+dte+'.'+station+'.'+idname+'.IGC', 'w')
            fd.write('AGNE001GLIDER\n')     # write the IGC header
            fd.write('HFDTE'+dte+'\n')      # write the date on the header
            if id[3:9] in kglid.kglid:
                fd.write('HFGIDGLIDERID: '+kglid.kglid[id[3:9]]+'\n')    # write the registration ID
            else:
                fd.write('HFGIDGLIDERID: '+id+'\n')                 # if we do not know it write the FLARM ID
            ffd[id] = fd                    # save the file descriptor
        fid[id] +=1                         # increase the number of records read
        p1=data.find(':/')+2                # scan for the body of the APRS message
        hora=data[p1:p1+6]                  # get the GPS time in UTC
        long=data[p1+7:p1+11]+data[p1+12:p1+14]+'0'+data[p1+14]         # get the longitude
        lati=data[p1+16:p1+21]+data[p1+22:p1+24]+'0'+data[p1+24]        # get the latitude
        p2=data.find('/A=')+3               # scan for the altitude on the body of the message
        altif=data[p2+1:p2+6]               # get the altitude in feet
        altim=altitude                      # convert the altitude in meters
        if altim > 15000 or altim < 0:
            altim=0
        alti='%05d' % altim                 # convert it to an string
        ffd[id].write('B'+hora+long+lati+'A00000'+alti+'\n') # format the IGC B record
        ffd[id].write('LGNE '+data)         # include the original APRS record for documentation
 
        if speed > 50 and ftkot[id] == 0:   # if we do not have the take off time ??
                ftkot[id] = otime           # store the take off time
                ftkok[otime]=id             # list by take off time 
        if speed < 20 and speed > 5 and ftkot[id] != 0:   # if we do not have the take off time ??
                flndt[id] = otime           # store the landing time
        if station in fsloc:                # if we have the station yet
                distance=vincenty((latitude, longitude), fsloc[station]).km    # distance to the station
                if distance > 250.0:
                    print ">>>Distcheck: ", distance, data, cin
                elif distance > fsmax[station]: # if higher distance
                    fsmax[station]=distance     # save the new distance
        if altim > tmaxa:
                tmaxa = altim               # maximum altitude for the day
                tmaxt = hora                # and time
                tmid  = id                  # who did it
                tmsta = station             # station capturing the max altitude
                mlong = longitude           # longitude of the max alt point
                mlati = latitude            # latitude
        cin +=1                             # one more record read
     
    #else:
	#print "Unkown station: ", station   

# -----------------  final process ----------------------
datafilei.close()                           # close the input file
datef=datetime.datetime.now()               # get the time & date
                                            # Close libfap.py to avoid memory leak
libfap.fap_cleanup()
if tmid[3:9] in kglid.kglid:                     # if it is a known glider ???
    gid=kglid.kglid[tmid[3:9]]                   # report the registration
else:
    gid=tmid                                # just report the flarmid 
#geolocator = Nominatim(timeout=5)	    # define the geolocator, we need 5 second timeout 
#loc = geolocator.reverse([mlati,mlong])     # locate the point of maximun altitue for the day.
   
#addr=loc.address                            # the location name                           
#addr=addr.encode('utf8')                    # convert it to UTF-8
#addr=str(addr)                              # convert to str just in case, in order to avoid problems when is redirected to a file. 
addr=' '

if prt: print "Maximun altitude for the day:", tmaxa, ' meters MSL at:', tmaxt, 'Z by:', gid, 'Station:', tmsta, "At: ", mlati, mlong, addr
if prt: print 'Bye ... Time now and Time used:', datef, datef-date      # report the processing time

    
