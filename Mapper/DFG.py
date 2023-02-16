#node of the DFG
class node:
    def __init__(self, id, rOp, lOp, predicate, name, opcode):
        self.id = id
        self.rOp = rOp
        self.lOp = lOp
        self.name = name
        self.predicate = predicate
        self.opcode = opcode
        self.index = -1
        self.lowlink = 0
        self.onstack = False
        self.time = 1
        self.latency = 1
    def __del__(self):
        self.index = -1
        self.lowlink = 0
        self.onstack = False
        self.time = 1
        self.latency = 1
#edge of the DFG
class edge:
    def __init__(self, source, destination, distance, latency):
        self.source = source
        self.destination = destination
        self.distance = distance
        self.latency = latency
#constant node associate to the DFG
class constant:
    def __init__(self, id, destination, value, opPos):
        self.id = id
        self.destination = destination
        self.value = value
        self.opPos = opPos

#data flow graph of the loop, with information on livein, liveout and constants
#constants, livein, liveout could be handled better
class DFG:
    
    nodes = []
    edges = []
    index = 0
    stack = []
    livein_nodes = []
    liveout_nodes = []
    livein_edges = []
    liveout_edges = []

    constants = []

    def __init__(self):
        pass

    def __del__(self):
        self.nodes.clear()
        self.edges.clear()
        self.constants.clear()
        self.stack.clear()
        self.livein_nodes.clear()
        self.liveout_nodes.clear()
        self.livein_edges.clear()
        self.liveout_edges.clear()
        self.index = 0

    def addNode(self, n):
        self.nodes.append(n)

    def addLiveInNode(self, n):
        self.livein_nodes.append(n)
    
    def addLiveOutNode(self, n):
        self.liveout_nodes.append(n)

    def addConstant(self, n):
        self.constants.append(n)

    def addEdge(self, n):
        self.edges.append(n)
    
    def addLiveInEdge(self, n):
        self.livein_edges.append(n)
    
    def addLiveOutEdge(self, n):
        self.liveout_edges.append(n)

    def getEdge(self, source, destination):
        for e in self.edges:
            if e.source == source and e.destination == destination:
                return e
        return None

    def resetTime(self):
        for n in self.nodes:
            n.time = 0

    def resetLatency(self):
        for n in self.nodes:
            n.latency = 1

    def getSuccessors(self, n):
        succ = []
        for e in self.edges:
            if e.source.id == n.id:
                succ.append(e.destination)
        return succ

    def getPredecessors(self, n):
        preds = []
        for e in self.edges:
            if e.destination.id == n.id:
                preds.append(e.source)
        return preds

    #return nodes that have no predecessor (phi nodes usually)
    def getStartingNodes(self):
        starting_nodes = set()
        for n in self.nodes:
            if len(self.getPredecessors(n)) == 0 or n.name == "phi":
                starting_nodes.add(n)

        return starting_nodes

    #return nodes that have no successor or node whose only successor is a phi node
    def getEndingNodes(self):
        ending_nodes = set()
        
        for n in self.nodes:
            if len(self.getSuccessors(n)) == 0:
                ending_nodes.add(n)

            allphi = True
            for suc in self.getSuccessors(n):
                if suc.name != "phi":
                    allphi = False
            
            if allphi == True:
                ending_nodes.add(n)

        return ending_nodes

    #Get Strongly Connected Components in the DFG
    def getSCCs(self):

        sccs = []
        for n in self.nodes:
            if n.index == -1:
                self.strongConnect(n, sccs)
        
        return sccs
    
    #Utility function used by getSCCs
    def strongConnect(self, n, sccs):
        n.index = self.index
        n.lowlink = self.index
        self.index += 1
        self.stack.append(n)
        n.onstack = True

        for succ in self.getSuccessors(n):
            if succ.index == -1:
                self.strongConnect(succ, sccs)
                n.lowlink = min(n.lowlink, succ.lowlink)
            elif succ.onstack == True:
                n.lowlink = min(n.lowlink, succ.index)
        tmp_sccs = []

        if n.lowlink == n.index:
            while len(self.stack) != 0:
                w = self.stack.pop()
                tmp_sccs.append(w)
                w.onstack = False

                if n.id == w.id:
                    break
        
            if len(tmp_sccs) > 1:
                sccs.append(tmp_sccs[:])

    #Utility function used by getSCCs
    def getPathDelay(self, scc):

        #roots should be only phi nodes
        roots = set()

        for n in scc:
            #print(n.id)
            r = None    
            for e in self.edges:
                if e.distance > 0 and n.id == e.destination.id:
                    r = n

            if r == None:
                continue
        
            to_explore = []
            visited = []
            curr = []
            delay = 0 
        
            
            visited.append(r)
            to_explore.append(r)
            explored = 1
            while explored > 0:
                explored = 0
                #print("exploring")
                for n in to_explore:
                    #print(n.id)
                    for succ in self.getSuccessors(n):
                        if succ.name == "phi":
                            continue
                        if succ in scc:
                            #print("scc")
                            #print(succ.id)
                            if succ.latency <= n.latency:
                                succ.latency = n.latency + 1
                            
                            delay = max(delay, succ.latency)
                            
                            if succ not in visited:
                                curr.append(succ)
                                visited.append(succ)
                            explored += 1
                
                to_explore = curr[:]#create shadow copy
                curr.clear()
        
        return delay

    def getNode(self, id):
        for n in self.nodes:
            if n.id == id:
                return n
        return None

    def getLiveInNode(self, id):
        for n in self.livein_nodes:
            if n.id == id:
                return n
        return None
    
    def getLiveOutNode(self, id):
        for n in self.liveout_nodes:
            if n.id == id:
                return n
        return None

    def resetNodeTime(self, t):
        for n in self.nodes:
            n.time = t

    def getConstant(self, dest_id):
        for c in self.constants:
            if dest_id == c.destination:
                return c
        
        return None

    def getAssociateLiveIn(self, id):
        for le in self.livein_edges:
            if le.destination.id == id:
                return le.source
        return None

    def getAssociateLiveOut(self, id):
        for le in self.liveout_edges:
            if le.source.id == id:
                return le.destination
        return None
