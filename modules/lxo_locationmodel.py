# lxo, 20.06.2008
# code to support mapping position to regions to locations to assets
# currently gps (only with region spheres) and wifi, but can be extended easily!

import math
from lxo_mappers import oidmapper
from lxo_helpers import listhelpers

class location_aggregator:
    '''
    top level location class which gets locations from the intersecter classes (gps, wifi).
    will implement some sort of prioritisation of intersecters if we get non uniform results, e.g. might
    prioritize gps over wifi.
    this class knows which assets belong to the current location.
    '''
    def __init__(self):
        self.map_location2asset={}
        self.assets={}
        self.clintCallback=None
        pass
    def __del__(self):
        pass
    def inflate(self, fromdict):
        '''
        load state from dictionary
        returns 1 on success, otherwise 0
        will not load partial data, so all dicts must be present
        '''
        print "\n***Init: Inflating location_aggregator"
        if fromdict.has_key("Asset"):
            if fromdict.has_key("Map_GameLocationAsset"):
                # parse assets
                assets = fromdict["Asset"]
                for id in assets:
                    self.assets[id] = assets[id]
                # parse mapping from location to asset
                mgla=fromdict["Map_GameLocationAsset"]
                self.map_location2asset = {}
                for id in mgla:
                    #print id
                    mapping = mgla[id]
                    assetID = mapping["assetID"]
                    locationID = mapping["locationID"]
                    #print locationID, assetID
                    # manage 0..n assets per locationID in a list
                    if self.map_location2asset.has_key(locationID):
                        self.map_location2asset[locationID].append(assetID)
                    else:
                        self.map_location2asset[locationID]=[assetID]
                # done
                #print self.assets
                print self.map_location2asset
                return 1
            else:
                print "cannot inflate location_aggregator, missing 'Map_GameLocationAsset'"
                return 0
        else:
            print "cannot inflate location_aggregator, missing 'Asset'"
            return 0
    def inputLocation(self,locationID):
        '''
        to be called by intersecters
        will pass on to client if clientCallback defined
        '''
##        print locationID
        #print "\n--- received callback for location %s" % (locationID)
        # look for assets for this location
        if self.map_location2asset.has_key(locationID):
            assetIDs = self.map_location2asset[locationID]
            #print "Assets for this location:"
            #print assetIDs
            #print self.assets[locationID]
        else:
            assetIDs=[]
            #print "No asset for location %s" % (locationID)

        # callback to the client
        if self.clientCallback!=None:
            self.clientCallback(locationID, assetIDs)

    def registerClientCallback(self, callback):
        '''
        register a callback to a function that consumes (locationID,[assetIDs])
        '''
        self.clientCallback = callback

class position_intersecter:
    '''
    intersects a position reading (e.g. from a gps) with the current game region definitions
    preferred setup:
    input:  via callback(lat,lon,alt) to input(lat,lon,alt)
            incoming data is assumed to be fine, i.e. calling code should maybe prefilter gps data to remove position jumps
    output: registered callback will pass locations on to location aggregator
    '''
    def __init__(self):
        self.region_sphere={}
        # for passing the current location on to the aggregator
        self.callback2aggregator=None
        # for mapping the obtained region to a location
        self.map_region2location =None
        pass
    def __del__(self):
        pass
    def addRegionSphere(self,id,centerlat,centerlon,centeralt,radius):
        '''
        adds a sphere region to the list of regions
        '''
        rs = region_sphere((centerlat,centerlon,centeralt),radius)
        #print "Adding region %s: (%f,%f,%d), r=%d"%(id, centerlat,centerlon,centeralt,radius)
        self.region_sphere[id]=rs
    def delRegionSphere(self,id):
        '''
        removes a sphere region with the give name
        '''
        del region_sphere[id]
    def input2D(self,(lat,lon)):
        '''
        preferred interface. intersets position with regions and triggers callbacks.
        '''
        # get all intersecting region IDs
        intersections = self.intersect2D((lat,lon))
        # trigger callback for each region
        #print "input2D: %s" % str(intersections)
        for id in intersections:
            self.reportRegion(id)
    def intersect2D(self,(lat,lon)):
        '''
        returns a list of regions ids of those regions that the given lat/lon intersects
        e.g. ["RS504", "RP501"]
        '''
        intersects = []
        for id in self.region_sphere:
            rs = self.region_sphere[id]
            if rs.isPointInGeoCircle((lat,lon)):
                intersects.append(id)
                # callback?
                #self.reportRegion(id)
        #print "pint.intersect2D: %s" % str(intersects)
        return intersects
    def registerCallback2Aggregator(self, callback):
        '''
        register a callback to a function that consumes (locationID)
        '''
        self.callback2aggregator = callback
    def reportRegion(self,regionID):
        '''
        internal function that maps region to location and then
        sends the locationID to the registered callback (if any)
        '''
