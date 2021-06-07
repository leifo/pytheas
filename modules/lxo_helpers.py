# common helpers
# lxo 2006-2008

class dicthelpers:
    # returns dictionary from given file
    # return empty dict {} if file not found
    def loadDictionary(self,filename):
        dict = {}
        try:
            file=open(filename,"r")
            s = file.read()
            dict=eval(s)
            file.close()
        except:
            pass
        return dict
    # save given dictionary to given filename
    # fails silently in case of error
    def saveDictionary(self, dict, filename):
        try:
            file=open(filename,"w")
            file.write(repr(dict))
            file.close()
        except:
            pass

class listhelpers:
    '''
    # list tricks from http://bytes.com/forum/thread19083.html
    intersection = filter(lambda x: x in l1, l2)
    union = l1 + filter(lambda x: x not in l1, l2)
    difference = filter(lambda x: x not in l2, l1)
    '''
    def __init__(self):
        pass
    def intersection(self,l1,l2):
        return filter(lambda x: x in l1, l2)
    def union(self,l1,l2):
        return l1 + filter(lambda x: x not in l1, l2)
    def difference(self,l1,l2):
        filter(lambda x: x not in l2, l1)
'''
lh = listhelpers()
l1 = [1,2,3,4]
l2 = [2,3,4]
l3 = [3,4]
l4 = [4]
l5 = [5]
print lh.intersection(l1,l2)
print lh.intersection(l1,l3)
print lh.intersection(l1,l4)
print lh.intersection(l1,l5)
'''

class normalizer:
    '''
    normalize coordinates of given min and max into 0..1 range
    init with test = normalizer(100,200)
    print test.norm(150)
    should return 0.5
    lxo, october 2007
    '''
    min=max=range=0
    def __init__(self,min, max):
        if max<min:
            temp = max
            max = min
            min = temp
        self.min = min
        self.max = max
        self.range = max - min
        #print "got min: %f, max: %f (range: %f)" %(min,max,self.range)
    def norm(self,value):
        '''
        normalizes a value into 0..1
        results will be clamped, so never go beyond bounds of 0 and 1
        '''
        if value > self.max: return 1
        if value < self.min: return 0

        if self.range==0:
            return self.min
        else:
            return float(value - self.min)/self.range


