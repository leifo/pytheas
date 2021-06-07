# for quick signatures (oidmapper puts the speed into the wifi fingerprinter)
# lxo, 15.04.2008

class oidmapper:
    '''
    object to id (and back) mapper class
    can be used to accelerate object based functions by using integers instead
    lxo, 15.04.2008
    '''
    def __init__(self):
        self.objecttable = {}
        self.idtable = {}
        self.nextid = 1
    def deflate(self):
        '''
        save state to dictionary
        '''
        ret = {}
        ret["objecttable"]=self.objecttable
        ret["idtable"]=self.idtable
        return ret
    def getHighestIntegerKey(self):
        '''
        find the highest integer id in the idtable dict
        returns either that integer value or None
        '''
        l = self.idtable.keys()
        l.sort()
        ll=len(l)
##        print "lenght of dict: %d" %ll
        if ll>0:
            #id = l[ll-1]+1  # this might try to concatenate strings and ints which doesn't work
            testint=1  #create an integer instance
            #test.__class__
            # go backwards through sorted list of keys and look for integer
            # (the first match IS NOT guaranteed to be the highest int in a mixed list, so step through all)
            highestint=0
            for i in range (ll-1, 0,-1):
                if l[i].__class__==testint.__class__:
                    # success, we have found the highest integer
                    thisint = l[i]
                    #print thisint, highestint
                    if thisint > highestint:
                        highestint = thisint
##            print "highestint: %d" % highestint
            return highestint
        else:
            return None
    def inflate(self, fromdict):
        '''
        load state from dictionary
        returns 1 on success, otherwise 0
        will not load partial data, so idtable and objecttable must be present
        '''
        if fromdict.has_key("objecttable"):
            if fromdict.has_key("idtable"):
                self.objecttable = fromdict["objecttable"]
                self.idtable = fromdict["idtable"]
                # find the highest integer id in the dict and set self.nextid accordingly (+1)
                highestint = self.getHighestIntegerKey()
                # the next id asked for by getId will be highestint + 1
                if highestint!=None:
                    self.nextid = highestint+1
                else:
                    self.nextid = 1
##                keys = d["graph"]["nodes"].keys()
##                highestkey = 1
##                for key in keys:
##                    if str(key).isdigit():
##                        print int(key)
##                    else:
##                        print "not: %s" % key
                return 1
            else:
                return 0
        else:
            return 0
    def getID(self,o):
        '''
        get ID for object o (generate one if it doesn't exist)
        '''
        ohash = repr(o)
        if self.objecttable.has_key(ohash):
            # get id
            return self.objecttable[ohash]
        else:
            # generate id
            if 0:
                pass
##                # works great on int only, but doesn't work with string ids as from equip2 waf
##                l = self.idtable.keys()
##                l.sort()
##                ll=len(l)
##                if ll>0:
##                    #id = l[ll-1]+1  # this might try to concatenate strings and ints which doesn't work
##                    test=1  #create an integer instance
##                    #test.__class__
##                    # go backwards through sorted list of keys and look for integer
##                    # (the first match will be the highest int in the list)
##                    for i in range (ll-1, 0,-1):
##                        if l[i].__class__==test.__class__:
##                            # success, we have found the highest integer
##                            newid = l[i]+1
##                        else:
##                            if i==1:
##                                newid=1
##
##                else:
##                    id = 1
            else:
                id = self.nextid
                self.nextid += 1
            # put object to table
            self.objecttable[ohash]=id
            self.idtable[id]=ohash
            # return id
            return id
    def setObjectAndID(self,o,id):
        '''
        set object and id. to be used if an already known id must be used.
        '''
        ohash = repr(o)
        # put object to table
        self.objecttable[ohash]=id
        self.idtable[id]=ohash
        # return id
        return id

    def getObject(self,id):
        '''
        get object for that ID, or None if that ID is not in use
        '''
        if self.idtable.has_key(id):
            return eval(self.idtable[id])
        else:
            return None

if __name__ == "__main__":
    from lxo_helpers import dicthelpers
    dh = dicthelpers()
    #d = dh.loadDictionary("fp+graph_waf.dict")
    d = dh.loadDictionary("fp+graph_waf_broken.dict")
    #print d.keys()
    #print d["wififingerprinter"]
    oid = oidmapper()
    d2 = d["wififingerprinter"]
    print d2
    oid.inflate(d2)
    print oid.getHighestIntegerKey()
##    highestkey = 1
##    for key in keys:
##        if str(key).isdigit():
##            print int(key)
##        else:
##            print "not: %s" % key

'''
oid = oidmapper()
l1 = [1,2,3,4]
l2 = [2,3,4]
l3 = [3,4]
l4 = [4]
l5 = [5]

print oid.getID(l1)
print oid.getID(l2)
print oid.getID(l3)
print oid.getID(l4)
print oid.idtable
print oid.objecttable

'''

## sidmapper is presumably slightly faster than oidmapper when applied to strings only.
## but oidmapper is more general (can be applied to anything that goes into repr() and eval() )
## and has inflate/deflate support by now. therefore sidmapper is deprecated.

##class sidmapper:
##    '''
##    string to id (and back) mapper class
##    can be used to accelerate string based functions by using integers instead
##    lxo, 15.04.2008
##    '''
##    def __init__(self):
##        self.stringtable = {}
##        self.idtable = {}
##
##    def getStringID(self,s):
##        '''
##        get ID for that string
##        '''
##        if self.stringtable.has_key(s):
##            return self.stringtable[s]
##        else:
##            # get id
##            l = self.idtable.keys()
##            l.sort()
##            if len(l)>0:
##                id = l[len(l)-1]+1
##            else:
##                id = 1
##            # put to table
##            self.stringtable[s]=id
##            self.idtable[id]=s
##            # return id
##            return id
##
##    def getString(self,id):
##        '''
##        get string for that ID, or None if that ID is not in use
##        '''
##        if self.idtable.has_key(id):
##            return self.idtable[id]
##        else:
##            return None
'''
m = sidmapper()
print m.getStringID("a")
print m.getStringID("b")
print m.getStringID("c")
print m.getStringID("d")

print m.getStringID("d")
print m.getStringID("b")
print m.getStringID("c")
print m.getStringID("a")
print m.stringtable
print m.idtable

print m.getString(1)
print m.getString(2)
print m.getString(3)
print m.getString(4)

'''