##        print "reportRegion: called!"
        if self.callback2aggregator != None:
            if self.map_region2location.has_key(regionID):
                locationIDs = self.map_region2location[regionID]
                for locationID in locationIDs:
##                    print "reportRegion: %s" % locationID
                    self.callback2aggregator(locationID)
    def inflate(self, fromdict):
        '''
        load state from dictionary
        returns 1 on success, otherwise 0
        will not load partial data, so all dicts must be present
        '''
        print "\n***Init: Inflating position_intersecter"
        if fromdict.has_key("Region"):
            if fromdict.has_key("Map_GameLocationRegion"):
                # parse regions
                regions=fromdict["Region"]
                for id in regions:
                    region = regions[id]
                    if id.startswith("RS"):
                        # is regionSphere
                        lat=region["center"]["lat"]
                        lon=region["center"]["lon"]
                        alt=region["center"]["alt"]
                        radius = region["radius"]
                        print "Adding region %s: (%f,%f,%d,%d)" %(id, lat,lon,alt,radius)
                        self.addRegionSphere(id, lat,lon,alt,radius)
                    else:
                        print "not a sphere region: %s" % id
                # parse mapping from region to location
                mglr=fromdict["Map_GameLocationRegion"]
                self.map_region2location = {}
                for id in mglr:
                    #print id
                    mapping = mglr[id]
                    locationID = mapping["locationID"]
                    regionID = mapping["regionID"]
                    #print locationID, regionID
                    #self.map_region2location[regionID]=locationID
                    if self.map_region2location.has_key(regionID):
                        self.map_region2location[regionID].append(locationID)
                    else:
                        self.map_region2location[regionID]=[locationID]
                # done
                #print self.map_region2location
                return 1
            else:
                print "cannot inflate position_intersecter, missing 'Map_GameLocationRegion'"
                return 0
        else:
            print "cannot inflate position_intersecter, missing 'Region'"
            return 0

class region_sphere:
    '''
    A region defined as a sphere with a center point in WGS84 (lat/lon/alt) with a radius in meters.
    This class allows testing for point in sphere.
    '''
    def __init__(self, (lat,lon,alt),radius):
        self.lat=lat
        self.lon=lon
        self.alt=alt
        self.radius=radius

    def rad2deg(self, rad):
        return rad * 180 / math.pi

    def deg2rad(self, deg):
        return deg * math.pi / 180

    def distance(self, lat1, lon1, lat2, lon2):
        lat1 = self.deg2rad(lat1)
        lon1 = self.deg2rad(lon1)
        lat2 = self.deg2rad(lat2)
        lon2 = self.deg2rad(lon2)
        theta = lon1 - lon2
        dist = math.sin(lat1) * math.sin(lat2) \
             + math.cos(lat1) * math.cos(lat2) * math.cos(theta)
        dist = math.acos(dist)
        dist = self.rad2deg(dist)
        meters = dist * 60 * 1852
        return meters

    def isPointInGeoCircle(self,(lat, lon)):
        '''
        Just test in 2D (without altitude) if point is in the circle (sphere).
        '''
        if (self.distance(lat,lon,self.lat,self.lon) < self.radius):
            return 1
        else:
            return 0