class superCongruent:
    '''
    1:1 conversion from superCongruent.cpp/.h
    lxo, 30.07.2007
    // lxo, 31.5.2005
    // allows conversion between two congruent 2d coordinate systems

    // this class is currently in use with A being British OSGB coordinates
    // and B being normalized texture coordinates (0..1/0..1)
    '''

    m_newAPoints= m_newBPoints= False
    x1_A= y1_A= x2_A= y2_A=0.0
    x1_B= y1_B= x2_B= y2_B=0.0
    deltaX_A= deltaY_A=0.0
    deltaX_B= deltaY_B=0.0
    factorLeft= factorRight= factorUp= factorDown=0.0

    width_A= height_A=0.0
    inverseWidth_A= inverseHeight_A=0.0
    originX_A= originY_A=0.0
    A_11X=A_11Y=0.0

    m_systemReady=False;

    def __init(self):
        self.m_systemReady=False
        self.m_newBPoints=False
        self.m_newAPoints=False

    def setReferencePointsA(self, x1, y1, x2, y2,debug=False):
        self.x1_A = x1
        self.x2_A = x2
        self.y1_A = y1
        self.y2_A = y2

        if debug:
            print "setReferencePointsA:"
            print x1,y1,x2,y2

        self.m_newAPoints = True
        self.recalcRelations()

    def getReferencePointsA(self):
        return (self.x1_A, self.x2_A,self.y1_A,self.y2_A)

    def getReferencePointsB(self):
        return (self.x1_B, self.x2_B,self.y1_B,self.y2_B)

    def setReferencePointsB(self, x1, y1, x2, y2,debug=False):
        self.x1_B = x1
        self.x2_B = x2
        self.y1_B = y1
        self.y2_B = y2

        if debug:
            print "setReferencePointsB:"
            print x1,y1,x2,y2

        self.m_newBPoints = True
        self.recalcRelations()

    def getSystemReady(self):
        return self.m_systemReady

    def recalcRelations(self,debug=False):
        # only calc when reference points have been set
        if (self.m_newAPoints) & (self.m_newBPoints):
            # deltas
            #print "reference points have been set!"
            self.deltaX_B = self.x2_B - self.x1_B
            self.deltaY_B = self.y2_B - self.y1_B
            self.deltaX_A = self.x2_A - self.x1_A
            self.deltaY_A = self.y2_A - self.y1_A
            if debug:
                print "deltas:"
                print self.deltaX_B,self.deltaY_B,self.deltaX_A,self.deltaY_A

            # create relations to origin and 11 (read "one one") from B coordinates
            if debug: print self.deltaX_B,  self.x1_B
            self.factorLeft = self.deltaX_B / self.x1_B
            self.factorRight = self.deltaX_B / (1-self.x2_B)
            self.factorDown = self.deltaY_B / self.y1_B
            self.factorUp = self.deltaY_B / (1-self.y2_B)

            # apply relations to calculate unknown A origin and 11 coordinates in B space
            # origin
            lx = self.deltaX_A / self.factorLeft
            self.originX_A = self.x1_A - lx

            rx = self.deltaX_A / self.factorRight
            self.A_11X = self.x2_A + rx

            dy = self.deltaY_A / self.factorDown
            self.originY_A = self.y1_A - dy

            uy = self.deltaY_A / self.factorUp
            self.A_11Y = self.y2_A + uy

            # width and height of space in A-coordinates
            self.width_A = self.A_11X - self.originX_A
            self.height_A = self.A_11Y - self.originY_A

            # calculate inverses to speed up convertA2B routines
            self.inverseWidth_A = 1.0 / self.width_A
            self.inverseHeight_A = 1.0 / self.height_A

            self.m_systemReady = True

    def convertA2B_X(self,xB):
        # return error when not yet initialized
        if not self.m_systemReady:
            return -1

        # substract origin from coordinate
        lessOrigin = xB - self.originX_A

        # scale by width and return
        #print xB, lessOrigin * self.inverseWidth_A
        return lessOrigin * self.inverseWidth_A

    def convertA2B_Y(self,yB):
        # return error when not yet initialized
        if not self.m_systemReady:
            return -1

        # substract origin from coordinate
        lessOrigin = yB - self.originY_A

        # scale by width and return
        #print yB, lessOrigin * self.inverseHeight_A
        return lessOrigin * self.inverseHeight_A

    def clippedA(self,xA, yA):
        # check x for clipping
        if (xA>self.x2_A) | (xA<self.x1_A):
            print "clippedA:x (%f>%f) | (%f<%f)" %(xA,self.x2_A,xA,self.x1_A)
            return True

        # check y for clipping
        if (yA>self.y2_A) | (yA<self.y1_A):
            print "clippedA:y (%f>%f) | (%f<%f)" %(yA,self.y2_A,yA,self.y1_A)
            return True

        # no clipping. draw it!
        return False

    def clippedB(self,xB, yB):
        # check x for clipping
        if (xB>self.x2_B) | (xB<self.x1_B):
            print "clippedB:x (%f>%f) | (%f<%f)" %(xB,self.x2_B,xB,self.x1_B)
            return True

        # check y for clipping
        if (yB>self.y2_B) | (yB<self.y1_B):
            print "clippedB:y (%f>%f) | (%f<%f)" %(yB,self.y2_B,yB,self.y1_B)
            return True

        # no clipping. draw it!
        return False

'''
        #all data needs to get normalised into this
        cc = superCongruent()

        cc.setReferencePointsA(lon1,lat1,lon2,lat2)

        cc.setReferencePointsB(1,1,0,0)
        if not cc.getSystemReady():
            print "***ERROR: Could not init coordinate converter"
            sys.exit()

##        print "lower left:"
##        print cc.convertA2B_X(-0.210950), cc.convertA2B_Y(50.829006)
##        print "upper right:"
##        print cc.convertA2B_X(-0.207989), cc.convertA2B_Y(50.830811)

        x = cc.convertA2B_X(lon)
        y = cc.convertA2B_Y(lat)

'''