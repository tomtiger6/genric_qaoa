from sympy import *
from qiskit import QuantumCircuit

SIMULATOR_ENGINE = 'qasm_simulator'
REAL_ENGINE = ''


class QaoaCircut(QuantumCircuit):
    def __init__(self, *regs, to_qubit_index=None):
        super().__init__(*regs)
        self.to_qubit_index = to_qubit_index

    def append_clause_to_circut(self, expanded_H, angle):
        args = Add.make_args(expanded_H)
        for _arg in args:
            self._add_z_rotation(_arg, angle)

    def _add_cnot(self, control, target):
        control_index, target_index = self.to_qubit_index(control), self.to_qubit_index(target)
        self.cnot(control_index, target_index)

    def _add_z_rotation(self, _arg, angle):
        if _arg.is_number:
            return
        terms = Mul.make_args(_arg)
        _terms, angle = (terms[1:], float(terms[0]*angle)) if terms[0].is_number else (terms, angle)
        if len(_terms) == 1:
            self.barrier()
            self.rz(angle, self.to_qubit_index(_terms[0]))
            self.barrier()
            return
        self.barrier()
        for i in range(len(_terms) - 1):
            self._add_cnot(_terms[i], _terms[i + 1])
        self.rz(angle, self.to_qubit_index(_terms[-1]))
        for i in reversed(range(len(_terms) - 1)):
            self._add_cnot(_terms[i], _terms[i + 1])
        self.barrier()

    def add_hadamard(self, qubits_indexes):
        for q_idx in qubits_indexes:
            self.h(q_idx)

    def add_prepare_gate(self, clauses, angle):
        for clause in clauses:
            self.append_clause_to_circut(clause.parse_h(), angle)

    def add_mix_gate(self, angle, qubits_indexes):
        for q_idx in qubits_indexes:
            self.rx(2 * angle, q_idx)
