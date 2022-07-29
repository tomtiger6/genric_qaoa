from copy import copy
from typing import List
from sympy import *
from qiskit import Aer
from qiskit import QuantumCircuit, execute
from matplotlib import pyplot as plt
from qiskit.tools import job_monitor
from qiskit.visualization import plot_histogram

SIMULATOR_ENGINE = 'local_qasm_simulator'
REAL_ENGINE = ''


class QaoaCircut(QuantumCircuit):
    def __init__(self, *regs):
        super().__init__(*regs)

    def append_clause_to_circut(self, expanded_H, angle):
        args = Add.make_args(expanded_H)
        for _arg in args:
            self._add_z_rotation(_arg, angle)

    def _add_cnot(self, control, target):
        control_index, target_index = Clause.to_qubit_index(control), Clause.to_qubit_index(target)
        self.cnot(control_index, target_index)

    def _add_z_rotation(self, _arg, angle):
        if _arg == 1:
            return
        terms = Mul.make_args(_arg)
        _terms, angle = (terms[1:], -angle) if terms[0] == -1 else (terms, angle)
        if len(_terms) == 1:
            self.barrier()
            self.rz(angle, Clause.to_qubit_index(_terms[0]))
            self.barrier()
            return
        self.barrier()
        for i in range(len(_terms) - 1):
            self._add_cnot(_terms[i], _terms[i + 1])
        self.rz(angle, Clause.to_qubit_index(_terms[-1]))
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


class Clause(object):
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

    def parse_h(self) -> Symbol:
        one_symbols = [(1 - symbols('z' + str(l))) for l in self.one_literals]
        zero_symbols = [(1 + symbols('z' + str(l))) for l in self.zero_literals]
        H = 1
        for sym in one_symbols:
            H *= sym
        for sym in zero_symbols:
            H *= sym
        return H.expand()

    def as_circuit(self, angle) -> QaoaCircut:
        qc = QaoaCircut(self.width)
        H = self.parse_h()
        qc.append_clause_to_circut(H.expand(), angle)
        return qc

    @staticmethod
    def to_qubit_index(term):
        return int(term.name[1:])


class GenericQAOA(object):
    def __init__(self, clauses: List[Clause], p: int, simulate: bool):
        self.clauses = clauses
        self.p = p
        self.beta = [1] * p
        self.gamma = [2] * p
        self.shots = 512
        self.backend = SIMULATOR_ENGINE if simulate else REAL_ENGINE
        self.result = None
        self.expectation = None
        self.qubits_indexes = range(self.number_of_bits)
        self.circuit = self._create_circuit()

    @property
    def number_of_bits(self) -> int:
        return max([clause.msb for clause in self.clauses]) + 1

    def run(self):
        for _ in range(self.p):
            self._execute_circuit()
            self._update_theta()
        return self.calc_expectation()

    def add_hadamard(self, qc: QuantumCircuit):
        for q_idx in self.qubits_indexes:
            qc.h(q_idx)
        return qc

    def add_prepare_gate(self, qc: QaoaCircut, angle):
        for clause in self.clauses:
            qc.append_clause_to_circut(clause.parse_h(), angle)
        return qc

    def add_mix_gate(self, qc: QuantumCircuit, angle):
        for q_idx in self.qubits_indexes:
            qc.rx(2 * angle, q_idx)
        return qc

    def _create_circuit(self):
        qc = QaoaCircut(self.number_of_bits)
        qc.add_hadamard(self.qubits_indexes)
        for i in range(0, self.p):
            qc.add_prepare_gate(self.clauses, self.gamma[i])
            qc.add_mix_gate(self.beta[i], self.qubits_indexes)
        qc.measure_all()
        return qc

    def __str__(self):
        return self.circuit.draw().__str__()

    def _execute_circuit(self):
        self.result = None  # execute(self.circuit)
        print(self.result)

    def calc_expectation(self):
        pass

    def _opt_results(self):
        pass

    def _update_theta(self):
        beta, gamma = self._opt_results()
        self.beta = copy(beta)
        self.gamma = copy(gamma)
        self.circuit = self._create_circuit()


if __name__ == '__main__':
    clause = Clause([0, 2], [1, 4], 1)
    qaoa = GenericQAOA([clause], 2, true)
    circ = qaoa.circuit
    circ.draw(output="mpl")
    plt.show()
    job = execute(circ, backend=Aer.get_backend('qasm_simulator'))
    job_monitor(job, interval=2)
    answer = job.result().get_counts()
    plot_histogram(answer)
    plt.show()
