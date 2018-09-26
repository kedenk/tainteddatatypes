import codecs

import datatypes.taintedbytes as taintbytes
import datatypes.taintedint as taintint


def assertTBytes(value):
    assert isinstance(value, taintbytes.tbytes)


def test_equality():

    currentComparisonCount = len(taintbytes.Comparisons)

    # test equality
    a = taintbytes.tbytes(b"6010")
    b = taintbytes.tbytes(b"6010")

    assertTBytes(a)
    assertTBytes(b)
    assert a == b

    # test not equal
    b = taintbytes.tbytes(b"Hello")
    assertTBytes(b)
    assert a != b

    #assert len(taintbytes.Comparisons) == (currentComparisonCount + 2)

    b = taintbytes.tbytes(b"10")
    assert b in a


def test_iterator_and_loop():

    tbytesValue = taintbytes.tbytes(b"601020304010Hello")

    assertTBytes(tbytesValue)

    idx = 0
    for value in tbytesValue:
        # check if iterator result is tint
        # documentation says that the result of index access is an int, not bytes
        assert isinstance(value, taintint.tint)
        # check if result has taint
        assert value.has_taint()
        # check, if taints match
        assert value.x() == tbytesValue.x(idx)
        # check if 'in' operator works
        assert value in tbytesValue

        idx += 1


def test_getitem():

    b = taintbytes.tbytes(b"60106002")
    assert isinstance(b, taintbytes.tbytes)
    assert b.has_taint()

    # test if index access result is tint
    # and if taints are copied
    idx = 0
    b1 = b[idx]
    assert isinstance(b1, taintint.tint)
    assert b.x(idx) == b1.x(0) # index of tint is always 0

    idx = 2
    b1 = b[idx]
    assert b.x(idx) == b1.x()


def test_byte_to_int():

    b = taintbytes.tbytes(b"600160024a")
    assert b.has_taint()
    bTaints = [t for t in b._taint]

    i = taintint.tint.from_bytes(b, 'big')
    iTaints = [t for t in i._taint]
    assert i.has_taint()

    b = b[0:2]
    bTaints = [t for t in b._taint]

    i = taintint.tint.from_bytes(b, 'big')
    iTaints = [t for t in i._taint]
    assert i.has_taint()

    b = taintbytes.tbytes(codecs.decode("600160024a", 'hex'))
    for value in b:
        assert value.has_taint()
        valueTaint = [t for t in value._taint]
        vt = value.x()
        assert isinstance(value, taintint.tint)