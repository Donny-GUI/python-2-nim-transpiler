import ast
from util import extract_list_items



def python_hint_to_nim(python_hint):
    if python_hint == 'int':
        return "int"
    elif python_hint == 'str':
        return "string"
    elif python_hint == 'float':
        return "float"
    elif python_hint == 'bool':
        return "bool"
    elif python_hint == None:
        return "nil"
    elif python_hint.startswith('List[') and python_hint.endswith(']'):
        inner_type = python_hint[5:-1]
        nim_inner_type = python_hint_to_nim(inner_type)
        return f"seq[{nim_inner_type}]"
    elif python_hint.startswith('Dict[') and python_hint.endswith(']'):
        inner_types = python_hint[5:-1].split(', ')
        nim_key_type = python_hint_to_nim(inner_types[0])
        nim_value_type = python_hint_to_nim(inner_types[1])
        return f"Table[{nim_key_type}, {nim_value_type}]"
    else:
        # For other cases, return as is (may need to handle more cases)
        return python_hint
    
def get_param_info(node: ast.FunctionDef):
    params = []
    defaults = [ast.unparse(node) for node in node.args.defaults]
    defaults_length = len(defaults)
    argslength = len(node.args.args)
    diff = argslength - defaults_length
    using_defaults = []
    for i in range(0, diff):
        using_defaults.append("$NONE")
    
    for item in defaults:
        using_defaults.append(item)
    
    rd = iter(using_defaults)
    
    for param in node.args.args:

        deef = next(rd)
        if deef == "$NONE":deef = None
        param_info = {'name': param.arg, 'type': None, 'default': deef}

        if param.annotation:
            # Get the type hint using ast.unparse
            param_info['type'] = ast.unparse(param.annotation)

        params.append(param_info)
    
    return params

def python_default_to_nim(python_default):
    
    if python_default == 'None':
        return 'nil'
    elif python_default == 'True':
        return 'true'
    elif python_default == 'False':
        return 'false'
    elif python_default == None:
        return "nil"
    elif python_default.isdigit() or (python_default[0] == '-' and python_default[1:].isdigit()):
        # Numeric values
        return python_default
    elif python_default.startswith('"') and python_default.endswith('"'):
        # String values
        return python_default
    elif python_default.startswith('[') and python_default.endswith(']'):
        listitems = extract_list_items(python_default)
        nimitems = [python_default_to_nim(x) for x in listitems]
        return f"[{", ".join(nimitems)}]"
        
    elif python_default.startswith('(') and python_default.endswith(')'):
        listitems = extract_list_items(python_default)
        nimitems = [python_default_to_nim(x) for x in listitems]
        return f"({", ".join(nimitems)})"
    
    else:
        # For other cases, return as is (may need to handle more cases)
        return python_default
    

class ArgumentConverter(object):
    def __init__(self) -> None:
        self.parameters = []
    
    def convert_arguments(self, node: ast.FunctionDef):
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