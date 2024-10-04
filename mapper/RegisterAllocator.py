from interference import *
from instruction import *
from ISA import *

#Allocate and assign registers for a mapping
class RegisterAllocator:

    interference_graphs = {}

    def __init__(self, dfg, pke, kernel, instructions, x, y, z):
        self.rf = {}
        self.DFG = dfg
        self.pke = pke
        self.kernel = kernel
        self.instructions = instructions
        #init the rf to 0 => all the register of that pe are free to use
        #TODO: this behaviour needs to be handled in a better way
        for i in range(0, x*y):
            if i not in self.rf:
                self.rf[i] = {}
            for j in range(0,z):
                if j not in self.rf[i]:
                    self.rf[i][j] = 0

    def __del__(self):
        self.DFG = None
        self.rf.clear()
        self.pke.clear()
        self.kernel.clear()
        self.instructions.clear()
        self.interference_graphs.clear()

    def addInterferenceGraphs(self, g):
        for i in g:
            if i not in self.interference_graphs:
                self.interference_graphs[i] = g[i]
            else:
                print("Interference graph already in structure for PE " + str(i))
    
    #Does graph coloring
    #TODO: improve the code and handle colouring failures
    def allocateRegisters(self):

        #For each interference graph find the chromatic number
        #TODO: Since the graphs are small we can implement a different algorithm
        #      maybe using a sat solver or an ILP solver
        for p in self.interference_graphs:
            peo = []
            g = self.interference_graphs[p]
            tmp_max = -1
            #this is just a temporary and ugly fix to the infinite loop that can happen
            max_i = 0
            max_v = None
            for interval in g.intervals:
                interval.weigth = 0

            intervals_g = g.intervals.copy()
            
            while (len(intervals_g) > 0 and max_i < 1000):
                max_i += 1
                for interval in intervals_g:
                    if interval.weigth >= tmp_max:
                        tmp_max = interval.weigth
                        max_v = interval
            
                #remove maxv from interval_g
                intervals_g = [x for x in intervals_g if x != max_v]
                peo.append(max_v)
                neighbors = max_v.neighbors
                for neigbour in neighbors:
                    neigbour.weigth = neigbour.weigth + 1
            
            colors_needed = 0
            for v in peo:
                colors_needed = max(colors_needed, len(v.neighbors) + 1)

            print("Colors needed: " + str(colors_needed))
            if colors_needed > g.rf_size:
                print("Number of registers needed: " + str(colors_needed + 1) + "\nAvailable: " + str(g.rf_size))
                exit(0)

            for v in peo:
                #if not already colored
                if v.color == -1:
                    colortable = {}
                    #to color with more colors increase the range
                    colors = [i for i in range(g.rf_size,-1,-1)]
                    
                    if len(v.neighbors) == 0:
                        v.color = int(colors[0])
                    
                    for neigbour in v.neighbors:
                        if neigbour.color not in colortable:
                            colortable[neigbour.color] = 0
                        colortable[neigbour.color] = 1
                    
                    for color in colors:
                        if color not in colortable:
                            v.color = color
                    
                    colors.clear()
                    colortable.clear()

            g.setOutputRegisters()

        #update rf
        for p in self.rf:
            if p in self.instructions:
                for inst in self.instructions[p]:
                    if inst.outreg != -1:
                        self.rf[p][inst.outreg] = 1

    def getInstruction(self, id):
        for p in self.instructions:
            for inst in self.instructions[p]:
                if inst.nodeid == id:
                    #print("found ", id, inst.nodeid, inst.LOp, inst.ROp)
                    return inst
        
        return None

    #TODO: Improve the code
    def assignRegisters(self, cols, rows):
        #assign registers to operands
        #Only handle the RCL,RCR,RCT,RCB and ROUT cases
        #To use the internal registers the interference graph must be colored
        for e in self.DFG.edges:
            #print(e.source.id, "--->" ,e.destination.id)
            source = self.getInstruction(e.source.id)
            destination = self.getInstruction(e.destination.id)
            #print(e.source.id, "--->" ,e.destination.id)
            #print("")
            if source == None:
                print("Cannot find instructions associate to " + str(e.source.id))
                exit(0)
            if destination == None:
                print("Cannot find instructions associate to " + str(e.destination.id))
                exit(0)

            ps = -1     #source pe
            pd = -1     #destination pe

            for t in self.kernel:
                for p in self.kernel[t]:
                    if self.kernel[t][p] == source.nodeid:
                        ps = p
                    elif self.kernel[t][p] == destination.nodeid:
                        pd = p

            if ps == -1 or pd == -1:
                print("Cannot find pe for nodes " + str(source.nodeid) + " - " + str(destination.nodeid))
                exit(0)

            #print(str(source.nodeid) + " -> " + str(destination.nodeid) + " pe_s: " + str(ps) + " pe_d: " + str(pd) + " " + str(destination.predicate))
            if ps != pd:
                i1 = ps // cols
                j1 = ps % cols

                i2 = pd // cols
                j2 = pd % cols
                #TODO: add if to check if operand already set
                #same row
                if i1 == i2:
                    #print("same row")
                    #is on the rigth
                    if ps == pd + 1:
                        #print("rigth1")
                        if destination.LOp == source.nodeid:
                            destination.opA = RCR
                        elif destination.ROp == source.nodeid:
                            destination.opB = RCR
                        elif destination.predicate == source.nodeid:
                            destination.muxflag = RCR
                        else:
                            print("Dep " + str(source.nodeid) + " -> " + str(destination.nodeid))
                            print("1) Error assignment for inst " + str(destination.nodeid) + " lOp: " + str(destination.LOp) + " rOp: " + str(destination.ROp))
                    #is on left
                    if ps == pd - 1:
                        #print("left1")
                        if destination.LOp == source.nodeid:
                            destination.opA = RCL
                        elif destination.ROp == source.nodeid:
                            destination.opB = RCL
                        elif destination.predicate == source.nodeid:
                            destination.muxflag = RCL
                        else:
                            print("Dep " + str(source.nodeid) + " -> " + str(destination.nodeid))
                            print("2) Error assignment for inst " + str(destination.nodeid) + " lOp: " + str(destination.LOp) + " rOp: " + str(destination.ROp) + " pred: " +str(destination.predicate))
                    
                    #is on the rigth (wrap around)
                    if (pd - ps) == cols - 1:
                        #print("rigth2")
                        if destination.LOp == source.nodeid:
                            destination.opA = RCR
                        elif destination.ROp == source.nodeid:
                            destination.opB = RCR
                        elif destination.predicate == source.nodeid:
                            destination.muxflag = RCR
                        else:
                            print("Dep " + str(source.nodeid) + " -> " + str(destination.nodeid))
                            print("3) Error assignment for inst " + str(destination.nodeid) + " lOp: " + str(destination.LOp) + " rOp: " + str(destination.ROp))

                    #is on the left (wrap around)
                    if (ps - pd) == cols - 1:
                        #print("left2")
                        if destination.LOp == source.nodeid:
                            destination.opA = RCL
                        elif destination.ROp == source.nodeid:
                            destination.opB = RCL
                        elif destination.predicate == source.nodeid:
                            destination.muxflag = RCL
                        else:
                            print("Dep " + str(source.nodeid) + " -> " + str(destination.nodeid))
                            print("4) Error assignment for inst " + str(destination.nodeid) + " lOp: " + str(destination.LOp) + " rOp: " + str(destination.ROp))
                
                #same col
                if (j1 == j2):
                    #print("same col")
                    #is down
                    if ps == pd + cols:
                        #print("down1")
                        if destination.LOp == source.nodeid:
                            destination.opA = RCB
                        elif destination.ROp == source.nodeid:
                            destination.opB = RCB
                        elif destination.predicate == source.nodeid:
                            destination.muxflag = RCB
                        else:
                            print("Dep " + str(source.nodeid) + " -> " + str(destination.nodeid))
                            print("5) Error assignment for inst " + str(destination.nodeid) + " lOp: " + str(destination.LOp) + " rOp: " + str(destination.ROp))
                    #is up
                    if ps == pd - cols:
                        #print("top1")
                        if destination.LOp == source.nodeid:
                            destination.opA = RCT
                        elif destination.ROp == source.nodeid:
                            destination.opB = RCT
                        elif destination.predicate == source.nodeid:
                            destination.muxflag = RCT
                        else:
                            print("Dep " + str(source.nodeid) + " -> " + str(destination.nodeid))
                            print("6) Error assignment for inst " + str(destination.nodeid) + " lOp: " + str(destination.LOp) + " rOp: " + str(destination.ROp))

                    #is top (wrap around)
                    if (i1 - i2) == rows - 1:
                        #print("top2")
                        if destination.LOp == source.nodeid:
                            destination.opA = RCT
                        elif destination.ROp == source.nodeid:
                            destination.opB = RCT
                        elif destination.predicate == source.nodeid:
                            destination.muxflag = RCT
                        else:
                            print("Dep " + str(source.nodeid) + " -> " + str(destination.nodeid))
                            print("7) Error assignment for inst " + str(destination.nodeid) + " lOp: " + str(destination.LOp) + " rOp: " + str(destination.ROp))

                    #is down (wrap around)
                    if (i2 - i1) == rows - 1:
                        #print("down2")
                        if destination.LOp == source.nodeid:
                            destination.opA = RCB
                        elif destination.ROp == source.nodeid:
                            destination.opB = RCB
                        elif destination.predicate == source.nodeid:
                            destination.muxflag = RCB
                        else:
                            print("Dep " + str(source.nodeid) + " -> " + str(destination.nodeid))
                            print("8) Error assignment for inst " + str(destination.nodeid) + " lOp: " + str(destination.LOp) + " rOp: " + str(destination.ROp))     
            elif ps == pd:
                #print("same pe")
                #assign outputreg to operands
                if source.outreg != -1 :
                    if destination.LOp == source.nodeid:
                        destination.opA = source.outreg
                    elif destination.ROp == source.nodeid:
                        destination.opB = source.outreg
                    elif destination.predicate == source.nodeid:
                        #should not be possible
                        destination.muxflag = source.outreg
                    else:
                        print("Dep " + str(source.nodeid) + " -> " + str(destination.nodeid))
                        print("9) Error assignment for inst " + str(destination.nodeid) + " lOp: " + str(destination.LOp) + " rOp: " + str(destination.ROp))
                else:
                    #print("outreg")
                    if destination.LOp == source.nodeid:
                        destination.opA = ROUT
                    elif destination.ROp == source.nodeid:
                        destination.opB = ROUT
                    elif destination.predicate == source.nodeid:
                        destination.muxflag = ROUT
                    else:
                        print("Dep " + str(source.nodeid) + " -> " + str(destination.nodeid))
                        print("9) Error assignment for inst " + str(destination.nodeid) + " lOp: " + str(destination.LOp) + " rOp: " + str(destination.ROp))
            # Handle if left and right operands have the same node
            # opA is set above so we only need to set opB
            if destination.ROp == destination.LOp:
                destination.opB = destination.opA

        # Assign immediate values
        for c in self.DFG.constants:
            inst = self.getInstruction(c.destination)
            if inst == None:
                print("Error Input File Format: All the constants must refer to a node in the DFG")
                print("destination: " + str(c.destination))
                exit(0)
            if c.id == inst.LOp:
                inst.opA = CONST
                inst.immediate = c.value
            if c.id == inst.ROp:
                inst.opB = CONST
                inst.immediate = c.value
            
            if inst.ROp == CONST and inst.LOp == CONST:
                print("Error: Const in both operands")
                print(inst.nodeid, inst.LOp, inst.ROp)
                exit(0)

            #if c.id == inst.LOp and c.opPos == 1:  
            #    if c.value == 0:              
            #        inst.opA = ZERO
            #        inst.immediate = c.value
            #    elif c.value == 1:
            #        inst.opA = "1"
            #    else:
            #        inst.opA = CONST
            #        inst.immediate = c.value                  
            #elif c.id == inst.ROp and c.opPos == 1:
            #    if c.value == 0:
            #        inst.opB = ZERO
            #        inst.immediate = c.value
            #    elif c.value == 1:
            #        inst.opB = "1"
            #        inst.immediate = c.value
            #    else:
            #        inst.opB = CONST
            #        inst.immediate = c.value
        
        #for c in self.DFG.constants:
        #    inst = self.getInstruction(c.destination)
        #    if inst == None:
        #        print("Should not happed... All the constants must refer to a node in the DFG")
        #        print("destination: " + str(c.destination))
        #        continue
        #
        #    if c.opPos == 0:
        #        if c.value == 0:              
        #            inst.opA = ZERO
        #            inst.immediate = c.value
        #        elif c.value == 1:
        #            inst.opA = "1"
        #        else:
        #            inst.opA = "Need reg"
            #else:
            #    if c.value == 0:              
            #        inst.opB = ZERO
            #        inst.immediate = c.value
            #    elif c.value == 1:
            #        inst.opB = ONE
            #    else:
            #        inst.opB = "Need reg"
        
    def getAvailableRegister(self, p):
        available_registers = []
        for r in self.rf[p]:
            if self.rf[p][r] == 0:
                available_registers.append(r)
        
        return available_registers

    #Generates all the interference graphs needed (one for each PE)
    def generateInterferenceGraphs(self, kernel, grid_size, DFG, instructions, n_colors):

        graphs = {}
        for i in range(0, grid_size):
            if i in instructions:
                if i not in graphs:
                    graphs[i] = None
                g = interference(i)
                g.rf_size = n_colors
                addNodes(instructions[i], g, kernel, DFG, i)
                #g.removeOverlappingIntervals()
                self.generateOverlaps(g)
                graphs[i] = g
                

        return graphs

    #Generate dependencies between the nodes of the interference graph
    #Each node is and interval. Two nodes are connected if the two intervals overlap
    def generateOverlaps(self, g):
        intervals = g.intervals
        overlapId = 0
        for i in range(0,len(g.intervals) - 1):
            for j in range(i + 1,len(g.intervals)):
                #wrap around first interval
                if intervals[i].start > intervals[i].end:
                    #wrap around second interval
                    if intervals[j].start > intervals[j].end:
                        #if they both wrap around then they overlap for sure
                        #since they must pass for the end kernel
                        tmp_ovlp = overlap(overlapId, intervals[i], intervals[j])
                        intervals[i].addNeighbour(intervals[j])
                        intervals[j].addNeighbour(intervals[i])
                        g.addOverlap(tmp_ovlp)
                        overlapId += 1
                    elif intervals[j].start <= intervals[i].end or intervals[j].start >= intervals[i].start or intervals[j].end >= intervals[i].start:
                        tmp_ovlp = overlap(overlapId, intervals[i], intervals[j])
                        intervals[i].addNeighbour(intervals[j])
                        intervals[j].addNeighbour(intervals[i])
                        g.addOverlap(tmp_ovlp)
                        overlapId += 1
                    else:
                        # no overlap
                        pass
                else:
                    #no wrap around first interval
                    #wrap around second interval
                    if intervals[j].start > intervals[j].end:
                        if intervals[j].start < intervals[i].start or intervals[j].start < intervals[i].end:
                            tmp_ovlp = overlap(overlapId, intervals[i], intervals[j])
                            intervals[i].addNeighbour(intervals[j])
                            intervals[j].addNeighbour(intervals[i])
                            g.addOverlap(tmp_ovlp)
                            overlapId += 1
                        elif intervals[i].start < intervals[j].end:
                            tmp_ovlp = overlap(overlapId, intervals[i], intervals[j])
                            intervals[i].addNeighbour(intervals[j])
                            intervals[j].addNeighbour(intervals[i])
                            g.addOverlap(tmp_ovlp)
                            overlapId += 1
                        else:
                            # no overlap
                            pass
                    else:
                        #no wrap around from both
                        if intervals[i].start < intervals[j].end and intervals[j].start < intervals[i].end:
                            tmp_ovlp = overlap(overlapId, intervals[i], intervals[j])
                            intervals[i].addNeighbour(intervals[j])
                            intervals[j].addNeighbour(intervals[i])
                            g.addOverlap(tmp_ovlp)
                            overlapId += 1
                        else:
                            # no overlap
                            pass

