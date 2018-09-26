import ast

from astrewrite.dictlookuptransformer import DictLookupTransformer, nodeProcessors, AstVisitor, vars, ASSIGNMENTS, \
    resetTracking, getAssignments

EASY_SUBJECT_PATH = "./test/astrewrite/subject/easy_subject.py"
SUBJECT_1 = "./test/astrewrite/subject/easy/subject_1.py"


def sourceCodeToConsole(tree):
    import astunparse
    print(astunparse.unparse(tree))

def getTree(path: str):
    data = open(path).read()
    return ast.parse(data, path)


def test_easyTraverseAST():

    tree = getTree(EASY_SUBJECT_PATH)
    resetTracking()
    AstVisitor().visit(tree)
    DictLookupTransformer(nodeProcessors, getAssignments()).visit(tree)
    ast.fix_missing_locations(tree)

    sourceCodeToConsole(tree)

    prg = compile(tree, EASY_SUBJECT_PATH, mode="exec")
    #eval(prg)

    resetTracking()


def test_AstVisitor():

    resetTracking()
    assert len(getAssignments().keys()) == 0

    tree = getTree(EASY_SUBJECT_PATH)
    AstVisitor().visit(tree)

    assert len(getAssignments().keys()) == 1

    resetTracking()