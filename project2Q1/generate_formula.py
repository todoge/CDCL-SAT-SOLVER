import argparse
import itertools
import random
from math import ceil
import os
class FormulaGenerator:
    __terminal = '0'
    def __getRandomClause(self):
        variables = random.sample(range(1, self.n+1), self.k)
        clause_type = random.choice(self.clause_types)
        clause = [str(a*b) for a,b in zip(variables,clause_type)]
        clause.append(self.__terminal)
        return ' '.join(clause)

    def __init__(self, k, r, n) -> None:
        self.cnf = ['p cnf {} {}'.format(n, ceil(r*n))]
        self.clause_types = list(itertools.product((-1, 1), repeat=k))
        self.n = n
        self.r = r
        self.k = k

    def getFormula(self):
        for _ in range(ceil(self.r*self.n)):
            self.cnf.append(self.__getRandomClause())
        return '\n'.join(self.cnf)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--k', type=int, help='k is the size of the clause', default=3)
    parser.add_argument('--r', type=float, help='r size', default=0.2)
    parser.add_argument('--n', type=int, help='n size', default=150)
    args = parser.parse_args()
    k, r, n = args.k, args.r, args.n
    generator = FormulaGenerator(k, r, n)
    with open('formula.txt', 'w') as f:
        f.write(generator.getFormula())
    