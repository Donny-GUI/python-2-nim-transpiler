import ast



class MethodAnalyzer(ast.NodeVisitor):
    def __init__(self, node: ast.FunctionDef=None):
        super().__init__()
        if node is None:
            self.name = None
            self.arguments = None
            self.returns = None
            self.argument_types = None
            self.default_arguments = None
        else:
            self.visit_MethodDef(node)

    def data(self):
        return {
            'name': self.name, 
            'arguments': self.arguments, 
            'returns': self.returns, 
            'argument_types': self.argument_types, 
            'default_arguments': self.default_arguments,
            'body': self.body
            }

    def visit_MethodDef(self, node: ast.FunctionDef):
        self.name = node.name
        self.arguments = node.args.args
        self.argument_types = [arg.type_comment for arg in self.arguments]
        self.returns = node.returns
        self.body = [ast.unparse(n) for n in node.body]
        self.default_arguments = [arg for arg in node.args.defaults]