class wifi_intersecter:
    '''
    based on the wififingerprinter in lxo_wifi, but modified to suit inscape:
    - RW* region ids handled
    - inverted control (throws trigger events based on wifi input rather than actively scanning for wifi)
    '''
    def __init__(self):
        self.sid = oidmapper()
        self.oid = oidmapper()
        self.lh  = listhelpers()
        # for passing the current location on to the aggregator
        self.callback2aggregator=None
        # for mapping the obtained region to a location
        self.map_region2location =None
        self.lastscan= []    # raw results from wlantools
        self.lastaps = []     # filtered and sorted list of bssids
    def inflate(self, fromdict):
        '''
        load state from dictionary
        returns 1 on success, otherwise 0
        will not load partial data, so all dicts must be present
        '''
        print "\n***Init: Inflating wifi_intersecter"
        if fromdict.has_key("Region"):
            if fromdict.has_key("Map_GameLocationRegion"):
                # parse regions
                regions=fromdict["Region"]
                for id in regions:
                    region = regions[id]
                    if id.startswith("RW"):
                        # is region wifi
                        apsstring=region["aps"]
                        apnum=region["apnum"]
                        apslist=apsstring.split(",")
                        #print apslist
                        print "Adding region %s: (%d, %s)" %(id, apnum, str(apslist) )
                        self.addRegionWifi(apslist,id)
                    else:
                        print "not a wifi region: %s" % id
                # parse mapping from region to location
                mglr=fromdict["Map_GameLocationRegion"]
                self.map_region2location = {}
                for id in mglr:
                    #print id
                    mapping = mglr[id]
                    locationID = mapping["locationID"]
                    regionID = mapping["regionID"]
                    #print locationID, regionID
                    #self.map_region2location[regionID]=locationID
                    if self.map_region2location.has_key(regionID):
                        self.map_region2location[regionID].append(locationID)
                    else:
                        self.map_region2location[regionID]=[locationID]
                # done
                #print self.map_region2location
                return 1
            else:
                print "cannot inflate position_intersecter, missing 'Map_GameLocationRegion'"
                return 0
        else:
            print "cannot inflate position_intersecter, missing 'Region'"
            return 0

    def addRegionWifi(self,listOfBssids,regionid=None):
        '''
        Adds the list of bssids to the internal mapping. Internal subroutine for inflate()
        This is not the preffered way of setting up the instance. Consider using inflate instead.
        '''
        l = []
        # build a list of integers for faster comparision
        for elem in listOfBssids:
            # get/add id for each bssid
            id = self.sid.getID(elem)
            l.append(id)
        l.sort()

        # get/add id for this region
        if regionid==None:
            # generate an ID
            objectid =  self.oid.getID(l)
        else:
            # use the given ID
            objectid =  self.oid.setObjectAndID(l,regionid)
        print objectid, l
        return objectid
    def getFingerprintNum(self):
        '''
        returns the number of fingerprints currently known
        '''
        #print self.oid.idtable.keys()
        return len(self.oid.idtable.keys())
    def calculateOverlap(self,referencelist,testlist):
        '''
        calculated overlap in 0..1 for the testlist within the referencelist
        overlap of 1 means that the lists are equal (no, but that the referencelist is fully matched
                                                    even if the testlist might be much bigger)
        overlap of 0 means that they have nothing in common
        overlap of 0.5 means that half the elements are in the intersection
        '''
        # check for empty lists
        lenreference=float(len(referencelist))
        lentest=float(len(testlist))
        if lenreference==0.0:
            return 0.0
        if lentest==0.0:
            return 0.0
        # get intersection list
        il = self.lh.intersection(referencelist,testlist)
        lenintersection = float(len(il))
        if len(il)==0.0:
            return 0.0
        # calculate overlap value and return
        # take the longer of the two input lists
        lenlongest = lenreference
        if 0:
            # took it out again because I suspect this might be one of the two possible
            # causes why the N95 testwalk returned to different results from the N800 testwalk
            # (the other cause being the string hashes which have been added in the last minute)
            if lentest>lenlongest:
                lenlongest = lentest
        return lenintersection/lenlongest
    def inputAPS(self, apslist, threshold=-80,limit=5,overlap=0.3,debug=True):
        '''
        preferred interface. intersets apslist with wifi regions and triggers callbacks.

        constructs wifi fingerprint from wifi apslist
        returns (new,fingerprint number) (or None if none could be created (means no wifi ever seen since running)
        new is 1 if this is a new fingerprint
        - apslist [{BSSIDS and RxLevel}]
        - p1: drop below threshold RxLevel
        - p2: only maintain top N BSSIDS, where top means strongest RxLevel
        - p3: fuzzy match with % overlap
        '''
        # get aps above threshold, but no more than "limit"
        #ret = [{'Capability': 1073, 'BeaconInterval': 100, 'SecurityMode': 'Wep', 'SSID': u'CSiT', 'BSSID': u'00:20:A6:51:C6:CF', 'ConnectionMode': 'Infrastructure', 'InformationElements': {42: u'00', 50: u'1224606C'}, 'SupportedRates': u'82848B960C183048', 'Channel': 11, 'RxLevel': -61}, {'Capability': 1073, 'BeaconInterval': 100,'SecurityMode': 'Wep', 'SSID': u'CSiTrobots', 'BSSID': u'00:17:0E:86:01:E1', 'ConnectionMode': 'Infrastructure', 'InformationElements': {42: u'00', 221: u'0050F2020101020003A4000027A4000042435E0062322F00', 50: u'3048606C', 133: u'000081000F00FF03190063666131302D6170000000000000000005000025'}, 'SupportedRates': u'82848B0C12961824', 'Channel': 6, 'RxLevel': -62}, {'Capability': 1073, 'BeaconInterval': 100, 'SecurityMode': 'Wep', 'SSID': u'CSiT28', 'BSSID': u'00:17:0E:86:01:E0', 'ConnectionMode': 'Infrastructure', 'InformationElements': {42: u'00', 221: u'0050F2020101020003A4000027A4000042435E0062322F00', 50: u'3048606C', 133: u'000081000F00FF03190063666131302D6170000000000000000005000025'}, 'SupportedRates': u'82848B0C12961824', 'Channel': 6, 'RxLevel': -67}, {'Capability': 1073, 'BeaconInterval': 100, 'SecurityMode': 'Wep', 'SSID': u'CSiTwep', 'BSSID': u'00:17:0E:86:01:E2', 'ConnectionMode': 'Infrastructure', 'InformationElements': {42: u'00', 221: u'0050F2020101020003A4000027A4000042435E0062322F00', 50: u'3048606C', 133: u'000081000F00FF03190063666131302D6170000000000000000005000025'}, 'SupportedRates': u'82848B0C12961824', 'Channel': 6, 'RxLevel': -67}]
        #apslist = self.scanner.getAPS()
        self.lastscan = apslist                 # store for later use, e.g. by the logger
        #filter by threshold, then limit
        filtered = []
        for ap in apslist:
            if ap["RxLevel"] > threshold:
                filtered.append(ap)
        # limit number of returned aps
        if limit!=0:
            if limit<len(filtered):
                # need to limit the list
                filtered = filtered[0:limit]
        # convert strings to ids and put to sorted list
        l = []
        for elem in filtered:
            s = elem["BSSID"]
            id = self.sid.getID(s)
            l.append(id)
        l.sort()
        self.lastaps = l
        # output to console
        if debug:
            print "Scanresults: %s" %(str(self.lastaps))
        #objectid =  self.oid.getID(l)
        # if no object indexed, yet, this is going to be our first fingerprint (maybe)
        if len(self.oid.idtable)==0:
            # check for empty scan results (otherwise couldn't make this a fingerprint)
            return 0,None
