class base:
    def __init__(self, s):
        self.str = s

    def matches(self, str2):
        return self.str == str2

    def __invert__(self):
        return Not(self)


class contains(base):
    def matches(self, str2):
        return self.str in str2


class endswith(base):
    def matches(self, str2):
        return str2.endswith(self.str)


class startswith(base):
    def matches(self, str2):
        return str2.startswith(self.str)


class Not(base):
    def matches(self, str2):
        return not self.str.matches(str2)


def evalme(query, **kwargs):
    descriptor = kwargs['descriptor'] if 'descriptor' in kwargs else None

    def is_file(s=contains("")):
        if isinstance(s, str):
            s = base(s)

        return descriptor and descriptor['type'] == 'file' and s.matches(descriptor['path'])

    a = {
        "process": None,
        "descriptor": None,
        **kwargs,
        "is_file": is_file,
        "contains": contains,
        "endswith": endswith,
        "startswith": startswith,
        "exactmatch": base,
        "Not": Not
    }
    return eval(query, a)
