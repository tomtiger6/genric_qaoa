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
        self.size = len(one_literals) + len(zero_literals)
        self.clause = self._parse_h()

    @property
    def msb(self):
        return max(self.one_literals + self.zero_literals)

    def _parse_h(self) -> Symbol:
        one_symbols = [(1 - symbols('z' + str(l))) for l in self.one_literals]
        zero_symbols = [(1 + symbols('z' + str(l))) for l in self.zero_literals]
        new_clause = 1
        for sym in one_symbols:
            new_clause *= sym
        for sym in zero_symbols:
            new_clause *= sym
        return new_clause.expand()

    @staticmethod
    def to_qubit_index(term):
        return int(term.name[1:])

    def objective(self, selected_bitstring):
        for l in self.one_literals:
            if selected_bitstring[-l] == '0':
                return 0
        for l in self.zero_literals:
            if selected_bitstring[-l] == '1':
                return 0

        return -1
