from taintedstr import Op


class Instr:
    def __init__(self, o, a, b):
        self.opA = a
        self.opB = b
        self.op = o

    def o(self):
        if self.op == Op.EQ:
            return 'eq'
        elif self.op == Op.NE:
            return 'ne'
        else:
            return '?'

    def opS(self):
        if not self.opA.has_taint() and type(self.opB) is tbytes:
            return (self.opB, self.opA)
        else:
            return (self.opA, self.opB)

    @property
    def op_A(self): return self.opS()[0]

    @property
    def op_B(self): return self.opS()[1]

    def __repr__(self):
        return "%s,%s,%s" % (self.o(), repr(self.opA), repr(self.opB))

    def __str__(self):
        if self.op == Op.EQ:
            if str(self.opA) == str(self.opB):
                return "%s = %s" % (repr(self.opA), repr(self.opB))
            else:
                return "%s != %s" %  (repr(self.opA), repr(self.opB))
        elif self.op == Op.NE:
            if str(self.opA) == str(self.opB):
                return "%s = %s" %  (repr(self.opA), repr(self.opB))
            else:
                return "%s != %s" %  (repr(self.opA), repr(self.opB))
        elif self.op == Op.IN:
            if str(self.opA) in str(self.opB):
                return "%s in %s" % (repr(self.opA), repr(self.opB))
            else:
                return "%s not in %s" %  (repr(self.opA), repr(self.opB))
        elif self.op == Op.NOT_IN:
            if str(self.opA) in str(self.opB):
                return "%s in %s" % (repr(self.opA), repr(self.opB))
            else:
                return "%s not in %s" %  (repr(self.opA), repr(self.opB))
        else:
            assert False
