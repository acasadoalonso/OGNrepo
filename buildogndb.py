#!/usr/bin/python3
#
# This program reads the the records received from the OGN APRS server for SPAIN
# and generates the OGN database
# It runs 30 minutes after the sunset in Lillo(TO) - LELT
#
# Author: Angel Casado - August 2015
#
import time
import sys
import os
sys.path.insert(0, '/nfs/OGN/src/funcs')
import kglid                                # import the list on known gliders
import datetime
import sqlite3                              # the SQL data base routines
import MySQLdb                              # the SQL data base routines
from parserfuncs import *                   # the ogn/ham parser functions
from geopy.distance import vincenty         # use the Vincenty algorithm
from geopy.geocoders import GeoNames        # use the Nominatim as the geolocator
from datetime import datetime

#
# ---------- main code ---------------
#

pgmver = 'V2.0'
fid   = {'NONE  ': 0}                       # FLARM ID list
fsta  = {'NONE  ': 'NONE  '}                # STATION ID list
ftkot = {'NONE  ': 0}                       # take off time
flndt = {'NONE  ': 0}                       # take off time
fsloc = {'NONE  ': (0.0, 0.0)}              # station location
fslla = {'NONE  ': 0.0}			    # station latitude
fsllo = {'NONE  ': 0.0}			    # station longitude
fslal = {'NONE  ': 0.0}			    # station altitude
fsmax = {'NONE  ': 0.0}                     # maximun coverage
fsalt = {'NONE  ': 0}                       # maximun altitude
ftkok = {datetime.utcnow(): 'NONE  '}  	    # Take off time
tmaxa = 0                                   # maximun altitude for the day
tmaxt = 0                                   # time at max altitude
tmid = 0                                    # glider ID obtaining max altitude
relaycnt = 0				    # counter of relay packages
relaycntr = 0				    # counter of std relay packages
relayglider = {}			    # list of relay glider and tracker
tmsta = ''
print("Start build OGN database "+pgmver)
print("==============================")
prt = False
import config                               # import the main settings
DBname = config.DBname
DBhost = config.DBhost
DBuser = config.DBuser
DBpasswd = config.DBpasswd
blacklist = ['FLR5B0041']                   # blacklist


MySQL = False				    # False unless the MySQL option is requested
dtereq = sys.argv[1:]
if dtereq and dtereq[0] == 'date':
    dter = True                             # request the date
else:
    dter = False                            # do not request the date
if dtereq and dtereq[0] == 'name':
    nmer = True                             # request the name
    # prt=True
    prt = False
elif dtereq and dtereq[0] == 'MYSQL':
    nmer = True                             # request the name
    prt = False
    MySQL = True
    print("MySQL DB :", DBname, "User:", DBuser, "@", DBhost)
else:
    nmer = False                            # do not request the name

cin = 0                                     # input record counter
cout = 0                                    # output record counter
cfile = 0                                   # output file counter
date = datetime.now()                	    # get the date
dte = date.strftime("%y%m%d")               # today's date
fname = 'DATA'+dte+'.log'                   # file name from logging

# fname='DATA150722.log'                    # example of file name

if not dter and not nmer:                   # check if we need to request date
    print('User: ', os.environ['USER'])     # tell that
    fname = 'DATA'+dte+'.log'               # build the file name with today's date
elif nmer:
    fn = sys.argv[2:]                       # take the name of the second arg
    fname = str(fn)[2:16]
                                            # take the date from the file name
    dte = str(fn)[6:12]
else:
    dte = input('Enter date:')              # otherwise ask for the date
    if dte == '':                           # if no input
        dte = date.strftime("%y%m%d")       # use the default
                                            # build the file name with the date entered
    fname = 'DATA'+dte+'.log'

                                            # display file name and time
print('File name:', fname, 'Process date/time:', date.strftime(
    " %y-%m-%d %H:%M:%S"))

geolocator = GeoNames(country_bias='Spain', username='acasado')
                                            # open the file with the logged data
datafilei = open(fname, 'r')
if (MySQL):
                                            # connect with the database
    conn = MySQLdb.connect(host=DBhost, user=DBuser,
                           passwd=DBpasswd, db=DBname)
else:
    conn = sqlite3.connect(r'OGN.db')       # connect with the database
curs = conn.cursor()                        # set the cursor

nrec = 0
paths=[]

