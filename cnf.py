from typing import List
class Clause:
    caused_by = 0
    def __init__(self, clause, var_len, caused_by=0) -> None:
        self.var_len = var_len
        tmp_clause = [2] * var_len
        for literal in clause:
            idx = abs(literal) - 1
            prop = 1 if literal > 0 else -1
            if tmp_clause[idx] != 2 and tmp_clause[idx] != prop:
                tmp_clause[idx] = 0
            else:
                tmp_clause[idx] = prop
        
        for idx, lit in enumerate(tmp_clause):
            if lit == 2:
                tmp_clause[idx] = 0
        self.clause = tmp_clause
        self.size = 0
        for lit in self.clause:
            if lit != 0:
                self.size += 1
        self.caused_by = caused_by
    

    # Check is assignment fulfils clause
    def isSAT(self, assignment:List[int]):
        if len(assignment) != self.var_len:
            raise Exception('Assignment length not equal to variable length!')
        for idx, val in enumerate(assignment):
            if self.clause[idx] * val == 1:
                return True
        return False

    # Check if clause is empty
    def isEmpty(self):
        for lit in self.clause:
            if lit != 0:
                return False
        return True

    def isEqual(self, other):
        for i in self.size:
            if other[i] != self.clause[i]:
                return False
        return True
    
    # Check is clause is a unit clause
    def isUnit(self):
        flag = 0
        print(self.clause)
        for lit in self.clause:
            if lit != 0:
                if flag < 1:
                    flag += 1
                else:
                    return False
        return True
 
    # Get idx and value of unit clause
    def get_unit(self):
        if not self.isUnit():
            raise Exception('Not Unit')
        for idx, lit in enumerate(self.clause):
            if lit != 0:
                return idx, lit

    def __repr__(self):
        tkns = ['(']
        count = self.size
        for idx, lit in enumerate(self.clause):
            if abs(lit) == 1:
                if lit < 0:
                    tkns.append('~')
                tkns.append(str(idx+1))
                if count > 1:
                    tkns.append(' \/ ')
                count -= 1
        tkns.append(')')
        return ''.join(tkns)

class CNF:
    clauses : List[Clause]
    def __init__(self, var_len, clauses) -> None:
        self.var_len = var_len
        self.clauses = []
        for clause in clauses:
            self.clauses.append(Clause(clause, var_len))
    
    # Check is assignment can fulfil a CNF
    def isSAT(self, assignment:List[int]):
        for clause in self.clauses:
            if not clause.isSAT(assignment):
                return False
        return True

    # Finds the first unit clause in the CNF
    def findUnit(self):
        for clause in self.clauses:
            if clause.isUnit():
                return clause
        return None

    # Performs resolution on 2 Clause
    def resolution(clause1:Clause, clause2:Clause):
        resolved = []
        for idx, lit in enumerate(clause1):
            resolved_lit = lit + clause2[idx]
            if resolved_lit > 0:
                resolved.append(1)
            elif resolved_lit < 0:
                resolved.append(-1)
            else:
                resolved.append(0)
        return resolved

    def __repr__(self):
        rep = ''
        for idx, clause in enumerate(self.clauses):
            rep += clause.__repr__()
            if idx < len(self.clauses) - 1:
                rep += ' /\ '
        return rep