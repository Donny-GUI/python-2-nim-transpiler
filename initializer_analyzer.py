import ast
from method_analyzer import MethodAnalyzer
from value_analyzer import ValueAnalyzer
from typing import Optional, List, Dict


class InitializerAnalyzer(MethodAnalyzer):
    """
    Analyzes an initializer method (__init__) in a Python class.

    Attributes:
    - class_properties (List[Tuple[str, Optional[str], ast.AST, ast.ctx]]): List of class properties.
    - body (List[str]): List of unparsed AST nodes in the method body.
    """
    def __init__(self, node: Optional[ast.FunctionDef] = None):
        """
        Initialize InitializerAnalyzer.

        Parameters:
        - node (Optional[ast.FunctionDef]): The AST node representing the initializer method.
        """
        self.class_properties = []
        self.body = []
        super().__init__(node)
        if node is not None:
            for prop in node.body:
                
                if isinstance(prop, ast.Attribute) and isinstance(prop.value, ast.Name) and prop.value.id == node.name:
                    self.class_properties.append((prop.attr, prop.type_comment, prop.value, prop.ctx))
                
                self.body.append(ast.unparse(prop))

    def evaluate_assign_type(self, node: ast.Assign) -> str:
        """
        Evaluate the type of the assigned value in an assignment node.

        Parameters:
        - node (ast.Assign): The AST node representing an assignment.

        Returns:
        - str: The type of the assigned value.
        """
        va = ValueAnalyzer(node.value)
        return va.type

    def search_properties(self, bodynode: ast.AST) -> None:
        """
        Search for class properties within the AST nodes of the method body.

        Parameters:
        - bodynode (ast.AST): The AST node to search for class properties.
        """
        targets = []
        values: dict[str:list] = {}
        types: dict[str:list] = {}
    
        if isinstance(bodynode, ast.Assign):
            ts = bodynode.targets

            props = {}
            for t in ts:
                if isinstance(t, ast.Attribute):
                    if isinstance(t.value, ast.Name) and t.value.id == "self":
                        value = ast.unparse(bodynode.value)
                        type = self.evaluate_assign_type(bodynode)
                        isin = False
                        for item in targets:
                            if item == t.attr:
                                values[t.attr].append(value)
                                types[t.attr].append(type)
                                isin = True
                                break
                        if isin == False:
                            targets.append(t.attr)
                            values[t.attr] = [value, ]
                            types[t.attr] = [type, ]

            targets = list(set(targets))
            for target in targets:
                props["name"] = target
                v = values[target]
                t = types[target]
                vv = "None"
                tt = "None"
                for index, xx in enumerate(v):
                    if xx != "None":
                        vv = xx
                        tt = t[index]
            
                props["value"] = vv
                props["type"] = tt
                self.class_properties.append(props)
        
        for child in ast.iter_child_nodes(bodynode):
            self.search_properties(child)

    def visit_MethodDef(self, node: ast.FunctionDef) -> None:
        """
        Visit the MethodDef AST node to extract information about the method.

        Parameters:
        - node (ast.FunctionDef): The AST node representing the method.
        """
        super().visit_MethodDef(node)

        for prop in node.body:
            self.search_properties(prop)
            self.body.append(ast.unparse(prop))
    
    def data(self) -> dict:
        """
        Get the analyzed data of the initializer method.

        Returns:
        - Dict: The analyzed data of the initializer method.
        """
        return {"name": self.name,
                "arguments": self.arguments,
                "properties": self.class_properties,
                'returns': self.returns, 
                'argument_types': self.argument_types, 
                'default_arguments': self.default_arguments,
                'body': self.body
                }