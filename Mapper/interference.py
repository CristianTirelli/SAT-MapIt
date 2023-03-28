#this is a class similar to node, but with more information 
class instruction:

    def __init__(self,id):
        self.id = id
        self.name = ""

        self.outreg = -1
        self.time = -1
        self.pe = -1

        self.LOp = -1
        self.ROp = -1
        self.predicate = -1



        self.opA = -1
        self.opB = -1
        self.muxflag = -1
        self.immediate = 0
        self.opcode = -1
        self.cycle_destinaton = -1

    def printAssembly(self):
        output = ""
        BRs = ["BEQ","BNE","BLT","BGE","BLE","BGT"]
        NB = ["RCT", "RCL", "RCR", "RCB", "ROUT"]
    
        if self.getOpcodeName() == "MV":
            output += "ADD "
            if self.outreg == -1:
                output += "ROUT"
            else:
                output += "R" + str(self.outreg)
            if self.opA in NB:
                output += ", " + self.opA
            elif self.opA == "ZERO":
                if self.opB in NB:
                    output += ", " + self.opB
                else:
                    output += ", R" + str(self.opB)
                    
            elif self.opA == -1:
                output += ", ROUT"
            elif self.opA > -1 or self.opA < 4:#TODO: should be < n_register
                output += ", R" + str(self.opA)
            else:
                print("Handle this case (MV operands)", self.opA)
                exit(0)

            output += ", ZERO"
            #if self.opB == "CONST":
            #    output += ", " + str(self.immediate)
            #else:
            #    output += ", " + str(self.opB)

        elif self.getOpcodeName() == "LWI":
            output += "LWI "
            if self.outreg == -1:
                output += "ROUT"
            else:
                output += "R" + str(self.outreg)
            
            if self.opA == "CONST":
                output += ", " + str(self.immediate)
            else:
                if self.opA == -1:
                    output += ", ROUT"
                else:
                    if self.opA in NB:
                        output += ", " + str(self.opA)
                    #TODO: 4 is number of register in a pe. should put a var there not a constant
        
                    else:
                        print(self.opA)
                        print("Handle this case")
                        exit(0)
                #output += ", " + self.opA
        elif self.getOpcodeName() == "LWD":
            output += "LWD "
            if self.outreg == -1:
                output += "ROUT"
            else:
                output += "R" + str(self.outreg)
        elif self.getOpcodeName() == "SWI":
            output += "SWI "
            if self.outreg == -1:
                output += "ROUT"
            else:
                output += "R" + str(self.outreg)
            
            if self.opA == "CONST":
                output += ", " + str(self.immediate)
            else:
                if self.opA == -1:
                    output += ", ROUT"
                else:
                    if self.opA in NB:
                        output += ", " + str(self.opA)
                    #TODO: 4 is number of register in a pe. should put a var there not a constant
                    elif self.opA > -1 or self.opA < 4:
                        output += ", R" + str(self.opA)
                    else:
                        print(self.opA)
                        print("Handle this case")
                        exit(0)
                        
                    #output += ", R" + str(self.opA)
                #output += ", " + self.opA
        elif self.getOpcodeName() == "SWD":
            output += "SWD "
            if self.outreg == -1:
                output += "ROUT"
            else:
                output += "R" + str(self.outreg)  
        elif self.getOpcodeName() == "BSFA" or self.getOpcodeName() == "BZFA":
            output += self.getOpcodeName()
            output += " "
            if self.outreg == -1:
                output += "ROUT"
            else:
                output += "R" + str(self.outreg)  
            output += ", " + self.opA + ", " + self.opB + ", " + self.muxflag
        elif self.getOpcodeName() in BRs:
            output += self.getOpcodeName() + " "
            output += self.opA
            if self.opB == "CONST":
                print("BR opcode can only have one immediate and it's the br destination.\nStore the constant in a register.")
                #exit(0)
            output += ", " + self.opB
            output += ", " + str(self.cycle_destinaton)
        elif self.getOpcodeName() == "NOP":
            output = "NOP"
        else:
            output += self.getOpcodeName() + " "
            if self.outreg == -1:
                output += "ROUT"
            else:
                output += "R" + str(self.outreg)
            
            if self.opA == "CONST":
                output += ", " + str(self.immediate)
            else:
                output += ", " + str(self.opA)
            
            if self.opB == "CONST":
                output += ", " + str(self.immediate)
            else:
                output += ", " + str(self.opB)

        return output
    
    def getOpcodeName(self):

        if self.opcode == 0:
            return "EXIT"
        if self.opcode == 1:
            return "SADD"
        if self.opcode == 2:
            return "SSUB"
        if self.opcode == 3:
            return "SMUL"
        if self.opcode == 4:
            return "SDIV"
        if self.opcode == 5:
            return "UADD"
        if self.opcode == 6:
            return "USUB"
        if self.opcode == 7:
            return "UMUL"
        if self.opcode == 8:
            return "UDIV"
        if self.opcode == 9:
            return "SLT"
        if self.opcode == 10:
            return "SRT"
        if self.opcode == 11:
            return "LAND"
        if self.opcode == 12:
            return "LOR"
        if self.opcode == 13:
            return "LXOR"
        if self.opcode == 14:
            return "LNAND"
        if self.opcode == 15:
            return "LNOR"
        if self.opcode == 16:
            return "LXNOR"
        if self.opcode == 17:
            return "BSFA"
        if self.opcode == 18:
            return "INA"
        if self.opcode == 19:
            return "INB"
        if self.opcode == 20:
            return "FXP_ADD"
        if self.opcode == 21:
            return "FXP_SUB"
        if self.opcode == 22:
            return "FXP_MUL"
        if self.opcode == 23:
            return "FXP_DIV"
        if self.opcode == 24:
            return "BEQ"
        if self.opcode == 25:
            return "BNE"
        if self.opcode == 26:
            return "BLT"
        if self.opcode == 27:
            return "BGE"
        if self.opcode == 28:
            return "LWD"
        if self.opcode == 29:
            return "LWI"
        if self.opcode == 30:
            return "LWIPI"
        if self.opcode == 31:
            return "SWD"
        if self.opcode == 32:
            return "SWI"
        if self.opcode == 33:
            return "SWIPI"
        if self.opcode == 34:
            return "NOP"
        if self.opcode == 40:
            return "MV"
        if self.opcode == 41:
            return "BLE"
        if self.opcode == 42:
            return "BGT"
        if self.opcode == 43:
            return "BZFA"
        if self.opcode == 44:
            return "SRA"
        #print(self.opcode)

        return "UNDEF"

