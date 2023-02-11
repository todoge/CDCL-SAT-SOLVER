import sys
from cnf import CNF
from solver import SATSolver

def parse_dimacs_cnf(filename):
    clauses = []
    with open(filename, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith('c'):
                continue
            if line.startswith('p'):
                n_vars, n_clauses = map(int, line.split()[2:4])
            else:
                clause = list(map(int, line.split()))[:-1]
                clauses.append(clause)
    return n_vars, n_clauses, clauses

if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else 'sample.txt'
    n_vars, n_clauses, clauses = parse_dimacs_cnf(filename)
    print('CONVERTING INTO CNF with', n_vars, 'variables', n_clauses, 'clauses')
    cnf = CNF(var_len=n_vars, clauses=clauses)
    print('CNF successfully converted')
    print(cnf)
    print('\nRunning solver\n')
    solver = SATSolver(var_len=n_vars, clause_len=n_clauses)
    isSolvable = solver.simpleSolver(cnf)
    print('SOLVER COMPLETED!')
    if isSolvable:
        print('CNF is SOLVABLE!!')
    else:
        print('CNF is NOT SOLVABLE!')