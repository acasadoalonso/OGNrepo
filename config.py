#!/usr/bin/python3
#-------------------------------------
# OGN-SAR Spain interface --- Settings
#-------------------------------------
#
#-------------------------------------
# Setting values
#-------------------------------------
#
APP = "SAR"
import socket
import os
from configparser import ConfigParser
configdir = os.getenv('CONFIGDIR')
if configdir == None:
    configdir = '/etc/local/'
configfile = configdir+'SARconfig.ini'
hostname = socket.gethostname()
processid = str(os.getpid())
# get the configuration parameters
cfg = ConfigParser()
# reading it for the configuration file
cfg.read(configfile)

APRS_SERVER_HOST    = cfg.get('APRS', 'APRS_SERVER_HOST').strip("'")
APRS_SERVER_PORT    = int(cfg.get('APRS', 'APRS_SERVER_PORT'))
APRS_USER           = cfg.get('APRS', 'APRS_USER').strip("'")
# See http://www.george-smart.co.uk/wiki/APRS_Callpass
APRS_PASSCODE       = int(cfg.get('APRS', 'APRS_PASSCODE'))
APRS_FILTER_DETAILS = cfg.get('APRS', 'APRS_FILTER_DETAILS').strip("'")
APRS_FILTER_DETAILS = APRS_FILTER_DETAILS + '\n '

FLOGGER_LATITUDE    = cfg.get('location', 'location_latitude').strip("'")
FLOGGER_LONGITUDE   = cfg.get('location', 'location_longitud').strip("'")
location_latitude   = cfg.get('location', 'location_latitude').strip("'")
location_longitude  = cfg.get('location', 'location_longitud').strip("'")

try:
    location_name   = cfg.get('location', 'location_name').strip("'").strip('"')
except:
    location_name   = ' '


DBpath              = cfg.get('server', 'DBpath').strip("'")
MySQLtext           = cfg.get('server', 'MySQL').strip("'")
DBhost              = cfg.get('server', 'DBhost').strip("'")
DBuser              = cfg.get('server', 'DBuser').strip("'")
DBpasswd            = cfg.get('server', 'DBpasswd').strip("'")
DBname              = cfg.get('server', 'DBname').strip("'")
try:
	SQLite3     = cfg.get('server', 'SQLite3').strip("'")
except:
	SQLite3     = 'SAROGN'

if (MySQLtext == 'True'):
    MySQL = True
else:
    MySQL = False
try:
    PIDfile         = cfg.get('server', 'pid').strip("'").strip('"')
except:
    PIDfile         = '/tmp/'+APP+'.pid'

# --------------------------------------#
assert len(APRS_USER) > 3 and len(str(APRS_PASSCODE)) > 0, 'Please set APRS_USER and APRS_PASSCODE in SARconfig.ini .'
if 'USER' in os.environ:
    user = os.environ['USER']
    # report the configuration paramenters
    print("Hostname:", hostname, " Process ID:", processid, "User:", user)
    # report the different sections
    print("Config server values:",              "MySQL=", MySQL, DBhost, DBuser, DBname, DBpath, SQLite3)
    print("Config APRS values:",                APRS_SERVER_HOST, APRS_SERVER_PORT, APRS_USER, APRS_PASSCODE, APRS_FILTER_DETAILS)
    print("Config location values:",   		location_name, FLOGGER_LATITUDE, FLOGGER_LONGITUDE)
# --------------------------------------#
