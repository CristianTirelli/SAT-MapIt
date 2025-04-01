import math
import itertools
import time
import logging
from typing import Dict, Optional
from z3 import Or, And, Not, Bool, Context, Solver, sat, is_true, set_option
from .RegisterAllocator import RegisterAllocator
from .instruction import instruction
from .ISA import *
from functools import wraps

def timeit(description: str, print_args: bool = False):
    """Decorator to time the execution of a function"""
    def decorator(func):
        @wraps(func)
        def wrap(*args, **kwargs):
            ts = time.time()
            if print_args:
                logging.info(f"{description} -- {func.__name__}({args}, {kwargs})")
            else:
                logging.info(f"{description} -- {func.__name__}")
            result = func(*args, **kwargs)
            te = time.time()
            if print_args:
                logging.info(f"{func.__name__} args:[{args}, {kwargs}] took: {te - ts:2.4f} sec")
            else:
                logging.info(f"{func.__name__} took {te - ts:2.4f} sec")
            return result
        return wrap
    return decorator

class Mapper:
    def __init__(self, x, y, r, dfg, benchmark, save_smt2_and_cnf: bool = False, seed: Optional[int] = None):
        self.save_smt2_and_cnf = save_smt2_and_cnf
        
        self.CGRA_X = x
        self.CGRA_Y = y    
        self.CGRA_R = r
        if seed is not None:
            set_option('smt.random_seed', seed)
        self.ctx = Context()
        self.s = Solver(ctx=self.ctx)
        # self.s = Solver()
        self.benchmark = benchmark
        
        self.DFG = dfg
        self.ResII = 0
        self.RecII = 0
        self.II = 0
        self.ASAP = {}
        self.ALAP = {}
        self.MS = {}
        self.KMS = {}
        self.scheduleLen = 0
        
        #schedule found by solver that can be modulo scheduled
        self.schedule = {}
        self.prolog = {}
        self.kernel = {}
        self.epilog = {}

        self.init = {}
        self.pke = {}
        self.fini = {}
        #init + pke + fini = mapping
        self.mapping : Dict[int, Dict[int, instruction]]= {}

        self.ra = None

    #Get Resource Iteration Interval
    def computeResII(self):
        self.ResII = math.ceil(len(self.DFG.get_instruction_nodes())/(self.CGRA_X*self.CGRA_Y))

    #Get Recurrence Iteration Interval
    def computeRecII(self):
        
        for s in self.DFG.getSCCs():
            self.RecII = max(self.DFG.getPathDelay(s), self.RecII)        

    #Get Minimum Iteration Interval (MII)
    def getStartingII(self):            
        self.computeRecII()
        self.computeResII()
        self.II = max(self.RecII, self.ResII)
        logging.debug(f"{self.RecII = }")
        logging.debug(f"{self.ResII = }")
        return self.II

    #Generate As-Soon-As-Possible schedule
    def generateASAP(self):
        self.ASAP.clear()
        self.DFG.resetNodeTime(0)
        to_explore = self.DFG.getStartingNodes()
        while to_explore:
            tmp = []
            for n in to_explore:
                for sn in self.DFG.getSuccessors(n):
                    if sn.name != "phi":
                        sn.time = max(sn.time, n.time + 1)
                        tmp.append(sn)
                        self.scheduleLen = max(self.scheduleLen, sn.time)
            to_explore = tmp[:]
            tmp.clear()
        
        for n in self.DFG.get_instruction_nodes():
            if n.time not in self.ASAP:
                self.ASAP[n.time] = []
            self.ASAP[n.time].append(n.id)

        logging.debug("ASAP Schedule")
        logging.debug(self.scheduleStr(self.ASAP))
    
    #Generate As-Late-As-Possible schedule
    def generateALAP(self):
        self.DFG.resetNodeTime(0)
        to_explore = self.DFG.getEndingNodes()
        while to_explore:
            tmp = []
            for n in to_explore:
                for sn in self.DFG.getPredecessors(n):
                    if sn.name != 'phi':
                        sn.time = max(sn.time, n.time + 1)
                        tmp.append(sn)
                        self.scheduleLen = max(self.scheduleLen, sn.time)
                    else:
                        sn.time = max(sn.time, n.time + 1)
                        self.scheduleLen = max(self.scheduleLen, sn.time)

            to_explore = tmp[:]
            tmp.clear()

        for n in self.DFG.get_instruction_nodes():
            if (self.scheduleLen - n.time) not in self.ALAP:
                self.ALAP[self.scheduleLen - n.time] = []
            self.ALAP[self.scheduleLen - n.time].append(n.id)
        
        logging.debug("ALAP Schedule")
        logging.debug(self.scheduleStr(self.ALAP))

    def getASAPTime(self, id):
        for t in self.ASAP:
            for nid in self.ASAP[t]:
                if nid == id:
                    return t
        return -1

    def getALAPTime(self, id):
        for t in self.ALAP:
            for nid in self.ALAP[t]:
                if nid == id:
                    return t
        return -1

    def scheduleStr(self, schedule) -> str:
        ret = ""
        for t in range(len(schedule)):
            line = " ".join([str(e) for e in schedule[t]])
            ret += line + "\n"
        return ret

    #Generate Mobility schedule
    def generateMS(self):
        self.ASAP.clear()
        self.ALAP.clear()
        self.generateASAP()
        self.generateALAP()

        for n in self.DFG.get_instruction_nodes():

            t_asap = self.getASAPTime(n.id)
            t_alap = self.getALAPTime(n.id)

            for t in range(t_asap, t_alap + 1):
                if t not in self.MS:
                    self.MS[t] = []
                self.MS[t].append(n.id)
        
        logging.debug("Mobility Schedule")
        logging.debug(self.scheduleStr(self.MS))

    
    #Generate Kernel Mobility Schedule
    def generateKMS(self, II):
        self.KMS.clear()
        if II <= self.scheduleLen + 1:
            for i in range(self.scheduleLen + 1):
                it = i//II
                
                if (i%II) not in self.KMS:
                    self.KMS[i%II] = []
                for nid in self.MS[i]:
                    self.KMS[i%II].append((it, nid))
        else:
            dup = II - (self.scheduleLen + 1)
            it = 0
            tmpKMS = {}
            for d in range(dup + 1):
                for i in range(self.scheduleLen + 1):
                    if (i + d) not in tmpKMS:
                        tmpKMS[i + d] = []
                    for nid in self.MS[i]:
                        if nid not in tmpKMS[i + d]:
                            tmpKMS[i + d].append(nid)

                d += 1
            
            for t in tmpKMS:
                if t not in self.KMS:
                    self.KMS[t] = []
                for nid in tmpKMS[t]:
                    self.KMS[t].append((it, nid))

    #Add constraint1 of the formulation
    #Only one literal for each node must be set to True
    @timeit("Adding C1...")
    def addConstraint1(self, node_literals):
        for nodeid in node_literals:
            phi = Or(node_literals[nodeid])
            tmp = []
            for i in range(len(node_literals[nodeid])-1):
                for j in range(i+1, len(node_literals[nodeid])):
                    tmp.append(Not(And(node_literals[nodeid][i], node_literals[nodeid][j])))
            tmp = And(tmp)
            exactlyone = And(phi,tmp)
            self.s.add(exactlyone)

    #Add constraint2 of the formulation
    #Avoid two nodes on the same PE at the same time
    @timeit("Adding C2...")
    def addConstraint2(self, cycle_pe_literals):
        for cycle in cycle_pe_literals:
            for pe in cycle_pe_literals[cycle]:
                tmp = []
                for i in range(len(cycle_pe_literals[cycle][pe])-1):
                    for j in range(i+1, len(cycle_pe_literals[cycle][pe])):
                        tmp.append(Or(Not(cycle_pe_literals[cycle][pe][i]), Not(cycle_pe_literals[cycle][pe][j])))
                if len(tmp) > 1:
                    tmp = And(tmp)
                elif len(tmp) == 0:
                    continue
                self.s.add(tmp)

    def add_contraints_forward_edge(self, II: int, c_n_it_p_literal: dict, cycle_pe_literals: dict) -> bool:
        all_dep_encoded = True
        SEL = ["bzfa", "bsfa"]
        found_br = False
        logging.info("Adding forward dependencies...")	
        for e in self.DFG.get_instruction_edges():
            if e.distance > 0: #backdependencies handled below
                continue
            ns = e.source.id
            nd = e.destination.id
            logging.debug(f"nodes = {ns, nd}")
            tmp = []
            is_dest_sel = self.DFG.getNode(nd).name in SEL and self.DFG.getNode(nd).predicate.id == ns
            
            for (cs,cd) in itertools.product(c_n_it_p_literal, c_n_it_p_literal):
                if (ns not in c_n_it_p_literal[cs]) or (nd not in c_n_it_p_literal[cd]):
                    continue
                if self.DFG.getNode(nd).name.upper() in BRs and cd != (II - 1):
                    continue
                else:
                    found_br = True
                for (it1, it2) in itertools.product(c_n_it_p_literal[cs][ns], c_n_it_p_literal[cd][nd]):
                    is_same_it = it1 == it2 and cd > cs
                    is_diff_it = abs(it1 - it2) == 1 and it1 < it2 and cd <= cs
                    if not (is_same_it or is_diff_it):
                        continue
                    for (p1, p2) in itertools.product(c_n_it_p_literal[cs][ns][it1], c_n_it_p_literal[cd][nd][it2]):
                        if not self.isNeighbor(p1, p2):
                            continue
                        lit1 = c_n_it_p_literal[cs][ns][it1][p1]
                        lit2 = c_n_it_p_literal[cd][nd][it2][p2]
                        distance = self.getCycleDistance(cs, cd, II)
                        if distance == 1 or (distance > 1 and p1 == p2 and not is_dest_sel):
                            tmp.append(And(lit1, lit2))
                        elif distance > 1:
                            tmp2 = []
                            for ci in range(cs + 1, cd if is_same_it else II):
                                tmp2.append(And(lit1, lit2, cycle_pe_literals[ci][p1]))
                            if is_diff_it:
                                for ci in range(cd):
                                    tmp2.append(And(lit1, lit2, cycle_pe_literals[ci][p1]))
                            if len(tmp2) > 0:
                                tmp.append(And(tmp2))
                        elif distance == 0 and is_diff_it and p1 != p2:
                            tmp2 = []
                            for ci in range(II):
                                if ci == cs:
                                    continue
                                tmp2.append(And(lit1, lit2, cycle_pe_literals[ci][p1]))
                            tmp.append(And(tmp2))
                    
            if len(tmp) == 0:
                logging.info(f"No constraint for dependency between {ns} and {nd}")
                all_dep_encoded = False
                break
            self.s.add(Or(tmp))
        if not found_br:
            logging.warning("Cannot find BR node in last cycle of the kernel.\n Comment this if you don't care or check DFG/MS")

        return all_dep_encoded


    def add_contraints_backward_edge(self, II: int, c_n_it_p_literal: dict, cycle_pe_literals: dict) -> bool:
        all_dep_encoded = True
        #handle backdeps
        logging.info("Adding back dependencies...")	
        for e in self.DFG.get_instruction_edges():
            if e.distance < 1: # forward dependencies are handled above
                continue 
            ns = e.source.id
            nd = e.destination.id
            logging.debug(f"nodes = {ns, nd}")
            tmp = []
            for (cs,cd) in itertools.product(c_n_it_p_literal, c_n_it_p_literal):
                if (ns not in c_n_it_p_literal[cs]) or (nd not in c_n_it_p_literal[cd]):
                    continue
                for (it1, it2) in itertools.product(c_n_it_p_literal[cs][ns], c_n_it_p_literal[cd][nd]):
                    if abs(it1 - it2) > 1:
                        continue

                    same_it_diff_cycle = it1 == it2 and cs > cd
                    diff_it = it1 > it2 and cs < cd
                    same_it_same_cycle = it1 == it2 and cs == cd
                    if not (same_it_diff_cycle or diff_it or same_it_same_cycle):
                        continue
                    for (p1, p2) in itertools.product(c_n_it_p_literal[cs][ns][it1], c_n_it_p_literal[cd][nd][it2]):
                        lit1 = c_n_it_p_literal[cs][ns][it1][p1]
                        lit2 = c_n_it_p_literal[cd][nd][it2][p2]
                        if not self.isNeighbor(p1, p2):
                            continue
                        if same_it_diff_cycle or diff_it:
                            distance = self.getCycleDistance(cs, cd, II)
                            if distance == 1 or (distance > 1 and p1 == p2):
                                tmp.append(And(lit1, lit2))
                            if distance > 1:
                                tmp2 = []
                                for ci in range(cs + 1, II):
                                    tmp2.append(And(lit1, lit2, cycle_pe_literals[ci][p1]))
                                for ci in range(cd):
                                    tmp2.append(And(lit1, lit2, cycle_pe_literals[ci][p1]))
                                tmp.append(And(tmp2))
                        elif same_it_same_cycle and p1 != p2:
                            tmp2 = []
                            for ci in range(II):
                                if ci == cs:
                                    continue
                                tmp2.append(And(lit1, lit2, cycle_pe_literals[ci][p1]))
                            tmp.append(And(tmp2))
            if len(tmp) == 0:
                logging.info(f"No constraint for backdep between source: {ns} and dest: {nd}. Need to check")
                all_dep_encoded = False
                break
            self.s.add(Or(tmp))
        return all_dep_encoded

    #Add constraint3 of the formulation
    #Map dependent nodes on neibours PEs
    #TODO: (High priority) avoid useing regfile from S to D when S is the predicate of D
    @timeit("Adding C3...")
    def addConstraint3(self, II, c_n_it_p_literal, cycle_pe_literals):
        encoded_forward_dependencies = self.add_contraints_forward_edge(II, c_n_it_p_literal, cycle_pe_literals)
        if not encoded_forward_dependencies:
            logging.info("Couldn't encode forward dependencies, stopping here")
            self.s.reset()
            return False

        encoded_backward_dependencies = self.add_contraints_backward_edge(II, c_n_it_p_literal, cycle_pe_literals)
        if not encoded_backward_dependencies:
            self.s.reset()
            return False
        #OUTPUT OF SMT AND CNF FILE
        
        if self.save_smt2_and_cnf:
            with open(f"{self.benchmark}_{II}.smt2", "w") as f:
                f.write(self.s.to_smt2())
            with open(f"{self.benchmark}_{II}.cnf", "w") as f:
                f.write(self.s.dimacs())
        return True

    #Find mapping of the DFG starting from the MII
    #TODO: (Low priority) add upperbound for II
    def findMapping(self):
        
        II = self.getStartingII()
        
        self.generateMS()

        solution = False
        while not solution:
            logging.info(f"{II = }")
            self.generateKMS(II)
            nit = math.ceil((self.scheduleLen + 1) / II)
            logging.debug("nit " + str(self.scheduleLen + 1)+"/"+str(II) +"= "+str((self.scheduleLen + 1) / II) +"= "+str(nit))
            
            iterations = {}
            logging.debug("KMS")
            for i in range(II):
                logging.debug(f"{self.KMS[i] = }")

            for it in range(nit):
                if it not in iterations:
                    iterations[it] = {}
                for t in self.KMS:
                    if t not in iterations[it]:
                        iterations[it][t] = []
                    for p in self.KMS[t]:
                        if p[0] == it:
                            iterations[it][t].append(p[1])

            #Generate all the literals for the formulation
            literals = []
            for it in iterations:
                for c in iterations[it]:
                    for nodeId in iterations[it][c]:
                        for pe in range(self.CGRA_X * self.CGRA_Y):
                            literals.append((Bool(f"v_{nodeId},{pe},{c},{it}", ctx = self.ctx), nodeId, pe, c, it))
            
            #Group literals in Map(nodeid, Value = 'list of literals')
            node_literals = {}
            for l in literals:
                literal = l[0]
                nodeid = l[1]
                if nodeid not in node_literals:
                    node_literals[nodeid] = []
                node_literals[nodeid].append(literal)
            
            #1)
            #exactly one variable True for each node
            self.addConstraint1(node_literals)


            #Group literals in Map(cycle, Value = Map(pe, literal))
            cycle_pe_literals = {}
            for l in literals:
                literal = l[0]
                pe = l[2]
                cycle = l[3]
                
                if cycle not in cycle_pe_literals:
                    cycle_pe_literals[cycle] = {}

                if pe not in cycle_pe_literals[cycle]:
                    cycle_pe_literals[cycle][pe] = []

                cycle_pe_literals[cycle][pe].append(literal)
            #2)
            #At most one node on one PE at a given time
            self.addConstraint2(cycle_pe_literals)
            

            #precompute data
            for ci in cycle_pe_literals:
                for pj in cycle_pe_literals[ci]:
                    cycle_pe_literals[ci][pj] = Not(Or(cycle_pe_literals[ci][pj]))

            #Group literals in Map(cycle, Value = Map(nodeid, Map(iteration,Map(pe, literal)))
            c_n_it_p_literal = {}
            for l in literals:

                literal = l[0]
                nodeid = l[1]
                pe = l[2]
                cycle = l[3]
                iteration = l[4]
                
                if cycle not in c_n_it_p_literal:
                    c_n_it_p_literal[cycle] = {}

                if nodeid not in c_n_it_p_literal[cycle]:
                    c_n_it_p_literal[cycle][nodeid] = {}
                
                if iteration not in c_n_it_p_literal[cycle][nodeid]:
                    c_n_it_p_literal[cycle][nodeid][iteration] = {}

                if pe not in c_n_it_p_literal[cycle][nodeid][iteration]:
                    c_n_it_p_literal[cycle][nodeid][iteration][pe] = ''

                c_n_it_p_literal[cycle][nodeid][iteration][pe] = literal
                    
            #3)
            #encode all dependencies
            if not self.addConstraint3(II, c_n_it_p_literal, cycle_pe_literals):
                logging.info("Can't encode all the dependency - II too small\nManually add routing nodes to solve this dep or let the code run.")
                logging.info("NOTE: we force the br instruction to be in the last time step of the kernel.")
                logging.info("This leads to suboptimal results, but makes easier the assembly generation. ")
                logging.info("To obtain optimal results set the BRs = [] and SEL = [] at the start of addConstraint3")
                II += 1
                continue

            start = time.time()

            if self.s.check() == sat:
                #model_number = 0
                #while self.s.check() == sat:
                #    
                #    print("MODEL " + str(model_number))
                #    model_number+=1
                #    m = self.s.model()
                #    block = []  
                #    for z3_decl in m: # FuncDeclRef
                #        arg_domains = []
                #        for i in range(z3_decl.arity()):
                #            domain, arg_domain = z3_decl.domain(i), []
                #            for j in range(domain.num_constructors()):
                #                arg_domain.append( domain.constructor(j) () )
                #            arg_domains.append(arg_domain)
                #        for args in itertools.product(*arg_domains):
                #            block.append(z3_decl(*args) != m.eval(z3_decl(*args)))
                #    self.s.add(Or(block))
                #    if model_number == 120:
                #        break
                solution = True
                logging.info("SAT")
                m = self.s.model()
                #parse z3 output
                for t in m.decls():
                    if is_true(m[t]):
                        tmp = str(t).split('_')[1].split(',')
                        p = int(tmp[1])
                        n = int(tmp[0])
                        t = int(tmp[2])
                        it = int(tmp[3])
                        logging.debug(f"Node {n} on PE {p} at time {t} of iteration {it}")
                        if t not in self.kernel:
                            self.kernel[t] = {}
                        if p not in self.kernel[t]:
                            self.kernel[t][p] = -1
                        self.kernel[t][p] = n

                        if (it * II + t) not in self.schedule:
                            self.schedule[it*II + t] = []

                        self.schedule[it*II + t].append(n)

                logging.debug("Kernel")
                for i in range(len(self.kernel)):
                    tmps = "[ "
                    for p in self.kernel[i]:
                        tmps += str(self.kernel[i][p]) + " "
                    logging.debug(tmps + "]")

                logging.debug("Schedule")
                for i in range(len(self.schedule)):
                    logging.debug(self.schedule[i])
                
            else:
                self.s.reset()
                II += 1

            end = time.time()
            logging.debug("Time: " + str(end - start))

        if solution == False:
            raise Exception("Mapping not found...\nLast II: " + str(II))

        self.II = II

        
        self.generateProlog()
        self.generateEpilog()
        self.generatePKE()

        
        #The code below needs to be adapted. 
        #It's used to generate more mapping for a given DFG at a given IIå
        #print("Solving...")
        #start = time.time()
        ##TODO: add function to generate different models (useful during RA)
        #model_number = 0
        #while self.s.check() == sat:
        #    solution = "False"
        #    print("MODEL " + str(model_number))
        #    model_number+=1
        #    
        #    block = []
        #    for z3_decl in m: # FuncDeclRef
        #        arg_domains = []
        #        for i in range(z3_decl.arity()):
        #            domain, arg_domain = z3_decl.domain(i), []
        #            for j in range(domain.num_constructors()):
        #                arg_domain.append( domain.constructor(j) () )
        #            arg_domains.append(arg_domain)
        #        for args in itertools.product(*arg_domains):
        #            block.append(z3_decl(*args) != m.eval(z3_decl(*args)))
        #    self.s.add(Or(block))
        #    if model_number == 1:
        #        break
        #print("Number of solutions: " + str(iii))

        #end = time.time()
        #print("Time: " + str(end - start))

    #Return True if pe1 and pe2 are neighbour on a 2D-mesh shaped topology
    #If the topology is different this function must be changed
    def isNeighbor(self, pe1, pe2):
        i1 = pe1 // self.CGRA_Y
        j1 = pe1 % self.CGRA_Y

        i2 = pe2 // self.CGRA_Y
        j2 = pe2 % self.CGRA_Y

        #same row
        if i1 == i2:
            if (pe1 == pe2 + 1) or (pe1 == pe2 - 1):
                return True
            if abs(pe1 - pe2) == self.CGRA_Y - 1:
                return True

        #same col
        if j1 == j2:
            if (pe1 == pe2 + self.CGRA_Y) or (pe1 == pe2 - self.CGRA_Y):
                return True
            if abs(i1 - i2) == self.CGRA_X - 1:
                return True
        #center
        if pe1 == pe2:
            return True

        return False

    def getCycleDistance(self, cs, cd, II):
        return (cd - cs + II) % II

    def generateProlog(self):

        first_row = []
        for p in self.kernel[0]:
            first_row.append(self.kernel[0][p])

        contained = True
        shift = 0

        for t in range(len(self.schedule)-1, -1, -1):

            contained = True
            for n in self.schedule[t]:
                if n not in first_row:
                    contained = False
            
            if contained:
                for i in range(t - 1, -1, -1):
                    for n in self.schedule[i]:
                        if (i + shift) not in self.prolog:
                            self.prolog[i + shift] = []
                        self.prolog[i + shift].append(n)
                shift += self.II

    def generateEpilog(self):
        last_row = []
        for p in self.kernel[len(self.kernel) - 1]:
            last_row.append(self.kernel[len(self.kernel) - 1][p])

        contained = True

        for t in range(len(self.schedule)):
            
            contained = True
            for n in self.schedule[t]:
                if n not in last_row:
                    contained = False
            
            if contained:
                for i in range(t + 1, len(self.schedule)):
                    for n in self.schedule[i]:
                        if ( i - t - 1) not in self.epilog:
                            self.epilog[i - t - 1] = []
                        self.epilog[i - t - 1].append(n)

    #Generate Prolog+Kernel+Epilog
    def generatePKE(self):

        self.pke.clear()
        n_pe = {}

        for t in self.kernel:
            for p in self.kernel[t]:
                if self.kernel[t][p] not in n_pe:
                    n_pe[self.kernel[t][p]] = -1
                n_pe[self.kernel[t][p]] = p

        t = 0

        for i in range(len(self.prolog)):
            if t not in self.pke:
                self.pke[t] = {}
            for n in self.prolog[i]:
                if n_pe[n] not in self.pke[t]:
                    self.pke[t][n_pe[n]] = -1
                self.pke[t][n_pe[n]] = n

            t += 1

        for i in range(len(self.kernel)):
            if t not in self.pke:
                self.pke[t] = {}
            for p in self.kernel[i]:
                if p not in self.pke[t]:
                    self.pke[t][p] = -1
                self.pke[t][p] = self.kernel[i][p]

            t += 1



        for i in range(len(self.epilog)):
            if t not in self.pke:
                self.pke[t] = {}
            for n in self.epilog[i]:
                if n_pe[n] not in self.pke[t]:
                    self.pke[t][n_pe[n]] = -1
                self.pke[t][n_pe[n]] = n

            t += 1

    #Get schedule found by the Z3
    def getSchedule(self):
        if len(self.schedule) > 0:
            return self.schedule
        return None
    
    def getProlog(self):
        if len(self.prolog) > 0:
            return self.prolog
        return None

    def getKernel(self):
        if len(self.kernel) > 0:
            return self.kernel
        return None

    def getEpilog(self):
        if len(self.epilog) > 0:
            return self.epilog
        return None

    def getPKE(self):
        if len(self.pke) > 0:
            return self.pke
        return None

    #Add initialization phase before the prolog
    #Loading of LiveIn variables and constants used usually by the phi nodes
    #TODO: This function can be writte in a much better way
    def generateInit(self, instructions):

        p_live = {}
        p_const = {}
        self.init.clear()
        #get all the constants and livein vars to use in the init phase
        for p in instructions:
            for inst in instructions[p]:
                live_in_node = self.DFG.getAssociateLiveIn(inst.nodeid)
                logging.debug(f"{live_in_node = }")
                init_const = self.DFG.getConstant(inst.nodeid)
                if live_in_node != None:
                    dest_p = p
                    #check if it should be in the righr or left operand
                    if inst.name == "phi":
                        if inst.LOp == live_in_node.id:
                            for p1 in instructions:
                                for inst1 in instructions[p1]:
                                    if inst1.nodeid == inst.ROp:
                                        dest_p = inst1.pe
                        elif inst.ROp == live_in_node.id:
                            for p1 in instructions:
                                for inst1 in instructions[p1]:
                                    if inst1.nodeid == inst.LOp:
                                        dest_p = inst1.pe
                            

                    if dest_p not in p_live:
                        p_live[dest_p] = []
                    if live_in_node not in p_live[dest_p]:
                        p_live[dest_p].append(live_in_node)

                if init_const != None:
                    p1 = 0
                    if inst.LOp == init_const.id:
                        #get pe of the ROp and save constant in that register or pe
                        nlop = self.DFG.getNode(inst.ROp)
                        for t in self.kernel:
                            for p2 in self.kernel[t]:
                                if self.kernel[t][p2] == nlop.id:
                                    p1 = p2
                        if p1 not in p_const:
                            p_const[p1] = []
                        p_const[p1].append(init_const)
                    elif inst.ROp == init_const.id and inst.name == "phi":
                        nrop = self.DFG.getNode(inst.LOp)
                        for t in self.kernel:
                            for p2 in self.kernel[t]:
                                if self.kernel[t][p2] == nrop.id:
                                    p1 = p2
                        if p1 not in p_const:
                            p_const[p1] = []
                        p_const[p1].append(init_const)

        #get len of the init phase
        init_len = 0
        for i in range(self.CGRA_X * self.CGRA_Y):
            if i in p_live and i in p_const:
                init_len = max(init_len, len(p_live[i]) + len(p_const[i]))
            if i in p_live:
                init_len = max(init_len, len(p_live[i]))
            if i in p_const:
                init_len = max(init_len, len(p_const[i]))
                
        #set to None each element of init
        for i in range(init_len):
            if i not in self.init:
                self.init[i] = {}
        
        tmp_id = 1000
        #create load instructions for live-in vars
        occupied_spot = {}
        for p in p_live:
            for i in range(len(p_live[p])):
                if i not in occupied_spot:
                    occupied_spot[i] = {}
                if p not in occupied_spot[i]:
                    occupied_spot[i][p] = True

                tmp = instruction(tmp_id, p_live[p][i].id)
                tmp_id +=1
                tmp.pe = p
                tmp.time = i    
                tmp.opcode = LWD
                #get where the instruction must save the loaded value
                space_full = True
                for j in range(len(self.ra.rf[p])):
                    if self.ra.rf[p][j] == 0:
                        tmp.outreg = j
                        self.ra.rf[p][j] = 1
                        space_full = False
                        break

                if space_full:
                    raise Exception("No register available on PE " + str(p) + " to store livein " + str(tmp.nodeid))

                #search the instruction and update it's left or right operand with the register that stores the livein
                for e in self.DFG.get_livein_edges():
                    if e.source.id == p_live[p][i].id:
                        for inst in instructions[p]:
                            if inst.nodeid == e.destination.id:
                                #check if it should be in the righr or left operand
                                if inst.LOp == e.source.id:
                                    inst.opA = tmp.outreg
                                elif inst.ROp == e.source.id:
                                    inst.opB = tmp.outreg

                self.init[i][p] = tmp
        #create add instructions for constants (usually for phi nodes, so they are going to be used only once)
        
        for pe in p_const:

            #get first time slot available to store instruction
            free_time_slot = 0
            for t in range(len(occupied_spot)):
                if pe not in occupied_spot[t]:
                    free_time_slot = t
                    break
            for i in range(len(p_const[pe])):
                if t + i not in occupied_spot:
                    occupied_spot[t + i] = {}
                if pe not in occupied_spot[t + i]:
                    occupied_spot[t + i][pe] = True
                
                tmp = instruction(tmp_id, p_const[pe][i].id)
                tmp_id += 1
                tmp.pe = pe
                tmp.time = t + i
                tmp.LOp = -1
                tmp.ROp = -1
                tmp.opA = CONST
                tmp.opB = ZERO
                tmp.immediate = p_const[pe][i].immediate
                tmp.opcode = SADD
                
                nrop = None
                nlop = None
                #find associate instruction and then Rop instruction to get the Rop outreg (where to save the loaded value)
                for p1 in instructions:
                    for inst in instructions[p1]:
                        if inst.LOp == p_const[pe][i].id:
                            nrop = self.DFG.getNode(inst.ROp)
                        elif inst.ROp == p_const[pe][i].id:
                            nlop = self.DFG.getNode(inst.LOp)

                if nrop != None:
                    for pe1 in instructions:
                        for inst in instructions[pe1]:
                            if inst.nodeid == nrop.id:
                                tmp.outreg = inst.outreg
                elif nlop != None:
                    for pe1 in instructions:
                        for inst in instructions[pe1]:
                            if inst.nodeid == nlop.id:
                                tmp.outreg = inst.outreg
                else:
                    raise Exception("should not happen (Create inst for constant)")

                for p1 in instructions:
                    for inst in instructions[p1]:
                        init_const = self.DFG.getConstant(inst.nodeid)
                        if init_const != None:    
                            if inst.LOp == p_const[pe][i].id:
                                tmp.opA = CONST
                                tmp.opB = ZERO

                self.init[i + t][pe] = tmp


        #set to NOP instruction all the other PEs
        for t in range(len(self.init)):
            if t not in self.init:
                self.init = {}
            for p in range(self.CGRA_X * self.CGRA_Y):
                if p not in self.init[t]:
                    self.init[t][p] = None
                if self.init[t][p] == None:
                    
                    tmp = instruction(-p-1, -2)
                    tmp.opcode = NOP
                    self.init[t][p] = tmp
        
    #Add finalization phase after epilogue
    #Store LiveOut variables
    #TODO: This function can be writte in a much better way
    #TODO: fix convention for operands storing value and address (now swd and swi are different:
    #      swi storest value to save in opA and address in opB)
    def generateFini(self, instructions):
        p_live = {}
        self.fini.clear()
        #get all the liveout vars to use in the fini phase
        for p in instructions:
            for inst in instructions[p]:
                live_out_node = self.DFG.getAssociateLiveOut(inst.nodeid)
                
                if live_out_node != None:  
                    if p not in p_live:
                        p_live[p] = []
                    p_live[p].append(live_out_node)  
        #get length of fini phase 
        fini_len = 0
        for i in range(self.CGRA_X * self.CGRA_Y):
            if i in p_live:
                fini_len = max(fini_len, len(p_live[i]))
            
        #initialize the fini phase
        for i in range(fini_len):
            if i not in self.fini:
                self.fini[i] = {}
            for j in range(self.CGRA_X * self.CGRA_Y):
                if j not in self.fini[i]:
                    self.fini[i][p] = None

        #create store instructions for the liveout var
        tmp_id = 0
        for p in p_live:
            for i in range(len(p_live[p])):
                tmp = instruction(tmp_id, p_live[p][i].id)
                tmp_id += 1
                tmp.pe = p
                tmp.time = i
                #TODO: check if value to save is in lop or rop
                #get the register that store the value to save in memory
                for e in self.DFG.get_liveout_edges():
                    if e.destination.id == p_live[p][i].id:
                        for inst in instructions[p]:
                            if inst.nodeid == e.source.id:
                                tmp.outreg = inst.outreg

                tmp.opcode = SWD
                self.fini[i][p] = tmp

        #fill the other PEs with NOP instructions
        for t in range(len(self.fini)):
            if t not in self.fini:
                self.fini = {}
            for p in range(self.CGRA_X * self.CGRA_Y):
                if p not in self.fini[t]:
                    self.fini[t][p] = None
                if self.fini[t][p] == None:
                    tmp = instruction(-p-1, -2)
                    tmp.opcode = NOP
                    self.fini[t][p] = tmp
        
    #Generate the mapping after a solution to the SAT problem is found
    #This function also does:
    #1) Register Allocation and Assignment
    #2) Creates: Init+Prolog+Kernel+Epilog+Fini
    #3) Set br address for the node in the kernel
    #TODO: Can be written in a better way and findmapping could be called here
    #TODO: Create other instructions objcts that replace the BR nodes outside the kernel
    #      since those nodes needs a different jumping address (for now done manually)
    def generateMapping(self, instructions):

        self.mapping = {}
        self.generatePKE()
        logging.debug("PKE")
        for i in range(len(self.pke)):
            s = "t: " + str(i) + "     "
            for p in self.pke[i]:
                s += str(self.pke[i][p]) + " "
            logging.debug(s)

        #init ra and do register allocation
        self.ra = RegisterAllocator(self.DFG, self.pke, self.kernel, instructions, self.CGRA_Y, self.CGRA_X, self.CGRA_R)
        graphs = self.ra.generateInterferenceGraphs(self.kernel, self.CGRA_Y * self.CGRA_X, self.DFG, self.ra.instructions, self.CGRA_R)

        self.ra.addInterferenceGraphs(graphs)
        logging.debug("\n\n**************\n\n")
        logging.debug("Interference graphs : " + str(len(graphs)))
        self.ra.allocateRegisters()
        for p in graphs:
            #Uncomment following line to print the interference graphs for each PE
            #graphs[p].printDot(str(p))
            logging.debug("#Nodes: " + str(len(graphs[p].intervals)))
        self.ra.assignRegisters(self.CGRA_Y, self.CGRA_X)
        logging.debug("\n\n**************\n\n")
        
        self.generateInit(instructions)
        self.generateFini(instructions)
        t = 0
        #append init to mapping
        self.mapping = self.init
        t = len(self.mapping)
        init_len = len(self.init)
        prolog_len = len(self.prolog)
        kernel_len = len(self.kernel)
        epilog_len = len(self.epilog)
        fini_len = len(self.fini)
        logging.debug("\n\n**************\n\n")
        logging.debug(f"{init_len = }")
        logging.debug(f"{prolog_len = }")
        logging.debug(f"{kernel_len = }")
        logging.debug(f"{epilog_len = }")
        logging.debug(f"{fini_len = }")
        logging.debug("\n\n**************\n\n")



        logging.debug("\n\n**************\n\n")
        if len(self.init) > 0:
            logging.debug("Init: 0 - " + str(len(self.init) - 1))
        if len(self.prolog) > 0:
            logging.debug("Prolog: " + str(len(self.init)) + " - " + str(len(self.init) + len(self.prolog) - 1))
        logging.debug("Kernel: " + str(len(self.prolog) + len(self.init)) + " - " + str(len(self.init) + len(self.prolog) + len(self.kernel) - 1))
        if len(self.epilog) > 0:
            logging.debug("Epilog: " + str(len(self.init) + len(self.pke) - len(self.epilog)) + " - " + str(len(self.init) + len(self.pke) - 1))
        if len(self.fini) > 0:
            logging.debug("Fini: " + str(len(self.init) + len(self.pke)) + " - " + str(len(self.init) + len(self.pke) + len(self.fini) - 1))
        logging.debug("\n\n**************\n\n")
        #append pke to mapping
        for tk in range(len(self.pke)):
            if (tk + t) not in self.mapping:
                self.mapping[tk + t] = {}
            for pk in range(self.CGRA_Y * self.CGRA_X):
                if pk not in self.mapping[tk + t]:
                    self.mapping[tk + t][pk] = None
                #get instruction
                if pk in instructions:
                    for inst in instructions[pk]:
                        if pk in self.pke[tk]:
                            if inst.nodeid == self.pke[tk][pk]:
                                self.mapping[tk + t][pk] = inst
                #if the pe is empty put a nop instruction on it
                tmp_id = 0
                if self.mapping[tk + t][pk] == None:
                    tmp = instruction(-pk-1, -2)
                    tmp.opcode = NOP
                    self.mapping[tk + t][pk] = tmp
        

        t = len(self.mapping)        
        #append fini to mapping
        for tk in range(len(self.fini)):
            if (tk + t) not in self.mapping:
                self.mapping[tk + t] = {}
            for pk in range(self.CGRA_Y * self.CGRA_X):
                if pk not in self.mapping[tk + t]:
                    self.mapping[tk + t][pk] = None
                #fini is already populated, just copy it into mapping
                self.mapping[tk + t][pk] = self.fini[tk][pk]

        # Add last time slot with EXIT instruction
        t = len(self.mapping)
        if t not in self.mapping:
            self.mapping[t] = {}
        # Fill time slot with NOPs
        for pk in range(self.CGRA_Y * self.CGRA_X):
            if pk not in self.mapping[t]:
                tmp = instruction(-pk-1, -2)
                tmp.opcode = NOP
                self.mapping[t][pk] = tmp
        # Add exit instruction
        tmp = instruction(-3, -2)
        tmp.opcode = EXIT
        self.mapping[t][0] = tmp

        #update br node destination cycle and opcode
        #TODO: fix br problem here
        br_count = 0
        br_to_copy = None
        br_location = []
        # Count how many br instruction there are in the code
        # Number of brs instructions is the same as number of iterations 
        # since we support only DFGs that have exactly 1 br instruction
        for t in self.mapping:
            for p in self.mapping[t]:
                if self.mapping[t][p].getOpcodeName() in BRs:
                    br_count += 1
                    br_location.append(t)
                    br_to_copy = self.mapping[t][p]

        logging.debug(f"Number of br instructions {br_count}")
        logging.debug(f"Loop length should be = Loop lengh - {br_count}")
        logging.debug("")
        logging.debug("If loop length is not know at runtime")
        logging.debug("running the code could produce wrong results")
        logging.debug("if a br in the prologue gets hit")
        # This can be solved by increasing the code length or decreasing the performances
        # Currently we do not deploy any fix, since its outside the scope of our research

        # Create a different instruction for each br and change the jmp location
        # WARNING: Currently we only support DFGs with 1 br instruction
        
        if br_to_copy == None:
            raise Exception("No br instruction in the kernel")
        
        logging.info("BR location in the prologue must be set manually")

        # Update brs before kernel
        for t in range(init_len + prolog_len):#, init_len + prolog_len + kernel_len):
            for p in self.mapping[t]:
                if self.mapping[t][p].getOpcodeName() in BRs:
                    tmp = instruction(0, self.mapping[t][p].nodeid)
                    tmp.pe = self.mapping[t][p].pe
                    tmp.time = t
                    tmp.name = self.mapping[t][p].name
                    tmp.opA = self.mapping[t][p].opA
                    tmp.opB = self.mapping[t][p].opB
                    tmp.LOp = self.mapping[t][p].LOp
                    tmp.ROp = self.mapping[t][p].ROp
                    tmp.outreg = self.mapping[t][p].outreg
                    tmp.predicate = self.mapping[t][p].predicate
                    tmp.immediate = self.mapping[t][p].immediate
                    tmp.muxflag = self.mapping[t][p].muxflag
                    tmp.opcode = self.mapping[t][p].opcode
                    #TODO: compute cycle_destination
                    jmp_destination = -1
                    tmp.cycle_destination = jmp_destination
                    self.mapping[t][p] = tmp

        # Update brs after kernel
        for t in range(init_len + prolog_len + kernel_len, len(self.mapping) - 1):
            for p in self.mapping[t]:
                if self.mapping[t][p].getOpcodeName() in BRs:
                    tmp = instruction(0, self.mapping[t][p].nodeid)
                    tmp.pe = self.mapping[t][p].pe
                    tmp.time = t
                    tmp.name = self.mapping[t][p].name
                    tmp.opA = self.mapping[t][p].opA
                    tmp.opB = self.mapping[t][p].opB
                    tmp.LOp = self.mapping[t][p].LOp
                    tmp.ROp = self.mapping[t][p].ROp
                    tmp.outreg = self.mapping[t][p].outreg
                    tmp.predicate = self.mapping[t][p].predicate
                    tmp.immediate = self.mapping[t][p].immediate
                    tmp.muxflag = self.mapping[t][p].muxflag
                    tmp.opcode = self.mapping[t][p].opcode

                    jmp_destination = t + 1
                    tmp.cycle_destination = jmp_destination
                    self.mapping[t][p] = tmp
        
        # Invert jmp condition for  br in the kernel
        for t in range(init_len + prolog_len, init_len + prolog_len + kernel_len):
            for p in self.mapping[t]:
                if self.mapping[t][p].getOpcodeName() in BRs:
                    self.mapping[t][p].cycle_destination = init_len + prolog_len
                    #invert jump condition
                    if self.mapping[t][p].opcode in BR_OPPOSITES:
                        self.mapping[t][p].opcode = BR_OPPOSITES[self.mapping[t][p].opcode]

    def getAssembly(self) -> str:
        if len(self.mapping) == 0:
            raise Exception("No mapping in memory")

        lines = []
        for t in range(len(self.mapping)):
            lines.append(f"T = {t}")
            for p in range(self.CGRA_X * self.CGRA_Y):    
                lines.append(self.mapping[t][p].getAssemblyStr())

        separator = "| " + " -" * (2 + 2*self.CGRA_X + 2*self.CGRA_X) + " |"
        for t in range(len(self.mapping)):
            lines.append(f"T = {t}")
            lines.append(separator)
            for y in range(self.CGRA_Y):
                line = '|  '
                line += '  ||  '.join([
                    f"{self.mapping[t][x + y * self.CGRA_X].getOpcodeName():4s}"
                    for x in range(self.CGRA_X)
                ])
                line += '  |'
                lines.append(line)
                lines.append(separator)
            lines.append("")

        lines.append("Output of the mapping with node id")
        for t in range(len(self.mapping)):
            lines.append(f"T = {t}")
            lines.append(separator)
            for y in range(self.CGRA_Y):
                line = '|  '
                line += '  ||  '.join([
                    f"{self.mapping[t][x + y * self.CGRA_X].nodeid:2d}"
                    for x in range(self.CGRA_X)
                ])
                line += '  |'
                lines.append(line)
                lines.append(separator)
            lines.append("")
                
        return '\n'.join(lines)
    def generateBinary(self):
        #TODO: Convert in binary code the assembly generated
        pass
