from datatypes.taintedbytes import tbytes
from datatypes.taintedint import tint


def test_tint():

    value = 5

    tainted = tint(value)
    assert isinstance(tainted, tint)
    assert tainted.has_taint()

    # test equal operator
    assert tainted == value

    # test not equal operator
    tainted = tint(2)
    assert tainted != value

    # TODO test also lt and gt operators...


def test_to_bytes():

    value = tint(5)
    asBytes = value.to_bytes(length=2, byteorder='big')

    assert isinstance(value, tint)
    assert isinstance(asBytes, tbytes)