#Generate nodes for the interference graphs
#Each node is an interval that rapresents the liveness of a node
def addNodes(instructions, g, kernel, DFG, p):

    kernel_length = len(kernel) - 1
    #print(kernel)
    #print("Kernel length: " + str(kernel_length))
    interval_id = 0
    for e in DFG.edges:
        for s in instructions:
            if s.nodeid == e.source.id:
                for d in instructions:
                    if d.nodeid == e.destination.id:
                        if needRegister(kernel_length, p ,s.time, d.time, kernel):
                            length = 0
                            length = (d.time - s.time + kernel_length + 1) % (kernel_length + 1)
                            #prnt = str(s.id) + " -> " + str(d.id) + " t1: " + str(s.time) + " t2: " + str(d.time) + " len: " + str(length)
                            #print(prnt)
                            tmp_int = interval(interval_id, s.time, d.time, s, d, length)
                            #print("Interval for dep ", s.nodeid, d.nodeid)
                            g.addInterval(tmp_int)

                            interval_id += 1
                        else:
                            #print("no interval for dep ", s.nodeid, d.nodeid)
                            #assign register
                            if d.ROp == s.nodeid:
                                #
                                d.opB = ROUT
                            elif d.LOp == s.nodeid:
                                #
                                d.opA = ROUT
                            elif d.predicate == s.nodeid:
                                #
                                d.muxflag = ROUT
                            else:
                                print("Cannot set rout for node " + str(d.nodeid))
                                #exit(0)