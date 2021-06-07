# lxo 15. - 17.04.08

# 02.07.08
# - added fakewifiscanner class
# - added addFingerprint to wififingerprinter
# - added test
# - modified overlap comparision to use >= instead of >

from lxo_mappers import oidmapper
from lxo_helpers import listhelpers
try:
    # required for real scanning on N95
    import wlantools
except:
    # but not required for testing with fake scanner on desktop
    pass

class wififingerprinter:
    def __init__(self,useFakeScanner=0):
        self.sid = oidmapper()
        self.oid = oidmapper()
        self.lh  = listhelpers()
        if useFakeScanner:
            self.scanner = fakewifiscanner()
        else:
            self.scanner = wifiscanner()
        self.lastscan= []    # raw results from wlantools
        self.lastaps = []     # filtered and sorted list of bssids
    def deflate(self):
        '''
        save state to dictionary
        '''
        ret = {}
        ret["siddict"]=self.sid.deflate()
        ret["oiddict"]=self.oid.deflate()
        return ret
    def inflate(self, fromdict):
        '''
        load state from dictionary
        returns 1 on success, otherwise 0
        will not load partial data, so siddict and oiddict must be present
        '''
        if fromdict.has_key("oiddict"):
            if fromdict.has_key("siddict"):
                self.sid.inflate(fromdict["siddict"])
                self.oid.inflate(fromdict["oiddict"])
                return 1
            else:
                return 0
        else:
            return 0
    def getFingerprintNum(self):
        '''
        returns the number of fingerprints currently known
        '''
        #print self.oid.idtable.keys()
        return len(self.oid.idtable.keys())
    def addFingerprint(self,listOfBssids):
        '''
        Adds the list of bssids to the internal mapping.
        This is not the preffered way of setting the instance up. Consider using inflate/deflate instead.
        '''
        l = []
        for elem in listOfBssids:
            print elem
            id = self.sid.getID(elem)
            l.append(id)
        l.sort()
        objectid =  self.oid.getID(l)
        print objectid, l
        return objectid

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
    def scan(self,threshold=-80,limit=5,overlap=0.3):
        '''
        construct wifi fingerprint from wifi environment
        returns (new,fingerprint number) (or None if none could be created (means no wifi ever seen since running)
        new is 1 if this is a new fingerprint
        - scan wifi (BSSIDS and RxLevel)
        - p1: drop below threshold RxLevel
        - p2: only maintain top N BSSIDS, where top means strongest RxLevel
        - p3: fuzzy match with % overlap
        '''
        # get aps above threshold, but no more than "limit"
        #ret = [{'Capability': 1073, 'BeaconInterval': 100, 'SecurityMode': 'Wep', 'SSID': u'CSiT', 'BSSID': u'00:20:A6:51:C6:CF', 'ConnectionMode': 'Infrastructure', 'InformationElements': {42: u'00', 50: u'1224606C'}, 'SupportedRates': u'82848B960C183048', 'Channel': 11, 'RxLevel': -61}, {'Capability': 1073, 'BeaconInterval': 100,'SecurityMode': 'Wep', 'SSID': u'CSiTrobots', 'BSSID': u'00:17:0E:86:01:E1', 'ConnectionMode': 'Infrastructure', 'InformationElements': {42: u'00', 221: u'0050F2020101020003A4000027A4000042435E0062322F00', 50: u'3048606C', 133: u'000081000F00FF03190063666131302D6170000000000000000005000025'}, 'SupportedRates': u'82848B0C12961824', 'Channel': 6, 'RxLevel': -62}, {'Capability': 1073, 'BeaconInterval': 100, 'SecurityMode': 'Wep', 'SSID': u'CSiT28', 'BSSID': u'00:17:0E:86:01:E0', 'ConnectionMode': 'Infrastructure', 'InformationElements': {42: u'00', 221: u'0050F2020101020003A4000027A4000042435E0062322F00', 50: u'3048606C', 133: u'000081000F00FF03190063666131302D6170000000000000000005000025'}, 'SupportedRates': u'82848B0C12961824', 'Channel': 6, 'RxLevel': -67}, {'Capability': 1073, 'BeaconInterval': 100, 'SecurityMode': 'Wep', 'SSID': u'CSiTwep', 'BSSID': u'00:17:0E:86:01:E2', 'ConnectionMode': 'Infrastructure', 'InformationElements': {42: u'00', 221: u'0050F2020101020003A4000027A4000042435E0062322F00', 50: u'3048606C', 133: u'000081000F00FF03190063666131302D6170000000000000000005000025'}, 'SupportedRates': u'82848B0C12961824', 'Channel': 6, 'RxLevel': -67}]
        ret = self.scanner.getAPS()
        self.lastscan = ret                 # store for later use, e.g. by the logger
        #filter by threshold, then limit
        filtered = []
        for ap in ret:
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
        print "Scanresults: %s" %(str(self.lastaps))
        #objectid =  self.oid.getID(l)
        # if no object indexed, yet, this is going to be our first fingerprint (maybe)
        if len(self.oid.idtable)==0:
            # check for empty scan results (otherwise couldn't make this a fingerprint)
            if len(l)==0: return 0,None
            objectid =  self.oid.getID(l)
            return 1,objectid   # must be (1,1) - first fingerprint ever is new and has id 1!
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
            print "Possible places: %s" % (str(templist))
            # find the most likely place based on overlapvalue
            bestid = None
            bestoverlap=0
            for place in possibleplaces:
                id, overlapvalue = place
                if overlapvalue>bestoverlap:
                    bestid = id
                    bestoverlap = overlapvalue
                    print " took: %s (%.2f)" %(id,overlapvalue)
            # nothing matched, lets make a new place!
            if bestid == None:
                if len(test)==0:
                    # nothing found this time
                    return 0,None
                else:
                    print "New place found!"
                    objectid =  self.oid.getID(test)
                    return 1,objectid
            else:
                return 0,bestid

