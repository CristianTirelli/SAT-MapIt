from DFG import *

#parser for all the input file that generates the DFG

class Parser:
    nodes = []
    edges = []
    livein_nodes = []
    liveout_nodes = []
    livein_edges = []
    liveout_edges = []
    constants = []

    def __init__(self):
        self.dfg = DFG()
    
    def __del__(self):
        self.nodes.clear()
        self.edges.clear()
        self.livein_nodes.clear()
        self.liveout_nodes.clear()
        self.livein_edges.clear()
        self.liveout_edges.clear()
        self.constants.clear()
        self.dfg = None
    
    def parseNodeFile(self, nodefile):
        with open(nodefile,"r") as fd: 
            for l in fd.read().splitlines():
                tmp_n = [x for x in l.split(' ')]
                if tmp_n[1] == "instruction":
                    node = [tmp_n[0]] + [tmp_n[2]] + [tmp_n[4]] + [tmp_n[5]] + [tmp_n[6]] + [tmp_n[3]]
                    self.nodes.append(node)   
                elif tmp_n[1] == "constant":
                    node = [tmp_n[0]] + [tmp_n[7]] + [tmp_n[8]]
                    # second position updated during edge parsing
                    self.constants.append(node)
                elif tmp_n[1] == "live_in":
                    node = [tmp_n[0]]
                    self.livein_nodes.append(node)   
                elif tmp_n[1] == "live_out":
                    node = [tmp_n[0]]
                    self.liveout_nodes.append(node) 
                else:
                    print("none")


    
    def parseEdgeFile(self, edgefile):
        with open(edgefile,"r") as fd: 
            for l in fd.read().splitlines():
                tmp_e = [x for x in l.split(' ')]
                #print(self.nodes)
                if tmp_e[0] in [x[0] for x in self.nodes] and tmp_e[1] in [x[0] for x in self.nodes]:
                    self.edges.append([x for x in l.split(' ')])
                elif tmp_e[0] in [x[0] for x in self.constants]:
                    #update constant
                    for i in range(len(self.constants)):
                        if self.constants[i][0] == tmp_e[0]:
                            self.constants[i] = [self.constants[i][0]] + [tmp_e[1]] + self.constants[i][1:]
                elif tmp_e[0] in [x[0] for x in self.livein_nodes]:
                    self.livein_edges.append([x for x in l.split(' ')])
                elif tmp_e[0] in [x[0] for x in self.nodes] and tmp_e[1] in [x[0] for x in self.liveout_nodes]: 
                    self.liveout_edges.append([x for x in l.split(' ')])
                    


    def parseConstantsFile(self, constfile):
        with open(constfile,"r") as fd: 
            for l in fd.read().splitlines():
                self.constants.append([x for x in l.split(' ')])
                #print(self.constants)
    
    def getDFG(self):
        #generate DFG nodes
        for n in self.nodes:
            id = int(n[0])
            #print("Id: " + str(id))
            rOp = int(n[3])
            lOp = int(n[2])
            predicate = int(n[4])
            name = n[1]
            opcode = int(n[5])
            #print(name, rOp, lOp)
            
            tmp = node(id, rOp, lOp, predicate, name, opcode) 
            self.dfg.addNode(tmp)
        

        for n in self.livein_nodes:
            id = int(n[0])
            rOp = -1
            lOp = -1
            predicate = -1
            name = "livein"
            opcode = -1

            tmp = node(id, rOp, lOp, predicate, name, opcode) 
            self.dfg.addLiveInNode(tmp)
        
        for n in self.liveout_nodes:
            id = int(n[0])
            rOp = -1
            lOp = -1
            predicate = -1
            name = "liveout"
            opcode = -1

            tmp = node(id, rOp, lOp, predicate, name, opcode) 
            self.dfg.addLiveOutNode(tmp)

        for n in self.constants:
            id = int(n[0])
            destination = int(n[1])
            value = int(n[2])
            opPos = int(n[3])

            tmp = constant(id, destination, value, opPos) 
            self.dfg.addConstant(tmp)

        #generate DFG edges
        for e in self.edges:
            source = self.dfg.getNode(int(e[0]))
            destination = self.dfg.getNode(int(e[1]))
            if source == None or destination == None:
                if source == None:
                    print("Source")
                if destination == None:
                    print("Destination")
                print("Error parsing dep " + e[0] + " -> " + e[1])
                exit(0)
            distance = int(e[2])
            latency = int(e[3])

            tmp = edge(source, destination, distance, latency)
            self.dfg.addEdge(tmp)

        for e in self.livein_edges:
            source = self.dfg.getLiveInNode(int(e[0]))
            destination = self.dfg.getNode(int(e[1]))
            if source == None or destination == None:
                if source == None:
                    print("Source")
                if destination == None:
                    print("Destination")
                print("Error parsing dep " + e[0] + " -> " + e[1])
                exit(0)
            distance = int(e[2])
            latency = int(e[3])

            tmp = edge(source, destination, distance, latency)
            self.dfg.addLiveInEdge(tmp)
        
        for e in self.liveout_edges:
            source = self.dfg.getNode(int(e[0]))
            destination = self.dfg.getLiveOutNode(int(e[1]))
            if source == None or destination == None:
                if source == None:
                    print("Source")
                if destination == None:
                    print("Destination")
                print("Error parsing dep " + e[0] + " -> " + e[1])
                exit(0)
            distance = int(e[2])
            latency = int(e[3])

            tmp = edge(source, destination, distance, latency)
            self.dfg.addLiveOutEdge(tmp)

        return self.dfg








