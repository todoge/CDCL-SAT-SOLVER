import argparse
from ast import List
import os
import time
from typing import Tuple, Optional
from matplotlib import pyplot as plt
import numpy as np
from cnf import CNF

def cdcl(cnf_formula: CNF, heuristic: int = 1):
    """
    cdcl algorithm
    """
    # Initialize the decision level and the number of decisions
    decision_level = 0
    decisions = 0
    unit_propagations = 0
    restarts = 0
    conflicts = 0
    conflicts_limit = 1000
    lbd_limit = 3

    # Unit propagation
    propagated_literals, antecedent_of_conflict = cnf_formula.unit_propagation(decision_level)
    unit_propagations += len(propagated_literals)

    if antecedent_of_conflict:
        return False, [], decisions, unit_propagations, restarts


    while not cnf_formula.all_variables_assigned():
        decision_literal = cnf_formula.pick_branching_variable(heuristic)

        decision_level += 1

        # Assign the decision literal
        cnf_formula.assign_literal(decision_literal, decision_level)
        decisions += 1

        # Unit propagation
        propagated_literals, antecedent_of_conflict = cnf_formula.unit_propagation(decision_level)
        unit_propagations += len(propagated_literals)

        while antecedent_of_conflict:
            conflicts += 1

            # Restart if conflicts limit is reached
            if conflicts == conflicts_limit:
                conflicts = 0
                conflicts_limit = int(conflicts_limit * 1.1)
                lbd_limit = lbd_limit * 1.1
                restarts += 1
                decision_level = 0
                cnf_formula.restart()
                cnf_formula.delete_learned_clauses_by_lbd(lbd_limit)
                break
            
            # Conflict analysis
            backtrack_level = cnf_formula.conflict_analysis(antecedent_of_conflict, decision_level)
            if backtrack_level < 0:
                return False, [], decisions, unit_propagations, restarts

            # Backtracking
            cnf_formula.backtrack(backtrack_level)
            decision_level = backtrack_level

            # Unit propagation of the learned clause
            propagated_literals, antecedent_of_conflict = cnf_formula.unit_propagation(decision_level)
            unit_propagations += len(propagated_literals)

    return True, list(cnf_formula.assignment_stack), decisions, unit_propagations, restarts


def execute(input_file: str, heuristic: int = 1) -> Optional[Tuple[bool, list, float, int, int, int]]:
    """
    Execute the cdcl algorithm on the given input file.
    """
    input = open(input_file, mode="r")
    dimacs_formula = input.read()
    dimacs_formula = dimacs_formula.splitlines()

    formula = [list(map(int, clause[:-2].strip().split())) for clause in dimacs_formula if clause != "" and
               clause[0] not in ["c", "p", "%", "0"]]

    cnf_formula = CNF(formula)
    start_time = time.time()
    sat, model, decisions, unit_propagations, restarts = cdcl(cnf_formula, heuristic)
    cpu_time = time.time() - start_time

    if sat:
        model.sort(key=abs)
        print("CNF IS SAT!! :D")
        print("Solution is", model)
        print("Possible missing literals can have arbitrary value.")
    else:
        print("CNF IS UNSAT... :C")
    print()
    print("Total time taken =", cpu_time, "s")
    print("Number of picks =", decisions)
    print("Number of steps of unit propagation =", unit_propagations)
    print("Number of restarts =", restarts)

    return sat, model, cpu_time, decisions, unit_propagations, restarts


