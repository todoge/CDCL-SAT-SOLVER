from cnf import CNF
from solver import SATSolver, ComplexSatSolver
import argparse

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
    print('This program is a SAT solver for checking satisfiability of CNFs in Dimacs.')
    print('Project by JS Peh and Shion S.')
    print('Run program with -h for options.')
    parser = argparse.ArgumentParser(prog='SAT SOLVER')
    parser.add_argument('--file', help='Path to file', type=str, default='sample.txt')
    args = parser.parse_args()
    filename = args.file
    n_vars, n_clauses, clauses = parse_dimacs_cnf(filename)
    print()
    print('CONVERTING INTO CNF with', n_vars, 'variables', n_clauses, 'clauses')
    cnf = CNF(var_len=n_vars, clauses=clauses)
    print(cnf,'\n')
    solver = SATSolver(var_len=n_vars, clause_len=n_clauses)
    isSolvable = solver.simpleSolver(cnf)
    # solver = ComplexSatSolver(n_vars, cnf)
    # isSolvable = solver.solve()
    print('SOLVER COMPLETED!')
    if isSolvable:
        print('CNF is SOLVABLE!!')
    else:
        print('CNF is NOT SOLVABLE!')