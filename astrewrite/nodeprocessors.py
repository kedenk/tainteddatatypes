import ast


class NodeProcessor(object):

    def __init__(self, nodeName: str):
        self.name = nodeName

    def process(self, node: ast.AST):
        raise NotImplementedError()


class CallProcessor(NodeProcessor):

    def __init__(self, nodeName: str):
        super().__init__(nodeName)

    def process(self, node: ast.AST):
        return node.func, None


class NameProcessor(NodeProcessor):

    def __init__(self, nodeName: str):
        super().__init__(nodeName)

    def process(self, node: ast.AST):
        return node.id, node.ctx


class AttributeProcessor(NodeProcessor):

    def __init__(self, nodeName: str):
        super().__init__(nodeName)

    def process(self, node: ast.AST):
        return node.value, node.ctx