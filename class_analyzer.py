import ast
from initializer_analyzer import InitializerAnalyzer
from method_analyzer import MethodAnalyzer
from typing import Optional, List, Dict, Union


class ClassAnalyzer(ast.NodeVisitor):
    """
    Analyzes a Python class and extracts information about its properties and methods.

    Attributes:
    - node (Optional[ast.ClassDef]): The AST node representing the class.
    - name (Optional[str]): The name of the class.
    - arguments (List[str]): The list of arguments used in the class.
    - class_properties (List[str]): The list of class properties.
    - method_names (List[str]): The list of method names.
    - methods (List[Dict]): The list of methods with their details.
    - dunder_methods (Dict[str, Dict]): The dictionary of dunder methods with their details.
    - initializer_method (Dict): Details of the initializer method if present.
    """
    def __init__(self, node: Optional[ast.ClassDef] = None):
        """
        Initialize ClassAnalyzer.

        Parameters:
        - node (Optional[ast.ClassDef]): The AST node representing the class.
        """
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
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """
        Visit the ClassDef AST node to extract information about the class.

        Parameters:
        - node (ast.ClassDef): The AST node representing the class.
        """
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
    
    def data(self) -> Dict[str, Union[str, List[str], List[Dict], Dict, Dict[str, Dict]]]:
        """
        Get the analyzed data of the class.

        Returns:
        - Dict[str, Union[str, List[str], List[Dict], Dict, Dict[str, Dict]]]: The analyzed data of the class.
        """
        return {
            "name": self.name,
            "properties": self.class_properties,
            "methods": self.methods,
            "arguments": self.arguments,
            "initializer": self.initializer_method,
            "dunders": self.dunder_methods
        }