if __name__ == "__main__":
    print('This program is a SAT solver for checking satisfiability of CNFs in Dimacs.')
    print('Project by JS Peh and Shion S.')
    print('Run program with -h for options.')
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str, help="Input file which contains a description of a formula.")
    parser.add_argument("--heuristic", type=int, default=1, help="Specify a decision heuristic: `0` is 2-clause, `1` is VSIDS, `2` is unassigned, `3` is random, `4` is jeroslow-wang.")
    args = parser.parse_args()

    execute(args.input, args.heuristic)
    # cnf_folder = args.input # folder name
    # cnf_files = sorted([os.path.join(cnf_folder, f) for f in os.listdir(cnf_folder) if f.endswith('.cnf')])
    # cpu_times_list = []
    # decisions_list = []
    # unit_propagations_list = []
    # restarts_list = []
    # sat_count = 0
    # unsat_count = 0
    
    # for file_path in cnf_files:
    #     sat, model, cpu_time, decisions, unit_propagations, restarts = execute(file_path, args.heuristic)
    #     if sat:
    #         sat_count += 1
    #     else :
    #         unsat_count += 1
    #     cpu_times_list.append(cpu_time)
    #     decisions_list.append(decisions)
    #     unit_propagations_list.append(unit_propagations)
    #     restarts_list.append(restarts)
            
    # print(f"Total number of SAT: {sat_count}")
    # print(f"Total number of UNSAT: {unsat_count}")

    # print(f"Avg. CPU time: {sum(cpu_times_list)/len(cpu_times_list):.7f}s")
    # print(f"Avg. decision count: {sum(decisions_list)/len(decisions_list)}")
    # print(f"Avg. unit propagation count: {sum(unit_propagations_list)/len(unit_propagations_list)}")
    # print(f"Avg. restart count: {sum(restarts_list)/len(restarts_list)}")
    
    '''
    The following generates the graphs for the report
    '''
    # # Parameters
    # n_values = [50, 75, 100] # [20, 50, 75, 100]  # corresponds to tc_1.cnf, tc_2.cnf, .. tc_5.cnf

    # heuristics = [0, 1, 2, 3, 4]
    # # Initialize arrays to store the result times
    # result_times = {heuristic: [] for heuristic in heuristics}
    
    # # Loop over values of n and heuristics
    # for n in n_values:
    #     for heuristic in heuristics:
    #         cnf_folder = '../test/n_{}_unsat'.format(n)
    #         cnf_files = sorted([os.path.join(cnf_folder, f) for f in os.listdir(cnf_folder) if f.endswith('.cnf')])
    #         cnf_files = cnf_files[:10]
    #         # if n >= 100 :
    #         #     cnf_files = cnf_files[:10]
    #         cpu_times_list = []
    #         decisions_list = []
    #         unit_propagations_list = []
    #         restarts_list = []
    #         sat_count = 0
    #         unsat_count = 0
    #         for file_path in cnf_files:
    #             sat, model, cpu_time, decisions, unit_propagations, restarts = execute(file_path, heuristic)
    #             if sat:
    #                 sat_count += 1
    #             else :
    #                 unsat_count += 1
    #             cpu_times_list.append(cpu_time)
    #             decisions_list.append(decisions)
    #             unit_propagations_list.append(unit_propagations)
    #             restarts_list.append(restarts)
            
    #         avg_time = sum(cpu_times_list)/len(cpu_times_list)
    #         print(f"Total number of SAT: {sat_count}")
    #         print(f"Total number of UNSAT: {unsat_count}")
    #         print(f"Avg. CPU time: {avg_time:.7f}s")
    #         print(f"Avg. decision count: {sum(decisions_list)/len(decisions_list)}")
    #         print(f"Avg. unit propagation count: {sum(unit_propagations_list)/len(unit_propagations_list)}")
    #         print(f"Avg. restart count: {sum(restarts_list)/len(restarts_list)}")
        
    #         # Append the average result time to the appropriate array
    #         result_times[heuristic].append(avg_time)
    # legend = ["2-clause", "VSIDS", "Unassigned", "Random", "Jeroslow-Wang"]
    # # Plot the results
    # plt.figure()
    # plt.title('Average Time on UNSAT 3-SAT vs. n variables')
    # plt.xlabel('n variables')
    # plt.ylabel('Average CPU Time (seconds)')
    # for heuristic in heuristics:
    #     plt.plot(n_values, result_times[heuristic], label=legend[heuristic])
    # # set the x-axis tick labels to the test case file names
    # plt.legend()
    # plt.savefig('result_time_plot.png')