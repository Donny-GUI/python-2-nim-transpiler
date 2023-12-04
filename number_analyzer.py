import ast


class NumberAnalyzer(ast.NodeVisitor):
    def __init__(self, node: ast.Num = None) -> None:
        super().__init__()
        if node is None: 
            self.node = None
        else:
            string = ast.unparse(node.value)
            integer = int(string)
            if "." in string:
                self.type = determine_nim_float_type(integer)
            else:
                self.type = determine_nim_integer_type(integer)

def determine_nim_float_type(value_str):
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
        return "Invalid float format"          

def determine_nim_integer_type(value_str):
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
    