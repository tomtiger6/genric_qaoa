from sympy import *

from clause import Clause


def count_unique(symbols) -> int:
    pass


def _parse_clause(clauses, symbol_to_qubit):
    new_clauses = clauses.expand()
    for sym in new_clauses.free_symbols:
        new_clauses = new_clauses.subs(sym, f"z{symbol_to_qubit[sym]}").expand()
    for sym in new_clauses.free_symbols:
        new_sym = (1 / 2) * (1 - sym)
        new_clauses = new_clauses.subs(sym, new_sym).expand()
    for sym in new_clauses.free_symbols:
        new_clauses = new_clauses.subs(sym ** 2, 1).expand()

    return new_clauses.expand()


class VQFClause(Clause):

    def msb(self):
        return self._msb

    def __init__(self, clause: Symbol, msb, m, qubit_to_symbol_map):
        """
        In the Clause constructor we must translate the clauses to Hamiltonian
        """
        self.clause = _parse_clause(clause, {sym: idx for idx, sym in qubit_to_symbol_map.items()})
        self.m = m
        self._msb = msb
        self.qubit_to_symbol_map = qubit_to_symbol_map

    def objective(self, selected_bitstring):
        subs_map = {f"z{idx}": 1 if value == '1' else -1 for idx, value in enumerate(selected_bitstring)}
        obj = float(self.clause.subs(subs_map))
        return obj


