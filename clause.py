from abc import abstractmethod

from qaoa_circut import QaoaCircut


class Clause:
    @property
    @abstractmethod
    def msb(self):
        pass

    @abstractmethod
    def objective(self, selected_bitstring):
        pass