class wifiscanner:
    '''
    implements wifi scanning using the wlantools api
    see http://discussion.forum.nokia.com/forum/showthread.php?t=118218
        http://chris.berger.cx/
    '''
    def __init__(self):
        import wlantools
        self.lastresult=None
        pass
    def comparatorAP(self,e1,e2):
        '''
        custom comparator for the list of access points
        sorts on signal strength, i.e. "RxLevel" in the dict
        '''
        return cmp(e1["RxLevel"],e2["RxLevel"])
    def reverseComparatorAP(self,e1,e2):
        '''
        custom comparator for the list of access points
        sorts on signal strength, i.e. "RxLevel" in the dict, reverse order (highest first)
        '''
        return cmp(e2["RxLevel"],e1["RxLevel"])
    def getAPS(self):
        '''
        scans for wifi and returns list sorted by RxLevel (strongest first)
        '''
        scanresult = wlantools.scan(False)  # note: not setting it to False will cause a crash on some APs!
        # sort remaining
        scanresult.sort(self.reverseComparatorAP)
##        # limit number of returned aps
##        if limit==0:
##            # special case: 0 == infinity
##            return ret
##        if limit<len(ret):
##            # need to limit the returned list
##            lret = []
##            for i in range(limit):
##                lret.append(ret[i])
##            #print lret
##            return lret
##        # otherwise just return everything
        self.lastresult=scanresult
        return scanresult
    def getAPSFiltered(self,threshold,limit=0):
        '''
        scans for wifi and returns those BSSIDs where RxLevel > threshold, sorted by RxLevel
        '''
        ret = []
        scanresult = self.getAPS()
        # filter on threshold
        for ap in scanresult:
            if ap["RxLevel"] > threshold:
                ret.append(ap)
        # sort remaining (could be omitted as already sorted?)
        ret.sort(self.reverseComparatorAP)
        # limit number of returned aps
        if limit==0:
            # special case: 0 == infinity
            self.lastresult=ret
            return ret
        if limit<len(ret):
            # need to limit the returned list
            lret = []
            for i in range(limit):
                lret.append(ret[i])
            #print lret
            self.lastresult=lret
            return lret
        # otherwise just return everything
        self.lastresult=ret
        return ret
    def getLastResult(self):
        '''
        return the last scan result, either raw or filtered, depending on what has been done before
        - will be raw & sorted if getAPS() has been called before
        - will be filtered & sorted if getAPSFiltered() has been called before
        '''
        return self.lastresult


class fakewifiscanner:
    '''
    fakes wifi scanning for desktop development
    '''
    def __init__(self):
        pass
    def comparatorAP(self,e1,e2):
        '''
        custom comparator for the list of access points
        sorts on signal strength, i.e. "RxLevel" in the dict
        '''
        return cmp(e1["RxLevel"],e2["RxLevel"])
    def reverseComparatorAP(self,e1,e2):
        '''
        custom comparator for the list of access points
        sorts on signal strength, i.e. "RxLevel" in the dict, reverse order (highest first)
        '''
        return cmp(e2["RxLevel"],e1["RxLevel"])
    def getAPS(self):
        '''
        scans for wifi and returns list sorted by RxLevel (strongest first)
        '''
