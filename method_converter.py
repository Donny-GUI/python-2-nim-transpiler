import ast 
from argument_converter import ArgumentConverter
from util import snake_to_camel, convert_assign_to_nim
from assign_converter import AssignConverter
from typer import TypeConverter
from keyword_converter import convert_string_to_nim


class MethodConverter(object):
    def __init__(self) -> None:
        self.variables = []
        self.types = []
        self.parent:str = ""
        self.node = ast.AST
        self.string = "func  "
    
    def convert_initializer_signature(self, method: ast.FunctionDef, parent: ast.ClassDef):
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

    def convert_method_signature(self, method: ast.FunctionDef, parent_class: ast.ClassDef):
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
    
    def convert_method_body(self, node: ast.FunctionDef, parent: ast.ClassDef):
        
        def count_indent(string):
            co = 0
            for char in string:
                if char != " ":
                    break
                co+=1
            return co

        nimstring = convert_string_to_nim(ast.unparse(node.body))
        splitlines = ["  " + x for x in nimstring.split("\n")]
        return "\n".join(splitlines)


def adjust_indentation(lines):
    result = []
    current_indent = 0
    last_indentation = -1
    indentation = 0
    for line in lines:
        stripped_line = line.lstrip()
        last_indentation = indentation
        indentation = len(line) - len(stripped_line)

        if last_indentation < indentation:
            current_indent = indentation
        

        if stripped_line.startswith(("for ", "while ", "if ", "else ", "elif ", "try ", "except ", "finally ", "with ")):
            result.append(" " * current_indent + stripped_line)
            current_indent += 4  # Assuming 4 spaces per level of indentation
        elif stripped_line.startswith(("continue", "break", "return", "pass")):
            result.append(" " * current_indent + stripped_line)
            current_indent -= 4
            current_indent = abs(current_indent)
        elif current_indent > 0:
            result.append(" " * current_indent + stripped_line)
        else:
            result.append(line)

    return result
 