while True:                                 # until end of file
    data = datafilei.readline()             # read one line
    if not data:                            # end of file ???
                                            # report the findings and close the files
        # report number of records read and files generated
        print('===> Input records: ', dte, cin, cout, 'Ouput files:', cfile, len(fid))
        # list the IDs for debugging purposes
        k = list(fid.keys())
        k.sort()                            # sort the list

        for key in k:                       # report data
            if key[3:9] in kglid.kglid:     # if it is a known glider ???
                r = kglid.kglid[key[3:9]]   # get the registration
            else:
                r = 'NOREG '                # no registration
            ttime = 0                       # flying time
            if ftkot[key] != 0 and flndt[key] != 0:
                ttime = flndt[key] - ftkot[key]
            else:
                ttime = ' '
            if flndt[key] != 0:
                ltime = flndt[key]
            else:
                ltime = ' '
            if prt:
                print(key, '=>', 'Base:', fsta[key], 'Reg:', r, 'Take off:', ftkot[
                    key], 'Landing:', ltime, ttime, 'Nrecs:', fid[key])
                # report FLARM ID, station used,  record counter, registration, take off time and landing timecd ../..

        k = list(ftkok.keys())              # list the takes off times
        k.sort()                            # sort the list
        for to in k:                        # report by take off time
            key = ftkok[to]
            if key[3:9] in kglid.kglid:     # if it is a known glider ???
                r = kglid.kglid[key[3:9]]   # get the registration
            else:
                r = 'Noreg '                # no registration
            ttime = 0                       # flying time
            if ftkot[key] != 0 and flndt[key] != 0:  # if both
                ttime = flndt[key] - ftkot[key]
            else:
                ttime = ' '
            if flndt[key] != 0:
                ltime = flndt[key]
            else:
                ltime = ' '
            if prt:
                print(to, ':::>', key, fsta[key], r, ftkot[key], ltime, ttime)

        k = list(fsloc.keys())              # list the receiving stations
        k.sort()                            # sort the list
        for key in k:                       # report data distances
            if fsmax[key] > 0:              # only if we have measured distances
                if prt:
                    print(key, '==>', fsmax[key], ' Kms. ')      # distance
                if (MySQL):
                    addcmd = "insert into STATIONS values ('" + key + "','" + dte + "'," + str(fsmax[key]) + "," + str(fsalt[key]) + ")"
                    curs.execute(addcmd)
                else:
                    addcmd = "insert into STATIONS values (?,?,?,?)"
                    curs.execute(addcmd, (key, dte, fsmax[key], fsalt[key]))
        #
            if (MySQL):
                selcmd = "select idrec from RECEIVERS where idrec='" + \
                    key + "'"               # SQL command to execute: SELECT
                curs.execute(selcmd)
            else:
                                            # SQL command to execute: SELECT
                selcmd = "select idrec from RECEIVERS where idrec=?"
                curs.execute(selcmd, (key,))
            if curs.fetchone() == None:
                gid = 'Noreg '              # for unknown receiver
                if config.hostname == "CHILEOGN" or config.hostname == "OGNCHILE" or spanishsta(key) or frenchsta(key):
                    if key in kglid.kglid:
                        gid = kglid.kglid[key]  # report the station name
                    else:
                        gid = "NOSTA"       # marked as no sta
                lati = fslla[key]           # latitude
                longi = fsllo[key]          # longitude
                alti = fslal[key]           # altitude

                if key != "None" and key != None:
                    if prt:
                        print(key, 'Adding ==>', gid, lati, longi, alti)
                    if (MySQL):
                        if len(gid) > 30:
                            gid = gid[0:30]
                        inscmd = "insert into RECEIVERS values ('" + key + "','" + gid + "'," + str(lati) + "," + str(longi) + "," + str(alti) + ")"
                        try:
                            curs.execute(inscmd)
                        except MySQLdb.Error as e:
                            try:
                                print(">>>MySQL Error [%d]: %s" % (
                                    e.args[0], e.args[1]))
                            except IndexError:
                                print(">>>MySQL Error: %s" % str(e))
                            print(">>>MySQL error:", inscmd)
                    else:
                        inscmd = "insert into RECEIVERS values (?, ?, ?, ?, ?)"
                        curs.execute(inscmd, (key, gid, lati, longi, alti))
        #
        conn.commit()
        # commit the changes
        break                               	# work done
# ---------------------------------------------------------------------------------------
    # that is the case of end of file when the ognES.py process is still
    if len(data) < 40:
        continue                            # nothing else to do
