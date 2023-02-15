from mapper import *
from parser import *


def generateInstructions(kernel, DFG):
    instructions = {}
    
    for t in kernel:
        for p in kernel[t]:
            inst_id = kernel[t][p]
            inst = instruction(inst_id)
            inst.pe = p
            inst.time = t
            n = DFG.getNode(inst_id)
            inst.ROp = n.rOp
            inst.LOp = n.lOp
            inst.name = n.name
            inst.predicate = n.predicate
            inst.opcode = n.opcode
            if DFG.getConstant(n.id) != None:
                inst.immediate = DFG.getConstant(n.id).value
            
            if p not in instructions:
                instructions[p] = []
            instructions[p].append(inst)
    
    return instructions


#TODO: (Medium priority) handle two edges to same node eg mul %1,%1
#TODO: (Medium priority) fix register assignment when lwd in init needs to store va(isqrt problem)
#(The above TODOs are solved manually for now)

n_cols = 4
n_rows = 4
n_regs = 10

def main():
    
    #Name of the benchmark filße
    bench = "isqrt321"
    #Path to the folder containing the benchmark
    path = "../benchmarks/sqrt/"

    #Names of the files generated by the LLVM pass
    nodefile = path + bench + "_nodes"
    edgefile = path + bench + "_edges"
    liveinnodefile = path + bench + "_liveinnodes"
    liveoutnodefile = path + bench + "_liveoutnodes"
    liveinedgefile = path + bench + "_livein_edges"
    liveoutedgefile = path + bench + "_liveout_edges"
    constants = path + bench + "_constants"

    #Parse all the files generated by the LLVM pass
    p = Parser()
    p.parseNodeFile(nodefile)
    p.parseEdgeFile(edgefile)
    p.parseLiveInNodeFile(liveinnodefile)
    p.parseLiveOutNodeFile(liveoutnodefile)
    p.parseLiveInEdgeFile(liveinedgefile)
    p.parseLiveOutEdgeFile(liveoutedgefile)
    p.parseConstantsFile(constants)

    #Get the parsed DFG
    DFG = p.getDFG()
    print("#nodes: " + str(len(DFG.nodes)))

    #Initialize the mapper with the CGRA dimensions,
    #number of registers of each PE and the DFG
    m = Mapper(n_rows, n_cols, n_regs, DFG, bench)

    #Find the mapping and get the mapped kernel
    m.findMapping()
    kernel = m.getKernel()

    #Generate instructions for the kernel, final mapping and than assembly
    #A node in the DFG does not contain all the information needed to 
    #generate the assembly code, that's why we generate the list instructions
    #Final mapping is: 
    #Initialization (e.g., live in loading) + Prologue + Kernel + Epilogue + Finalization (e.g., store of liveout)
    instructions = generateInstructions(kernel, DFG)
    m.generateMapping(instructions)
    m.printAssembly()

    #Debug
    for p in instructions:
        for inst in instructions[p]:
            tmps = "Id: " + str(inst.id) + " name: " + str(inst.name)+ " time: " + str(inst.time) + " pe: " + str(inst.pe)
            tmps += " Rout: " + str(inst.outreg) + " opA: " + str(inst.opA) + " opB: " + str(inst.opB) + " immediate: " + str(inst.immediate)
            print(tmps+"\n")


    


if __name__ == "__main__":
    main()