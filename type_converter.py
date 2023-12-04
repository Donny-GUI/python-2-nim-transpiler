import ast
from typing import Type, Union, Optional


class TypeConverter:

    def convert_typehint_to_nim(string):
        pytypes = ["str", "int", "float", "complex", "bytes", "list", "dict", "set", "bytearray"]
        nimtypes = ["string", "int", "float", "complex", "byte", "seq", "Table","set", "seq[byte]"]
        newstring:str = string
        for index, type in enumerate(pytypes):
            newstring = newstring.replace(type, nimtypes[index])
        return newstring

    def convert_type_by_string_name(string: str):
        match string:
            case 'str':
                return "string"
            case 'bytes':
                return "bytes"
            case 'bool':
                return "bool"
            case 'int':
                return "int"
            case 'float':
                return "float"
            case 'list':
                return "seq"
            case 'dict':
                return "Table"
            case 'set':
                return "set"
            case 'None':
                return "nil"
            case other:
                return "auto"      

    def convert_collection(node: ast.AST) -> str:
        """
        Convert an AST node representing a Python collection type to a corresponding Nim type.

        Args:
            node (ast.AST): The AST node representing a Python collection type.

        Returns:
            str: The corresponding Nim type for the given Python collection type.
        """
        if isinstance(node, ast.List):
            element_type = TypeConverter.convert_collection(node.elts[0]) if node.elts else "auto"
            return f"seq[{element_type}]"
        elif isinstance(node, ast.Tuple):
            element_types = [TypeConverter.convert_collection(elt) for elt in node.elts]
            return f"tuple[{', '.join(element_types)}]"
        elif isinstance(node, ast.Dict):
            key_type = TypeConverter.convert_collection(node.keys[0]) if node.keys else "auto"
            value_type = TypeConverter.convert_collection(node.values[0]) if node.values else "auto"
            return f"Table[{key_type}, {value_type}]"
        elif isinstance(node, ast.Set):
            element_type = TypeConverter.convert_collection(node.elts[0]) if node.elts else "auto"
            return f"set[{element_type}]"
        else:
            raise ValueError("Unsupported collection type")
    
    def convert_number_node(self, node: ast.Num) -> str:
        value_str = ast.unparse(node.value)
        try:
            value = float(value_str)
            if value.is_integer():
                return "float"  # Assume a general float if it's an integer
            elif -3.4028235e38 <= value <= 3.4028235e38:
                return "float32"
            elif -1.7976931348623157e308 <= value <= 1.7976931348623157e308:
                return "float64"
            elif -1.189731495357231765e4932 <= value <= 1.189731495357231765e4932:
                return "float128"
            else:
                return "Unknown float type"
        except ValueError:
            try:
                value = int(value_str)
                if -128 <= value <= 127:
                    return "int8"
                elif -32768 <= value <= 32767:
                    return "int16"
                elif -2147483648 <= value <= 2147483647:
                    return "int32"
                elif -9223372036854775808 <= value <= 9223372036854775807:
                    return "int64"
                elif 0 <= value <= 255:
                    return "uint8"
                elif 0 <= value <= 65535:
                    return "uint16"
                elif 0 <= value <= 4294967295:
                    return "uint32"
                elif 0 <= value <= 18446744073709551615:
                    return "uint64"
                else:
                    return "Unknown integer type"
            except ValueError:
                return "Invalid integer format"
    

def get_python_type(node: ast.AST) -> Optional[Type[Union[int, float, str, bool, list, tuple, dict, set]]]:
    """
    Determine the Python data type of an AST node.

    Args:
        node (ast.AST): The AST node to analyze.

    Returns:
        Type[Union[int, float, str, bool, list, tuple, dict, set]]: The corresponding Python data type,
            or None if the type couldn't be determined.
    """
    if isinstance(node, ast.Num):
        return int if isinstance(node.n, int) else float
    elif isinstance(node, ast.Str):
        return str
    elif isinstance(node, ast.NameConstant):
        return bool if node.value in {True, False, None} else None
    elif isinstance(node, ast.List):
        return list
    elif isinstance(node, ast.Tuple):
        return tuple
    elif isinstance(node, ast.Dict):
        return dict
    elif isinstance(node, ast.Set):
        return set
    else:
        return None