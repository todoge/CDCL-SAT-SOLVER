import argparse
import itertools
import random
from math import ceil
import os
from pycryptosat import Solver
import matplotlib.pyplot as plt
import numpy as np
import time

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
        isSAT = self.solver.is_satisfiable()
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
    parser.add_argument('--rstart', type=float, help='r size', default=0)
    parser.add_argument('--rend', type=float, help='r size', default=5)
    parser.add_argument('--n', type=int, help='n size', default=150)
    parser.add_argument('--numOfForms', type=int, help='number of formulas', default=50)
    parser.add_argument('--rinterval', type=float, help='r interval size', default=0.2)
    args = parser.parse_args()
    kstart, kend, rstart, rend, n, numOfForms, rinterval = args.kstart, args.kend, args.rstart, args.rend, args.n, args.numOfForms, args.rinterval
    # We can plot multiple k-graphs at once if needed
    if kstart > kend:
        kend = kstart
    if rstart > rend:
        rend = rstart
    print('Parameters:', 'kstart={}'.format(kstart), 'kend={}'.format(kend),\
           'r={}'.format(rend), 'r-interval={}'.format(rinterval), 'numOfForms={}'.format(numOfForms), 'n={}'.format(n))
    # Set the title of graph
    plt.suptitle("$F_{}({}, {}r)$ against r".format(','.join(str(x) for x in range(kstart, kend+1)), n, n),fontsize=18)
    plt.xlabel("r: Clause Density (#Clauses/#Variables)")
    plt.ylabel("Probability of Satisfiability")
    plt.xlim([rstart, rend+rinterval])
    plt.ylim([0, 1.2])
    legend = []
    # Start Timer
    tic = time.perf_counter()
    # Plot the graph
    for k in range(kstart, kend+1):
        legend.append('k={}'.format(k))
        # Track the first time probability < 1 and probability = 0
        isOne, isZero = True, False
        xpoints = []
        ypoints = []
        for r_val in np.arange(rstart, rend+rinterval, rinterval):
            # Get Probability for r_val, k and n
            generator = FormulaGenerator(k, r_val, n)
            SAT_prob = generator.getSATProbability(numOfForms)
            if isOne and SAT_prob < 1:
                prev_x, prev_y = xpoints[-1], ypoints[-1]
                plt.text(prev_x, prev_y, '({:.2f}, {:.2f})'.format(prev_x, prev_y), color='red')
                isOne = False
            if not isZero and SAT_prob == 0:
                plt.text(r_val, SAT_prob, '({:.2f}, {:.2f})'.format(r_val, SAT_prob), color='red', verticalalignment='bottom')
                isZero = True
                
            xpoints.append(r_val)
            ypoints.append(SAT_prob)
        plt.plot(xpoints, ypoints)
    # Stop timer
    toc = time.perf_counter()
    plt.title('#FORMS={}, r-interval={}, Time-taken={:0.4f}s'.format(numOfForms, rinterval, toc - tic),fontsize=10)
    plt.grid()
    plt.legend(legend)
    plt.savefig('{}cnf-n{}.png'.format(k,n))
    

    # plt.title('Solve time vs r',fontsize=18)
    # plt.xlabel("n")
    # plt.ylabel("Time taken (s)")

    # xpoints = [25,50,75,100,125,150]
    # ypoints = [2.06, 4.017, 6.03, 8.18, 12.279, 31.5]
    # plt.xlim([20, 160])
    # plt.plot(xpoints, ypoints)

    # xpoints = [25,35,40,45,50]
    # ypoints = [4.65, 7.73, 11.287, 13.539, 22.955]
    # plt.plot(xpoints, ypoints)

    # xpoints = [25,30,35,40]
    # ypoints = [30, 80.3, 156, 579.8]
    # plt.plot(xpoints, ypoints)
    # plt.legend(['k=3','k=4','k=5'])
    # plt.savefig('compare_time.png')