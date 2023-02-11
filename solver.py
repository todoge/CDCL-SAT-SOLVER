from cnf import CNF
import itertools
class SATSolver:
    def __init__(self, var_len:int, clause_len:int):
        self.var_length = var_len
        self.clause_len = clause_len

    def simpleSolver(self, cnf:CNF):
        print('Running SIMPLE SAT SOLVER')
        assignments = itertools.product((0, 1), repeat=self.var_length)
        isSolv = False
        for assignment in assignments:
            if cnf.isSAT(assignment=assignment):
                print(assignment, 'SOLVABLE!')
                isSolv = True
            else:
                print(assignment, 'NOT SOLVABLE')
        return isSolv