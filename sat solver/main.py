from ast import List
from cnf import CNF
from solver import ComplexSatSolver
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

def complexSolverClauses(n_vars, clauses):
    complex_clauses = set() # set of tuples of (var, val)
    for clause in clauses:
        complex_clauses.add(complex_solver_clause(n_vars, clause))
    return complex_clauses

def complex_solver_clause(n_vars, clause):
    for literal in clause:
        tmp_clause = [2] * (n_vars + 1)
        idx = abs(literal)
        prop = 1 if literal > 0 else -1
        if tmp_clause[idx] != 2 and tmp_clause[idx] != prop:
            tmp_clause[idx] = 0 # both -1 and 1 -> 0
            
        elif tmp_clause[idx] == 0:
            continue
        else:
            tmp_clause[idx] = prop

        for idx, lit in enumerate(tmp_clause):
            if lit == 2:
                tmp_clause[idx] = 0

    complex_clause_tup = tuple()
    for idx, lit in enumerate(tmp_clause):
        if lit != 0:
            complex_clause_tup += ((idx, lit),)

    return complex_clause_tup

if __name__ == "__main__":
    print('This program is a SAT solver for checking satisfiability of CNFs in Dimacs.')
    print('Project by JS Peh and Shion S.')
    print('Run program with -h for options.')
    parser = argparse.ArgumentParser(prog='SAT SOLVER')
    parser.add_argument('--file', help='Path to file', type=str, default='sample.txt')
    args = parser.parse_args()
    filename = args.file
    n_vars, n_clauses, clauses = parse_dimacs_cnf(filename)
    complex_clauses = complexSolverClauses(n_vars, clauses)
    print()
    print('CONVERTING INTO CNF with', n_vars, 'variables', n_clauses, 'clauses')
    cnf = CNF(var_len=n_vars, clauses=clauses)
    print(cnf,'\n')
    # solver = SATSolver(var_len=n_vars, clause_len=n_clauses)
    # isSolvable = solver.simpleSolver(cnf)
    solver = ComplexSatSolver(n_vars, complex_clauses)
    isSolvable = solver.solve()
    print('SOLVER COMPLETED!')
    if isSolvable:
        print('CNF is SOLVABLE!!')
    else:
        print('CNF is NOT SOLVABLE!')
