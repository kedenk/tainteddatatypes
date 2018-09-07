import ast
from typing import Dict
from astrewrite.nodeprocessors import NameProcessor, AttributeProcessor, CallProcessor, NodeProcessor

nodeProcessors = {
    "Name":         NameProcessor("Name"),
    "Call":         CallProcessor("Call"),
    "Attribute":    AttributeProcessor("Attribute")
}


class DictLookupTransformer(ast.NodeTransformer):

    def __init__(self, nodeProcessor: Dict[str, NodeProcessor]):
        self.handler = nodeProcessor
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
        while not isinstance(result, str):
            processor = self.getHandlerFunc(result)
            result, ctx = processor.process(result)

        return result, ctx

    def visit_Compare(self, node):
        """"
            node has following attributs: left, ops, comparators

            Method should transform:
            'i in dict.keys()' => 'i.in_(dict.keys())'
        """

        if len(node.ops) > 0 and isinstance(node.ops[0], ast.In):

            # get caller and callee
            caller, callerCtx = self.__getExpr(node.left)
            callee, calleeCtx = self.__getExpr(node.comparators[0])

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
