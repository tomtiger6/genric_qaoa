from sympy import *

from clause import Clause


def count_unique(symbols) -> int:
    pass


class VQFClause(Clause):
    def parse_h(self):
        new_H = self.H.copy()
        for l in self.unique:
            new_sym = (1 / 2) * (1 - symbols('z' + str(self.to_qubit_index(l))))
            new_H = new_H.subs(l, new_sym).expand()
        for sym in new_H.free_symbols:
            new_H = new_H.subs(sym * sym, 1).expand()

        return new_H.expand()

    def msb(self):
        return self.msb

    def __init__(self, _symbols: Symbol, to_qubit_index, m):
        self.H = _symbols.expand()
        self.to_qubit_index = to_qubit_index
        self.unique = list(_symbols.free_symbols)
        self.H = self.parse_h()
        self.msb = len(self.H.free_symbols)-1
        self.m = m

    def objective(self, selected_bitstring):
        subs_map = {f"z{idx}": 1 if value is '1' else -1 for idx,value in enumerate(selected_bitstring)}
        return float(self.H.subs(subs_map))


    @classmethod
    def make_to_qubit_index_function(cls, clauses):
        unique_symbols = list(set().union(*[clause.free_symbols for clause in clauses]))

        def map_function(term):
            if 'z' in str(term) and '_' not in str(term):
                return int(str(term)[1:])
            return unique_symbols.index(term)

        return map_function

