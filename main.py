from comb_clause import CombClause
from vfq_clause import VQFClause
from vqf.vqf.preprocessing import create_clauses
from generic_qaoa import *

if __name__ == '__main__':
    # # example for MaxCut
    # clauses = [CombClause([0], [1], 1), CombClause([1], [0], 1), CombClause([2], [1], 1), CombClause([1], [2], 1),
    #            CombClause([2], [3], 1), CombClause([3], [2], 1), CombClause([3], [0], 1), CombClause([0], [3], 1)]
    # qaoa = GenericQAOA(clauses, 5, true,to_qubit_index=CombClause.to_qubit_index)
    # circ = qaoa.circuit
    # circ.draw(output="mpl")
    # plt.show()
    # qaoa.run()
    # print(qaoa.result)
    # VQF
    # define m=p*q
    m = 233*241
    # 1. define clauses
    p_dict, q_dict, z_dict, clauses = create_clauses(m)
    # 3. create to_qubit_index function
    to_qubit_index = VQFClause.make_to_qubit_index_function(clauses)

    # 4. create QAOA circut
    final_clauses = [VQFClause((clause * clause).expand(), to_qubit_index, m) for clause in
                     clauses if clause != 0]
    vqf_qaoa = GenericQAOA(final_clauses, p=2, simulate=true, to_qubit_index=to_qubit_index)

    # 5. run
    circ = vqf_qaoa.circuit
    circ.draw(output="mpl")
    plt.show()
    vqf_qaoa.run()
    print(vqf_qaoa.result)
    print(vqf_qaoa.selected)
    for k, v in p_dict.items():
        if isinstance(v, int):
            continue
        for term in v.free_symbols:
            p_dict[k] = p_dict[k].subs(term, vqf_qaoa.selected[to_qubit_index(term)])
    for k, v in q_dict.items():
        if isinstance(v, int):
            continue
        for term in v.free_symbols:
            q_dict[k] = q_dict[k].subs(term, vqf_qaoa.selected[to_qubit_index(term)])
    print(q_dict, p_dict)
