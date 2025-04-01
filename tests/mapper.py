import unittest
# from z3 import Solver, Context, parse_smt2_string, Not, And, unsat, sat
from z3 import Solver, Context, parse_smt2_string, Not, And, unsat, sat

import os, sys
sys.path.append("..")
from mapper.mapper import Mapper
from mapper.parser import Parser

class TestMapper(unittest.TestCase):
    CGRA_X = 4
    CGRA_Y = 4
    CGRA_R = 10

    def parseDFG(self, path):
        p = Parser()
        edgefile = os.path.join(path, "acc_edges")
        nodefile = os.path.join(path, "acc_nodes")
        p.parseNodeFile(nodefile)
        p.parseEdgeFile(edgefile)
        return p.getDFG()


    def get_DFGs(self, path):
        ret = []
        for dir in os.listdir(os.path.join(path, "dfg")):
            ret.append((dir, self.parseDFG(os.path.join(path, "dfg", dir))))
        return ret

    def are_smt2_files_equivalent(self, formula1, formula2, ctx):
        solver = Solver(ctx=ctx)
        solver.add(Not(And(*formula1) == And(*formula2)))
        # solver.add(And(*formula2))

        return solver.check() == unsat

    def _test_benchmark(self, problem):
        root_path = "tests/res/" + problem
        dfgs = self.get_DFGs(root_path)
        for i, dfg in dfgs:
            ctx = Context()
            m = Mapper(self.CGRA_X, self.CGRA_Y, self.CGRA_R, dfg, problem)
            m.findMapping()
            actual = parse_smt2_string(str(m.s.to_smt2()), ctx=ctx)
            path = os.path.join(root_path, "smt2", str(i), problem + "_" + str(m.II) + ".smt2")

            with open(path, "r") as f:
                content = f.read()
                expected = parse_smt2_string(content, ctx=ctx)
                self.assertTrue(self.are_smt2_files_equivalent(actual, expected, ctx), f"Failed on {problem} {i}, II = {m.II}")

            m.s.reset()
    def test_bitcount(self):
        self._test_benchmark("bit_count")

    def test_gsm(self):
        self._test_benchmark("gsm")

    def test_reverse_bits(self):
        self._test_benchmark("reverse_bits")

    def test_sha1(self):
        self._test_benchmark("sha1")

    def test_sha2(self):
        self._test_benchmark("sha2")

    def test_sqrt(self):
        self._test_benchmark("sqrt")

    def test_string_search(self):
        self._test_benchmark("string_search")

