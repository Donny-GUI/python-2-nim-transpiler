import ast
from typing import Optional, List, Dict, Union


class MethodAnalyzer(ast.NodeVisitor):
    """
    Analyzes a Python method/function definition.

    Attributes:
    - name (Optional[str]): The name of the method.
    - arguments (Optional[List[ast.arg]]): List of arguments in the method.
    - returns (Optional[ast.AST]): The return type of the method.
    - argument_types (Optional[List[Union[str, None]]]): List of type comments for arguments.
    - default_arguments (Optional[List[ast.AST]]): List of default values for arguments.
    - body (Optional[List[str]]): List of unparsed AST nodes in the method body.
    """
    def __init__(self, node: ast.FunctionDef=None):
        super().__init__()
        if node is None:
            self.name: Optional[str] = None
            self.arguments: Optional[List[ast.arg]] = None
            self.returns: Optional[ast.AST] = None
            self.argument_types: Optional[List[Union[str, None]]] = None
            self.default_arguments: Optional[List[ast.AST]] = None
            self.body: Optional[List[str]] = None
        else:
            self.visit_MethodDef(node)


    def data(self) -> Dict:
        """
        Get the analyzed data of the method.

        Returns:
        - Dict: The analyzed data of the method.
        """
        return {
            'name': self.name, 
            'arguments': self.arguments, 
            'returns': self.returns, 
            'argument_types': self.argument_types, 
            'default_arguments': self.default_arguments,
            'body': self.body
            }

    def visit_MethodDef(self, node: ast.FunctionDef):
        """
        Visit the MethodDef AST node to extract information about the method.

        Parameters:
        - node (ast.FunctionDef): The AST node representing the method.
        """
        self.name = node.name
        self.arguments = node.args.args
        self.argument_types = [arg.type_comment for arg in self.arguments]
        self.returns = node.returns
        self.body = [ast.unparse(n) for n in node.body]
        self.default_arguments = [arg for arg in node.args.defaults]
