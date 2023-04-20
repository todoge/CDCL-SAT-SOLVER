from collections import Counter, deque
import random
import numpy as np
from typing import Tuple, Optional
class Clause:
    def __init__(self, literals, w1=None, w2=None, learned=False, lbd=0):
        self.literals = literals  # describes how exactly does this clause look like
        self.size = len(self.literals)
        self.w1 = w1
        self.w2 = w2
        self.learned = learned
        self.lbd = lbd

        if (not w1) and (not w2):
            if len(self.literals) > 1:
                self.w1 = 0
                self.w2 = 1
            elif len(self.literals) > 0:
                self.w1 = self.w2 = 0

    def partial_assignment(self, assignment: list) -> list:
        unassigned = []
        for literal in self.literals:
            if assignment[abs(literal)] == literal:
                return []

            if assignment[abs(literal)] == 0:
                unassigned.append(literal)

        return list(unassigned)

    def update_watched_literal(self, assignment: list, new_variable: int) -> Tuple[bool, int, Optional[int]]:

        # If the new variable assignment is the same as the watched literal, then swap the watched literals
        if new_variable == abs(self.literals[self.w2]):
            temp = self.w1
            self.w1 = self.w2
            self.w2 = temp

        if (self.literals[self.w1] == assignment[abs(self.literals[self.w1])] or
                self.literals[self.w2] == assignment[abs(self.literals[self.w2])]):
            return True, self.literals[self.w1], False


        if (-self.literals[self.w1] == assignment[abs(self.literals[self.w1])] and
                -self.literals[self.w2] == assignment[abs(self.literals[self.w2])]):
            return False, self.literals[self.w1], False


        if (-self.literals[self.w1] == assignment[abs(self.literals[self.w1])] and
                assignment[abs(self.literals[self.w2])] == 0):
            old_w1 = self.w1
            for w in [(self.w1 + i) % self.size for i in range(self.size)]:
                if w == self.w2 or -self.literals[w] == assignment[abs(self.literals[w])]:
                    continue

                self.w1 = w
                break


            if self.w1 == old_w1:
                return True, self.literals[self.w1], True

            return True, self.literals[self.w1], False

    def is_satisfied(self, assignment: list) -> bool:
        return (self.literals[self.w1] == assignment[abs(self.literals[self.w1])] or
                self.literals[self.w2] == assignment[abs(self.literals[self.w2])])

