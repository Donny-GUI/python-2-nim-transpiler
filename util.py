import ast 
import re 
from string import ascii_letters, digits
import os
import shutil 


WordCharacters = ascii_letters + digits

def replicate_directory_structure(source_dir='.', target_dir='project_nim'):
    # Get the absolute paths of source and target directories
    source_dir = os.path.abspath(source_dir)
    target_dir = os.path.abspath(target_dir)

    # Create the target directory if it doesn't exist
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # Walk through the source directory and replicate the structure
    for root, dirs, files in os.walk(source_dir):
        # Create corresponding directories in the target directory
        relative_path = os.path.relpath(root, source_dir)
        target_root = os.path.join(target_dir, relative_path)
        if not os.path.exists(target_root):
            os.makedirs(target_root)

        # Copy files to the target directory
        for file in files:
            source_path = os.path.join(root, file)
            target_path = os.path.join(target_root, file)
            shutil.copy2(source_path, target_path)
    return target_dir

def get_module_filepath(module_name: str):
    try:
        module = __import__(module_name)
        filepath = getattr(module, "__file__", None)

        if filepath:
            # Convert to absolute path
            filepath = os.path.abspath(filepath)
            return filepath
        else:
            return f"Module '{module_name}' is not associated with a file."
    except ImportError as e:
        return f"Error: {e}"

def python_hint_to_nim(python_hint: str):
    if python_hint == 'int':
        return "int"
    elif python_hint == 'str':
        return "string"
    elif python_hint == 'float':
        return "float"
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
    
def snake_to_camel(snake_case):
    return re.sub(r'_([a-z])', lambda match: match.group(1).upper(), snake_case)

def determine_call_type(node: ast.Call):
    if isinstance(node.func, ast.Name):
        return "function"
    elif isinstance(node.func, ast.Attribute):
        return "method"

def find_function_end(signature_str:str):
    open_parentheses = 0
    in_quotes = False
    for i, char in enumerate(signature_str):
        if char == '(' and not in_quotes:
            open_parentheses += 1
        elif char == ')' and not in_quotes:
            open_parentheses -= 1
        elif char == '"':
            in_quotes = not in_quotes
        elif char == ':' and open_parentheses == 0 and not in_quotes:
            return i + 1  # Return the index after the colon, indicating the end of the function definition
    return -1  # Return -1 if the end is not found

def extract_signature(node: ast.FunctionDef):
    string = ast.unparse(node)
    end = find_function_end(string)
    return string[:end]

def find_substring_end(original_string, substring):
    start_index = original_string.find(substring)

    if start_index != -1:
        end_index = start_index + len(substring)
        return end_index
    else:
        return -1

def extract_list_items(input_string):
    try:
        # Safely parse the input string as an abstract syntax tree (AST)
        tree = ast.parse(input_string, mode='eval')

        # Extract the items from the AST
        items = ast.literal_eval(tree.body)

        # Convert all items to strings
        items_as_strings = [str(item) for item in items]

        return items_as_strings

    except (SyntaxError, ValueError) as e:
        print(f"Error parsing the input string: {e}")
        return None

def extract_variable_types(list_string):
    pattern = re.compile(r'\b(\w+)\s*:\s*([\w\[\],]+)')
    matches = pattern.findall(list_string)

    variable_types = {}

    for match in matches:
        variable_name, variable_type = match
        variable_types[variable_name] = variable_type

    return variable_types


def python_value_to_nim(value):
    if isinstance(value, ast.Num):
        return value.n
    elif isinstance(value, ast.Str):
        return f'"{value.s}"'
    elif isinstance(value, ast.List):
        elements = ', '.join(python_value_to_nim(elt) for elt in value.elts)
        return f'@[{elements}]'
    elif isinstance(value, ast.Tuple):
        elements = ', '.join(python_value_to_nim(elt) for elt in value.elts)
        return f'({elements})'
    elif isinstance(value, ast.Name):
        return value.id
    else:
        # Handle more cases based on your specific needs
        return value
   
def translate_expr(expr):
    if isinstance(expr, ast.Name):
        return expr.id
    elif isinstance(expr, ast.Num):
        return str(expr.n)

