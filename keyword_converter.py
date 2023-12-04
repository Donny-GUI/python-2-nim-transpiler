import ast
from stringmap import MasterKeyMap


def convert_string_to_nim(string: str) -> str:
    new_string = string
    for name, value in MasterKeyMap.items():
        new_string = new_string.replace(name, value)
    return new_string

class KeywordConverter:

    def convert_keyword(node: ast.keyword) -> str:
        string = ast.unparse(node.value)
        try:
            return MasterKeyMap[string]
        except NameError:
            return string
