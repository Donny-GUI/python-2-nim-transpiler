import ast
from number_analyzer import NumberAnalyzer



class ValueAnalyzer(ast.NodeVisitor):
    def __init__(self, node: ast.AST=None):
        self.node = node
        self.type = "None"
        if self.node is None:
            self.type = "None"

        if isinstance(self.node, ast.Str):
            self.type = "str"
        elif isinstance(self.node, ast.Num):
            number_analyzer = NumberAnalyzer(self.node)
            self.type = number_analyzer.type
        elif isinstance(self.node, ast.Dict):
            self.type = "dict"
        elif isinstance(self.node, ast.List):
            self.type = "list"
        elif isinstance(self.node, ast.Set):
            self.type = "set"
        elif isinstance(self.node, ast.ListComp):
            self.type = "listcomp"