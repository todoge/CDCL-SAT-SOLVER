from typing import List
class Clause:
    def __init__(self, clause, var_len) -> None:
        self.var_len = var_len
        tmp_clause = [2] * var_len
        for literal in clause:
            idx = abs(literal) - 1
            prop = 1 if literal > 0 else -1
            if tmp_clause[idx] != 2 and tmp_clause[idx] != prop:
                tmp_clause[idx] = 0
            else:
                tmp_clause[idx] = prop
        self.clause = tmp_clause
    
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

    # Check is clause is a unit clause
    def isUnit(self):
        flag = 0
        for lit in self.clause:
            if lit != 0:
                if flag < 1:
                    flag += 1
                else:
                    return False
        return True

    def __repr__(self):
        tkns = ['(']
        for idx, lit in enumerate(self.clause):
            if abs(lit) == 1:
                if lit < 0:
                    tkns.append('~')
                tkns.append(chr(idx + 97))
                if idx < len(self.clause) - 1:
                    tkns.append(' \/ ')
        tkns.append(')')
        return ''.join(tkns)

class CNF:
    cnf : List[Clause]
    def __init__(self, var_len, clauses) -> None:
        self.var_len = var_len
        self.cnf = []
        for clause in clauses:
            self.cnf.append(Clause(clause, var_len))
    
    # Check is assignment can fulfil a CNF
    def isSAT(self, assignment:List[int]):
        for clause in self.cnf:
            if not clause.isSAT(assignment):
                return False
        return True

    # Finds the first unit clause in the CNF
    def findUnit(self):
        for clause in self.cnf:
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
        for idx, clause in enumerate(self.cnf):
            rep += clause.__repr__()
            if idx < len(self.cnf) - 1:
                rep += ' /\ '
        return rep