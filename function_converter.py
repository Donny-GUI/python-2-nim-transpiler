import ast
from argument_converter import ArgumentConverter
from util import snake_to_camel
from typer import TypeConverter
from keyword_converter import convert_string_to_nim


#class FunctionDef(stmt):
#    if sys.version_info >= (3, 12):
#        __match_args__ = ("name", "args", "body", "decorator_list", "returns", "type_comment", "type_params")
#    elif sys.version_info >= (3, 10):
#        __match_args__ = ("name", "args", "body", "decorator_list", "returns", "type_comment")
#    name: _Identifier
#    args: arguments
#    body: list[stmt]
#    decorator_list: list[expr]
#    returns: expr | None
#    if sys.version_info >= (3, 12):
#        type_params: list[type_param]

class FunctionConverter(object):
    def __init__(self) -> None:
        self.names = []
        self.signatures = {}
        self.bodies = {}
        self.sources = {}
    
    def convert_function_signature(self, function_definition: ast.FunctionDef):
        string = "proc "
        string += snake_to_camel(function_definition.name) + "("
        arg_converter = ArgumentConverter()
        string += arg_converter.convert_arguments(function_definition)
        string += "): "

        try:
            returns = TypeConverter.convert_typehint_to_nim(ast.unparse(function_definition.returns))
        except AttributeError:
            returns = "nil"

        string += returns + " = "
        
        return string
    
    def convert_function_body(self, function_definition: ast.FunctionDef):
        nimstring = convert_string_to_nim(ast.unparse(function_definition.body))
        splitlines = ["  " + x for x in nimstring.split("\n")]
        return "\n".join(splitlines)

    def add_function(self, function_definition: ast.FunctionDef):
        name = snake_to_camel(function_definition.name)
        self.names.append(name)
        self.signatures[name] = self.convert_function_signature(function_definition)
        self.bodies[name] = self.convert_function_body(function_definition)

    def assemble(self):
        return_string = "\n\n##########################################\n#  Functions  \n##########################################\n"
        for name in self.names:
            return_string += "\n"
            return_string += self.signatures[name] + "\n"
            return_string += self.bodies[name] + "\n"
        return return_string

def convert_all_functions(filepath: str):

    with open(filepath, 'r') as f:
        content=f.read()

    tree = ast.parse(content)
    funcdefs = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            pass
        else:
            for subnode in ast.walk(node):
                if isinstance(subnode, ast.FunctionDef):
                    funcdefs.append(subnode)
    
    fn_converter = FunctionConverter()
    for n in funcdefs:
        fn_converter.add_function(n)
    
    return fn_converter
    
    
