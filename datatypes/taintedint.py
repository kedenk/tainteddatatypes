#
# based on TaintedStr by Rahul Gopinath
# https://github.com/vrthra/taintedstr
#

import os

from taintedstr import Op, TaintException
from instr import Instr

Python_Specific = (os.getenv('PY_OPT') or 'false') in ['true', '1']


Comparisons = []
Ins = 0
IComparisons = []


class tint(int):

    def __new__(cls, value, *args, **kw):
        return super(tint, cls).__new__(cls, value)

    def __init__(self, value, taint=None, parent=None):
        super().__init__()
        self.parent = parent
        if taint:
            self._taint = taint
        else:
            self._taint = list(range(0, 1))

    def __repr__(self):
        return int.__repr__(self)

    def __str__(self):
        return int.__str__(self)

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

        else:
            return super().__eq__(other)

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

    def from_bytes(cls, bytes, byteorder, *args, **kwargs) -> int:
        res = super().from_bytes(bytes, byteorder, *args, **kwargs)
        return tint(res)

    def to_bytes(self, length, byteorder, *args, **kwargs) -> bytes:
        import datatypes.taintedbytes as taintbytes

        res = super().to_bytes(length, byteorder, *args, **kwargs)
        return taintbytes.tbytes(res)

    def x(self, i=0):
        v = self._x(i)
        if v < 0:
            raise TaintException('Invalid mapped char idx in tstr')
        return v

    def _x(self, i=0):
        return self.get_mapped_char_idx(i)

    def get_mapped_char_idx(self, i):
        # if the current string is not mapped to input till
        # char 10 (_unmapped_till), but the
        # character 10 is mapped to character 5 (_idx)
        # then requesting 10 should return 5
        #   which is 5 - 10 + 10
        # and requesting 11 should return 6
        #   which is 5 - 10 + 11
        if self._taint:
            return self._taint[i]
        else:
            if i != 0: raise TaintException('Invalid request idx')
            # self._tcursor gets created only for empty strings.
            # use the exception to determine which ones need it.
            return self._tcursor