from mapper import *
from parser import *

import argparse

def generateInstructions(kernel, DFG):
    instructions = {}
    inst_id = 0
    for t in kernel:
        for p in kernel[t]:
            node_id = kernel[t][p]
            inst = instruction(inst_id, node_id)
            inst.pe = p
            inst.time = t
            n = DFG.getNode(node_id)
            inst.ROp = n.rOp
            inst.LOp = n.lOp
            inst.name = n.name
            inst.predicate = n.predicate
            inst.opcode = n.opcode
            inst_id += 1
            if DFG.getConstant(n.id) != None:
                inst.immediate = DFG.getConstant(n.id).value
            if p not in instructions:
                instructions[p] = []
            instructions[p].append(inst)
    
    return instructions

CGRA_X = 4
CGRA_Y = 4
CGRA_R = 100


def main():

    global CGRA_X, CGRA_Y, CGRA_R
    
    parser = argparse.ArgumentParser(description='SAT-MapIt mapper usage')
    parser.add_argument('-path', type=str, help='Path of the folder containing the extracted DFG')
    parser.add_argument('-x', type=int, help='Number or rows in the CGRA (default value: 4)', default=4)
    parser.add_argument('-y', type=int, help='Number or rows in the CGRA (default value: 4)', default=4)
    parser.add_argument('-r', type=int, help='Number of internal registers (default value: 5)', default=5)
    parser.add_argument('-no_assembly', type=bool, help='Disable assmbly generation (only return the mapping)', default=False)
    

    #Parse Arguments
    args = parser.parse_args()
    
    CGRA_X = int(args.x)
    CGRA_Y = int(args.y)
    CGRA_R = int(args.r)

    no_assembly = bool(args.no_assembly)


    #Path to the folder containing the benchmark
    path = args.path
    bench = "acc"
    #Names of the files generated by the LLVM pass
    nodefile = path + bench + "_nodes"
    edgefile = path + bench + "_edges"
    
    #Parse all the files generated by the LLVM pass
    p = Parser()
    p.parseNodeFile(nodefile)
    p.parseEdgeFile(edgefile)
    #p.parseLiveInNodeFile()
    #p.parseLiveOutNodeFile()
    #p.parseLiveInEdgeFile()
    #p.parseLiveOutEdgeFile()
    #p.parseConstantsFile()
 
    #Get the parsed DFG
    DFG = p.getDFG()
    print("#nodes: " + str(len(DFG.nodes)))

    #Initialize the mapper with the CGRA dimensions,
    #number of registers of each PE and the DFG
    m = Mapper(CGRA_X, CGRA_Y, CGRA_R, DFG, bench)

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
            tmps = "Id: " + str(inst.nodeid) + " name: " + str(inst.name)+ " time: " + str(inst.time) + " pe: " + str(inst.pe)
            tmps += " Rout: " + inst.getOutputOperandAssignedRegister() + " opA: " + inst.getLeftOperandAssignedRegister() + " opB: " + inst.getRigthOperandAssignedRegister() + " immediate: " + str(inst.immediate)
            print(tmps+"\n")


    


if __name__ == "__main__":
    main()