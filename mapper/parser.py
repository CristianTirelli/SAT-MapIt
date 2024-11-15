from DFG import *

#parser for all the input file that generates the DFG

class Parser:
    def __init__(self):
        self.dfg = DFG()
    
    def parseNodeFile(self, nodefile):
        with open(nodefile,"r") as fd: 
            for line in fd.readlines():
                tmp_node = line.split(' ')
                id = int(tmp_node[0])
                node_type = tmp_node[1]
                if node_type == "instruction":
                    node = instruction_node(id, tmp_node[2], int(tmp_node[3]), int(tmp_node[4]), int(tmp_node[5]), int(tmp_node[6]))
                elif node_type == "constant":
                    node = constant_node(id, int(tmp_node[7]), int(tmp_node[8]))
                elif node_type == "live_in":
                    node = livein_node(id)
                elif node_type == "live_out":
                    node = liveout_node(id)
                else:
                    raise ValueError(f"Unsupported node type '{node_type}'")
                self.dfg.addNode(node)

    def parseEdgeFile(self, edgefile):
        with open(edgefile,"r") as fd: 
            for l in fd.readlines():
                tmp_e = l.split(' ')
                source_id = int(tmp_e[0])
                dest_id = int(tmp_e[1])
                distance = int(tmp_e[2])
                latency = int(tmp_e[3])

                e = edge(
                    self.dfg.getNode(source_id),
                    self.dfg.getNode(dest_id),
                    distance,
                    latency
                )
                self.dfg.addEdge(e)
                    
    def getDFG(self):
        return self.dfg
