import unittest

import os, sys
sys.path.append("..")
from mapper.parser import Parser

class TestMapper(unittest.TestCase):
    CGRA_X = 4
    CGRA_Y = 4
    CGRA_R = 100
    maxDiff = None

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
            ret.append(self.parseDFG(os.path.join(path, "dfg", dir)))
        return ret

    def _test_benchmark(self, problem):
        path = "tests/res/" + problem
        dfgs = self.get_DFGs(path)
        for i, dfg in enumerate(dfgs, 1):
            with open(os.path.join(path, "dfg", str(i), "expected_dfg.txt")) as f:
                expected = f.read()
                self.assertEqual(str(dfg), expected)

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

