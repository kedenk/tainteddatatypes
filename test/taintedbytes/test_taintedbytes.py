import datatypes.taintedbytes as taintbytes
import datatypes.taintedint as taintint
import os


def setup_init():
    os.environ["PY_OPT"] = "1"


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

    assert len(taintbytes.Comparisons) == (currentComparisonCount + 2)

    b = taintbytes.tbytes(b"10")
    assert b in a


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