# Pytheas example 2 - using GPS
# Leif Oppermann, 30.09.2009

'''
This example shows how to get GPS readings via the abstract GPSInterface (file modules/lxo_gps.py).
It uses the variables introduced in example 1 to instantiate different implementations of the GPSInterface 
depending on the current system environment. This code works on actual phones (via GPS_S603RD), 
as well as on the desktop or in the emulator (via class GPS_FAKE).
'''

#---again, use the template to bootstrap

#---take the following code to automatically distinguish between real phone, phone emulator or desktop
#   and set Python import paths accordingly. also sets "PROGDIR:" assign to where the code is running from
#   (see modules/assigns.py for more details)
#BEGIN
try:
    # for platforms that have a notion of current directory
    execfile("lxo_bootstrap.py")
except:
    # for series 60, which doesn't have a current directory
    try:
        execfile("e:\\python\\lxo_bootstrap.py")
    except:
        try:
            execfile("c:\\python\\lxo_bootstrap.py")
        except:
            g_isPhone=False
            print "***Error: lxo_bootstrap.py not found"
#END

#--- import gps module
print "Pytheas example 2 - using GPS for five seconds"
import lxo_gps

#--- decide whether to use actual GPS code, or not

if g_isRealPhone:
    # use 3rd edition GPS code
    gps = lxo_gps.GPS_S603RD()
    print "Using GPS_S603RD class on actual hardware"
else:
    # use fake GPS because not running on phone
    gps = lxo_gps.GPS_FAKE()
    print "Using GPS_FAKE class on other hardware"
    
#--- callback that will be called by the GPSInterface
def cbGPS(data):
    d={}
    d["TYPE"] = "GPS"
    d["TIME"] = "%d000" % (int(time.time()))
    t = time.gmtime(data["satellites"]["time"])
    d["DATE"] = "%d%02d%02d" %(t[2],t[1],t[0]-2000)         # e.g. 190408
    d["TIMEOFFIX"]= "%d%02d%.3f" %(t[3],t[4],t[5])            # e.g. 101653.000000
    d["LAT"] = data["position"]["latitude"]
    d["LON"] = data["position"]["longitude"]
    d["SOG"] = data["course"]["speed"]
    d["COG"] = data["course"]["heading"]
    #|RSSI=-88|WEP=true|INFR=true)
    print d

#--- run for 5 seconds, then quit
gps.registerCallback(cbGPS)
gps.start()
# call GPSInterface update method regularly
for i in range(5):
    wait(1)	# also from lxo_bootstrap module
    gps.update()
gps.stop()
print "End of example 2"