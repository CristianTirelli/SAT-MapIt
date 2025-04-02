from .ISA import *

#this is a class similar to node, but with more information 
class Instruction:
    REGISTER_NAMES = {
        RCR: "RCR",
        RCL: "RCL",
        RCT: "RCT",
        RCB: "RCB",
        ROUT: "ROUT",
    }

    def __init__(self,instruction_id, nodeid):
        self.instruction_id = instruction_id                # instruction id node not necessarly the same as the node id
        self.nodeid = nodeid
        self.name = ""

        self.outreg = -1   
        self.time = -1
        self.pe = -1

        self.LOp = -1               # left operand node id
        self.ROp = -1               # rigth operand node id
        self.predicate = -1         # predicate operand node id

        self.opA = -1               # left operand assigned register (look constants.py file)
        self.opB = -1               # rigth operand assigned register (look constants.py file)
        self.muxflag = -1           # predicate operand assigned register (look constants.py file)
        self.immediate = 0          # immediate value
        self.opcode = -1            # instruction opcode
        self.cycle_destination = -1 # jmp location

    @staticmethod
    def copy(old: "Instruction") -> "Instruction":
        ret = Instruction(old.instruction_id, old.nodeid)
        ret.name = old.name
        ret.outreg = old.outreg
        ret.time = old.time
        ret.pe = old.pe
        ret.LOp = old.LOp
        ret.ROp = old.ROp
        ret.predicate = old.predicate
        ret.opA = old.opA
        ret.opB = old.opB
        ret.muxflag = old.muxflag
        ret.immediate = old.immediate
        ret.opcode = old.opcode
        ret.cycle_destination = old.cycle_destination
        return ret

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f"Instruction({self.instruction_id} {self.nodeid} {self.name} {self.outreg} {self.time} {self.pe} {self.LOp} {self.ROp} {self.predicate} {self.opA} {self.opB} {self.muxflag} {self.immediate} {self.opcode} {self.cycle_destination})"


    def hasPredicate(self):
        if self.predicate == -1:
            return False
        return True

    def hasConstant(self):
        if self.opA == CONST or self.opB == CONST:
            return True
        return False

    def getOutputOperandAssignedRegister(self):
        if self.outreg == -1:
            return "ROUT"        
        if self.outreg >= 0:
            return "R" + str(self.outreg)

        print("should not be here", self.outreg)
        exit(0)

    @staticmethod
    def getAssignedRegister(op: int) -> str:
        ret = Instruction.REGISTER_NAMES.get(op, None)
        if ret is not None:
            return ret
        if op == ZERO:
            return "ZERO"
        if op == CONST:
            #print("Remove this after debug, opa")
            return ""
        if op >= 0:
            return "R" + str(op)
        
        raise ValueError(f"Invalid operand value: {op}")

    def getLeftOperandAssignedRegister(self) -> str:
        return Instruction.getAssignedRegister(self.opA)

    def getRigthOperandAssignedRegister(self) -> str:
        return Instruction.getAssignedRegister(self.opB)

    def getPredicateOperandAssignedRegister(self):
        if self.muxflag not in Instruction.REGISTER_NAMES:
            raise ValueError(f"Invalid muxflag value: {self.muxflag}")
        return Instruction.REGISTER_NAMES[self.muxflag]

    def getAssemblyStr(self):
        output = ""
        if self.getOpcodeName() == "MV":
            output += "SADD " + self.getOutputOperandAssignedRegister() + ", "
            if self.opA == ZERO or self.opA == CONST:
                output += self.getRigthOperandAssignedRegister() + ", "
            else:
                output += self.getLeftOperandAssignedRegister() + ", "

            output += "ZERO"
        elif self.getOpcodeName() == "LWI":
            output += "LWI " + self.getOutputOperandAssignedRegister() + ", "
            # not sure this case actually makes sense, but in theory it should be allowed
            if self.opB == CONST:
                output += str(self.immediate)
            else:    
                output += self.getLeftOperandAssignedRegister()      
        elif self.getOpcodeName() == "LWD":
            output += "LWD " + self.getOutputOperandAssignedRegister()
        elif self.getOpcodeName() == "SWI":
            output += "SWI " + self.getLeftOperandAssignedRegister() + ", "
            # not sure this case actually makes sense, but in theory it should be allowed
            if self.opB == CONST:
                output += str(self.immediate)
            else:    
                output += self.getRigthOperandAssignedRegister()              
        elif self.getOpcodeName() == "SWD":
            output += "SWD " + self.getOutputOperandAssignedRegister()
        elif self.getOpcodeName() == "BSFA" or self.getOpcodeName() == "BZFA":
            output += self.getOpcodeName() + " " + self.getOutputOperandAssignedRegister() + ", "
            output += self.getLeftOperandAssignedRegister() + ", " + self.getRigthOperandAssignedRegister() 
            output +=  ", " + self.getPredicateOperandAssignedRegister()
        elif self.getOpcodeName() in BRs:
            output += self.getOpcodeName() + " " + self.getLeftOperandAssignedRegister() + ", "
            output += self.getRigthOperandAssignedRegister() + ", " + str(self.cycle_destination)
            if self.opB == CONST:
                print("BR opcode can only have one immediate and it's the br destination.\nStore the constant in a register.")
                #exit(0)
        elif self.getOpcodeName() == "NOP":
            output = "NOP"
        elif self.getOpcodeName() == "EXIT":
            output = "EXIT"
        else:
            if self.hasConstant():
                if self.opA == CONST:
                    #print("opA Const")
                    output += self.getOpcodeName() + " " + self.getOutputOperandAssignedRegister() + ", " 
                    output += self.getRigthOperandAssignedRegister() + ", " + str(self.immediate)
                elif self.opB == CONST:
                    #print("opB Const")
                    output += self.getOpcodeName() + " " + self.getOutputOperandAssignedRegister() + ", "
                    output += self.getLeftOperandAssignedRegister() + ", " + str(self.immediate)
                else:
                    print("Error in CONST checking.")
                    print(self.nodeid, self.opA, self.opB)
                    exit(0)
            else:
                output += self.getOpcodeName() + " " + self.getOutputOperandAssignedRegister() + ", " 
                output += self.getLeftOperandAssignedRegister() + ", " + self.getRigthOperandAssignedRegister()
            
        return output
    
    def getOpcodeName(self):

        if self.opcode == EXIT:
            return "EXIT"
        if self.opcode == SADD:
            return "SADD"
        if self.opcode == SSUB:
            return "SSUB"
        if self.opcode == SMUL:
            return "SMUL"
        if self.opcode == SDIV:
            return "SDIV"
        if self.opcode == UADD:
            return "UADD"
        if self.opcode == USUB:
            return "USUB"
        if self.opcode == UMUL:
            return "UMUL"
        if self.opcode == UDIV:
            return "UDIV"
        if self.opcode == SLT:
            return "SLT"
        if self.opcode == SRT:
            return "SRT"
        if self.opcode == LAND:
            return "LAND"
        if self.opcode == LOR:
            return "LOR"
        if self.opcode == LXOR:
            return "LXOR"
        if self.opcode == LNAND:
            return "LNAND"
        if self.opcode == LNOR:
            return "LNOR"
        if self.opcode == LXNOR:
            return "LXNOR"
        if self.opcode == BSFA:
            return "BSFA"
        if self.opcode == INA:
            return "INA"
        if self.opcode == INB:
            return "INB"
        if self.opcode == FXP_ADD:
            return "FXP_ADD"
        if self.opcode == FXP_SUB:
            return "FXP_SUB"
        if self.opcode == FXP_MUL:
            return "FXP_MUL"
        if self.opcode == FXP_DIV:
            return "FXP_DIV"
        if self.opcode == BEQ:
            return "BEQ"
        if self.opcode == BNE:
            return "BNE"
        if self.opcode == BLT:
            return "BLT"
        if self.opcode == BGE:
            return "BGE"
        if self.opcode == LWD:
            return "LWD"
        if self.opcode == LWI:
            return "LWI"
        if self.opcode == LWIPI:
            return "LWIPI"
        if self.opcode == SWD:
            return "SWD"
        if self.opcode == SWI:
            return "SWI"
        if self.opcode == SWIPI:
            return "SWIPI"
        if self.opcode == NOP:
            return "NOP"
        if self.opcode == MV:
            return "MV"
        if self.opcode == BLE:
            return "BLE"
        if self.opcode == BGT:
            return "BGT"
        if self.opcode == BZFA:
            return "BZFA"
        if self.opcode == SRA:
            return "SRA"
        #print(self.opcode)

        return "UNDEF"
