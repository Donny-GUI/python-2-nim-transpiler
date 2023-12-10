import sys
import ast
from typing import List, Set, Optional
import json


def get_python_builtin_modules():
    retv = []
    for bt in sys.builtin_module_names:
        if bt.startswith('_codecs_') or bt.startswith('_xx') or bt.startswith("xx"):
            continue
        retv.append(bt.strip("_"))
    return retv

def get_builtin_module_objects(module_name):
    """
    Get the names of all objects defined in a built-in module.

    Args:
        module_name (str): The name of the built-in module.

    Returns:
        List[str]: A list of strings representing object names.
    """
    try:
        # Import the module
        module = __import__(module_name)
        
        # Get the names of all objects in the module
        module_objects = dir(module)
        
        return module_objects
    except ImportError:
        return []

def get_all_module_objects():
    python_modules = get_python_builtin_modules()
    mods = {}
    for pymod in python_modules:
        mods[pymod] = get_builtin_module_objects(pymod)
    return mods

def make_module_map():
    python_modules = get_python_builtin_modules()
    mods = {}
    for pymod in python_modules:
        mods[pymod] = get_builtin_module_objects(pymod)
    with open("module_map.json", "w") as jsonfile:
        json.dump(mods, jsonfile)


def extract_used_functions_and_classes(file_path: str) -> List[str]:
    """
    Extracts all used functions and classes from a Python file.

    Args:
        file_path (str): The path to the Python file to analyze.

    Returns:
        List[str]: A list of strings representing the used functions and classes.
    """
    with open(file_path, 'r') as file:
        code = file.read()

    tree = ast.parse(code)

    used_functions_and_classes: Set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            # This handles cases like `module.function()` or `module.Class()`
            module_name = ""
            if isinstance(node.value, ast.Name):
                module_name = node.value.id
            elif isinstance(node.value, ast.Attribute):
                # Handles cases like `module.submodule.function()`
                module_name = get_full_attribute_name(node.value)
            
            if module_name:
                used_functions_and_classes.add(f"{module_name}.{node.attr}")

        elif isinstance(node, ast.Name):
            # This handles cases like `function()` or `Class()`
            used_functions_and_classes.add(node.id)

    return list(used_functions_and_classes)

def get_full_attribute_name(node: ast.Attribute) -> str:
    """
    Recursively constructs the full attribute name for an ast.Attribute node.

    Args:
        node (ast.Attribute): The ast.Attribute node.

    Returns:
        str: The full attribute name.
    """
    if isinstance(node.value, ast.Name):
        return f"{node.value.id}.{node.attr}"
    elif isinstance(node.value, ast.Attribute):
        return f"{get_full_attribute_name(node.value)}.{node.attr}"


def find_import_from_objects(file_path):
    with open(file_path, 'r') as file:
        code = file.read()

    tree = ast.parse(code)

    imported_objects = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_objects.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module
            for alias in node.names:
                imported_objects.add(f"{module}.{alias.name}")
            
        #elif isinstance(node, ast.Attribute):
        #    if (
        #        isinstance(node.value, ast.Name) and
        #        node.value.id 
        #    )

    return imported_objects

def make_python_module_file():
    return
    # Meta Programming, do not use this
    from util import snake_to_camel

    mod_objects = get_all_module_objects()
    with open("python_module_maps.py", "w") as wfile:
        for name in mod_objects.keys():
            wfile.write(f'python_{name}_map = ' + "{\n")
            namelength = len(name)
            for item in mod_objects[name]:
                itemlength = len(item)
                extra_space = 25 - (namelength+itemlength)
                second_extra_space = extra_space + namelength + 1
                space = extra_space * " "
                second_space = second_extra_space * " "
                wfile.write(f'    "{name}.{item}"{space} : "{name}.{snake_to_camel(item)}",\n')
                wfile.write(f'    "{item}"{second_space} : "{snake_to_camel(item)}",\n')
            wfile.write("}\n")

def tests():
    

