import ast 
from argument_converter import ArgumentConverter
from util import snake_to_camel
from type_converter import TypeConverter
from keyword_converter import convert_string_to_nim
from typing import Optional


class MethodConverter(object):
    """
    Converts Python method/function definitions to Nim syntax.

    Attributes:
    - variables (list[str]): List of variable names in the method.
    - types (list[str]): List of variable types in the method.
    - parent (str): The name of the parent class.
    - node (Optional[ast.AST]): The AST node representing the method.
    - string (str): Nim code representation of the method.
    """
    def __init__(self) -> None:
        self.variables = []
        self.types = []
        self.parent:str = ""
        self.node = ast.AST
        self.string = "func  "
    
    def convert_initializer_signature(self, method: ast.FunctionDef, parent: ast.ClassDef) -> str:
        """
        Convert the initializer method signature to Nim syntax.

        Parameters:
        - method (ast.FunctionDef): The AST node representing the initializer method.
        - parent (ast.ClassDef): The AST node representing the parent class.

        Returns:
        - str: Nim syntax representation of the initializer method signature.
        """
        self.string = "func "
        self.parent = parent.name
        self.node = method
        self.returns = str(self.node.returns)
        self.variables = [name.id for name in self.node.body if isinstance(name, ast.Name)]
        
        self.attributes = [attr for attr in self.node.body if isinstance(attr, ast.Attribute)]
        self.attribute_names = [attr.attr for attr in self.attributes if isinstance(attr, ast.Name)]
        self.attribute_values = [name.value for name in self.attributes]
        
        self.string+="init"+ self.parent + f"(obj: var {self.parent}"
        
        arg_converter = ArgumentConverter()
        self.nim_args = arg_converter.convert_arguments(self.node)
        
        if self.nim_args != "":
            self.string += ", "
        
        self.string+=self.nim_args
        self.string += f"): {self.parent} = "
        
        return self.string

    def convert_method_signature(self, method: ast.FunctionDef, parent_class: ast.ClassDef) -> str:
        """
        Convert the method signature to Nim syntax.

        Parameters:
        - method (ast.FunctionDef): The AST node representing the method.
        - parent_class (ast.ClassDef): The AST node representing the parent class.

        Returns:
        - str: Nim syntax representation of the method signature.
        """
        # def name(args:type=default) -> returns: ==> proc nameFunc(obj: var ClassName, args:type=default): returns =
        self.string = "func "
        self.parent = parent_class.name
        self.node = method
        #evaluate_return_object(self.node.returns)
        try:
            self.returns = TypeConverter.convert_typehint_to_nim(ast.unparse(self.node.returns))
        except AttributeError:
            self.returns = "nil"

        self.variables = [name.id for name in self.node.body if isinstance(name, ast.Name)]
        
        self.attributes = [attr for attr in self.node.body if isinstance(attr, ast.Attribute)]
        self.attribute_names = [attr.attr for attr in self.attributes if isinstance(attr, ast.Name)]
        self.attribute_values = [name.value for name in self.attributes]
        
        self.string+=snake_to_camel(self.node.name) + f"(obj: {self.parent}"
        
        arg_converter = ArgumentConverter()
        self.nim_args = arg_converter.convert_arguments(self.node)
        
        if self.nim_args != "":
            self.string += ", "
        self.string+=self.nim_args
        
        if self.returns != None:
            self.string += f"): {self.returns} = "
        else:
            self.string += ") = "
        
        return self.string
    
    def convert_method_body(self, node: ast.FunctionDef, parent: ast.ClassDef) -> str:
        """
        Convert the method body to Nim syntax.

        Parameters:
        - node (ast.FunctionDef): The AST node representing the method.
        - parent (ast.ClassDef): The AST node representing the parent class.

        Returns:
        - str: Nim syntax representation of the method body.
        """

        nimstring = convert_string_to_nim(ast.unparse(node.body))
        splitlines = ["  " + x for x in nimstring.split("\n")]
        return "\n".join(splitlines)

