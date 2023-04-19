import argparse
import time
from typing import Tuple, Optional
import numpy as np
from cnf import Clause, CNFFormula

def cdcl(cnf_formula: CNFFormula, assumption: Optional[list] = None, heuristic: int = 1, conflicts_limit: int = 100,
         lbd_limit: int = 3) -> Tuple[bool, list, int, int, int]:
    """
    CDCL algorithm for deciding whether the DIMACS CNF formula in the argument `cnf_formula` is satisfiable (SAT) or
    unsatisfiable (UNSAT). In the case of SAT formula, the function also returns a model.
    :param cnf_formula: DIMACS CNF formula
    :param heuristic: Specifies a decision heuristic: `0`, `1` or `2`
    :param assumption: a list of integers representing assumption about the initial values of specified variables
    :param lbd_limit: a limit for LBD
    :param conflicts_limit: a limit for number of conflicts before a restart is used
    :return: a tuple (sat, model, decisions, unit_propagations, restarts) which describes whether the formula is SAT,
             what is its model, how many decisions were made during the derivation of the model, how many literals
             were derived by unit propagation and how many restarts were used
        """
    # Counters for number of decisions, unit propagations
    decision_level = 0
    decisions = 0
    unit_propagations = 0
    restarts = 0
    conflicts = 0

    # Unit propagation
    propagated_literals, antecedent_of_conflict = cnf_formula.unit_propagation(decision_level)
    unit_propagations += len(propagated_literals)

    if antecedent_of_conflict:
        return False, [], decisions, unit_propagations, restarts

    # Reverse the assumption list in order to pop elements from back which is done in O(1), because
    # popping the first element from the list is expensive.
    if assumption:
        assumption.reverse()

    while not cnf_formula.all_variables_assigned():
        # Find the literal for decision by either picking one from assumption or finding one using decision heuristic
        if assumption:
            decision_literal = assumption.pop()

        else:
            decision_literal = cnf_formula.pick_branching_variable(heuristic)

        decision_level += 1

        # Perform the partial assignment of the formula with the decision literal
        cnf_formula.assign_literal(decision_literal, decision_level)
        decisions += 1

        # Unit propagation
        propagated_literals, antecedent_of_conflict = cnf_formula.unit_propagation(decision_level)
        unit_propagations += len(propagated_literals)

        while antecedent_of_conflict:
            conflicts += 1

            # If the amount of conflicts reached the limit, perform restart and delete learned clauses with big LBD
            if conflicts == conflicts_limit:
                conflicts = 0
                conflicts_limit = int(conflicts_limit * 1.1)
                lbd_limit = lbd_limit * 1.1
                restarts += 1
                decision_level = 0
                cnf_formula.restart()
                cnf_formula.delete_learned_clauses_by_lbd(lbd_limit)
                break

            # Analyse conflict: learn new clause from the conflict and find out backtrack decision level
            backtrack_level = cnf_formula.conflict_analysis(antecedent_of_conflict, decision_level)
            if backtrack_level < 0:
                return False, [], decisions, unit_propagations, restarts

            # Backtrack
            cnf_formula.backtrack(backtrack_level)
            decision_level = backtrack_level

            # Unit propagation of the learned clause
            propagated_literals, antecedent_of_conflict = cnf_formula.unit_propagation(decision_level)
            unit_propagations += len(propagated_literals)

    return True, list(cnf_formula.assignment_stack), decisions, unit_propagations, restarts


def find_model(input_file: str, assumption: Optional[list] = None, heuristic: int = 1, conflicts_limit: int = 100,
               lbd_limit: int = 3) -> Optional[Tuple[bool, list, float, int, int, int]]:
    """
    Finds the model of the SAT formula from the `input_file` or returns `UNSAT`.
    :param input_file: describes the input formula. The file can contain either CNF formula in DIMACS format and in
                       that case ends with ".cnf" extension, or NNF formula in simplified SMT-LIB format and ends with
                        ".sat" extension.
    :param heuristic: specifies a decision heuristic: `0` - pick the unassigned literal which occurs in the largest
        number of not satisfied clauses, `1` - pick the unassigned literal based on VSIDS heuristic,
        `2` - pick the random unassigned literal
    :param assumption: a list of integers representing assumption about the initial values of specified variables
    :param conflicts_limit: a limit for number of conflicts before a restart is used
    :param lbd_limit: a limit for LBD
    :return: a tuple (sat, model, cpu_time, decisions, unit_propagations, restarts) which describes whether the formula
        is SAT or UNSAT, what is its model, how long the computation took, number of decisions, number of literals
        derived by unit propagation and number of restarts
    """
    input = open(input_file, mode="r")
    dimacs_formula = input.read()
    dimacs_formula = dimacs_formula.splitlines()

    formula = [list(map(int, clause[:-2].strip().split())) for clause in dimacs_formula if clause != "" and
               clause[0] not in ["c", "p", "%", "0"]]

    cnf_formula = CNFFormula(formula)
    start_time = time.time()
    sat, model, decisions, unit_propagations, restarts = cdcl(cnf_formula, assumption, heuristic, conflicts_limit,
                                                              lbd_limit)
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
    print("Number of decisions =", decisions)
    print("Number of steps of unit propagation =", unit_propagations)
    print("Number of restarts =", restarts)

    return sat, model, cpu_time, decisions, unit_propagations, restarts


if __name__ == "__main__":
    print('This program is a SAT solver for checking satisfiability of CNFs in Dimacs.')
    print('Project by JS Peh and Shion S.')
    print('Run program with -h for options.')
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str, help="Input file which contains a description of a formula.")
    parser.add_argument("--assumption", type=int, default=None, nargs="+", help="A space separated sequence of "
                                                                                "integers representing assumption "
                                                                                "about initial values of specified "
                                                                                "variables")
    parser.add_argument("--heuristic", type=int, default=1, help="Specify a decision heuristic: `0` - pick the "
                                                                 "unassigned literal which occurs in the largest "
                                                                 "number of not satisfied clauses, `1` - pick the "
                                                                 "unassigned literal based on VSIDS heuristic, "
                                                                 "`2` - pick the random unassigned literal")
    parser.add_argument("--conflicts_limit", default=100, help="The initial limit on the number of conflicts before "
                                                               "the CDCL solver restarts")
    parser.add_argument("--lbd_limit", default=3, help="The initial limit on the number of different decision levels "
                                                       "in the learned clause for clause deletion")
    args = parser.parse_args()

    find_model(args.input, args.assumption, args.heuristic, args.conflicts_limit, args.lbd_limit)