##            if len(l)==0: return 0,None
##            objectid =  self.oid.getID(l)
##            return 1,objectid   # must be (1,1) - first fingerprint ever is new and has id 1!
            # no need for triggers as there was no intersection
        else:
            # check our scan list against already stored fingerprints
            test = l
            possibleplaces=[]
            for id in self.oid.idtable.keys():
                reference = self.oid.getObject(id)
                #print "compare id: %s, value: %s" %(id,reference)
                overlapvalue = self.calculateOverlap(reference,test)
                #print "overlap value: %s, overlap required: %s" % (overlapvalue,overlap)
                if overlapvalue >= overlap: # >= because > (as in rider spoke) would forbid looking for 100% matches
                #    print "overlapped!"
                    possibleplaces.append((id,overlapvalue))
                ##                else:
                ##                    print "did not overlap"
            # just get the place id without the overlap
            templist=[]
            for place in possibleplaces:
                id, overlapvalue = place
                templist.append(id)
            if debug:
                print "Possible places: %s" % (str(templist))
            # find the most likely place based on overlapvalue
            bestid = None
            bestoverlap=0
            for place in possibleplaces:
                id, overlapvalue = place
                if overlapvalue>bestoverlap:
                    bestid = id
                    bestoverlap = overlapvalue
                    if debug:
                        print " took: %s (%.2f)" %(id,overlapvalue)
            # nothing matched, lets make a new place!
            if bestid == None:
                # let's ignore new places for this (otherwise uncomment below)
                if debug: print "nothing found, sucks"
                return 0, None
