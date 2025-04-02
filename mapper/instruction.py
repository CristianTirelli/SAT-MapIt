from .ISA import *

# this is a class similar to node, but with more information
class Instruction:
    def __init__(self, instruction_id, nodeid):
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
        self.cycle_destination = -1   # jmp location

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

        raise ValueError(f"Invalid outreg value: {self.outreg}")

    @staticmethod
    def getAssignedRegister(op: int) -> str:
        ret = REGISTER_NAMES.get(op, None)
        if ret is not None:
            return ret
        if op == ZERO:
            return "ZERO"
        if op == CONST:
            # print("Remove this after debug, opa")
            return ""
        if op >= 0:
            return "R" + str(op)

        raise ValueError(f"Invalid operand value: {op}")

    def getLeftOperandAssignedRegister(self) -> str:
        return Instruction.getAssignedRegister(self.opA)

    def getRigthOperandAssignedRegister(self) -> str:
        return Instruction.getAssignedRegister(self.opB)

    def getPredicateOperandAssignedRegister(self):
        if self.muxflag not in REGISTER_NAMES:
            raise ValueError(f"Invalid muxflag value: {self.muxflag}")
        return REGISTER_NAMES[self.muxflag]

    def getAssemblyStr(self):
        handler = self._assembly_dispatch().get(self.getOpcodeName(), self._handle_default)
        return handler()

    def _assembly_dispatch(self):
        return {
            "MV": self._handle_mv,
            "LWI": self._handle_lwi,
            "LWD": self._handle_lwd,
            "SWI": self._handle_swi,
            "SWD": self._handle_swd,
            "BSFA": self._handle_bsfa_bzfa,
            "BZFA": self._handle_bsfa_bzfa,
            "NOP": lambda: "NOP",
            "EXIT": lambda: "EXIT",
            **{op: self._handle_branch for op in BRs},
        }

    def _handle_mv(self):
        reg_out = self.getOutputOperandAssignedRegister()
        if self.opA in (ZERO, CONST):
            reg_src = self.getRigthOperandAssignedRegister()
        else:
            reg_src = self.getLeftOperandAssignedRegister()
        return f"SADD {reg_out}, {reg_src}, ZERO"

    def _handle_lwi(self):
        reg_out = self.getOutputOperandAssignedRegister()
        if self.opB == CONST:
            return f"LWI {reg_out}, {self.immediate}"
        return f"LWI {reg_out}, {self.getLeftOperandAssignedRegister()}"

    def _handle_lwd(self):
        return f"LWD {self.getOutputOperandAssignedRegister()}"

    def _handle_swi(self):
        reg_src = self.getLeftOperandAssignedRegister()
        if self.opB == CONST:
            return f"SWI {reg_src}, {self.immediate}"
        return f"SWI {reg_src}, {self.getRigthOperandAssignedRegister()}"

    def _handle_swd(self):
        return f"SWD {self.getOutputOperandAssignedRegister()}"

    def _handle_bsfa_bzfa(self):
        return (
            f"{self.getOpcodeName()} {self.getOutputOperandAssignedRegister()}, "
            f"{self.getLeftOperandAssignedRegister()}, {self.getRigthOperandAssignedRegister()}, "
            f"{self.getPredicateOperandAssignedRegister()}"
        )

    def _handle_branch(self):
        if self.opB == CONST:
            print(
                "BR opcode can only have one immediate and it's the br destination.\n"
                "Store the constant in a register."
            )
            # exit(0)
            # TODO: ask Cristian about this
        return (
            f"{self.getOpcodeName()} {self.getLeftOperandAssignedRegister()}, "
            f"{self.getRigthOperandAssignedRegister()}, {self.cycle_destination}"
        )

    def _handle_default(self):
        opcode = self.getOpcodeName()
        reg_out = self.getOutputOperandAssignedRegister()

        if self.hasConstant():
            if self.opA == CONST:
                reg_b = self.getRigthOperandAssignedRegister()
                return f"{opcode} {reg_out}, {reg_b}, {self.immediate}"
            elif self.opB == CONST:
                reg_a = self.getLeftOperandAssignedRegister()
                return f"{opcode} {reg_out}, {reg_a}, {self.immediate}"
            else:
                raise ValueError(
                    f"CONST error: nodeid={self.nodeid}, opA={self.opA}, opB={self.opB}"
                )
        else:
            reg_a = self.getLeftOperandAssignedRegister()
            reg_b = self.getRigthOperandAssignedRegister()
            return f"{opcode} {reg_out}, {reg_a}, {reg_b}"

    def getOpcodeName(self):
        return OPCODE_NAMES.get(self.opcode, "UNDEF")
