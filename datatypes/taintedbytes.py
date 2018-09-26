import os
import datatypes.taintedint as taintint
from datatypes.instr import Instr

from taintedstr import Op, TaintException

Python_Specific = (os.getenv('PY_OPT') or 'false') in ['true', '1']


class tbytes_iterator():
    def __init__(self, tbytes):
        self._tbytes = tbytes
        self._bytes_idx = 0

    def __next__(self):
        if self._bytes_idx == len(self._tbytes): raise StopIteration

        # calls _tbytes getitem should be _tbytes
        c = self._tbytes[self._bytes_idx]
        # the documentation says, that the result of index access
        # is an int, not a byte
        assert type(c) is taintint.tint
        self._bytes_idx += 1
        return c


def subbytes(s, l):
    for i in range(len(s)-(l-1)):
        yield (i, s[i:i+l])


Comparisons = []
Ins = 0
IComparisons = []


def reset_comparisons():
    global Comparisons
    global IComparisons
    global Ins
    Comparisons.clear()
    IComparisons.clear()
    Ins = 0


class tbytes(bytes):

    def __new__(cls, value, *args, **kw):
        return super(tbytes, cls).__new__(cls, value)

    def __init__(self, value, taint=None, parent=None):
        # tain map contains non-overlapping portions that are mapped to the
        # original bytes
        self.parent = parent
        l = len(self)
        if taint:
            # assert that the provided tmap carries only
            # as many entries as len.
            assert len(taint) == len(self)
            self._taint = taint
        else:
            self._taint = list(range(0, len(self)))

    def __repr__(self):
        return bytes.__repr__(self)

    def __str__(self):
        return bytes.__str__(self)

    def __format__(self, format_spec):
        return bytes.__format__(self, format_spec)

    def untaint(self):
        self._taint = [-1] * len(self)
        return self

    def has_taint(self):
        return any(True for i in self._taint if i >= 0)

    def __eq__(self, other):
        global Ins
        Ins += 1
        return self.__eq(other)

    def __eq(self, other):
        global Comparisons
        if Python_Specific:
            Comparisons.append(Instr(Op.EQ, self, other))
            IComparisons.append(Ins)
            return super().__eq__(other)

        if len(self) == 0 and len(other) == 0:
            Comparisons.append(Instr(Op.EQ, self, other))
            IComparisons.append(Ins)
            return True
        elif len(self) == 0:
            Comparisons.append(Instr(Op.EQ, self, other[0]))
            IComparisons.append(Ins)
            return False
        elif len(other) == 0:
            Comparisons.append(Instr(Op.EQ, self[0], other))
            IComparisons.append(Ins)
            return False
        elif len(self) == 1 and len(other) == 1:
            Comparisons.append(Instr(Op.EQ, self, other))
            IComparisons.append(Ins)
            return super().__eq__(other)
        else:
            if not self[0].__eq__(other[0]): return False
            return self[1:].__eq__(other[1:])

    def __ne__(self, other):
        global Ins
        Ins += 1
        return self.__ne(other)

    def __ne(self, other):
        global Comparisons
        if Python_Specific:
            Comparisons.append(Instr(Op.NE, self, other))
            IComparisons.append(Ins)
            return super().__ne__(other)
        return not self.__eq(other)

    def __iter__(self):
        return tbytes_iterator(self)

    def __getitem__(self, item):
        res = super().__getitem__(item)

        if type(item) == slice:

            if res:
                return tbytes(res, self._taint[item], self)
            else:
                start = item.start
                stop = item.stop
                if start >= len(self) or stop >= len(self):
                    raise AssertionError("Can't access range [%s,%s] of bytes of length %s" % (start, stop, len(self)))

                else:
                    raise NotImplementedError

        elif type(item) == int:
            if item < 0:
                item = len(self) + item
            return taintint.tint(res, [self._taint[item]], self)

        else:
            assert False

    def in_(self, s):
        global Ins
        Ins += 1
        return self.__in_(s)

    def __in_(self, s):
        # c in '0123456789'
        # to
        # c.in_('0123456789')
        # ensure that all characters are compared
        result = [self.__eq(c) for i,c in subbytes(s, len(self))]
        return any(result)

    def x(self, i=0):
        v = self._x(i)
        if v < 0:
            raise TaintException('Invalid mapped char idx in tbytes')
        return v

    def _x(self, i=0):
        return self.get_mapped_char_idx(i)

    def get_mapped_char_idx(self, i):

        if self._taint:
            return self._taint[i]
        else:
            if i != 0: raise TaintException('Invalid request idx')
            # self._tcursor gets created only for empty strings.
            # use the exception to determine which ones need it.
            return self._tcursor