class CNF:

    def __init__(self, formula):
        self.formula = formula  # list of lists of lits
        self.clauses = [Clause(literals) for literals in self.formula]  # list of clauses
        self.learned_clauses = []
        self.variables = set()  # set of variables in the formula
        self.watched_lists = {}  # dict: list of clauses with `key` literal watched
        self.unit_clauses_queue = deque()  # queue for unit clauses
        self.assignment_stack = deque()  # stack: current assignment for backtracking
        self.assignment = None  # list with `variable` as index and `+variable/-variable/0` as values
        self.antecedent = None  # list with `variable` as index and `Clause` as value
        self.decision_level = None  # list with `variable` as index and `decision level` as value
        self.positive_literal_counter = None
        self.negative_literal_counter = None

        for clause in self.clauses:
            if clause.w1 == clause.w2:
                self.unit_clauses_queue.append((clause, clause.literals[clause.w2]))

            for literal in clause.literals:
                variable = abs(literal)
                self.variables.add(variable)

                if variable not in self.watched_lists:
                    self.watched_lists[variable] = []

                if clause.literals[clause.w1] == literal or clause.literals[clause.w2] == literal:
                    if clause not in self.watched_lists[variable]:
                        self.watched_lists[variable].append(clause)

        max_variable = max(self.variables)
        self.assignment = [0] * (max_variable + 1)
        self.antecedent = [None] * (max_variable + 1)
        self.decision_level = [-1] * (max_variable + 1)
        self.positive_literal_counter = np.zeros((max_variable + 1), dtype=np.float64)
        self.negative_literal_counter = np.zeros((max_variable + 1), dtype=np.float64)

    def all_variables_assigned(self) -> bool:
        return len(self.variables) == len(self.assignment_stack)

    def assign_literal(self, literal: int, decision_level: int) -> Tuple[bool, Optional[Clause]]:
        self.assignment_stack.append(literal)
        self.assignment[abs(literal)] = literal
        self.decision_level[abs(literal)] = decision_level

        watched_list = self.watched_lists[abs(literal)][:]


        for clause in watched_list:
            success, watched_literal, unit = clause.update_watched_literal(self.assignment, abs(literal))

            # if not unsat
            if success:
                # if watched changed
                if abs(watched_literal) != abs(literal):
                    # add clause to watched list of new watched literal
                    if clause not in self.watched_lists[abs(watched_literal)]:
                        self.watched_lists[abs(watched_literal)].append(clause)

                    # remove clause from watched list of old watched literal
                    self.watched_lists[abs(literal)].remove(clause)

                # clause is unit then add the clause to the unit clauses queue
                if unit:
                    if clause.literals[clause.w2] not in [x[1] for x in self.unit_clauses_queue]:
                        self.unit_clauses_queue.append((clause, clause.literals[clause.w2]))

            # clause is unsatisfied return False
            if not success:
                return False, clause

        return True, None

    def backtrack(self, decision_level: int) -> None:
        """
        Backtrack to the given decision level by removing all the literals from the assignment stack
        """
        while self.assignment_stack and self.decision_level[abs(self.assignment_stack[-1])] > decision_level:
            literal = self.assignment_stack.pop()
            self.assignment[abs(literal)] = 0
            self.antecedent[abs(literal)] = None
            self.decision_level[abs(literal)] = -1

    @staticmethod
    def resolve(clause1: list, clause2: list, literal: int) -> list:
        in_clause1 = set(clause1)
        in_clause2 = set(clause2)
        in_clause1.remove(-literal)
        in_clause2.remove(literal)
        return list(in_clause1.union(in_clause2))

    def conflict_analysis(self, antecedent_of_conflict: Clause, decision_level: int) -> int:
        # conflict at decision level 0, return -1
        if decision_level == 0:
            return -1

        # find literals of assertive clause
        assertive_clause_literals = antecedent_of_conflict.literals
        current_assignment = deque(self.assignment_stack)
        while len([l for l in assertive_clause_literals if self.decision_level[abs(l)] == decision_level]) > 1:
            while True:
                literal = current_assignment.pop()
                if -literal in assertive_clause_literals:
                    assertive_clause_literals = self.resolve(assertive_clause_literals,
                                                             self.antecedent[abs(literal)].literals, literal)
                    break

        assertion_level = 0
        unit_literal = None
        w2 = None
        decision_level_present = [False] * (decision_level + 1)
        for index, literal in enumerate(assertive_clause_literals):
            if assertion_level < self.decision_level[abs(literal)] < decision_level:
                assertion_level = self.decision_level[abs(literal)]

            if self.decision_level[abs(literal)] == decision_level:
                unit_literal = literal
                w2 = index

            if not decision_level_present[self.decision_level[abs(literal)]]:
                decision_level_present[self.decision_level[abs(literal)]] = True

            self.positive_literal_counter = self.positive_literal_counter * 0.9
            self.negative_literal_counter = self.negative_literal_counter * 0.9
            if literal > 0:
                self.positive_literal_counter[literal] += 1

            else:
                self.negative_literal_counter[(abs(literal))] += 1

        # get lbd of assertive clause
        lbd = sum(decision_level_present)

        # get the second watched literal
        w1 = None
        if len(assertive_clause_literals) > 1:
            current_assignment = deque(self.assignment_stack)
            found = False
            while current_assignment:
                literal = current_assignment.pop()
                if self.decision_level[abs(literal)] == assertion_level:
                    for index, clause_literal in enumerate(assertive_clause_literals):
                        if abs(literal) == abs(clause_literal):
                            w1 = index
                            found = True
                            break
                if found:
                    break
        else:
            w1 = w2

        # create then update
        assertive_clause = Clause(assertive_clause_literals, w1=w1, w2=w2, learned=True, lbd=lbd)
        self.watched_lists[abs(assertive_clause.literals[assertive_clause.w1])].append(assertive_clause)
        if assertive_clause.w1 != assertive_clause.w2:
            self.watched_lists[abs(assertive_clause.literals[assertive_clause.w2])].append(assertive_clause)

        # add to learned clauses
        self.learned_clauses.append(assertive_clause)

        self.unit_clauses_queue.clear()
        self.unit_clauses_queue.append((assertive_clause, unit_literal))

        return assertion_level

    def unit_propagation(self, decision_level: int) -> Tuple[list, Optional[Clause]]:
        """
        Unit propagation algorithm
        """
        propagated_literals = []
        while self.unit_clauses_queue:
            unit_clause, unit_clause_literal = self.unit_clauses_queue.popleft()
            propagated_literals.append(unit_clause_literal)
            self.antecedent[abs(unit_clause_literal)] = unit_clause

            success, antecedent_of_conflict = self.assign_literal(unit_clause_literal, decision_level)
            if not success:
                return propagated_literals, antecedent_of_conflict

        return propagated_literals, None  
    

    def pick_branching_variable(self, heuristic: int) -> int:
        """
        Picks a branching variable based on the given heuristic
        """
        if heuristic == 0:
            return self.two_clause_heuristic()

        if heuristic == 1:
            return self.vsids_heuristic()
        
        if heuristic == 2:
            return self.unassigned_heuristic()
        
        if heuristic == 3:
            return self.random_heuristic()
        
        if heuristic == 4:
            return self.jeroslow_wang_heuristic()
        
