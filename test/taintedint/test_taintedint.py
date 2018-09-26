import random
import sys

from cffi.backend_ctypes import xrange
from datatypes.taintedbytes import tbytes
from datatypes.taintedint import tint, Comparisons, reset_comparisons, Ins, Python_Specific
import os


def setup_test_init():
    os.environ["PY_OPT"] = "1"
    global Python_Specific
    Python_Specific = True



def test_tint():

    value = 5

    tainted = tint(value)
    assert isinstance(tainted, tint)
    assert tainted.has_taint()

    assert int(2) == tint(2)
    assert int(0) == tint(0)
    assert int(-12321) == tint(-12321)
    assert int(sys.maxsize) == tint(sys.maxsize)

    assert not(tint(5) == tint(2))
    assert not(tint(sys.maxsize) == tint(-1))

    # test equal operator
    assert tainted == value

    # test not equal operator
    tainted = tint(2)
    assert tainted != value

    assert 1 == tint(1)

    # TODO test also lt and gt operators...


def test_to_bytes():

    value = 5

    tintValue = tint(value)
    tintAsBytes = tintValue.to_bytes(length=2, byteorder='big')
    intValue = int(value)
    intAsBytes = intValue.to_bytes(length=2, byteorder='big')

    assert isinstance(intValue, int)
    assert isinstance(tintValue, tint)
    assert isinstance(tintAsBytes, tbytes)

    assert tintAsBytes == intAsBytes


def test_hash_method():
    value = 5
    v1 = tint(value)

    assert int(2).__hash__() == tint(2).__hash__()
    assert int(0).__hash__() == tint(0).__hash__()
    assert int(-12321).__hash__() == tint(-12321).__hash__()
    assert int(sys.maxsize).__hash__() == tint(sys.maxsize).__hash__()

    assert v1.__hash__() == v1.__hash__()
    # test hashs 1000 times
    for i in range(0, 1000):
        assert v1.__hash__() == v1.__hash__()
        assert tint(i).__hash__() == tint(i).__hash__()

    # check if other hashes different from one hash
    def hashTestExtensive(value: tint):
        valueHash = value.__hash__()
        for i in range(0, 5000):
            if i != value:
                assert valueHash != tint(i).__hash__()
                assert valueHash != int(i).__hash__()

    hashTestExtensive(tint(3))
    hashTestExtensive(tint(-5))
    hashTestExtensive(tint(0))
    hashTestExtensive(tint(1132))

    intValue = int(value)
    assert intValue.__hash__() == int(value).__hash__()
    assert v1.__hash__() == tint(value).__hash__()
    assert v1.__hash__() != tint(4).__hash__()


def test_dictionary_access():
    """
    tint as key of dictionary
    :return:
    """

    reset_comparisons()
    assert len(Comparisons) == 0

    key1 = tint(10)
    key2 = tint(123)
    key3 = tint(109324)

    value1 = random.sample(xrange(100), 10)
    value2 = random.sample(xrange(100), 10)
    value3 = random.sample(xrange(100), 10)

    dictionary = {
        key1: value1,
        key2: value2,
        key3: value3
    }

    # check 'in' operator with list
    l = [1, 2, 3]
    assert tint(2) in l # works

    # test access via index
    assert dictionary[key1]
    assert dictionary[key2]
    assert dictionary[10]
    assert dictionary[tint(10)]

    # dictionary.keys() return type 'dict_keys' (set of dictionary view)
    assert key1 in dictionary.keys()
    assert key2 in dictionary.keys()
    assert key3 in dictionary.keys()
    assert 10 in dictionary.keys()
    assert tint(10) in dictionary.keys()
    assert tint(123) in dictionary.keys()
    assert tint(109324) in dictionary.keys()

    # tint has to be hashable
    for key in dictionary.keys():
        assert isinstance(key, tint)
        assert key.has_taint()

    for key, value in dictionary.items():
        assert isinstance(key, tint)
        assert key.has_taint()


def test_Comparison_bookkeeping():

    setup_test_init()

    def checkComparisons(expected):
        assert len(Comparisons) == expected

    reset_comparisons()
    assert len(Comparisons) == 0

    left = tint(5)
    right = tint(5)

    assert left == right
    checkComparisons(1)

    right = tint(3)
    assert not(left == right)
    checkComparisons(2)

    assert not(tint(5) == 3)
    assert not(3 == tint(1))
    assert tint(1) == tint(1)
    checkComparisons(5)

    # should not be counted
    assert 1 == 1
    checkComparisons(5)

    reset_comparisons()
    checkComparisons(0)

    assert tint(1232) != tint(3)
    assert not(tint(32123) != tint(32123))
    checkComparisons(2)

    # check if comparison 'in' and dictionary access is counted
    # reset counter
    reset_comparisons()
    checkComparisons(0)

    # check, if the result of hash is also tracked, if it is used in a comparison
    valueHash = tint(123).__hash__()
    assert not(valueHash == 4123)
    checkComparisons(1)
    assert valueHash == tint(123).__hash__()
    checkComparisons(2)

    reset_comparisons()
    checkComparisons(0)

    testlist = [tint(1), tint(10), tint(15), tint(3)]
    dictionary = {
        tint(1): "Hello",
        tint(2): "World",
        tint(123): "Bye"
    }

    assert tint(10) in testlist
    # two comparisons, because 10 is the second item in the list
    # the in operator tests all items if they are equal to the searched item
    # stating with the first one
    checkComparisons(2)
    # dictionary is always one comparison because of the hash table
    assert tint(123) in dictionary.keys()
    checkComparisons(3)
    # check same key again
    assert tint(123) in dictionary.keys()
    checkComparisons(4)
    assert tint(1) in dictionary.keys()
    assert tint(2) in dictionary.keys()
    assert tint(123) in dictionary.keys()
    checkComparisons(7)

    # here should also be comparisons, because we checked,
    # if the key is in the dictionary.
    # If the key is in the dictionary, we would see at least one comparison.
    # Number of comparisons == the number of comparisons until we reach the searched key
    #
    # => searched key = 3;
    # keys in dictionaries = [ 1, 2, 3, 4 ]
    # The result for: '3 in dict.keys()' would be 3 comparisons in this case
    #
    # Problem: hashes of the keys are probed with the CPython datatype, not tint or int
    # See: https://stackoverflow.com/questions/52037437/python-why-is-eq-not-invoked-if-key-is-not-in-dictionary
    #
    # SOLUTION
    # We rewrite the python programm ast and convert 'i in dict.keys()' to 'i.in_(dict.keys())'
    #
    reset_comparisons()
    checkComparisons(0)
    assert not(tint(55555).in_(dictionary.keys()))
    checkComparisons(len(dictionary.keys()))
    assert tint(2).in_(dictionary.keys())
    checkComparisons(len(dictionary.keys()) * 2)

    reset_comparisons()
    value = dictionary[1]

    # following code results in no comparison tracking
    #
    k = tint(5)
    try:
        tvalue = dictionary[k]
    except KeyError as ke:
        pass

    # -> workaround
    if tint(k).in_(dictionary.keys()):
        tvalue = dictionary[k]

    checkComparisons(1)


def test_from_bytes():

    bValue = bytes(b"5")
    tintResult = tint.from_bytes(bValue, 'big')
    intResult = int.from_bytes(bValue, 'big')

    assert isinstance(tintResult, tint)
    assert isinstance(intResult, int)

    assert tintResult == intResult
