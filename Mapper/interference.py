from instruction import *
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
        print("Need Register: Error 1")
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
