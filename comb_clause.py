from abc import abstractmethod

from sympy import symbols, Symbol

from clause import Clause
from typing import List


class CombClause(Clause):
    def __init__(self, one_literals: List[int], zero_literals: List[int], weight: int):
        for l in one_literals:
            assert l not in zero_literals
        self.one_literals = one_literals
        self.zero_literals = zero_literals
        self.weight = weight
        self.width = self.msb + 1
        self.size = len(one_literals) + len(zero_literals)

    @property
    def msb(self):
        return max(self.one_literals + self.zero_literals)

    def parse_h(self, to_qubit_index) -> Symbol:
        one_symbols = [(1 - symbols('z' + str(l))) for l in self.one_literals]
        zero_symbols = [(1 + symbols('z' + str(l))) for l in self.zero_literals]
        H = 1
        for sym in one_symbols:
            H *= sym
        for sym in zero_symbols:
            H *= sym
        return H.expand()

    @staticmethod
    def to_qubit_index(term):
        return int(term.name[1:])

    def objective(self, selected_bitstring):
        for index, str_value in enumerate(selected_bitstring):
            value = int(str_value)
            if value == 1 and index not in self.one_literals:
                return 0
            if value == 0 and index not in self.zero_literals:
                return 0
        return 1