def convert_assign_to_nim(node: ast.Assign, parent: ast.AST= None) -> tuple[str, str]:
    targets = []
    name = ""
    if parent is not None:
        name = parent.name

    for x in node.targets:
        target = ast.unparse(x)
        print("[TARGET]: " + target)
        if target.startswith("self."):
            target = "obj" + "." + target.split(".")[1]
            targets.append(target)
        elif not target.startswith("self."):
            target = "var " + target
            targets.insert(0, target)
    
    values = python_value_to_nim(node.value)
    if isinstance(values, ast.Call):
        values = ast.unparse(values)

    elif isinstance(values, ast.Attribute):
        
        parts = [values.attr]
        current_node = values.value
        
        while isinstance(current_node, ast.Attribute):
            parts.insert(0, current_node.attr)
            current_node = current_node.value
        
        if isinstance(current_node, ast.Name):
            parts.insert(0, current_node.id)
        
        values = ".".join(parts)
    
    elif isinstance(values, ast.ListComp):
        values = ast.unparse(values)
    
    return targets, values

def get_python_nodes(filename: str) -> list[ast.AST]:
    with open(filename, 'r') as rfile:
        source = rfile.read()
    
    tree = ast.parse(source=source, type_comments=True, feature_version=(3, 12), mode="exec")
    return [node for node in ast.walk(tree)]


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


token_mapping = {
            "if": "if",
            "elif": "elif",
            "else": "else",
            "while": "while",
            "for": "for",
            "in": "in",
            "range": "..",
            "return": "return",
            "break": "break",
            "continue": "continue",
            "pass": "discard",
            "int": "int",
            "float": "float",
            "str": "string",
            "bool": "bool",
            "list": "seq",
            "dict": "Table[string, int]",
            "set": "set",
            "tuple": "tuple",
            "def": "proc",
            "lambda": "proc",
            "class": "type",
            "self": "",
            "+": "+",
            "-": "-",
            "*": "*",
            "/": "/",
            "//": "div",
            "%": "mod",
            "**": "**",
            "=": "=",
            "==": "==",
            "!=": "!=",
            "<": "<",
            ">": ">",
            "<=": "<=",
            ">=": ">=",
            "and": "and",
            "or": "or",
            "not": "not",
            "print": "echo",
            "len": "len",
            "range": "0..",

            # Numeric Functions
            "abs": "abs",
            "max": "max",
            "min": "min",
            "sum": "sum",
            "round": "round",
            "pow": "math.pow",
            "divmod": "divmod",
            # String Functions
            "str": "string",
            "len": "len",
            "ord": "ord",
            "chr": "chr",
            "capitalize": "capitalize",
            "upper": "upcase",
            "lower": "downcase",
            "strip": "strip",
            "split": "split",
            "join": "join",
            "replace": "replace",
            "startswith": "startsWith",
            "endswith": "endsWith",
            # List Functions
            "list": "@[]",
            "range": "..",
            "sorted": "sorted",
            "reversed": "reversed",
            "append": "add",
            "extend": "add",
            "pop": "pop",
            "remove": "delete",
            "index": "find",
            "count": "count",
            "insert": "insert",
            "reverse": "reverse",
            # Dictionary Functions
            "dict": "Table[string, int]",
            "keys": "keys",
            "values": "values",
            "items": "items",
            "get": "getOrDefault",
            "setdefault": "getOrPut",
            "pop": "pop",
            "popitem": "popLast",
            "update": "update",
            "clear": "clear",
            # Set Functions
            "set": "set",
            "add": "add",
            "remove": "delete",
            "discard": "discard",
            "pop": "pop",
            "clear": "clear",
            "union": "union",
            "intersection": "intersection",
            "difference": "difference",
            "symmetric_difference": "symmetricDifference",
            # Conversion Functions
            "int": "parseInt",
            "float": "parseFloat",
            "bool": "bool",
            "str": "string",
            "list": "@[]",
            "tuple": "@[]",
            "set": "set",
            # Miscellaneous Functions
            "print": "echo",
            "input": "readLine",
            "len": "len",
            "enumerate": "enumerate",
            "zip": "zip",
            "any": "any",
            "all": "all",
            "range": "..",
            "__init__": " initialize", 
            "None": "nil",
            "\t": "  ",
            "    " : "  "
}