#nodes of the interference graph
#a node refers to the liveness of a value
class interval:

    def __init__(self,id, start, end, source, destination, length):

        self.id = id
        self.start = start
        self.end = end
        self.source = source
        self.destination = destination
        self.length = length
        self.weigth = 0
        self.color = -1
        self.name = ""

        self.neighbors = []

    def __del__(self):
        self.neighbors.clear()

    def addNeighbour(self, n):
        self.neighbors.append(n)

    def getColorName(self):
        color = ""
        if self.color == 0:
            color = "white"
        if self.color == 1:
            color = "orange"
        if self.color == 2:
            color = "yellow"
        if self.color == 3:
            color = "blue"

        return color
      
#edges of the interference graph
#two nodes are connected if the liveness overlaps
class overlap:

    def __init__(self, id, source, destination):
        self.id = id
        self.source = source
        self.destination = destination

#interference graph
class interference:
    
    def __init__(self, id):
        self.id = id
        self.intervals = []
        self.overlaps = []
        self.rf_size = 4
        

    def __del__(self):
        self.intervals.clear()
        self.overlaps.clear()

    def removeOverlappingIntervals(self):

        to_delete = []
        for i in range(0, len(self.intervals) -1):
            for j in range(i + 1, len(self.intervals)):
                if self.intervals[i].source.id == self.intervals[j].source.id:
                    if self.intervals[i].length >= self.intervals[j].length:
                        to_delete.append(self.intervals[j].id)
                    else:
                        to_delete.append(self.intervals[i].id)

        for inter in list(self.intervals):
            if inter.id in to_delete:
                self.intervals.remove(inter)
    
    def addInterval(self, interval):
        self.intervals.append(interval)

    def addOverlap(self, overlap):
        self.overlaps.append(overlap)
    
    def setOutputRegisters(self):
        for interval in self.intervals:
            if interval.color != -1:
                interval.source.outreg = interval.color

    def printDot(self, name):

        if len(self.intervals) < 1:
            return

        filename = name + "_interference.dot"
        f = open(filename, "w")
        f.write("digraph " + name + " {\n{\n compound=true;")

        #print nodes(intervals)
        for interval in self.intervals:
            f.write("\n" + str(interval.id) + " [style=filled, color=" + interval.getColorName() + ", label=\"" + str(interval.id) + "\"];\n")

        #print edges(overlaps)
        for overlap in self.overlaps:
            f.write(str(overlap.source.id) + " -> " + str(overlap.destination.id) + " [arrowhead=none]\n")

        f.write("\n}\n\n}")
        f.close()

def needRegister(kernel_length, p, time_s, time_d, kernel):

    if time_s < time_d:
        #1
        if time_d - time_s > 1:
            for i in range(time_s + 1, time_d):
                if p in kernel[i]:              
                    return True
        return False
    elif time_s == time_d:
        print("Error 1")
        exit(0)
    else:
        if time_s == kernel_length and time_d == 0:
            return False

        for i in range(0, time_d):
            if p in kernel[i]:
                return True
            
        for i in range(time_s + 1, kernel_length + 1):
            if p in kernel[i]:
                return True
        
        return False
