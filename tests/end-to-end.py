import unittest

import os, sys

sys.path.append("..")
from mapper.DFG import DFG
from mapper.main import generateInstructions
from mapper.mapper import Mapper
from mapper.parser import Parser

CGRA_X = 4
CGRA_Y = 4
CGRA_R = 100


class TestEndToEnd(unittest.TestCase):
    maxDiff = None

    def parseDFG(self, path):
        p = Parser()
        edgefile = os.path.join(path, "acc_edges")
        nodefile = os.path.join(path, "acc_nodes")
        p.parseNodeFile(nodefile)
        p.parseEdgeFile(edgefile)
        return p.getDFG()

    def getAssembly(self, dfg: DFG) -> str:
        m = Mapper(CGRA_X, CGRA_Y, CGRA_R, dfg, "", seed=85)
        m.findMapping()
        kernel = m.getKernel()
        instructions = generateInstructions(kernel, dfg)
        m.generateMapping(instructions)
        return m.getAssembly()

    def get_DFGs(self, path):
        ret = []
        for dir in os.listdir(os.path.join(path, "dfg")):
            ret.append(self.parseDFG(os.path.join(path, "dfg", dir)))
        return ret

    def _test_benchmark(self, problem):
        path = os.path.join("tests", "res", problem)

        dfgs = self.get_DFGs(path)
        for i, dfg in enumerate(dfgs, 1):
            actual_assembly = self.getAssembly(dfg)

            # with open(os.path.join(path, "assemblies", str(i), "assembly"), "w") as f:
            #     f.write(actual_assembly)

            with open(os.path.join(path, "assemblies", str(i), "assembly")) as f:
                expected_assembly = f.read()

            self.assertEqual(
                expected_assembly,
                actual_assembly,
                f"Benchmark {problem} (#dfg: {i})doesn't have matching final assembly",
            )

    def test_bitcount(self):
        self._test_benchmark("bit_count")

    # TODO: ask Cristian if he fixed the 'call' instruction issue
    # def test_gsm(self):
    #     self._test_benchmark("gsm")

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
