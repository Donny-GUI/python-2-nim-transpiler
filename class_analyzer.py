import ast
from initializer_analyzer import InitializerAnalyzer
from method_analyzer import MethodAnalyzer


class ClassAnalyzer(ast.NodeVisitor):
    def __init__(self, node: ast.ClassDef=None):
        super().__init__()
        self.node = node
        self.arguments = []
        self.class_properties = []
        self.method_names = []
        self.methods: list[dict] = []
        self.dunder_methods: dict[str:dict] = {}
        self.initializer_method: dict = {}
        if node is None:
            self.name= None
            self.initializer_method = None
        else:
            self.name = node.name
            for item in node.body:

                if isinstance(item, ast.FunctionDef) and item.name.startswith("__init") and item.name.endswith("__"):
                    analyzer = InitializerAnalyzer(item)
                    self.initializer_method = analyzer.data()
                    self.method_names.append(analyzer.name)
                elif isinstance(item, ast.FunctionDef) and item.name.startswith("__") and item.name.endswith("__"):
                    analyzer = MethodAnalyzer(item)
                    self.dunder_methods[analyzer.name] = analyzer.data()
                    self.method_names.append(analyzer.name)
                elif isinstance(item, ast.FunctionDef) and not item.name.startswith("__") and not item.name.endswith("__"):
                    analyzer = MethodAnalyzer(item)
                    self.methods.append(analyzer.data())
                    self.method_names.append(analyzer.name)
    
    def visit_ClassDef(self, node: ast.ClassDef):
        self.name = node.name
        for item in node.body:

            if isinstance(item, ast.FunctionDef) and item.name.startswith("__init") and item.name.endswith("__"):
                analyzer = InitializerAnalyzer(item)
                self.initializer_method = analyzer.data()
            elif isinstance(item, ast.FunctionDef) and item.name.startswith("__") and item.name.endswith("__"):
                analyzer = MethodAnalyzer(item)
                self.dunder_methods[analyzer.name] = analyzer.data()
            elif isinstance(item, ast.FunctionDef) and not item.name.startswith("__") and not item.name.endswith("__"):
                analyzer = MethodAnalyzer(item)
                self.methods.append(analyzer.data())
            
            self.method_names.append(analyzer.name)
    
    def data(self):
        return {
            "name": self.name,
            "properties": self.class_properties,
            "methods": self.methods,
            "arguments": self.arguments,
            "initializer": self.initializer_method,
            "dunders": self.dunder_methods
        }