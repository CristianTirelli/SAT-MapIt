#node of the DFG
from ISA import LWD, SWD

class node:
    def __init__(self, id: int):
        self.id = id

class constant_node(node):
    def __init__(self, id: int, immediate: int, immediate_position: int):
        super().__init__(id)
        self.immediate = immediate
        self.immediate_position = immediate_position

    def set_immediate(self, new_im: int):
        self.immediate = new_im

    def set_immediate_position(self, new_im_pos: int):
        self.immediate_position = new_im_pos

class live_node(node):
    def __init__(self, id: int, opcode: int):
        super().__init__(id)
        self.opcode = opcode
        self.name = ""

    def set_name(self, name):
        self.name = name

class livein_node(live_node):
    def __init__(self, id: int):
        super().__init__(id, LWD)

class liveout_node(live_node):
    def __init__(self, id: int):
        super().__init__(id, SWD)

class instruction_node(node):
    def __init__(self, id: int, name: str, opcode: int = -1, lOp_id: int = -1, rOp_id: int = -1, predicate_id: int = -1):
        super().__init__(id)
        self.name = name
        self.opcode = opcode
        self.lOp_id = lOp_id
        self.rOp_id = rOp_id
        self.predicate_id = predicate_id

        # Those will be populated by DFG.fix_references
        self.lOp: node = None
        self.rOp: node = None
        self.predicate: node = None

        self.index = -1
        self.lowlink = 0
        self.onstack = False
        self.time = 1
        self.latency = 1

    def set_lOp(self, lOp):
        self.lOp = lOp

    def set_rOp(self, rOp):
        self.rOp = rOp

#edge of the DFG
class edge:
    def __init__(self, source: node, destination: node, distance: int, latency: int):
        self.source = source
        self.destination = destination
        self.distance = distance
        self.latency = latency

#data flow graph of the loop, with information on livein, liveout and constants
#constants, livein, liveout could be handled better
class DFG:
    def __init__(self):
        self.nodes: list[node] = []
        self.edges: list[edge] = []
        self.index = 0
        self.stack = []

    def addNode(self, n: node):
        self.nodes.append(n)

    def addEdge(self, n: edge):
        self.edges.append(n)
    
    def getEdge(self, source: node, destination: node):
        for e in self.edges:
            if e.source == source and e.destination == destination:
                return e
        return None

    def get_instruction_nodes(self) -> list[instruction_node]:
        return [node for node in self.nodes if isinstance(node, instruction_node)]

    def get_instruction_edges(self) -> list[edge]:
        return [edge for edge in self.edges if isinstance(edge.source, instruction_node) and isinstance(edge.destination, instruction_node)]

    def resetTime(self):
        for n in self.get_instruction_nodes():
            n.time = 0

    def resetLatency(self):
        for n in self.get_instruction_nodes():
            n.latency = 1

    def getSuccessors(self, n: instruction_node) -> list[instruction_node]:
        succ = []
        for e in self.get_instruction_edges():
            if e.source.id == n.id:
                succ.append(e.destination)
        return succ

    def getPredecessors(self, n: instruction_node) -> list[instruction_node]:
        preds = []
        for e in self.get_instruction_edges():
            if e.destination.id == n.id:
                preds.append(e.source)
        return preds

    #return nodes that have no predecessor (phi nodes usually)
    def getStartingNodes(self) -> set[instruction_node]:
        starting_nodes = set()
        for n in self.get_instruction_nodes():
            if len(self.getPredecessors(n)) == 0 or n.name == "phi":
                starting_nodes.add(n)

        return starting_nodes

    #return nodes that have no successor or node whose only successor is a phi node
    def getEndingNodes(self) -> set[instruction_node]:
        ending_nodes = set()
        
        for n in self.get_instruction_nodes():
            if len(self.getSuccessors(n)) == 0:
                ending_nodes.add(n)

            allphi = True
            for suc in self.getSuccessors(n):
                if suc.name != "phi":
                    allphi = False
            
            if allphi:
                ending_nodes.add(n)

        return ending_nodes

    #Get Strongly Connected Components in the DFG
    def getSCCs(self) -> list[instruction_node]:

        sccs = []
        for n in self.get_instruction_nodes():
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
        for n in scc:
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
                for n in to_explore:
                    for succ in self.getSuccessors(n):
                        if succ.name == "phi":
                            continue
                        if succ in scc:
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
        raise ValueError(f"Node with id '{id}' is not in the DFG")

    def getLiveInNode(self, id):
        for n in self.nodes:
            if n.id == id:
                return n
        raise ValueError(f"Live In Node with id '{id}' is not in the DFG")
    
    def getLiveOutNode(self, id):
        for n in self.nodes:
            if n.id == id:
                return n
        raise ValueError(f"Live Out Node with id '{id}' is not in the DFG")

    def resetNodeTime(self, t):
        for n in self.get_instruction_nodes():
            n.time = t

    def getConstant(self, dest_id):
        for e in self.edges:
            if isinstance(e.source, constant_node) and e.destination.id == dest_id:
                return e.source
        raise ValueError(f"There was no constant associated to node with id '{dest_id}'")

    def getAssociateLiveIn(self, id):
        for e in self.edges:
            if e.destination.id == id:
                return e.source
        raise ValueError(f"There was no live in node associated to node with id '{id}'")
        

    def getAssociateLiveOut(self, id):
        for le in self.edges:
            if le.source.id == id:
                return le.destination
        raise ValueError(f"There was no live out node associated to node with id '{id}'")

    def fix_references(self):
        for n in self.get_instruction_nodes():
            if n.lOp_id != -1:
                n.set_lOp(self.getNode(n.lOp_id))
            if n.rOp_id != -1:
                n.set_rOp(self.getNode(n.rOp_id))
            if n.predicate_id != -1:
                n.predicate = self.getNode(n.predicate_id)
