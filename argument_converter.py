import ast
from util import python_hint_to_nim, get_param_info, python_default_to_nim


class ArgumentConverter(object):
    def __init__(self) -> None:
        """Initialize ArgumentConverter."""
        self.parameters = []
    
    def convert_arguments(self, node: ast.FunctionDef) -> str:
        """
        Convert function arguments from Python to Nim syntax.

        Parameters:
        - node (ast.FunctionDef): The AST node representing the function.

        Returns:
        - str: Nim syntax representation of the function arguments.
        """
        string = ""
        self.parameters = get_param_info(node)
        
        for index, param in enumerate(self.parameters):
            if param["name"] == "self":
                continue

            name = param["name"]
            string+=name
            
            type = python_hint_to_nim(param["type"])
            string+=": " + type

            default = python_default_to_nim(param["default"])
            string+=" = " + default
            
            string +=", "

        return string[:-2]