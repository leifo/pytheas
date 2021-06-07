# Placelab Version 2 logger class
# lxo, 18.04.2008
# 06.05.2008
# - bumped version number to 1.1 (first version that logs TYPE=NOGSM)

# general Python imports
import time

# S60 specific imports
try:
    import sysinfo
    import e32db, e32
except:
    pass

class pv2logger_s60:
    '''
    s60 specific version
    '''
    def __init__(self,filename=None):
        '''
        Start a new log-file with S60 specific properties:
        - filename with IMEI and creation time located on Memory card (E-Drive)
        - S60 specific meta information
        '''
        self.VERSION = "1.1"
        #
        unixtime = (int) (time.time())
        imei = sysinfo.imei()
        # construct filename unless explicitly requested otherwise (usually not recommended, E-Drive is preferred)
        if filename==None:
            filename = u"e:/%s-%s.pv2" % (imei, unixtime)
            #filename = assign("logs:%s-%s.pv2" % (imei, unixtime))
            #print filename
        # generate meta information for the log-file
        meta = {}
        meta["CREATOR"] = "pv2logger_s60 v%s"% (self.VERSION)
        utime = (int) (time.time())
        stime = str(e32db.format_time(utime))
        meta["CREATED LOCALTIME"] = str(stime)
        meta["CREATED UNIXTIME"] = str(utime)
        meta["PHONE IMEI"] = str(imei)
        meta["PYS60 PY VERSION"] = str(e32.pys60_version)
        meta["PYS60 OS VERSION"] = str(sysinfo.os_version())
        meta["PYS60 SW VERSION"] = str(sysinfo.sw_version())
        #meta[""] = ""
        # instantiate file logger
        self.pv2 = pv2filelogger(filename, meta=meta)
    def __del__(self):
        del(self.pv2)
    def write(self, data):
        self.pv2.write(data)
    def flush(self):
        self.pv2.flush()

class genericlogger:
    '''
    generic logger (does not rely on S60)
    '''
    def __init__(self,filename):
        '''
        Start a new log-file:
        '''
        self.VERSION = "1.0"
        #
        unixtime = (int) (time.time())
        # generate meta information for the log-file
        meta = {}
        meta["CREATOR"] = "genericlogger v%s"% (self.VERSION)
        utime = (int) (time.time())
        stime = str(e32db.format_time(utime))
        meta["CREATED LOCALTIME"] = str(stime)
        meta["CREATED UNIXTIME"] = str(utime)
        #meta[""] = ""
        # instantiate file logger
        self.pv2 = pv2filelogger(filename, meta=meta)
    def __del__(self):
        del(self.pv2)
    def write(self, data):
        self.pv2.write(data)
    def flush(self):
        self.pv2.flush()
class fakelogger:
    '''
    fake logger (does nothing)
    instantiate with stdout=True to see the incoming data on the console.
    '''
    def __init__(self, stdout=False):
        self.stdout=stdout
        pass
    def __del__(self):
        pass
    def write(self, data):
        if self.stdout:
            print "Fakelog: %s" % str(data)
        pass
    def flush(self):
        pass

class pv2filelogger:
    '''
    General interface for generating PV2 logfiles from python data and meta-data dictionaries.
    Usually don't use directly, write a wrapper class like pv2logger_s60 and use that one!
    Writes coordinates, cellid related information , Wifi, Audio, time, etc. to PV2 fileformat.
    Takes meta information as dictionary at construction time
    Appends data to logfile via the write-method
    Doesn't write to file unless self.savedelay (default: 10) seconds have passed
    or flush() is explicitly called! Flushes on destruction.
    '''
    def __init__(self, filename , meta={},savedelay=10):
        self.queuetolog=[]
        self.lastflushtime=0
        self.filename = filename
        self.savedelay = savedelay
        # write header to new file
        f = open(filename,'w')
        f.write("#PlacelabStumbler Log Version 2\n")
        # write meta data
        for key in meta:
            value = meta[key]
            line = "#%s=%s\n" %(key,value)
            #print line
            f.write(line)
        f.close()
    def __del__(self):
        self.flush()
    def write(self, data={}):
        '''
        write to memory queue and eventually save to file if last save was self.SAVEDELAY ago
        use flush to make sure it gets written immediately
        values must not contain "|" as that character is used for seperation!
        return 1 on success, 0 otherwise
        required keys: TYPE, TIME (unixtime ms - extend with 000 if you only have seconds)
        TYPE could be anything, parsers currently support: GPS, GSM, WIFI, AUDIO
        '''
        if data.has_key("TYPE"):
            if data.has_key("TIME"):
                # write TYPE and TIME first
                line = "TYPE=%s|TIME=%s" % (data["TYPE"],data["TIME"])
                # then the rest
                for key in data:
                    if key != "TYPE":
                        if key != "TIME":
                            append = "|%s=%s" % (key.upper(),data[key])
                            line+=append
                line+="\n"
                self.queuetolog.append(line)
                # check if it is time to save again
                currenttime = time.time()
                if (currenttime - self.lastflushtime)>self.savedelay:
                    self.flush()
                return 1
            else:
                return 0
        else:
            return 0
    def flush(self):
        '''
        Flush memory queue to logfile
        '''
        copy = self.queuetolog
        self.queuetolog=[]
        if len(copy)>0:
            #print "flushing"
            f = open(self.filename,'a')
            for line in copy:
                f.write(line)
            f.close()
            self.lastflushtime = time.time()
'''
    # can be fed externally with lines to log by appending to self.queuetolog
def save_logs():
    while self.app_running:
        mcc, mnc, lac, cellid = location.gsm_location()
        unixtime = (int) (time.time())
        sig7 = sysinfo.signal()
        bat7 = sysinfo.battery()
        typeGSM = "TYPE=GSM|TIME=%s000|CELLID=%s|AREAID=%s|MCC=%s|MNC=%s|SIG7=%s|BAT7=%s\n" % (unixtime, cellid, lac, mcc, mnc, sig7, bat7)

        writeGPS = False;
        if self.pos.lat!=0:
            if self.pos.lon!=0:
                writeGPS =True

        typeGPS="TYPE=GPS|TIME=%s000|DATE=%s|LAT=%f|LON=%f|TIMEOFFIX=%s|STATUS=%s|SOG=%.1f|COG=%.1f|MODE=%d|NUMSAT=%d|PDOP=%s|HDOP=%s|VDOP=%s\n" % (
            unixtime,
            self.pos.date,
            self.pos.lat,
            self.pos.lon,
            self.pos.time,
            self.pos.gpsstatus,
            self.pos.speed_kmph,
            self.pos.course,
            self.pos.mode,
            self.pos.numsat,
            self.pos.PDOP,
            self.pos.HDOP,
            self.pos.VDOP)
        #write samples to log file on memory card ("e:\"
        try:
            f = open(filename,'a')
            # write GSM
            f.write(typeGSM)
            # write GPS
            if writeGPS is True:
                f.write(typeGPS)
            # write externally fed lines from self.queuetolog
            copy = self.queuetolog
            self.queuetolog=[]
            if len(copy) > 0:
                for line in copy:
                    f.write(line)
            del(copy)
            f.close()
        except:
            print "Error writing to %s at %s" % (filename, unixtime)
        e32.ao_sleep(3)
'''