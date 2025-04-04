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


class TestSchedule(unittest.TestCase):
    """
    Tests if the generated schedules respects the constraints that the source arrives before the destination of a forward edge in the DFG
    """

    maxDiff = None

    expected_IIs = {
        "bit_count": (4,),
        "reverse_bits": (3,),
        "gsm": (8,),
        "sha1": (9, 9),
        "sha2": (7,),
        "sqrt": (5,),
        "string_search": (9,),
    }

    def parseDFG(self, path) -> DFG:
        p = Parser()
        edgefile = os.path.join(path, "acc_edges")
        nodefile = os.path.join(path, "acc_nodes")
        p.parseNodeFile(nodefile)
        p.parseEdgeFile(edgefile)
        return p.getDFG()

    def getSchedule(self, dfg: DFG) -> dict[int, list[int]]:
        m = Mapper(CGRA_X, CGRA_Y, CGRA_R, dfg, "", seed=85)
        m.findMapping()
        sched = m.getSchedule()
        self.assertIsNotNone(sched)
        assert sched is not None   # for pylint
        return sched

    def getCyleOfNode(self, node: int, schedule: dict[int, list[int]]):
        for t, nodes in schedule.items():
            if node in nodes:
                return t
        raise ValueError(f"Node {node} not present in schedule {schedule}")

    def get_DFGs(self, path):
        ret = []
        for dir in os.listdir(os.path.join(path, "dfg")):
            ret.append(self.parseDFG(os.path.join(path, "dfg", dir)))
        return ret

    def assertCorrectDependencies(self, schedule: dict[int, list[int]], dfg: DFG):
        for edge in dfg.get_instruction_edges:
            if edge.is_backedge:
                continue

            cycle_source = self.getCyleOfNode(edge.source.id, schedule)
            cycle_dest = self.getCyleOfNode(edge.destination.id, schedule)
            self.assertLess(cycle_source, cycle_dest)

    def _test_benchmark(self, problem):
        path = os.path.join("tests", "res", problem)

        dfgs = self.get_DFGs(path)
        for i, dfg in enumerate(dfgs):
            schedule = self.getSchedule(dfg)
            self.assertEqual(len(schedule), self.expected_IIs[problem][i])
            self.assertCorrectDependencies(schedule, dfg)

    def test_bitcount(self):
        self._test_benchmark("bit_count")

    # TODO: ask Cristian if he fixed the 'call' instruction issue
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
