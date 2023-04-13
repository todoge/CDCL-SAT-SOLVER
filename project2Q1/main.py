import argparse
import itertools
import random
from math import ceil
import os
from pycryptosat import Solver
import matplotlib.pyplot as plt
import numpy as np
class FormulaGenerator:

    def __init__(self, k, r, n) -> None:
        self.clause_types = list(itertools.product((-1, 1), repeat=k))
        self.n = n
        self.r = r
        self.k = k
        self.solver = Solver()
    
    # Generate a random clause
    def __getRandomClause(self):
        variables = random.sample(range(1, self.n+1), self.k)
        clause_type = random.choice(self.clause_types)
        clause = [a*b for a,b in zip(variables,clause_type)]
        return clause

    # Generate a random forumla and check if it is SAT or UNSAT
    def getRandomFormulaSAT(self):
        for _ in range(ceil(self.r*self.n)):
            self.solver.add_clause(self.__getRandomClause())
        isSAT, SOL = self.solver.solve()
        # print(self.solver.nb_clauses(), self.solver.nb_vars(), isSAT)
        self.solver = Solver()
        return isSAT

    # Get SAT Probability
    def getSATProbability(self, numOfFormulas):
        numOfSATs = 0
        for _ in range(numOfFormulas):
            if self.getRandomFormulaSAT():
                numOfSATs += 1
        return numOfSATs / numOfFormulas

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--kstart', type=int, help='k is the size of the clause', default=3)
    parser.add_argument('--kend', type=int, help='k is the size of the clause', default=3)
    parser.add_argument('--r', type=float, help='r size', default=0.2)
    parser.add_argument('--n', type=int, help='n size', default=150)
    parser.add_argument('--numOfForms', type=int, help='number of formulas', default=50)
    parser.add_argument('--rinterval', type=float, help='r interval size', default=0.2)
    args = parser.parse_args()
    kstart, kend, r, n, numOfForms, rinterval = args.kstart, args.kend, args.r, args.n, args.numOfForms, args.rinterval
    if kstart > kend:
        kend = kstart
    print('Parameters:', 'kstart={}'.format(kstart), 'kend={}'.format(kend),\
           'r={}'.format(r), 'r-interval={}'.format(rinterval), 'numOfForms={}'.format(numOfForms), 'n={}'.format(n))
    plt.title('r={}, r-interval={}'.format(r, rinterval),fontsize=10)
    plt.suptitle("Fk(n, rn) against r",fontsize=18)
    plt.xlabel("r")
    plt.ylabel("Fk(n, rn)")
    plt.xlim([0, r+rinterval])
    plt.ylim([0, 1.2])
    legend = []
    # Plot the graph
    for k in range(kstart, kend+1):
        legend.append('k={}'.format(k))
        xpoints = []
        ypoints = []
        for r_val in np.arange(0, r+rinterval, rinterval):
            # Get Probability for r_val, k and n
            generator = FormulaGenerator(k, r_val, n)
            SAT_prob = generator.getSATProbability(numOfForms)
            xpoints.append(r_val)
            ypoints.append(SAT_prob)
        plt.plot(xpoints, ypoints)
    plt.legend(legend)
    plt.savefig('plot.png')
    