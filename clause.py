from abc import abstractmethod

from qaoa_circut import QaoaCircut


class Clause:
    @abstractmethod
    def msb(self):
        pass

    @abstractmethod
    def parse_h(self, to_qubit_index):
        pass

    @abstractmethod
    def objective(self, selected_bitstring):
        pass
