# generic gps interface with callback
# to be used for s60 1st, 2nd and 3rd edition phoness
# lxo 19.04.2008

'''
api (similar to position api, but also for 1st and 2nd edition)

position:
latitude
longitude
altitude
horizontal_accuracy (not on 1st and 2nd edition, yet)
vertical_accuracy (not on 1st and 2nd edition, yet)

course:  (not on 1st and 2nd edition, yet)
speed
speed_accuracy
heading
heading_accuracy

satellites:
time
time_dop
satellites
used_satellites
vertical_dop
horizontal_dop

# from placelab 04:
TYPE=GPS
|TIME=1096470106501
|HDOP=2.3                   - (could be added
|DGPSAGE=                   -
|DATE=290904                *
|QUALITY=1                  -
|LAT=47.66317666666668      *
|DGPSID=                    -
|STATUS=A                   *
|NUMSAT=05                  * (must be added - not in the pv2, yet!)
|MODE=A                     -
|ANTHEIGHT=61.8             -
|SOG=11.2                   *
|VARDIR=E                   -
|VAR=18.1                   -
|LON=-122.31086666666667    *
|TIMEOFFIX=150146           *
|GEOHEIGHT=-18.4            -
|COG=181.1                  *

# from own pv2:
TYPE=GPS
|TIME=1144778176000
|DATE=110406
|LAT=52.636635
|LON=-1.122172
|TIMEOFFIX=165640.976
|STATUS=A
|SOG=24.7
|COG=291.7

'''
try:
    import positioning
except:
    pass

class GPSInterface:
    '''
    An abstract interface to support different ways of reading GPS data across different devices.

    Currently targeted at S60 1st, 2nd and 3rd edition phones,
    but could be implemented on other platforms as well
    '''
    #---abstract methods
    def registerCallback(self, callback):
        '''
        register a callback which will receive dictionary when new data is available.
        the callback will get one parameter passed: dictionary
        '''
        #override and implement this method
        assert 0, 'GPSInterface.registerCallback() must be defined!'
    def update(self):
        '''
        to be periodically called by the main loop to get new data from the gps.
        some implementations, e.g. on 3rd edition position api might choose to do nothing here.
        '''
        #override and implement this method
        assert 0, 'GPSInterface.update() must be defined!'

class GPS_S603RD(GPSInterface):
    '''
    An implementation of the GPS interface for Series 60 3rd edition phones, e.g. Nokia N95
    '''
    def __init__(self,callback=None):
        # init 3rd edition position api
        self.start()
        # callback to outer world not defined, yet
        self.callback=callback
    def __del__(self):
        self.stop()
        pass
    def stop(self):
        positioning.stop_position()
        print "***Info: stopping positioning"
    def start(self):
        positioning.select_module(positioning.default_module())
        positioning.set_requestors([{"type":"service","format":"application","data":"test_app"}])
        # register callback
        #print positioning.position(course=1,satellites=1,interval=500000,partial=1)
        positioning.position(course=1,satellites=1,callback=self.onPosition, interval=5000000)
        #positioning.position(callback=self.onPosition, interval=1000000)
    def onPosition(self, data):
        #print data
        if self.callback!=None:
            self.callback(data)
    def registerCallback(self, callback):
        '''
        register a callback which will receive dictionary when new data is available
        '''
        self.callback = callback
    def update(self):
        '''
        to be periodically called by the main loop to get new data from the gps.
        some implementations, e.g. on 3rd edition position api might choose to do nothing here.
        '''
        #print positioning.position(course=1,satellites=1,interval=500000,partial=1)
        pass


class GPS_FAKE(GPSInterface):
    '''
    An FAKE implementation of the GPS interface to be used for development
    '''
    def __init__(self,callback=None):
        self.callback=callback
    def __del__(self):
        pass
    def onPosition(self, data):
        #print data
        if self.callback!=None:
            self.callback(data)
    def registerCallback(self, callback):
        '''
        register a callback which will receive dictionary when new data is available
        '''
        self.callback = callback
    def start(self):
        pass
     
    def stop(self):
        pass
        
    def update(self):
        '''
        to be periodically called by the main loop to get new data from the gps.
        some implementations, e.g. on 3rd edition position api might choose to do nothing here.
        '''
        #print positioning.position(course=1,satellites=1,interval=500000,partial=1)
        #52.953793,-1.187047
##        fakedata={'satellites': {'horizontal_dop': 3.5699999332428,
##         'used_satellites': 3, 'vertical_dop': 1.0, 'time': 1208434422.0, 'satellites': 13,
##         'time_dop': 1.27999997138977}, 'position': {'latitude': 52.953400831661,
##         'altitude': 73.5, 'vertical_accuracy': 0.5, 'longitude': -1.187133358502,
##         'horizontal_accuracy': 25.6371593475342},'course': {'speed': 0.0599999986588955,
##         'heading': 195.570007324219, 'heading_accuracy': 359.989990234375, 'speed_accuracy': 1.0900000333786}}
        fakedata={'satellites': {'horizontal_dop': 3.5699999332428,
         'used_satellites': 3, 'vertical_dop': 1.0, 'time': 1208434422.0, 'satellites': 13,
         'time_dop': 1.27999997138977}, 'position': {'latitude': 52.953793,
         'altitude': 73.5, 'vertical_accuracy': 0.5, 'longitude': -1.187047,
         'horizontal_accuracy': 25.6371593475342},'course': {'speed': 0.0599999986588955,
         'heading': 195.570007324219, 'heading_accuracy': 359.989990234375, 'speed_accuracy': 1.0900000333786}}
        self.onPosition(fakedata)

'''
*** test code:
gps = GPS_S603RD()
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

gps.registerCallback(cbGPS)
gps.start()
'''

'''
def cb(data):
    print data
gps = GPS_S603RD(cb)

gps.registerCallback(cb)

gps.stop()


del(gps)
positioning.stop_position()
'''
'''
from 3rd edition
>>> d = positioning.position(course=1,satellites=1,interval=500000,partial=1)
>>> d
{'satellites': {'horizontal_dop': 3.5699999332428, 'used_satellites': 3, 'vertic
al_dop': 1.0, 'time': 1208434422.0, 'satellites': 13, 'time_dop': 1.279999971389
77}, 'position': {'latitude': 52.953400831661, 'altitude': 73.5, 'vertical_accur
acy': 0.5, 'longitude': -1.187133358502, 'horizontal_accuracy': 25.6371593475342
}, 'course': {'speed': 0.0599999986588955, 'heading': 195.570007324219, 'heading
_accuracy': 359.989990234375, 'speed_accuracy': 1.0900000333786}}

>>> d.keys()
['satellites', 'position', 'course']

>>> d["satellites"]
{'horizontal_dop': 3.5699999332428, 'used_satellites': 3, 'vertical_dop': 1.0, '
time': 1208434422.0, 'satellites': 13, 'time_dop': 1.27999997138977}

>>> d["position"]
{'latitude': 52.953400831661, 'altitude': 73.5, 'vertical_accuracy': 0.5, 'longi
tude': -1.187133358502, 'horizontal_accuracy': 25.6371593475342}

>>> d["course"]
{'speed': 0.0599999986588955, 'heading': 195.570007324219, 'heading_accuracy': 3
59.989990234375, 'speed_accuracy': 1.0900000333786}
>>>

#--- example for the fake gps
def cb(data):
    print data
gps = GPS_FAKE(cb)
gps.update()
'''

