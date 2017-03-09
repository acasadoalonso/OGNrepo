#-------------------------------------
# OGN-SAR Spain interface --- Settings
#-------------------------------------
#
#-------------------------------------
# Setting values
#-------------------------------------
#
import socket
from configparser import ConfigParser
configfile="/etc/local/SARconfig.ini"
hostname=socket.gethostname()
print "Hostname:", hostname
cfg=ConfigParser()                                                              # get the configuration parameters
cfg.read(configfile)                                                            # reading it for the configuration file
print "Config.ini sections:", cfg.sections()                                    # report the different sections

APRS_SERVER_HOST        = cfg.get    ('APRS', 'APRS_SERVER_HOST').strip("'")
APRS_SERVER_PORT        = int(cfg.get('APRS', 'APRS_SERVER_PORT'))
APRS_USER               = cfg.get    ('APRS', 'APRS_USER').strip("'")
APRS_PASSCODE           = int(cfg.get('APRS', 'APRS_PASSCODE'))                 # See http://www.george-smart.co.uk/wiki/APRS_Callpass
APRS_FILTER_DETAILS     = cfg.get    ('APRS', 'APRS_FILTER_DETAILS').strip("'")
APRS_FILTER_DETAILS     = APRS_FILTER_DETAILS + '\n '

FLOGGER_LATITUDE        = cfg.get('location', 'location_latitude').strip("'")
FLOGGER_LONGITUDE       = cfg.get('location', 'location_longitud').strip("'")
location_latitude       = cfg.get('location', 'location_latitude').strip("'")
location_longitude      = cfg.get('location', 'location_longitud').strip("'")

try:
	location_name   = cfg.get('location', 'location_name').strip("'").strip('"')
except:
	location_name   = ' '


DBpath                  = cfg.get('server', 'DBpath').strip("'")
MySQLtext               = cfg.get('server', 'MySQL').strip("'")
DBhost                  = cfg.get('server', 'DBhost').strip("'")
DBuser                  = cfg.get('server', 'DBuser').strip("'")
DBpasswd                = cfg.get('server', 'DBpasswd').strip("'")
DBname                  = cfg.get('server', 'DBname').strip("'")
if (MySQLtext == 'True'):
        MySQL = True
else:
        MySQL = False
# --------------------------------------#
assert len(APRS_USER) > 3 and len(str(APRS_PASSCODE)) > 0, 'Please set APRS_USER and APRS_PASSCODE in settings.py.'
                                                                                # report the configuration paramenters
print "Config server values:",                  "MySQL=", MySQL, DBhost, DBuser, DBpasswd, DBname, DBpath
print "Config APRS values:",                    APRS_SERVER_HOST, APRS_SERVER_PORT, APRS_USER, APRS_PASSCODE, APRS_FILTER_DETAILS
print "Config location :",     			location_name, FLOGGER_LATITUDE, FLOGGER_LONGITUDE
# --------------------------------------#
APP="SAR"
