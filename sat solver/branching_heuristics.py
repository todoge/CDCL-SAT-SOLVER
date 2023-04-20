from collections import deque
import random
from typing import Tuple, Optional
import numpy as np

class Heuristics:
    def __init__(self, variables, assignment, positive_literal_counter, negative_literal_counter) -> None:
        self.variables = variables
        self.assignment = assignment
        self.positive_literal_counter = positive_literal_counter
        self.negative_literal_counter = negative_literal_counter

    def unassigned_heuristic(self) -> int:
        """
        Finds the unassigned literal which occurs in the largest number of not satisfied clauses.
        :return: the decision literal
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
        number_of_clauses = 0
        decision_literal = None
        for variable in self.variables:
            if self.assignment[variable] == 0:
                positive_clauses = 0
                negative_clauses = 0
                for clause in self.watched_lists[variable]:
                    if not clause.is_satisfied(self.assignment) and clause.number_of_literals() == 2:
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
            return self.random_heuristic()

        return decision_literal