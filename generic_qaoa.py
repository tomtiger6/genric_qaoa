import numpy as np
from scipy.optimize import minimize
from copy import copy
from typing import List, Callable
from qiskit import Aer

from qaoa_circut import SIMULATOR_ENGINE, REAL_ENGINE, QaoaCircut


def select_bitstring(counts):
    return max(counts, key=lambda x: counts[x])


class GenericQAOA(object):
    def __init__(self, clauses: List, p: int, simulate: bool):
        self.clauses = clauses
        self._p = p
        self.shots = 512
        self.backend = Aer.get_backend(SIMULATOR_ENGINE if simulate else REAL_ENGINE)
        self.qubits_indexes = range(self._number_of_bits)
        self.grid_size = (len(clauses) + self._number_of_bits)
        self._betas, self._gammas = self.find_good_theta()
        self.circuit = self._create_circuit()
        self.result = None
        self.expectation = None
        self.selected = None
        self.counts = None

    @property
    def _number_of_bits(self) -> int:
        return max([_clause.msb() for _clause in self.clauses]) + 1

    def _get_execute_circ(self, backend=None):
        if backend is None:
            backend = self.backend
            backend.shots = self.shots

        def execute_circ(theta=None):
            if theta is not None:
                self._update_beta_gamma(theta[:len(theta) // 2], theta[len(theta) // 2:])
            self.counts = backend.run(self.circuit, seed_simulator=13).result().get_counts()
            self.selected = select_bitstring(self.counts)
            self.expectation = sum([_clause.objective(self.selected) for _clause in self.clauses])
            return self.expectation

        return execute_circ

    def run(self):
        backend = self.backend
        backend.shots = self.shots

        execute_circ = self._get_execute_circ(backend)
        self.result = minimize(execute_circ,
                               np.hstack([self._betas, self._gammas]),
                               method='COBYLA')

    def _create_circuit(self):
        qc = QaoaCircut(self._number_of_bits)
        qc.add_hadamard(self.qubits_indexes)
        for i in range(self._p + 1):
            qc.add_prepare_gate(self.clauses, self._gammas[i])
            qc.barrier()
            qc.add_mix_gate(self._betas[i], self.qubits_indexes)
        qc.measure_all()
        return qc

    def __str__(self):
        return self.circuit.draw().__str__()

    def _update_beta_gamma(self, beta, gamma):
        self._betas = copy(beta)
        self._gammas = copy(gamma)
        self.circuit = self._create_circuit()

    def find_good_theta(self):
        self._betas = np.array([])
        self._gammas = np.array([])
        max_step = self._p
        backend = self.backend
        backend.shots = self.shots
        best_betas = np.array([])
        best_gammas = np.array([])
        for step in range(max_step + 1):
            self._p = step
            beta, gamma = self.one_step_grid_search()
            best_betas = np.append(best_betas, beta)
            best_gammas = np.append(best_gammas, gamma)
            self._betas = best_betas
            self._gammas = best_gammas
            print()
        self._p = max_step
        print("selected betta=", best_betas)
        print("selected gamma=", best_gammas)
        return best_betas, best_gammas

    def one_step_grid_search(self):
        """
        Grid search on QAOA angles.

        Returns:
            best_beta, best_gamma (floats): best values of the beta and gamma found.
        """
        best_beta = None
        best_gamma = None
        best_energy = np.inf
        best_selected_counts = 0

        beta_range = np.linspace(0, np.pi, self.grid_size)
        gamma_range = np.linspace(0, 2 * np.pi, self.grid_size)
        _betas = np.copy(self._betas)
        _gammas = np.copy(self._gammas)
        for beta in beta_range:
            print('.', end='')
            for gamma in gamma_range:
                print('.', end='')
                self._update_beta_gamma(np.hstack([_betas, beta]), np.hstack([_gammas, gamma]))
                energy = self._get_execute_circ()()
                selected_counts = self.counts[self.selected]
                if energy < best_energy:
                    best_selected_counts = 0
                    best_energy = energy
                    best_beta = beta
                    best_gamma = gamma
                elif energy == best_energy and best_selected_counts < selected_counts:
                    best_selected_counts = selected_counts
                    best_beta = beta
                    best_gamma = gamma

        return best_beta, best_gamma