#   ready to handle a record
    nrec += 1
    cin += 1
    ix = data.find('>')			    # translate to uppercase the ID
    cc = data[0:ix]
    cc = cc.upper()
    data = cc+data[ix:]
    msg = {}
    if len(data) > 0 and data[0] != "#":
        msg = parseraprs(data, msg)         # parser the data
        if msg == -1:			    # parser error
            print("Parser error:", data)
            continue
        ident = msg['id']          	    # id
        type = msg['aprstype']		    # message type
        longitude = msg['longitude']
        latitude = msg['latitude']
        if latitude == -1 or longitude == -1 or type == 8:  # check for the ogn tracker status report
            continue
        altitude = msg['altitude']
        path = msg['path']
        if path not in paths:
            paths.append(path)
        otime = msg['otime']
        source = msg['source']              # source of the data OGN/SPOT/SPIDER/...
        station = msg['station']
        if len(source) > 4:
            source = source[0:3]
        # if std records
        if path == 'qAS' or path == 'RELAY*' or path[0:3] == "OGN":
            station = msg['station']	    # get the station name
            if path == "RELAY*":
                relaycntr += 1
            if path[0:3] == "OGN":	    # if it is a OGN tracker relay msg
                if not id in relayglider:
                    rr = {} 		    # temp
                    #print "otime", otime.strftime("%y%m%d%H%M%S")
                    rr[path[0:9]] = otime.strftime("%H%M%S")
                    relayglider[ident] = rr    # add the id to the table of relays.
                relaycnt += 1		    # increase the counter

        if path == 'TCPIP*' or path == 'receiver' or path == 'aprs_receiver':
            if not ident in fsloc:		    # if not detected yet
                # save the loction of the station
                fsloc[ident] = (latitude, longitude)
                fslla[ident] = latitude
                fsllo[ident] = longitude
                fslal[ident] = altitude
                fsmax[ident] = 0.0          # initial coverage zero
                fsalt[ident] = 0            # initial coverage zero
            continue                        # go for the next record
        if cc in blacklist:
            continue
        ident = data[0:9]                      # the flarm ID/ICA/OGN
        idname = data[0:9]                  # exclude the FLR part
        # only Spanish/Chilean stations
        if config.hostname == "CHILEOGN" or config.hostname == "OGNCHILE" or spanishsta(station):
            if not ident in fid:            # if we did not see the FLARM ID
                fid[ident] = 0              # init the counter
                fsta[ident] = station       # init the station receiver
                # take off time/ initial seeing  - null for the time being
                ftkot[ident] = 0
                # landing  time - null for the time being
                flndt[ident] = 0
                cfile += 1                  # one more file to create

                                            # increase the number of records read
            fid[ident] += 1
            course = msg['course']
            speed = msg['speed']
            uniqueid = msg['uniqueid']
            if len(uniqueid) > 10:
                uniqueid = uniqueid[0:10]   # in this database only 10 chars
            extpos = msg['extpos']
            roclimb = msg['roclimb']
            rot = msg['rot']
            sensitivity = msg['sensitivity']
            gps = msg['gps']
            hora = msg['time']
            dist = -1			    # if we can not get the distance
            altim = altitude                # the altitude in meters

                                            # if we do not have the take off time ??
            if speed > 50 and ftkot[ident] == 0:
                ftkot[ident] = otime        # store the take off time
                ftkok[otime] = ident        # list by take off time
                                            # if we do not have the take off time ??
            if speed < 20 and speed > 5 and ftkot[ident] != 0:
                flndt[ident] = otime           # store the landing time
            if station in fsloc and longitude != -1:  # if we have the station yet
                                            # distance to the station
                distance = vincenty((latitude, longitude), fsloc[station]).km
                dist = distance
                if distance > 250.0:
                    print(">>Distcheck: ", distance, "Nrec:", nrec,  longitude, latitude, data)
                elif distance > fsmax[station]:  # if higher distance
                    fsmax[station] = distance  # save the new distance
                if altim > fsalt[station]:  	# if higher altitude
                    fsalt[station] = altim  # save the new altitude
            if source != 'OGN':
                distance = vincenty((latitude, longitude), (config.location_latitude,
                                                            config.location_longitude)).km    # distance to the station
                dist = distance

            if altim > tmaxa:
                tmaxa = altim               # maximum altitude for the day
                tmaxt = hora                # and time
                tmid = ident                # who did it
                tmsta = station             # station capturing the max altitude
            if uniqueid[0:2] != "id":	    # check for a valid uniqueid
                continue
                                            # write the DB record eithher on MySQL or SQLITE3
            if (MySQL):
                addcmd = "insert into OGNDATA values ('" + ident + "','" + dte + "','" + hora + "','" + station + "'," + str(latitude) + "," + \
                    str(longitude) + "," + str(altim) + "," + str(speed) + "," + \
                    str(course) + "," + str(roclimb) + "," + \
                    str(rot) + "," + str(sensitivity)
                addcmd = addcmd+",'" + gps + "','" + uniqueid + \
                    "'," + str(dist) + ",'" + extpos + "')"
                try:
                    curs.execute(addcmd)
                except MySQLdb.Error as e:
                    try:
                        print(">>>MySQL Error [%d]: %s" % ( e.args[0], e.args[1]))
                    except IndexError:
                        print(">>>MySQL Error: %s" % str(e))
                    print(">>>MySQL error:", nrec, cin, addcmd)
            else:                           # sqlite3
                addcmd = "insert into OGNDATA values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
                curs.execute(addcmd, (idname, dte, hora, station, latitude, longitude, altim,
                                      speed, course, roclimb, rot, sensitivity, gps, uniqueid, dist, extpos))
            cout += 1                        # one more record writen

# -----------------  final process ----------------------

datafilei.close()                           # close the input file
datef = datetime.now()                      # get the time & date
conn.commit()
# commit the DB
conn.close()                                # Close libfap.py to avoid memory leak

if tmid != 0 and tmid[3:9] in kglid.kglid:  # if it is a known glider ???
    gid = kglid.kglid[tmid[3:9]]            # report the registration
else:
    gid = tmid
print("Maximun altitude for the day:", tmaxa, ' meters MSL at:', tmaxt, 'Z by:', gid, 'Station:', tmsta)
print("Number of relay packages:", relaycntr, relaycnt)
if relaycnt > 0:
    print("List of relays:", relayglider)
print (paths)
print('Bye ...: Stored', cout, " records of ", nrec, ' read. Time and Time used:', datef, datef - \
    date)                                   # report the processing time
