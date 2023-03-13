import sys
from cnf import CNF

def parse_dimacs_cnf(filename):
    clauses = []
    with open(filename, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith('c'):
                continue
            if line.startswith('p'):
                n_vars, n_clauses = map(int, line.split()[2:4])
                continue
            clause = list(map(int, line.split()))[:-1]
            clauses.append(clause)
    return n_vars, n_clauses, clauses



def create_proposition_matrix(n_vars, clauses):
    matrix = []
    for clause in clauses:
        row = [0] * (n_vars + 1)
        for literal in clause:
            var = abs(literal)
            prop = 1 if literal > 0 else -1
            if row[var] != 0 and row[var] != prop:
                ##Setting to 0 if 2 literals in a clause is opposite
                row[var] = 0
            else:
                row[var] = prop
        matrix.append(row)
    return matrix

if __name__ == "__main__":
    filename = sys.argv[1]
    n_vars, n_clauses, clauses = parse_dimacs_cnf(filename)
    matrix = create_proposition_matrix(n_vars, clauses)
    print(matrix)
    cnf = CNF(n_var=n_vars, clauses=clauses)
    r = cnf.solve()
    print(r)