##        scanresult = []
##        scanresult.append({'BSSID': u'a', 'RxLevel': -55, })
##        scanresult.append({'BSSID': u'b', 'RxLevel': -60})
##        scanresult.append({'BSSID': u'c', 'RxLevel': -65})
##        scanresult.append({'BSSID': u'd', 'RxLevel': -70})
##        scanresult.append({'BSSID': u'e', 'RxLevel': -75})
##        scanresult.append({'BSSID': u'f', 'RxLevel': -80})

        scanresult = []
        scanresult.append({'Capability': 1073, 'BeaconInterval': 100, 'SecurityMode': 'Wep', 'SSID': u'CSiTrobots', 'BSSID': u'00:17:0E:86:00:B1', 'ConnectionMode': 'Infrastructure', 'InformationElements':  {42: u'02', 221: u'0050F20201010C0003A4000027A4000042435E0062322F00', 50: u'3048606C', 133: u'000081000F00FF031900636661372D617000000000000000000001000025'}, 'SupportedRates': u'82848B0C12961824', 'Channel': 1, 'RxLevel': -87})
        scanresult.append({'Capability': 1073, 'BeaconInterval': 100, 'SecurityMode': 'Wep', 'SSID': u'CSiTwep', 'BSSID': u'00:17:0E:86:03:82', 'ConnectionMode': 'Infrastructure', 'InformationElements':  {42: u'02', 221: u'0050F20201010E0003A4000027A4000042435E0062322F00', 50: u'3048606C', 133: u'000081000F00FF031900636661342D617000000000000000000000000025'}, 'SupportedRates': u'82848B0C12961824', 'Channel': 1, 'RxLevel': -84})
        scanresult.append({'Capability': 1073, 'BeaconInterval': 100, 'SecurityMode': 'Wep', 'SSID': u'MRL', 'BSSID': u'00:17:0E:85:FA:C3', 'ConnectionMode': 'Infrastructure', 'InformationElements': {42: u'00', 221: u'0050F2020101020003A4000027A4000042435E0062322F00', 50: u'3048606C', 133: u'000081000F00FF03190063666131322D6170000000000000000002000025'}, 'SupportedRates': u'82848B0C12961824', 'Channel': 1, 'RxLevel': -83})
        scanresult.append({'Capability': 49, 'BeaconInterval': 100, 'SecurityMode': 'Wep', 'SSID': u'CSiTmeeting', 'BSSID': u'00:17:0E:86:07:B1', 'ConnectionMode': 'Infrastructure', 'InformationElements': {42: u'07', 221: u'0050F2020101060003A4000027A4000042435E0062322F00', 50: u'3048606C', 133: u'000081000F00FF031900636661332D617000000000000000000002000025'}, 'SupportedRates': u'82848B0C12961824', 'Channel': 1, 'RxLevel': -71})
        scanresult.append({'Capability': 49, 'BeaconInterval': 100, 'SecurityMode': 'Wep', 'SSID': u'CSiT28', 'BSSID': u'00:17:0E:86:01:E0', 'ConnectionMode': 'Infrastructure', 'InformationElements': {42: u'07', 221: u'0050F2020101040003A4000027A4000042435E0062322F00', 50: u'3048606C', 133: u'000081000F00FF03190063666131302D6170000000000000000002000025'}, 'SupportedRates': u'82848B0C12961824', 'Channel': 6, 'RxLevel': -61})
        scanresult.append({'Capability': 49, 'BeaconInterval': 100, 'SecurityMode': 'Wep', 'SSID': u'CSiTrobots', 'BSSID': u'00:17:0E:86:01:E1', 'ConnectionMode': 'Infrastructure', 'InformationElements': {42: u'07', 221: u'0050F2020101040003A4000027A4000042435E0062322F00', 50: u'3048606C', 133: u'000081000F00FF03190063666131302D6170000000000000000002000025'}, 'SupportedRates': u'82848B0C12961824', 'Channel': 6, 'RxLevel': -62})
        scanresult.append({'Capability': 49, 'BeaconInterval': 100, 'SecurityMode': 'Wep', 'SSID': u'CSiTwep', 'BSSID': u'00:17:0E:86:01:E2', 'ConnectionMode': 'Infrastructure', 'InformationElements': {42: u'07', 221: u'0050F2020101040003A4000027A4000042435E0062322F00', 50: u'3048606C', 133: u'000081000F00FF03190063666131302D6170000000000000000002000025'}, 'SupportedRates': u'82848B0C12961824', 'Channel': 6, 'RxLevel': -61})
        scanresult.append({'Capability': 1057, 'BeaconInterval': 100, 'SecurityMode': 'Open', 'SSID': u'UoN-standard', 'BSSID': u'00:17:0E:86:03:84', 'ConnectionMode': 'Infrastructure', 'InformationElements': {221: u'0050F20201010E0003A4000027A4000042435E0062322F00', 42: u'02', 50: u'3048606C', 5: u'424B0000', 133: u'000081000F00FF031900636661342D617000000000000000000000000025'}, 'SupportedRates': u'82848B0C12961824', 'Channel': 1, 'RxLevel': -85})
        scanresult.append({'Capability': 49, 'BeaconInterval': 100, 'SecurityMode': 'Wep', 'SSID': u'CSiT28', 'BSSID': u'00:17:0E:86:07:B0', 'ConnectionMode': 'Infrastructure', 'InformationElements': {221: u'0050F2020101060003A4000027A4000042435E0062322F00', 42: u'07', 50: u'3048606C', 5: u'3A4B0000', 133: u'000081000F00FF031900636661332D617000000000000000000002000025'}, 'SupportedRates': u'82848B0C12961824', 'Channel': 1, 'RxLevel': -71})
        scanresult.append({'Capability': 49, 'BeaconInterval': 100, 'SecurityMode': 'Wep', 'SSID': u'MRL', 'BSSID': u'00:17:0E:86:01:E3', 'ConnectionMode': 'Infrastructure', 'InformationElements': {221: u'0050F2020101040003A4000027A4000042435E0062322F00', 42: u'07', 50: u'3048606C', 5: u'124B0000', 133: u'000081000F00FF03190063666131302D6170000000000000000002000025'}, 'SupportedRates': u'82848B0C12961824', 'Channel':6, 'RxLevel': -62})
        scanresult.append({'Capability': 3121, 'BeaconInterval': 100, 'SecurityMode': 'Wpa', 'SSID': u'UoN-secure', 'BSSID': u'00:18:73:31:C1:81', 'ConnectionMode': 'Infrastructure', 'InformationElements': {48: u'0100000FAC040100000FAC040100000FAC012800', 50: u'3048606C', 5: u'334B0000', 42: u'02', 221: u'0050F2020101820003A4000027A4000042435E0062322F00', 133: u'000084000F00FF031900746661372D617000000000000000000000000025'}, 'SupportedRates': u'82848B0C12961824', 'Channel': 6, 'RxLevel': -81})

        #print scanresult
        #scanresult = []

        #scanresult = wlantools.scan(False)  # note: not setting it to False will cause a crash on some APs!
        # sort remaining
        scanresult.sort(self.reverseComparatorAP)
        return scanresult
    def getAPSFiltered(self,threshold,limit=0):
        '''
        scans for wifi and returns those BSSIDs where RxLevel > threshold, sorted by RxLevel
        '''
        ret = []
        scanresult = self.getAPS()
        # filter on threshold
        for ap in scanresult:
            if ap["RxLevel"] > threshold:
                ret.append(ap)
        # sort remaining (could be omitted as already sorted?)
        ret.sort(self.reverseComparatorAP)
        # limit number of returned aps
        if limit==0:
            # special case: 0 == infinity
            return ret
        if limit<len(ret):
            # need to limit the returned list
            lret = []
            for i in range(limit):
                lret.append(ret[i])
            #print lret
            return lret
        # otherwise just return everything
        return ret

if __name__ == "__main__":
    wfp = wififingerprinter(useFakeScanner=1)
##    print "Only the first loop should generate a new place (line starts with 1)"
##    print "The other loops must find the same place and report is as known (line starts with 0)"
    print "Adding fingerprint a,b,c,d,e,f"
    wfp.addFingerprint([u"a",u"b",u"c",u"d",u"e",u"f"])
    print "Testing intersection with varying overlap values"
    maxi=5
    for i in range(maxi+1):
        print "---"
        normi=float(i*1.0/maxi)
        print "Required overlap: %s" %normi
        new, id = wfp.scan(limit=5, threshold = -70, overlap=normi)
        print new, id
