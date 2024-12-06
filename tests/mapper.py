import unittest

import os, sys
sys.path.append("..")
from mapper.mapper import Mapper
from mapper.parser import Parser

class TestMapper(unittest.TestCase):
    CGRA_X = 4
    CGRA_Y = 4
    CGRA_R = 100

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

    def _test_benchmark(self, problem):
        path = "tests/res/" + problem
        dfgs = self.get_DFGs(path)
        for i, dfg in dfgs:
            m = Mapper(self.CGRA_X, self.CGRA_Y, self.CGRA_R, dfg, problem)
            m.findMapping()
            smt2 = str(m.s.to_smt2())

            with open(os.path.join(path, "smt2", str(i), problem + "_" + str(m.II) + ".smt2")) as f:
                expected = str(f.read())

                self.assertEqual(smt2, expected, f"Failed on {problem} {i}, II = {m.II}")

            m.s.reset()
    def test_bitcount(self):
        self._test_benchmark("bitcount")

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