##                if len(test)==0:
##                    # nothing found this time
##                    # no need for triggers here
##                    return 0,None
##                else:
##                    if debug:
##                        print "New place found!"
##                    objectid =  self.oid.getID(test)
##                    # no need for triggers here, as this is a new location, which cannot have content attached so far
##                    return 1,objectid
            else:
                # finally, this is our known wifi location
                if debug: print "*** trigger"
                self.reportRegion(bestid)
                return 0,bestid

    def registerCallback2Aggregator(self, callback):
        '''
        register a callback to a function that consumes (locationID)
        '''
        self.callback2aggregator = callback
    def reportRegion(self,regionID):
        '''
        internal function that maps region to location and then
        sends the locationID to the registered callback (if any)
        '''
        if self.callback2aggregator != None:
            if self.map_region2location.has_key(regionID):
                locationIDs = self.map_region2location[regionID]
                for locationID in locationIDs:
                    self.callback2aggregator(locationID)

if __name__ == "__main__":
    wi = wifi_intersecter()
##    print "Adding fingerprint a,b,c,d,e,f"
##    wi.addRegionWifi([u"a",u"b",u"c",u"d",u"e",u"f"])
    print "Testing intersection with varying overlap values"
    # generate fake scanresult
    scanresult = []
    scanresult.append({'BSSID': u'a', 'RxLevel': -55})
    scanresult.append({'BSSID': u'b', 'RxLevel': -60})
    scanresult.append({'BSSID': u'c', 'RxLevel': -65})
    scanresult.append({'BSSID': u'd', 'RxLevel': -70})
    scanresult.append({'BSSID': u'e', 'RxLevel': -75})
    scanresult.append({'BSSID': u'f', 'RxLevel': -80})
    maxi=5
    for i in range(maxi+1):
        print "---"
        normi=float(i*1.0/maxi)
        print "Required overlap: %s" %normi
        new, id = wi.inputAPS(scanresult, limit=5, threshold = -70, overlap=normi)
        print new, id

