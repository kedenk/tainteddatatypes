from datatypes.taintedint import tint


def func(t: str):
    print(str(t) + " Hello")


d = {3: "Hello"}
i = 4

func("No")
b = tint(4)
b.to_bytes(2, 'big')
2 in d

i = int(5)
i in d

s = str("hello")
s in d