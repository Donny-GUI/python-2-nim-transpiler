import ast

token_mapping = {
            "if ": "if ",
            "elif ": "elif ",
            "else ": "else ",
            "while": "while",
            "for ": "for ",
            " in ": " in ",
            "range": "..",
            "return": "return",
            "break": "break",
            "continue": "continue",
            "pass": "discard",
            "int": "int",
            "float": "float",
            "bool": "bool",
            "list[": "seq[",
            "dict": "Table[string, int]",
            "tuple(": "tuple(",
            "def ": "proc ",
            "lambda": "proc",
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
            "len(": "len(",
            "range(0, ": "0..",
            "self.": "obj.",
            " = {}": " = new Table",
            "dict[str:": "Table[string,",

            # Numeric Functions
            "abs": "abs",
            "max": "max",
            "min": "min",
            "sum": "sum",
            "round": "round",
            "pow": "math.pow",
            "divmod": "divmod",
            # String Functions
            "[str]": "[string]",
            "ord(": "ord(",
            "chr(": "chr(",
            ".capitalize": ".capitalize",
            ".upper": ".upcase",
            ".lower": ".downcase",
            ".strip": ".strip",
            ".split": ".split",
            ".join(": ".join(",
            ".replace(": ".replace(",
            "startswith(": "startsWith(",
            "endswith(": "endsWith(",
            # List Functions
            "list": "@[]",
            "range": "..",
            ".sorted(": ".sorted(",
            "reversed(": "reversed(",
            ".append": ".add",
            ".extend": ".add",
            ".pop(": ".pop(",
            ".remove(": ".delete(",
            ".index(": ".find(",
            ".count(": ".count(",
            ".insert(": ".insert(",
            "reverse": "reverse",
            # Dictionary Functions
            "dict": "Table[string, int]",
            ".keys(": ".keys(",
            ".values(": ".values(",
            ".items(": ".items(",
            ".get()": ".getOrDefault()",
            ".setdefault(": ".getOrPut(",
            ".popitem(": ".popLast(",
            ".update(": ".update(",
            ".clear(": ".clear(",
            # Set Functions
            ".set": ".set",
            ".add": ".add",
            "remove": "delete",
            "discard": "discard",
            ".pop": ".pop",
            "clear": "clear",
            "union": "union",
            "intersection": "intersection",
            "difference": "difference",
            "symmetric_difference": "symmetricDifference",
            # Conversion Functions
            " int(": " parseInt(",
            " float(": " parseFloat(",
            "bool": "bool",
            " str(": " string(",
            " list(": "@[]",
            " tuple(": "@[]",
            " = []\n": " = @[]\n",
            # Miscellaneous Functions
            " print(": " echo(",
            "\tprint(": "  echo(",
            " input(": " readLine(",
            "enumerate": "enumerate",
            "zip": "zip",
            "any": "any",
            "all(": "all(",
            "range": "..",
            "None": "nil",
            "    " : "  ",
            "['" : '["',
            "']": '"]', 
            "'": '"',
            "f'":'fmt"',
            'f"':'fmt"',
            ".lower()": ".toLowerAscii()",
            '" + "': '" & "',
            '"[-':'"[^',
            ".dedent(": ".unindent(",
            "bool(": "parseBool(",
            


}




def convert_string_to_nim(string: str):
    new_string = string
    for name, value in token_mapping.items():
        new_string = new_string.replace(name, value)
    return new_string


class KeywordConverter:

    def convert_keyword(node: ast.keyword):
        string = ast.unparse(node.value)
        try:
            return token_mapping[string]
        except NameError:
            return string
        


