import matplotlib.pyplot as plt
from qiskit.visualization import plot_histogram

from combinatorics_clause import CombinatoricsClause
from utils import get_pq_from_selected
from mathematical_clause import MathematicalClause
from vqf.vqf.preprocessing import create_clauses, factor_56153, factor_291311
from generic_qaoa import *

if __name__ == '__main__':
    # example for MaxCut
    clauses = [CombinatoricsClause([0], [1]), CombinatoricsClause([1], [0]), CombinatoricsClause([2], [1]), CombinatoricsClause([1], [2]),
               CombinatoricsClause([2], [3]), CombinatoricsClause([3], [2]), CombinatoricsClause([3], [0]), CombinatoricsClause([0], [3])]

    qaoa = GenericQaoa(_p=2,
                       _clauses=clauses,
                       _qbits=range(4),
                       _grid_size=10,
                       _simulate=False)
    circ = qaoa.circuit
    qaoa.run()
    plot_histogram(qaoa.last_result.counts_histogram)
    plt.show()
    print(qaoa.last_result.selected)
    # VQF
    # define m=p*q
    # m = 11*5
    # # 1. define clauses
    # if m == 56153:
    #     p_dict, q_dict, z_dict, clauses = factor_56153()
    # elif m == 291311:
    #     p_dict, q_dict, z_dict, clauses = factor_291311()
    # else:
    #     p_dict, q_dict, z_dict, clauses = create_clauses(m, verbose=True)
    #
    # free_symbols = set().union(*[clause.free_symbols for clause in clauses])
    # qubit_index_to_symbol = {i: sym for i, sym in enumerate(free_symbols)}
    # symbol_to_qubit_index = {sym: i for i, sym in qubit_index_to_symbol.items()}
    # final_clauses = [MathematicalClause((clause * clause).expand(), symbol_to_qubit_index) for clause
    #                  in
    #                  clauses if clause != 0]
    # vqf_qaoa = GenericQaoa(_p=3,
    #                        _clauses=final_clauses,
    #                        _qbits=range(len(free_symbols)),
    #                        _grid_size=25)
    #
    # circ = vqf_qaoa.circuit
    # vqf_qaoa.run()
    # plot_histogram(vqf_qaoa.last_result.counts_histogram)
    # plt.show()
    # print(vqf_qaoa.last_result.selected)
    # p, p_dict, q, q_dict = get_pq_from_selected(p_dict, q_dict, vqf_qaoa.last_result.selected, symbol_to_qubit_index)
    # n = len(p_dict) + len(q_dict)
    # print("p,q=", p, q)
    # if p * q != m:
    #     print("Trying to fix with bit-flip.")
    #     for i in range(len(p_dict)):
    #         for j in range(len(q_dict)):
    #             new_p: int
    #             if p_dict[i] == 1:
    #                 new_p = p - 2 ** i
    #             else:
    #                 new_p = p + 2 ** i
    #             new_q: int
    #             if q_dict[j] == 1:
    #                 new_q = q - 2 ** j
    #             else:
    #                 new_q = q + 2 ** j
    #             if new_q == m or new_p == m:
    #                 break
    #             if new_p * q == m:
    #                 p = new_p
    #             elif p * new_q == m:
    #                 q = new_q
    #             if new_p * new_q == m:
    #                 p = new_p
    #                 q = new_q
    #             if p * q == m:
    #                 break
    #         if p * q == m:
    #             break
    #
    # print(f"final results: {p}*{q}={p*q}?={m}")
