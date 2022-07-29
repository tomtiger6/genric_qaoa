from scipy.optimize import minimize
from copy import copy
from typing import List, Callable
from sympy import *
from qiskit import Aer
from qiskit import QuantumCircuit
from matplotlib import pyplot as plt
from qiskit.visualization import plot_histogram

from comb_clause import CombClause
from qaoa_circut import SIMULATOR_ENGINE, REAL_ENGINE, QaoaCircut


def select_bitstring(counts):
    return max(counts, key=lambda x: counts[x])


class GenericQAOA(object):
    def __init__(self, clauses: List, p: int, simulate: bool, to_qubit_index: Callable):
        self.clauses = clauses
        self.p = p
        self.beta = [1.] * p
        self.gamma = [1.] * p
        self.shots = 512
        self.backend = Aer.get_backend(SIMULATOR_ENGINE if simulate else REAL_ENGINE)
        self.result = None
        self.expectation = None
        self.qubits_indexes = range(self.number_of_bits)
        self.to_qubit_index = to_qubit_index
        self.circuit = self._create_circuit()
        self.counts = None
        self.selected = None
    @property
    def number_of_bits(self) -> int:
        return max([_clause.msb for _clause in self.clauses]) + 1

    def run(self):
        backend = self.backend
        backend.shots = self.shots

        def execute_circ(theta):
            self._update_theta(theta)
            counts = backend.run(self.circuit, seed_simulator=13).result().get_counts()
            self.selected = select_bitstring(counts)
            self.counts = counts
            return self.calc_expectation(self.selected)

        self.result = minimize(execute_circ,
                               self.beta + self.gamma,
                               method='COBYLA')
        plot_histogram(self.counts)
        plt.show()

    def _create_circuit(self):
        print(f"creating circuit with {self.gamma=}, {self.beta=}")
        qc = QaoaCircut(self.number_of_bits, to_qubit_index=self.to_qubit_index)
        qc.add_hadamard(self.qubits_indexes)
        for i in range(0, self.p):
            qc.add_prepare_gate(self.clauses, self.gamma[i])
            qc.add_mix_gate(self.beta[i], self.qubits_indexes)
        qc.measure_all()
        return qc

    def __str__(self):
        return self.circuit.draw().__str__()

    def calc_expectation(self, selected_bitsrting):
        return sum([_clause.objective(selected_bitsrting) for _clause in self.clauses])

    def _update_theta(self, theta):
        beta, gamma = theta[:len(theta) // 2], theta[len(theta) // 2:]
        self.beta = copy(beta)
        self.gamma = copy(gamma)
        self.circuit = self._create_circuit()
