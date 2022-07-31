import matplotlib.pyplot as plt
from qiskit.visualization import plot_histogram

from comb_clause import CombClause
from vfq_clause import VQFClause
from vqf.vqf.preprocessing import create_clauses, factor_56153, factor_291311
from generic_qaoa import *


def get_pq_from_selected(p_dict, q_dict, selected):
    for index, value in p_dict.items():
        if isinstance(value, int):
            continue
        for term in value.free_symbols:
            p_dict[index] = p_dict[index].subs(term, selected[symbol_to_qubit_index[term]])
    for index, value in q_dict.items():
        if isinstance(value, int):
            continue
        for term in value.free_symbols:
            q_dict[index] = q_dict[index].subs(term, selected[symbol_to_qubit_index[term]])
    q_str = [str(v) for v in q_dict.values()]
    q_str.reverse()
    q = int(''.join(q_str), 2)
    p_str = [str(v) for v in p_dict.values()]
    p_str.reverse()
    p = int(''.join(p_str), 2)
    return p, p_dict, q, q_dict


if __name__ == '__main__':
    # example for MaxCut
    clauses = [CombClause([0], [1], 1), CombClause([1], [0], 1), CombClause([2], [1], 1), CombClause([1], [2], 1),
               CombClause([2], [3], 1), CombClause([3], [2], 1), CombClause([3], [0], 1), CombClause([0], [3], 1)]
    qaoa = GenericQAOA(clauses, 2, True)
    circ = qaoa.circuit
    print(circ.draw())
    plt.show()
    qaoa.run()
    plot_histogram(qaoa.counts)
    plt.show()
    print(qaoa.selected)
    # VQF
    # define m=p*q
    m = 7*5
    # 1. define clauses
    if m == 56153:
        p_dict, q_dict, z_dict, clauses = factor_56153()
    elif m == 291311:
        p_dict, q_dict, z_dict, clauses = factor_291311()
    else:
        p_dict, q_dict, z_dict, clauses = create_clauses(m, verbose=True)

    free_symbols = set().union(*[clause.free_symbols for clause in clauses])
    qubit_index_to_symbol = {i: sym for i, sym in enumerate(free_symbols)}
    symbol_to_qubit_index = {sym: i for i, sym in qubit_index_to_symbol.items()}
    final_clauses = [VQFClause((clause * clause).expand(), len(free_symbols) - 1, m, qubit_index_to_symbol) for clause
                     in
                     clauses if clause != 0]
    vqf_qaoa = GenericQAOA(final_clauses, p=4, simulate=True)

    circ = vqf_qaoa.circuit
    print(circ.draw())
    vqf_qaoa.run()
    plot_histogram(vqf_qaoa.counts)
    plt.show()
    print(vqf_qaoa.result)
    print(vqf_qaoa.selected)
    p, p_dict, q, q_dict = get_pq_from_selected(p_dict, q_dict, vqf_qaoa.selected)
    n = len(p_dict)+len(q_dict)
    print("p,q=", p, q)
    if p * q != m:
        print("Trying to fix with bit-flip.")
        for i in range(len(p_dict)):
            for j in range(len(q_dict)):
                new_p: int
                if p_dict[i] == 1:
                    new_p = p - 2**i
                else:
                    new_p = p + 2**i
                new_q: int
                if q_dict[j] == 1:
                    new_q = q - 2**j
                else:
                    new_q = q + 2**j
                if new_q == m or new_p == m:
                    break
                if new_p * q == m:
                    p = new_p
                elif p * new_q == m:
                    q = new_q
                if new_p * new_q == m:
                    p = new_p
                    q = new_q
                if p * q == m:
                    break
            if p * q == m:
                break

    print(f"final results: {p}*{q}={m}")