### Heuristics
    def unassigned_heuristic(self) -> int:
        """
        Finds the unassigned literal which is in largest occurrence in the unassigned clauses
        """
        number_of_clauses = -1
        decision_literal = None
        for variable in self.variables:
            if self.assignment[variable] == 0:
                positive_clauses = 0
                negative_clauses = 0
                for clause in self.watched_lists[variable]:
                    if not clause.is_satisfied(self.assignment):
                        unassigned = clause.partial_assignment(self.assignment)
                        if variable in unassigned:
                            positive_clauses += 1

                        if -variable in unassigned:
                            negative_clauses += 1
                if positive_clauses > number_of_clauses and positive_clauses > negative_clauses:
                    number_of_clauses = positive_clauses
                    decision_literal = variable

                if negative_clauses > number_of_clauses:
                    number_of_clauses = negative_clauses
                    decision_literal = -variable

        return decision_literal
    
    #jeroslow_wang_heuristic
    def jeroslow_wang_heuristic(self) -> int:
        max_j_score= -1
        decision_literal = None
        for variable in self.variables:
            curr_score = 0
            
            if self.assignment[variable] == 0:
                # positive_clauses = 0
                # negative_clauses = 0
                
                for clause in self.watched_lists[variable]:
                    clause_length = len(clause.literals)
                    curr_score += 2**(-clause_length)
                    
                    if curr_score > max_j_score:
                        max_j_score = curr_score
                        decision_literal = variable
                    
                #     if not clause.is_satisfied(self.assignment):
                #         unassigned = clause.partial_assignment(self.assignment)
                #         if variable in unassigned:
                #             positive_clauses += 1

                #         if -variable in unassigned:
                #             negative_clauses += 1
                # if positive_clauses > number_of_clauses and positive_clauses > negative_clauses:
                #     number_of_clauses = positive_clauses
                #     decision_literal = variable

                # if negative_clauses > number_of_clauses:
                #     number_of_clauses = negative_clauses
                #     decision_literal = -variable

        return decision_literal

    def vsids_heuristic(self) -> int:
        """
        Finds the unassigned literal based on VSIDS heuristic, i.e. the literal which is present the most in the
        learned clauses (when a clause is added).
        :return: the decision literal
        """
        decision_literal = None
        best_counter = 0
        for variable in self.variables:
            if self.assignment[variable] == 0:
                if self.positive_literal_counter[variable] > best_counter:
                    decision_literal = variable
                    best_counter = self.positive_literal_counter[variable]

                if self.negative_literal_counter[variable] >= best_counter:
                    decision_literal = -variable
                    best_counter = self.negative_literal_counter[variable]

        return decision_literal

    def random_heuristic(self) -> int:
        """
        Finds the unassigned literal at random.
        :return: the decision literal
        """
        unassigned = []
        for variable in self.variables:
            if self.assignment[variable] == 0:
                unassigned.append(variable)

        decision_variable = random.choice(unassigned)

        if random.random() <= 0.5:
            return decision_variable

        else:
            return -decision_variable
    
    def two_clause_heuristic(self) -> int:
        """
        Finds the unassigned literal based on 2-clause heuristic, i.e. the literal which is present the most in the 2-clause clauses.
        Otherwise, it returns a random literal.
        :return: the decision literal
        """
        unassigned_literals = []
        number_of_clauses = 0
        decision_literal = None
        for variable in self.variables:
            if self.assignment[variable] == 0:
                unassigned_literals.append(variable)
                positive_clauses = 0
                negative_clauses = 0
                for clause in self.watched_lists[variable]:
                    if not clause.is_satisfied(self.assignment) and clause.size == 2:
                        unassigned = clause.partial_assignment(self.assignment)
                        if variable in unassigned:
                            positive_clauses += 1

                        if -variable in unassigned:
                            negative_clauses += 1
                            
                if positive_clauses > number_of_clauses and positive_clauses > negative_clauses:
                    number_of_clauses = positive_clauses
                    decision_literal = variable

                if negative_clauses > number_of_clauses:
                    number_of_clauses = negative_clauses
                    decision_literal = -variable

        if number_of_clauses == 0:
            decision_variable = random.choice(unassigned_literals)
            if random.random() <= 0.5:
                return decision_variable
            else:
                return -decision_variable
    

        return decision_literal
######
        

    def delete_learned_clauses_by_lbd(self, lbd_limit: float) -> None:
        """
        Deletes the learned clauses with LBD greater than the given limit.
        """

        lbd_limit = int(lbd_limit)
        new_learned_clauses = []
        for clause in self.learned_clauses:
            if clause.lbd > lbd_limit:
                self.watched_lists[abs(clause.literals[clause.w1])].remove(clause)
                if clause.w1 != clause.w2:
                    self.watched_lists[abs(clause.literals[clause.w2])].remove(clause)

            else:
                new_learned_clauses.append(clause)

        self.learned_clauses = new_learned_clauses

    def restart(self) -> None:
        """
        Restarts the solver by clearing the unit clauses queue and backtracking to the root level.
        """
        self.unit_clauses_queue.clear()
        self.backtrack(decision_level=0)
