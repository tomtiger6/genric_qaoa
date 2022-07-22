import copy
from typing import Callable, List
import numpy as np
from qiskit import QuantumCircuit
import qiskit
from qiskit.circuit import Instruction
from sympy import *

SIMULATOR_ENGINE = 'local_qasm_simulator'
REAL_ENGINE = ''


class Clause(object):
    def __init__(self, one_literals: List[int], zero_literals: List[int], weight: int):
        for l in one_literals:
            assert l not in zero_literals
        self.one_literals = one_literals
        self.zero_literals = zero_literals
        self.weight = weight
        self.size = len(one_literals) + len(zero_literals)

    @property
    def msb(self):
        return max(self.one_literals + self.zero_literals)

    def as_circuit(self, angle) -> QuantumCircuit:
        one_symbols = [(1-symbols('z'+str(l))) for l in self.one_literals]
        zero_symbols = [(1+symbols('z'+str(l))) for l in self.zero_literals]
        H = 1
        for sym  in one_symbols:
            H *= sym
        for sym  in zero_symbols:
            H *= sym
        return self.to_circut(H.expand(), self.size, angle)

    @staticmethod
    def to_circut(symbol, size, angle) -> QuantumCircuit:
        args = Add.make_args(symbol)
        qc = QuantumCircuit(size)
        for arg in args:
            result = Clause.to_z_rotation(arg, size, angle)
            if result is not None:
                qc.append(result, range(size))
        return qc
    
    @staticmethod
    def to_z_rotation(arg: Symbol, size, angle) -> QuantumCircuit:
        qc = QuantumCircuit(size)
        if arg == 1:
            return None
        terms = Mul.make_args(arg)
        _terms = terms[1:] if terms[0] == -1 else terms
        if len(_terms) == 1:
            qc.rz(angle, Clause.to_qubit_index(_terms[0]))
            return qc
        for i in range(len(_terms)-1):
            qc.append(Clause.to_cnot(_terms[i],_terms[i+1], size), range(size))
        qc.rz(angle, Clause.to_qubit_index(_terms[-1]))
        for i in reversed(range(len(_terms)-1)):
            qc.append(Clause.to_cnot(_terms[i],_terms[i+1], size), range(size))
        return qc

    @staticmethod
    def to_cnot(control, target, size):
        qc = QuantumCircuit(size)
        control_index, target_index = Clause.to_qubit_index(control), Clause.to_qubit_index(target)
        qc.cnot(control_index, target_index)
        return qc

    @staticmethod
    def to_qubit_index(term):
        return int(term.name[1:])

class GenericQAOA(object):
    def __init__(self, clauses: List[Clause], p: int, simulate: bool):
        self.clauses = clauses
        self.p = p
        self.beta = [0] * p
        self.gamma = [0] * p
        self.shots = 512
        self.backend = SIMULATOR_ENGINE if simulate else REAL_ENGINE
        self.result = None
        self.expectation = None
        self.qubits_indexes = range(self.number_of_bits)
        self.circuit = self._create_circuit()

    @property
    def number_of_bits(self) -> int:
        return max([clause.msb for clause in self.clauses])

    def run(self):
        for _ in range(self.p):
            self._execute_circuit()
            self._update_theta()
        return self.calc_expectation()

    def add_hadamard(self, qc: QuantumCircuit):
        for q_idx in self.qubits_indexes:
            qc.h(q_idx)
        return qc

    def add_prepare_gate(self, qc: QuantumCircuit, angle):
        for clause in self.clauses:
            qc = qc.append(clause.as_circuit(angle), self.number_of_bits)
        return qc

    def add_mix_gate(self, qc: QuantumCircuit, angle):
        for q_idx in self.qubits_indexes:
            qc.rx(2 * angle, q_idx)
        return qc

    def _create_circuit(self):
        qc = QuantumCircuit(self.size)
        qc = self.add_hadamard(qc)
        for i in range(0, self.p):
            qc = self.add_prepare_gate(qc, self.gamma[i])
            qc = self.add_mix_gate(qc, self.beta[i])
        qc.measure_all()
        return qc

    def _execute_circuit(self):
        pass

    def calc_expectation(self):
        pass

    def _update_theta(self):
        pass


if __name__ == '__main__':
    clause = Clause([0,1,2],[3,4,5],1)
    qc = clause.as_circuit(0)
    print(qc.draw())
