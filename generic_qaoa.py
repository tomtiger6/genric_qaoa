from scipy.optimize import minimize

import dataclasses
from typing import List, Callable, Tuple, Any
from qiskit_ibm_runtime import QiskitRuntimeService
import numpy as np
from qiskit import Aer, IBMQ

from qaoa_circuit import QaoaCircuitFactory

SIMULATOR_ENGINE = 'aer_simulator'
REAL_ENGINE = ''
TOKEN = '8e3dad95805407e1f5eaa12f1e35089a95e65638fcd0ed837f4e4f64ccced5471c2a85c124b05552e3804dc6080b8aa70a0b3636723fb047bb30031a4af28776'
IBMQ.save_account(TOKEN, overwrite=True)


class GenericQaoa(object):
    def __init__(self, **qaoa_kwargs):
        self.qaoa_circuit_component = QaoaCircuitComponent(**qaoa_kwargs)

    @property
    def last_result(self):
        return self.qaoa_circuit_component.results[-1]

    @property
    def circuit(self):
        return self.qaoa_circuit_component.circuit

    def run(self):
        execute_circ = self.qaoa_circuit_component.get_execution_function()
        x0 = self.qaoa_circuit_component.best_angles
        result = minimize(fun=execute_circ,
                          x0=x0,
                          method=self.qaoa_circuit_component.minimize_method)
        return result


@dataclasses.dataclass
class QaoaResults:
    selected: str
    counts_histogram: dict


@dataclasses.dataclass
class QaoaCircuitComponent(object):
    _p: int
    _clauses: List
    _qbits: List
    _grid_size: int
    _minimize_method: str = 'COBYLA'
    _simulate: bool = True
    _shots: int = 512
    _backend = None
    results: List[QaoaResults] = dataclasses.field(default_factory=lambda: [])

    def __post_init__(self):
        if self._simulate:
            self._backend = Aer.get_backend(SIMULATOR_ENGINE)
        else:
            provider = IBMQ.load_account()
            self._backend = provider.backends.simulator_statevector
        self._backend.shots = self._shots

    @property
    def backend(self):
        return self._backend

    @property
    def minimize_method(self):
        return self._minimize_method

    @property
    def best_angles(self):
        best_angles = self._find_best_angles()
        print(best_angles)
        return best_angles

    @property
    def circuit(self):
        angles = [0.] * 2 * self._p
        return QaoaCircuitFactory.create_circuit(self._clauses,
                                                 angles[:len(angles) // 2],
                                                 angles[len(angles) // 2:],
                                                 self._p, len(self._qbits))

    def get_execution_function(self, return_also_counts_histogram=False) -> Callable[[List], float]:
        def execution_function(angles: List):
            circuit = QaoaCircuitFactory.create_circuit(self._clauses,
                                                        angles[:len(angles) // 2],
                                                        angles[len(angles) // 2:],
                                                        self._p, len(self._qbits))
            counts_histogram = self._backend.run(circuit).result().get_counts()
            selected = max(counts_histogram, key=lambda bitstring: counts_histogram[bitstring])
            energy: float = sum([clause.objective(selected) for clause in self._clauses])
            self.results.append(QaoaResults(selected, counts_histogram))
            if return_also_counts_histogram:
                return energy, counts_histogram
            return energy

        return execution_function

    def _find_best_angles(self):
        """
           Grid search on QAOA angles.

           Returns:
               best_beta, best_gamma (floats): best values of the beta and gamma found.
       """
        max_step = self._p
        best_betas = np.array([])
        best_gammas = np.array([])
        for step in range(max_step + 1):
            self._p = step
            beta, gamma = self.one_step_grid_search(best_betas, best_gammas)
            best_betas = np.append(best_betas, beta)
            best_gammas = np.append(best_gammas, gamma)
        self._p = max_step
        return best_betas, best_gammas

    def one_step_grid_search(self, _betas, _gammas):
        best_beta = None
        best_gamma = None
        best_counts = 0
        best_energy = np.inf
        beta_range = np.linspace(0, np.pi, self._grid_size)
        gamma_range = np.linspace(0, 2 * np.pi, self._grid_size)
        for beta in beta_range:
            for gamma in gamma_range:
                energy, counts_histogram = self.get_execution_function(return_also_counts_histogram=True)(
                    np.hstack([_betas, beta, _gammas, gamma]))
                if energy == best_energy:
                    selected_bitstring = max(counts_histogram, key=lambda bitstring: counts_histogram[bitstring])
                    if best_counts < counts_histogram[selected_bitstring]:
                        best_counts = counts_histogram[selected_bitstring]
                        best_beta = beta
                        best_gamma = gamma
                if energy < best_energy:
                    best_counts = 0
                    best_energy = energy
                    best_beta = beta
                    best_gamma = gamma

        return best_beta, best_gamma
