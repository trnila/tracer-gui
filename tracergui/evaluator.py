class Expr:
    def matches(self, str2):
        raise NotImplemented

    def __invert__(self):
        return Not(self)

    def __and__(self, other):
        return And(self, other)

    def __or__(self, other):
        return Or(self, other)

    def __bool__(self):
        raise SyntaxError("and, or, not operators not allowed, use &, |, ~ instead")


class UnaryExpr(Expr):
    def __init__(self, s):
        self.str = s


class BinaryExpr(Expr):
    def __init__(self, op1, op2):
        self.op1 = op1
        self.op2 = op2


class ExactMatch(UnaryExpr):
    def matches(self, str2):
        return self.str == str2


class Contains(UnaryExpr):
    def matches(self, str2):
        return self.str in str2


class Endswith(UnaryExpr):
    def matches(self, str2):
        return str2.endswith(self.str)


class Startswith(UnaryExpr):
    def matches(self, str2):
        return str2.startswith(self.str)


class Not(UnaryExpr):
    def matches(self, str2):
        return not self.str.matches(str2)


class And(BinaryExpr):
    def matches(self, str2):
        return self.op1.matches(str2) and self.op2.matches(str2)


class Or(BinaryExpr):
    def matches(self, str2):
        return self.op1.matches(str2) or self.op2.matches(str2)


def evalme(query, process=None, descriptor=None, type=None):
    def is_file(s=Contains("")):
        if isinstance(s, str):
            s = ExactMatch(s)

        return descriptor and descriptor['type'] == 'file' and s.matches(descriptor['path'])

    def is_file2(s=Contains("")):
        if isinstance(s, str):
            s = ExactMatch(s)

        return is_file(~Contains(".so") & ~Endswith(".pyc") & s)

    def is_child_of(pid):
        if process:
            p = process
            while p:
                if p['pid'] == pid:
                    return True
                p = p.parent

        return False





    a = {
        "process": process,
        "descriptor": descriptor,
        "type": type,
        "is_file": is_file,
        "is_file2": is_file2,
        "contains": Contains,
        "endswith": Endswith,
        "startswith": Startswith,
        "exactmatch": ExactMatch,
        "is_child_of": is_child_of,
        "Not": Not,
        "And": And,
        "Or": Or
    }
    return eval(query, a)
