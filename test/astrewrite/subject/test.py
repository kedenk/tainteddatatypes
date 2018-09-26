from datatypes.taintedint import tint
from taintedstr import tstr


def func(t: str):
    print((str(t) + ' Hello'))
d = {3: 'Hello'}
i = 4
func('No')
b = tint(4)
b.to_bytes(2, 'big')
tint(2).in_(d.keys())
i = int(5)
tint(i).in_(d.keys())
s = tstr('hello')
s.in_(d.keys())