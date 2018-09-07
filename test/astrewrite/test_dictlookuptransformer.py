import ast

from astrewrite.dictlookuptransformer import DictLookupTransformer, nodeProcessors

EASY_SUBJECT_PATH = "./subject/easy_subject.py"
SUBJECT_1 = "./subject/easy/subject_1.py"


def test_easyTraverseAST():

    data = open(EASY_SUBJECT_PATH).read()
    tree = ast.parse(data, EASY_SUBJECT_PATH)

    DictLookupTransformer(nodeProcessors).visit(tree)

    prg = compile(tree, EASY_SUBJECT_PATH, mode="exec")
    eval(prg)