import ast
from typing import Dict
from astrewrite.nodeprocessors import NameProcessor, AttributeProcessor, CallProcessor, NodeProcessor, NumProcessor

nodeProcessors = {
    "Name":         NameProcessor("Name"),
    "Call":         CallProcessor("Call"),
    "Attribute":    AttributeProcessor("Attribute"),
    "Num":          NumProcessor("Num")
}


vars = []
ASSIGNMENTS = {}

def resetTracking():
    global vars
    global ASSIGNMENTS
    vars = []
    ASSIGNMENTS = {}
    assert len(ASSIGNMENTS.keys()) == 0

def getAssignments():
    return ASSIGNMENTS


class DictLookupTransformer(ast.NodeTransformer):

    def __init__(self, nodeProcessor: Dict[str, NodeProcessor], assignments):
        self.handler = nodeProcessor
        self.assignments = assignments

        self.IN_KEYWORD = 'in_'

    def getHandlerFunc(self, node: ast.AST) -> NodeProcessor:

        name = self.__getNodeName(node)
        if name in self.handler:
            return self.handler[name]
        else:
            raise Exception("Not supported node type " + repr(name))

    def __getNodeName(self, node: ast.AST) -> str:
        return node.__class__.__name__

    def __getExpr(self, node: ast.AST) -> (str, str):

        result = node
        ctx = None
        nodeType = None
        while not isinstance(result, str) and not isinstance(result, int):
            processor = self.getHandlerFunc(result)
            result, ctx, nodeType = processor.process(result)

        if ctx == None:
            ctx = ast.Load()
        return str(result), ctx, nodeType

    def visit_Compare(self, node):
        """"
            node has following attributs: left, ops, comparators

            Method should transform:
            'i in dict.keys()' => 'i.in_(dict.keys())'
        """

        if len(node.ops) > 0 and isinstance(node.ops[0], ast.In):

            # get caller and callee
            caller, callerCtx, callerNodeType = self.__getExpr(node.left)
            if caller in self.assignments or isinstance(callerNodeType, ast.Num):
                caller = 'tint(' + caller + ')'
            else:
                return node

            callee, calleeCtx, calleeNodeType = self.__getExpr(node.comparators[0])
            callee = callee + '.keys()'

            # define attributes of call object
            attr = ast.Attribute(
                value=ast.Name(
                    id=caller,
                    ctx=callerCtx),
                attr=self.IN_KEYWORD,
                ctx=calleeCtx)

            # define Call object
            # v.in_(dict.keys())
            call = ast.Call()
            call.func = attr
            call.args = [ast.Name(id=callee, ctx=calleeCtx)]
            call.keywords = []

            return call

        else:
            return node


class AstVisitor(ast.NodeVisitor):

    def visit_Num(self, node):
        vars.append(node.n)

    def visit_Assign(self, node):

        if isinstance(node.value, ast.Num):
            identifier = node.targets[0].id
            ASSIGNMENTS[identifier] = (identifier, node.targets[0].ctx)
