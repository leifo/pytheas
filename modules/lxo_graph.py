# minimalistic graph class
# lxo, 18.04.2008

'''
must haves:
- nodes
- edges (undirected)

could haves:
- weights (maybe later)
'''

class graph:
    def __init__(self):
        self.nodes = {}
        self.edges = {}
        self.nodeedges = {} # extra index for fast access to neighbours
    def addNode(self, node):
        '''
        put node to internal mapping
        '''
        self.nodes[node] = 1
    def addEdge(self, node1, node2):
        # no loops
        if node1==node2:
            return
        # create nodes if not already present
        if not self.hasNode(node1):
            self.addNode(node1)
        if not self.hasNode(node2):
            self.addNode(node2)
        e = self.makeEdge(node1,node2)
        # add edge to dict
        self.edges[e]=1
        # add nodes to nodeedges
        if self.nodeedges.has_key(node1):
            self.nodeedges[node1].append(node2)
        else:
            self.nodeedges[node1]=[node2]
        if self.nodeedges.has_key(node2):
            self.nodeedges[node2].append(node1)
        else:
            self.nodeedges[node2]=[node1]
    def getNodes(self):
        return self.nodes.keys()
    def getEdges(self):
        return self.edges.keys()
    def getNodeEdges(self,node):
        res=[]
        for edge in self.edges.keys():
            if node in edge:
                res.append(edge)
        return res
    def getNodeNeighbours(self,node):
        res=[]
        if self.nodeedges.has_key(node):
            res = self.nodeedges[node]
        return res
    def hasNode(self,node):
        return self.nodes.has_key(node)
    def makeEdge(self,node1,node2):
        '''
        internal
        sort nodes to realize undirected graph
        '''
        if node1>node2:
            return (node2,node1)
        else:
            return (node1,node2)
    def hasEdge(self,node1,node2):
        e = self.makeEdge(node1,node2)
        return self.edges.has_key(e)
    def deflate(self):
        '''
        save state to dictionary
        '''
        ret = {}
        ret["nodes"]=self.nodes
        ret["edges"]=self.edges
        ret["nodeedges"]=self.nodeedges
        return ret
    def inflate(self, fromdict):
        '''
        load state from dictionary
        returns 1 on success, otherwise 0
        will not load partial data, so all 3 dicts must be present
        '''
        if fromdict.has_key("nodes"):
            if fromdict.has_key("edges"):
                if fromdict.has_key("nodeedges"):
                    self.nodeedges = fromdict["nodeedges"]
                    self.nodes = fromdict["nodes"]
                    self.edges = fromdict["edges"]
                return 1
            else:
                return 0
        else:
            return 0
if __name__ == "__main__":
    g = graph()
    print "adding 4 nodes"
    g.addNode(1)
    g.addNode(2)
    g.addNode(3)
    g.addNode(4)
    g.addNode(5)
    print "has 1: %s" % g.hasNode(1)
    print "has 2: %s" % g.hasNode(2)
    print "has 3: %s" % g.hasNode(3)
    print "has 4: %s" % g.hasNode(4)
    print "has 5: %s (unconnected)" % g.hasNode(5)
    print "adding some edges"
    g.addEdge(2,1)
    g.addEdge(2,2)  # not allowed
    g.addEdge(3,2)
    g.addEdge(4,3)
    print "has (1,2): %s" % g.hasEdge(1,2)
    print "has (2,3): %s" % g.hasEdge(2,3)
    print "has (3,4): %s" % g.hasEdge(3,4)
    print "has (2,1): %s  (undirected (1,2))" % g.hasEdge(2,1)
    print "has (2,2): %s (not allowed)" % g.hasEdge(2,2)
    print "has (4,1): %s (not defined)" % g.hasEdge(4,1)
    print
    print g.nodes
    print g.edges
    print
    print "getting nodes:"
    print g.getNodes(), len(g.getNodes())
    print "getting edges:"
    print g.getEdges(), len(g.getEdges())
    print
    print "getting edges for node 2"
    print g.getNodeEdges(2)
    print
    print "neighbours of node 1: %s" %(g.getNodeNeighbours(1))
    print "neighbours of node 2: %s" %(g.getNodeNeighbours(2))
    print "neighbours of node 3: %s" %(g.getNodeNeighbours(3))
    print "neighbours of node 4: %s" %(g.getNodeNeighbours(4))
    print "neighbours of node 5: %s" %(g.getNodeNeighbours(5))



